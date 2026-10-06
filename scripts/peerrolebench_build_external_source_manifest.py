#!/usr/bin/env python3
"""Build an external shared-source manifest from one completed source episode.

This utility is deliberately a preparation step, not a benchmark scorer.  It
reads one already recorded episode, constructs a source-only receipt outside
the policy-arm loop, computes the canonical digest, and immediately validates
the receipt with the shared-source v2 contract.  A future live runner must run
this parent-owned phase before any arm policy executes and must pass the
resulting digest into each arm; this script does not reclassify the historical
run as scientific evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_shared_source_v2 import (
    canonical_source_digest,
    freeze_source_receipt,
    validate_selection_binding,
)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def _file_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(x for x in path.rglob("*") if x.is_file()):
        data = item.read_bytes()
        rows.append({
            "path": str(item.relative_to(path)),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    return rows


def _json_digest(path: Path) -> str:
    return _digest(json.loads(path.read_text(encoding="utf-8")))


def _response_digest(decision_dir: Path, patterns: tuple[str, ...]) -> str:
    files = []
    for pattern in patterns:
        files.extend(decision_dir.rglob(pattern))
    manifest = []
    for item in sorted(set(files)):
        if item.is_file():
            data = item.read_bytes()
            manifest.append({
                "path": str(item.relative_to(decision_dir)),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            })
    return _digest(manifest)


def _api_cost(api: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize one API receipt without turning absent measurements into zero."""
    payload = api if isinstance(api, Mapping) else {}
    unknown: list[str] = []
    usage = payload.get("usage")
    if not isinstance(usage, Mapping):
        usage = {}
        unknown.extend(("input_tokens", "output_tokens"))

    tokens: dict[str, int | None] = {}
    for name in ("input_tokens", "output_tokens"):
        value = usage.get(name)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            tokens[name] = value
        else:
            tokens[name] = None
            if name not in unknown:
                unknown.append(name)

    usage_complete = payload.get("usage_complete") is True
    if not usage_complete:
        unknown.append("usage_complete")
    token_complete = usage_complete and all(value is not None for value in tokens.values())

    wall = payload.get("elapsed_seconds")
    if isinstance(wall, (int, float)) and not isinstance(wall, bool) and math.isfinite(float(wall)) and float(wall) >= 0:
        wall_seconds: float | None = float(wall)
        wall_complete = True
    else:
        wall_seconds = None
        wall_complete = False
        unknown.append("wall_seconds")

    return {
        "input_tokens": tokens["input_tokens"],
        "output_tokens": tokens["output_tokens"],
        "wall_seconds": wall_seconds,
        "usage_complete": usage_complete,
        "token_complete": token_complete,
        "wall_complete": wall_complete,
        "http_status": payload.get("http_status"),
        "unknown_fields": sorted(set(unknown)),
    }


def _seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and float(value) >= 0:
        return float(value)
    return None


