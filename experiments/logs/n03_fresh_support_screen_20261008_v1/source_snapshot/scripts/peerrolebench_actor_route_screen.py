"""One diagnostic PIPE3 source -> future target route with a persistent producer.

The selected producer is fixed across both tasks. This screens the generation and
recipient handoff, and makes no claim about learning a selection policy.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_actor_experience import ActorExperience, canonical_bytes, digest
from peerrolebench_candidate_registry import CandidateRegistryEntry
from peerrolebench_live_producer_stage import (finalize, model_config_digest, policy_digest,
                                               prepare_request, run_generation)
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, make_offer
from peerrolebench_baseline_policies import NoUpdatePolicy
from peerrolebench_pipe3_task_qualification import load_pipe3
from peerrolebench_pipe3_public_contract_v2 import build_materials
from peerrolebench_c1_pipe3_bounded_live import (
    _run_episode, _selection_binding, save_decision_capture, load_decision_capture,
    FixedIndexRNG, TASK_ID, PUBLIC_ENCODER, PUBLIC_SCHEMA,
)

VERSION = "peerrolebench-actor-route-screen-v1"
SELECTED_KEY = "peer-b@live-v1"


def _save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _cost_receipts(out: Path) -> dict[str, Any]:
    """Count observed attempts and all available receipts, including failures."""
    receipts: list[dict[str, Any]] = []
    attempts = 0
    observed_wall_seconds = 0.0
    observed_input_tokens = 0
    observed_output_tokens = 0
    unknown_paths: list[str] = []
    for raw in sorted(out.rglob("raw.jsonl")):
        for line in raw.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("event_type") == "request_start":
                attempts += 1
    for path in sorted(out.rglob("*_cost.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            receipts.append({"path": str(path.relative_to(out)), "receipt": value})
            wall = value.get("elapsed_seconds")
            if isinstance(wall, (int, float)) and not isinstance(wall, bool) and wall >= 0:
                observed_wall_seconds += float(wall)
            else:
                unknown_paths.append(str(path.relative_to(out)) + ":elapsed_seconds")
            usage = value.get("usage") or {}
            for key in ("input_tokens", "output_tokens"):
                token_value = usage.get(key)
                if isinstance(token_value, int) and not isinstance(token_value, bool) and token_value >= 0:
                    if key == "input_tokens":
                        observed_input_tokens += token_value
                    else:
                        observed_output_tokens += token_value
                else:
                    unknown_paths.append(str(path.relative_to(out)) + ":" + key)
            if value.get("usage_complete") is not True:
                unknown_paths.append(str(path.relative_to(out)) + ":usage_complete")
            if value.get("http_status") != "200" or value.get("exit_code") != 0:
                unknown_paths.append(str(path.relative_to(out)) + ":transport")
            if value.get("stop_reason") != "end_turn":
                unknown_paths.append(str(path.relative_to(out)) + ":completion")
        except (OSError, ValueError) as exc:
            receipts.append({"path": str(path.relative_to(out)), "status": "UNKNOWN",
                             "error": type(exc).__name__})
            unknown_paths.append(str(path.relative_to(out)) + ":unreadable")
    return {"attempted_api_requests": attempts, "receipts": receipts,
            "unreceipted_attempts": max(0, attempts - len(receipts)),
            "observed_wall_seconds": observed_wall_seconds,
            "observed_input_tokens": observed_input_tokens,
            "observed_output_tokens": observed_output_tokens,
            "unknown_fields": unknown_paths,
            "status": "COMPLETE" if attempts == len(receipts) and not unknown_paths else "UNKNOWN"}


def _materials(seed: int) -> dict[str, Any]:
    return deepcopy(build_materials(load_pipe3(seed)))


def _seal(boundary: Pipe3SelectionBoundary, index: int, candidate: CandidateRegistryEntry):
    offer = make_offer(offer_id=f"route-offer-{index}", task_id=TASK_ID,
                       task_index=index, role="producer", context_key=f"PIPE3:{index}",
                       candidate_keys=(candidate.key,), public_rows=(), evidence_version=VERSION,
                       available_index=index)
    return boundary.choose_and_seal(
        offer=offer, native_selection_id=f"selection-route-{index}", selector_id="peer-a",
        role="producer", base_scores=(0.0,), rng=FixedIndexRNG(0),
        state_version=f"route-state-{index}", encoder_version=PUBLIC_ENCODER,
        feature_schema=PUBLIC_SCHEMA, policy_version="no-update-v1",
        base_score_version=VERSION, rng_algorithm="fixed-index-0", rng_draw=0,
        selected_at=float(index), read_cut=index, decision_index=index,
        consume_evidence=False, captured_features={candidate.key: (1.0,)},
    )


def _validate_card(card: Mapping[str, Any]) -> CandidateRegistryEntry:
    if (card.get("runner_version") != VERSION or card.get("diagnostic_only") is not True
            or card.get("selected_key") != SELECTED_KEY
            or card.get("source_seed") != 0 or card.get("target_seed") != 1):
        raise ValueError("route card/version/diagnostic scope mismatch")
    episode_limit = card.get("episode_limit")
    calls = card.get("producer_calls")
    if episode_limit not in (1, 2) or not isinstance(calls, list) or len(calls) != episode_limit:
        raise ValueError("episode_limit must be one or two with one producer call per episode")
    first = calls[0]["card"]
    candidate = CandidateRegistryEntry("peer-b", "live-v1", policy_digest(),
                                       first["model"], model_config_digest(first))
    for index, call in enumerate(calls):
        producer_card = call["card"]
        if (producer_card.get("stream_id") != card.get("stream_id")
                or producer_card.get("arm_id") != "route"
                or producer_card.get("real_api_runs_allowed") is not True
                or model_config_digest(producer_card) != candidate.model_config_digest
                or digest(producer_card) != call["expected_card_digest"]
                or not Path(call["reservation_path"]).is_absolute()
                or len(call["expected_reservation_digest"]) != 64):
            raise ValueError(f"producer call {index} binding mismatch")
    recipient = card.get("recipient_card")
    if (not isinstance(recipient, Mapping) or recipient.get("model") != candidate.model_id
            or recipient.get("maximum_task_requests") != 2 * episode_limit
            or set(recipient.get("max_tokens", {})) != {"judgment", "action"}):
        raise ValueError("recipient card must budget exactly two judgment/action calls per episode")
    return candidate


def run(out: Path, *, card_path: Path) -> dict[str, Any]:
    """Execute two serial episodes; caller supplies externally frozen API cards/reservations."""
    card_bytes = card_path.read_bytes()
    card = json.loads(card_bytes)
    candidate = _validate_card(card)
    out = out.resolve()
    out.mkdir(parents=False, exist_ok=False)
    _save(out / "route_config.json", {"version": VERSION, "diagnostic_only": True,
          "card_sha256": hashlib.sha256(card_bytes).hexdigest(),
          "started_at_utc": datetime.now(timezone.utc).isoformat(),
          "scientific_claim_allowed": False, "recipient_fixture_patch": False,
          "material_source": "unmodified public-contract-v2 adapter"})
    _save(out / "card.json", card)
    (out / "raw.jsonl").write_text("", encoding="utf-8")
    boundary = Pipe3SelectionBoundary(NoUpdatePolicy(), (candidate,))
    experience = ActorExperience(stream_id=card["stream_id"], arm_id="route", actor_id=candidate.key)
    episodes: list[dict[str, Any]] = []
    try:
        for index, seed in enumerate((0, 1)[:card["episode_limit"]]):
            materials = _materials(seed)
            decision = out / f"decision_{index}"
            seal = _seal(boundary, index, candidate)
            capture = decision / "preexecution_capture.json"
            save_decision_capture(capture, seal, boundary)
            load_decision_capture(capture, ledger_events=boundary.ledger.events,
                                  auxiliary_rows=boundary.auxiliary_manifest_rows)
            _save(decision / "selection_binding.json", _selection_binding(seal, boundary))
            producer_call = card["producer_calls"][index]
            prepared = prepare_request(
                base_payload=materials["agent_payloads"]["producer"], candidate=candidate,
                experience=experience, task_index=index, card=producer_call["card"],
                interaction_id=f"route-producer-{index}")
            _save(decision / "producer_prepared.json", prepared)
            _save(decision / "actor_before.json", experience.snapshot())
            generated = run_generation(
                prepared=prepared, card=producer_call["card"],
                expected_card_digest=producer_call["expected_card_digest"],
                output_dir=out / f"producer_{index}",
                reservation_path=Path(producer_call["reservation_path"]),
                expected_reservation_digest=producer_call["expected_reservation_digest"])
            _save(decision / "generation_result.json", generated)
            if generated["status"] != "PARSED":
                raise RuntimeError(f"producer generation {index} is UNKNOWN")
            completed = finalize(
                prepared=prepared, output_dir=out / f"producer_{index}",
                expected_receipt_digest=generated["completion_receipt_sha256"],
                recipient_id="peer-a", interaction_id=f"route-producer-{index}",
                delivery_id=f"route-delivery-{index}",
                source_event_id=f"producer-request-route-{index}",
                selection_id=f"selection-route-{index}")
            _save(decision / "actor_after.json", completed["after"])
            experience = ActorExperience.restore(completed["after"], stream_id=card["stream_id"],
                                                 arm_id="route", actor_id=candidate.key)
            episode = _run_episode(
                arm="route", decision_index=index, arm_dir=out, decision_dir=decision,
                boundary=boundary, materials=materials, candidates={}, selected_key=candidate.key,
                card=card["recipient_card"], raw=out / "raw.jsonl", task_seed=seed,
                fresh_producer={"prepared": prepared, "output_dir": str(out / f"producer_{index}"),
                                "expected_receipt_digest": generated["completion_receipt_sha256"],
                                "completion": completed})
            _save(decision / "episode.json", episode)
            episodes.append(episode)
        status = ("COMPLETE_SOURCE_DIAGNOSTIC_ONLY" if card["episode_limit"] == 1
                  else "COMPLETE_ROUTE_DIAGNOSTIC_ONLY")
    except Exception as exc:
        status = "UNKNOWN"
        _save(out / "failure.json", {"error_type": type(exc).__name__, "error": str(exc),
                                      "completed_episodes": len(episodes)})
    result = {"version": VERSION, "status": status, "diagnostic_only": True,
              "scientific_claim_allowed": False,
              "recipient_visibility": "legacy producer.py-only prompt; incomplete recipient/support context",
              "terminal_measurement": "legacy derived conjunction; independent Y remains UNKNOWN",
              "policy_update": "none; fixed single candidate",
              "recipient_fixture_patch": False,
              "episodes": episodes,
              "cost": _cost_receipts(out), "ledger": boundary.ledger.events,
              "actor_after": experience.snapshot()}
    _save(out / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    return 0 if run(args.out, card_path=args.card)["status"].startswith("COMPLETE_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