def episode_cost(source: Mapping[str, Any]) -> dict[str, Any]:
    """Return one source/target episode cost receipt.

    Timing and token completeness are tracked independently.  Missing values
    remain ``None`` and are named in ``unknown_fields``.  The action API
    elapsed time and action result wall time describe the same call, so only
    one is included.  Scorer timing uses either the producer plus outcome
    total or the producer plus independent recipient/adoption timings.
    """
    judgment_api = _api_cost(source.get("judgment_api"))
    action_api = _api_cost(source.get("action_api"))
    unknown = [f"{name}.{field}" for name, meta in (("judgment_api", judgment_api), ("action_api", action_api)) for field in meta["unknown_fields"]]

    action = source.get("action") if isinstance(source.get("action"), Mapping) else {}
    action_result_seconds = _seconds(action.get("action_wall_seconds"))
    action_api_seconds = action_api["wall_seconds"]
    if action_result_seconds is not None:
        action_seconds = action_result_seconds
        action_timing_source = "action_wall_seconds"
        if action_api_seconds is not None and action_api_seconds != action_result_seconds:
            unknown.append("action_timing_disagreement")
    elif action_api_seconds is not None:
        action_seconds = action_api_seconds
        action_timing_source = "action_api.elapsed_seconds"
    else:
        action_seconds = None
        action_timing_source = None
        unknown.append("action_wall_seconds")
    if action_seconds is not None:
        unknown = [field for field in unknown if field != "action_api.wall_seconds"]

    producer_score = source.get("producer_score") if isinstance(source.get("producer_score"), Mapping) else {}
    recipient_score = source.get("recipient_score") if isinstance(source.get("recipient_score"), Mapping) else {}
    adoption_score = source.get("adoption_score") if isinstance(source.get("adoption_score"), Mapping) else {}
    outcome = source.get("outcome") if isinstance(source.get("outcome"), Mapping) else {}
    producer_seconds = _seconds(producer_score.get("scorer_wall_seconds"))
    outcome_seconds = _seconds(outcome.get("scorer_wall_seconds"))
    recipient_seconds = _seconds(recipient_score.get("scorer_wall_seconds"))
    adoption_seconds = _seconds(adoption_score.get("scorer_wall_seconds"))
    if producer_seconds is None:
        unknown.append("producer_scorer_seconds")

    if outcome_seconds is not None:
        scorer_mode = "producer_plus_outcome_total"
        scorer_seconds = (producer_seconds + outcome_seconds) if producer_seconds is not None else outcome_seconds
    elif recipient_seconds is not None and adoption_seconds is not None:
        scorer_mode = "producer_plus_recipient_adoption"
        scorer_seconds = (producer_seconds + recipient_seconds + adoption_seconds) if producer_seconds is not None else recipient_seconds + adoption_seconds
    else:
        scorer_mode = None
        scorer_seconds = producer_seconds
        if outcome_seconds is None:
            unknown.append("outcome_scorer_seconds")
        if recipient_seconds is None:
            unknown.append("recipient_scorer_seconds")
        if adoption_seconds is None:
            unknown.append("adoption_scorer_seconds")

    wall_complete = (
        judgment_api["wall_complete"]
        and action_seconds is not None
        and producer_seconds is not None
        and scorer_mode is not None
        and not any(field == "action_timing_disagreement" for field in unknown)
    )
    token_complete = bool(judgment_api["token_complete"] and action_api["token_complete"])
    source_cost_units = sum(
        value for value in (
            judgment_api["wall_seconds"], action_seconds, scorer_seconds,
        ) if value is not None
    )
    unknown = sorted(set(unknown))
    cost_status = "COMPLETE" if wall_complete and token_complete else "UNKNOWN"
    return {
        "source_cost_units": source_cost_units,
        "target_cost_units": 0.0,
        "unit": "wall_seconds_sum_source_only_with_explicit_measurement_status",
        "api": {"judgment": judgment_api, "action": action_api},
        "scorer_wall_seconds": {
            "producer": producer_seconds,
            "recipient": recipient_seconds,
            "adoption": adoption_seconds,
            "outcome_total": outcome_seconds,
            "selected_total": scorer_seconds,
        },
        "scorer_timing_mode": scorer_mode,
        "action_wall_seconds": action_seconds,
        "action_timing_source": action_timing_source,
        "wall_complete": wall_complete,
        "token_complete": token_complete,
        "unknown_fields": unknown,
        "cost_status": cost_status,
        "source_cost_units_observed": cost_status == "COMPLETE",
        "source_cost_units_semantics": (
            "measured_wall_seconds_sum_for_source_only_receipt"
            if cost_status == "COMPLETE"
            else "lower_bound_wall_seconds_sum_missing_token_or_timing_receipt"
        ),
    }


def build_source_receipt(run_dir: Path, arm: str, decision_index: int, manifest_id: str) -> dict[str, Any]:
    if int(decision_index) != 0:
        raise ValueError("external source manifests may only be built from decision_index=0")
    arm_dir = run_dir / arm
    summary = json.loads((arm_dir / "summary.json").read_text(encoding="utf-8"))
    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    registry = json.loads((arm_dir / "candidate_registry.json").read_text(encoding="utf-8"))
    selection_bindings = json.loads((arm_dir / "selection_bindings.json").read_text(encoding="utf-8"))
    source_key = "source" if decision_index == 0 else "target"
    source = summary[source_key]
    decision_dir = arm_dir / f"decision_{decision_index}"
    if not decision_dir.is_dir():
        raise FileNotFoundError(f"missing decision directory: {decision_dir}")

    material_manifest = arm_dir / "material_manifest.json"
    raw_path = arm_dir / "raw.jsonl"
    contract_digest = _json_digest(material_manifest)
    registry_digest = registry.get("digest")
    if not isinstance(registry_digest, str):
        raise ValueError("candidate registry has no digest")
    source_binding = next(
        (row for row in selection_bindings if row.get("native_selection_id") == source["selection_id"]),
        None,
    )
    if source_binding is None:
        raise ValueError("source selection binding is missing")
    validate_selection_binding(source_binding)
    if source_binding["chosen_candidate"] != source["selected_key"]:
        raise ValueError("source selection binding chose a different candidate")
    if source_binding["candidate_registry_digest"] != registry_digest:
        raise ValueError("source selection binding registry digest disagrees")

    producer_score = source["producer_score"]
    recipient_score = source.get("recipient_score", {})
    adoption_score = source.get("adoption_score", {})
    scorer_digest = _digest({
        "producer": producer_score,
        "recipient": recipient_score,
        "adoption": adoption_score,
        "outcome": source["outcome"],
    })
    prompt_digest = _response_digest(decision_dir, ("*_request.json",))
    raw_response_digest = _response_digest(
        decision_dir, ("*_response.sse", "*_parsed_response.json", "response.json")
    )
    artifact_digest = source["artifact_digest"]
    provenance = {
        "policy_invariant": True,
        "artifact_digest": artifact_digest,
        "contract_digest": contract_digest,
        "registry_digest": registry_digest,
        "scorer_digest": scorer_digest,
        "prompt_digest": prompt_digest,
        "raw_response_digest": raw_response_digest,
        "provenance_scope": "source-only decision directory and immutable parent material manifest",
    }

    episode_cost_receipt = episode_cost(source)
    source_event_id = f"{source['selection_id']}:source"
    cost = {
        "source_cost_id": source_event_id,
        **episode_cost_receipt,
    }

    raw_gate_status = source["source_gate"].get("status")
    q_complete = source["source_gate"].get("q_complete") is True
    y_complete = source["source_gate"].get("y_complete") is True
    if raw_gate_status == "ELIGIBLE":
        gate_status = "ELIGIBLE"
        episode_status = "SOURCE_COMPLETE"
        source_complete = True
        estimand_inclusion = "ITT_AND_ELIGIBLE"
    elif raw_gate_status == "PENDING_ATTRIBUTION":
        gate_status = "PENDING_ATTRIBUTION"
        episode_status = "STOPPED_PRE_TARGET"
        source_complete = True
        estimand_inclusion = "ITT_ONLY"
    elif raw_gate_status == "UNKNOWN" and q_complete and y_complete:
        # The source episode is complete, but responsibility attribution is
        # unresolved. Preserve the raw gate payload while keeping the typed
        # denominator state explicit for the shared-source contract.
        gate_status = "PENDING_ATTRIBUTION"
        episode_status = "STOPPED_PRE_TARGET"
        source_complete = True
        estimand_inclusion = "ITT_ONLY"
    else:
        # An incomplete scorer/transport event is the only source state that
        # can enter v2 as UNKNOWN.  A complete but unattributable event should
        # remain PENDING_ATTRIBUTION; callers must not turn it into a missing
        # observation by inspecting only evidence_publish_allowed.
        gate_status = "UNKNOWN"
        episode_status = "SOURCE_INCOMPLETE"
        source_complete = False
        estimand_inclusion = "ITT_ONLY"
    source_payload: dict[str, Any] = {
        "source_event_id": source_event_id,
        "task_id": config.get("task_id", source.get("task_id", "PIPE3_stream_processing")),
        "root": config.get("task_id", "PIPE3_stream_processing"),
        "seed": int(config.get("seed", 0)),
        "source_lineage": {
            "selection_id": source["selection_id"],
            "delivery_id": source["delivery_id"],
            "selected_candidate": source["selected_key"],
            "decision_index": int(source.get("decision_index", decision_index)),
            "candidate_registry_digest": registry_digest,
            "selection_binding_digest": source_binding["binding_digest"],
            "card_sha256": config.get("card_sha256"),
            "source_commit": config.get("source_commit"),
            "runner_version": config.get("version"),
            "source_root": config.get("task_id", "PIPE3_stream_processing"),
        },
        "source_selection_binding": source_binding,
        "delivery_digest": artifact_digest,
        "judgment": source["judgment"],
        "action": source["action"],
        "producer_score": producer_score,
        "outcome": source["outcome"],
        "gate": source["source_gate"],
        "cost": cost,
        "episode_status": episode_status,
        "gate_status": gate_status,
        "estimand_inclusion": estimand_inclusion,
        "source_complete": source_complete,
        "target_started": False,
        "target_status": "NOT_STARTED",
        "provenance": provenance,
        "source_seal": {
            "manifest_id": manifest_id,
            "source_digest": "",
            "parent_run": str(run_dir),
            "arm_observed": arm,
            "decision_index": decision_index,
        },
        "source_receipt_digest": "",
    }
    digest = canonical_source_digest(source_payload)
    source_payload["source_seal"]["source_digest"] = digest
    source_payload["source_receipt_digest"] = digest
    return source_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--decision-index", type=int, default=0)
    parser.add_argument("--manifest-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_source_receipt(args.run_dir.resolve(), args.arm, args.decision_index, args.manifest_id)
    expected = receipt["source_receipt_digest"]
    validated = freeze_source_receipt(receipt, expected)
    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "manifest_version": "peerrolebench-external-source-manifest-v1",
        "manifest_id": args.manifest_id,
        "expected_source_digest": expected,
        "source_receipt": validated,
        "scientific_claim_allowed": False,
        "historical_conversion": True,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "source_digest": expected, "validated": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
