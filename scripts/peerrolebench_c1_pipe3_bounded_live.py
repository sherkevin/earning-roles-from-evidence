"""C1: bounded real-API PIPE3 development stream.

This runner is intentionally smaller than a confirmation benchmark.  It uses
two immutable, versioned PIPE3 producer snapshots and a real recipient model
to exercise the first causal seam that the offline qualifications cannot test:
the chosen snapshot is delivered, judged, used/reworked, scored, and (when a
responsibility-safe source episode exists) made available before a later
assignment.  Each arm owns its policy state and raw API ledger.

The producer snapshots are fixed benchmark material, so this card is not a
claim about independently trained peer identities.  Every API response,
failure, UNKNOWN, cost receipt, and policy update is preserved.  The runner
never repairs labels after an API response.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

import peerrolebench_real_closed_loop as api  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, ProducerScore, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import (  # noqa: E402
    CandidateRef, Feedback, FeatureContextualTrustPolicy, NoUpdatePolicy,
    RarePolicy,
)
from peerrolebench_candidate_registry import CandidateRegistryEntry, registry_digest  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2 import run_producer_scorer  # noqa: E402
from peerrolebench_pipe3_recipient_scorer_v2 import run_scorer  # noqa: E402
from peerrolebench_pipe3_judgment_contract import validate_structured_judgment  # noqa: E402
from peerrolebench_pipe3_consumer_response_contract import extract_consumer_sources  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    adoption_scorer_sources, prepare_pipe3_action, recipient_scorer_sources,
    validate_pipe3_action_result,
)
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary, auxiliary_manifest_root, make_offer,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_two_stage_composition import (  # noqa: E402
    _patch_recipient, _source_offer, _public_features, _digest,
)
from peerrolebench_role_evidence_selection import (  # noqa: E402
    commit_role_evidence_selection, preview_role_evidence_selection_with_public_judgment,
)
from peerrolebench_role_evidence_scorer import JUDGMENT_LABELS, RoleEvidenceScoreConfig  # noqa: E402
from peerrolebench_two_stage_gate import (  # noqa: E402
    DelayedCreditLedger, derive_later_credit_from_ledger, evaluate_source_gate,
)
from peerrolebench_selection_preview import FixedChoiceRNG  # noqa: E402
from peerrolebench_shared_source_v2 import validate_selection_binding  # noqa: E402


VERSION = "c1-pipe3-bounded-live-v1"
TASK_ID = "PIPE3_stream_processing"
CARD = ROOT / "configs/aamas2027/n03_c1_pipe3_bounded_live_dev_v2.json"
CANDIDATE_KEYS = ("peer-b@v1", "peer-c@v1")
ARMS = ("no_update", "contextual_trust_linear", "RARE")
PUBLIC_ENCODER = "hash64-v1"
PUBLIC_SCHEMA = "matrix-features-v1"
PUBLIC_DIMENSION = 64


def _validate_responsibility_card(card: Mapping[str, Any]) -> None:
    """Require the active structural-owner contract before a v2 run."""
    if not str(card.get("manifest_version", "")).startswith(
            "peerrolebench-c1-pipe3-bounded-live-development-v2"):
        return  # historical v1 cards remain replayable but are never promoted
    gate = card.get("responsibility_gate")
    if not isinstance(gate, Mapping):
        raise ValueError("v2 card requires responsibility_gate")
    required = {
        "version": "two-stage-role-evidence-v3-structural-owner",
        "eligibility_owner_source": "contract_registry_scorer",
        "judged_role_policy": "calibration_only",
        "disagreement_field": "judged_role_agrees",
    }
    for key, expected in required.items():
        if gate.get(key) != expected:
            raise ValueError(f"responsibility_gate.{key} must equal {expected!r}")
    registered = gate.get("registered_producer_candidates")
    if registered != ["peer-b@v1"]:
        raise ValueError("v2 card must register only peer-b@v1 as the producer-defect source")


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _log(raw: Path, event_type: str, payload: Any) -> None:
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload,
        }, ensure_ascii=False, sort_keys=True, default=str) + "\n")
        handle.flush()


def _policy(name: str):
    if name == "no_update":
        return NoUpdatePolicy()
    if name == "contextual_trust_linear":
        return FeatureContextualTrustPolicy(
            dimension=PUBLIC_DIMENSION, ridge=1.0, trust_scale=2.0,
            encoder_version=PUBLIC_ENCODER, feature_schema=PUBLIC_SCHEMA,
        )
    if name == "RARE":
        return RarePolicy(dimension=PUBLIC_DIMENSION, exploration=0.0)
    raise ValueError(f"unsupported C1 arm {name!r}")


def _policy_contract(name: str) -> dict[str, Any]:
    payload = {
        "name": name,
        "version": {"no_update": "no-update-v1", "contextual_trust_linear": "linear-ridge-v1", "RARE": "rare-anchor-v1"}[name],
        "temperature": 1.0,
        "exploration": 0.0,
        "encoder_version": PUBLIC_ENCODER,
        "feature_schema": PUBLIC_SCHEMA,
        "dimension": PUBLIC_DIMENSION,
    }
    if name == "contextual_trust_linear":
        payload.update({"ridge": 1.0, "trust_scale": 2.0})
    return payload


def _candidate_materials(materials: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    producer = dict(materials["agent_payloads"]["producer"]["source_files"])
    fixed = dict(producer)
    timestamp_field = interfaces(materials)["timestamp_field"]
    anchor = "    return json.dumps(data, default=str)"
    if anchor not in fixed["producer.py"]:
        raise RuntimeError("producer correction anchor not found")
    fixed["producer.py"] = fixed["producer.py"].replace(
        anchor,
        f'    data["{timestamp_field}"] = event.{timestamp_field}.isoformat()\n    return json.dumps(data)',
        1,
    )
    return {"peer-b@v1": {"producer.py": producer["producer.py"]},
            "peer-c@v1": {"producer.py": fixed["producer.py"]}}


def _registry(materials: Mapping[str, Any], candidates: Mapping[str, Mapping[str, str]]) -> list[CandidateRegistryEntry]:
    model_config = hashlib.sha256(b"c1-pipe3-static-snapshot-model-envelope-v1").hexdigest()
    return [
        CandidateRegistryEntry("peer-b", "v1", digest_files(candidates["peer-b@v1"]), "fixture-model", model_config),
        CandidateRegistryEntry("peer-c", "v1", digest_files(candidates["peer-c@v1"]), "fixture-model", model_config),
    ]


def _features() -> dict[str, tuple[float, ...]]:
    values: dict[str, tuple[float, ...]] = {}
    for index, key in enumerate(CANDIDATE_KEYS):
        vector = [0.0] * PUBLIC_DIMENSION
        vector[index] = 1.0
        values[key] = tuple(vector)
    return values


def _card_with_budget(card: Mapping[str, Any]) -> dict[str, Any]:
    # call_api counts request_start events in each decision directory.  A
    # decision has exactly one judgment and one action request; a third slot
    # remains reserved for a future transport-safe actor response, but no
    # retry is enabled by this card.
    value = dict(card)
    value["maximum_task_requests"] = int(card["maximum_task_requests"])
    return value


def _call_actor(*, arm_dir: Path, decision_dir: Path, stage: str, prompt: str,
                card: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    decision_dir.mkdir(parents=True, exist_ok=False)
    raw = arm_dir / "raw.jsonl"
    if not raw.exists():
        raw.write_text("", encoding="utf-8")
    return api.call_api(arm_dir, decision_dir, stage, prompt, _card_with_budget(card))


def _score_producer(materials: Mapping[str, Any], source: Mapping[str, str], info: Mapping[str, Any],
                    task_seed: int, out: Path, raw: Path) -> dict[str, Any]:
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    result = run_producer_scorer(
        {"producer.py": source["producer.py"], "models.py": materials["agent_payloads"]["producer"]["source_files"]["models.py"]},
        info, TASK_ID, task_seed, out,
        lambda event, payload: _log(raw, event, payload),
    )
    result["scorer_wall_seconds"] = time.perf_counter() - started
    return result


def _score_outcome(materials: Mapping[str, Any], final_sources: Mapping[str, str], info: Mapping[str, Any],
                   task_seed: int, out: Path, raw: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    out.mkdir(parents=False, exist_ok=False)
    started = time.perf_counter()
    recipient = run_scorer(
        recipient_scorer_sources(final_sources), info, "recipient", TASK_ID, task_seed, out / "recipient",
        lambda event, payload: _log(raw, event, payload),
    )
    adoption = run_scorer(
        adoption_scorer_sources(final_sources), info, "adoption", TASK_ID, task_seed, out / "adoption",
        lambda event, payload: _log(raw, event, payload),
    )
    complete = all(
        row.get("status") in {"PASS", "FAIL"}
        and row.get("coverage_complete") is True
        and row.get("decision_complete") is True
        for row in (recipient, adoption)
    )
    status = "UNKNOWN" if not complete else ("PASS" if recipient.get("status") == "PASS" and adoption.get("status") == "PASS" else "FAIL")
    outcome = {
        "status": status,
        "quality_score": adoption.get("quality_score") if complete else None,
        "coverage_complete": complete,
        "decision_complete": complete,
        "scorer_wall_seconds": time.perf_counter() - started,
    }
    return recipient, adoption, outcome


def _public_judgment_prompt(materials: Mapping[str, Any], delivered: Mapping[str, str], digest: str) -> str:
    payload = deepcopy(materials["agent_payloads"]["recipient"])
    payload["source_files"] = dict(delivered)
    public_paths = sorted(payload["source_files"])
    return (
        "You are the recipient in a bounded public collaboration task. Review the delivered "
        "producer artifact before changing any file. Do not inspect hidden tests or external files. "
        "Return exactly one JSON object with fields: decision (accept, accept_with_rework, or "
        "reject_redo), confidence (number 0..1), rationale, repair_plan, observed_artifact_sha256, "
        "target_role (producer, recipient, sink, mixed, or unknown), target_paths (list chosen only "
        "from the public paths), defect_type (producer_contract, recipient_integration, sink_adoption, "
        "mixed, or unknown), evidence_refs (non-empty list of strings). The artifact digest is "
        f"{digest}. Public paths are {public_paths}.\nPUBLIC MATERIAL:\n"
        + json.dumps(payload, ensure_ascii=False)
    )


def _action_prompt(action_payload: Mapping[str, Any], judgment: Mapping[str, Any]) -> str:
    return (
        "Carry out the sealed recipient decision below. Do not inspect hidden tests or external files. "
        "Return exactly {\"source_files\":{...}} containing the complete current public snapshot. "
        "Change only paths listed in writable_paths and preserve every other path.\nSEALED JUDGMENT:\n"
        + json.dumps(judgment, ensure_ascii=False)
        + "\nACTION PAYLOAD:\n"
        + json.dumps(action_payload, ensure_ascii=False)
    )


def _run_episode(*, arm: str, decision_index: int, arm_dir: Path, decision_dir: Path,
                 boundary: Pipe3SelectionBoundary, materials: Mapping[str, Any],
                 candidates: Mapping[str, Mapping[str, str]], selected_key: str,
                 card: Mapping[str, Any], raw: Path, task_seed: int) -> dict[str, Any]:
    delivery_id = f"{arm}-delivery-{decision_index}"
    judgment_id = f"{arm}-judgment-{decision_index}"
    action_id = f"{arm}-action-{decision_index}"
    outcome_id = f"{arm}-outcome-{decision_index}"
    selection_id = f"selection-{arm}-{decision_index}"
    source = candidates[selected_key]
    artifact_digest = digest_files(source)
    entry = next(item for item in boundary.registry if item.key == selected_key)
    if entry.source_digest != artifact_digest:
        raise ValueError("candidate registry does not match delivered snapshot")
    boundary.ledger.record_task_start(TASK_ID, decision_index)
    delivery = Delivery(
        delivery_id, TASK_ID, entry.candidate_id, "peer-a", artifact_digest,
        f"request-{arm}-{decision_index}", decision_index, selection_id, entry.source_digest,
    )
    boundary.ledger.record_delivery(delivery)
    qp = _score_producer(materials, source, interfaces(materials), task_seed, decision_dir / "producer_scorer", raw)
    _save(decision_dir / "producer_score.json", qp)
    boundary.ledger.record_producer_score(ProducerScore(
        f"{arm}-producer-score-{decision_index}", delivery_id, artifact_digest,
        qp.get("scorer_version", "pipe3-producer-objective-v2"), qp.get("status", "UNKNOWN"),
        qp.get("label"), qp.get("quality_score"), qp.get("response_digest", _digest(qp)),
        qp.get("coverage_complete") is True, qp.get("decision_complete") is True,
    ))
    prompt = _public_judgment_prompt(materials, source, artifact_digest)
    judgment_raw, judgment_meta = _call_actor(
        arm_dir=arm_dir, decision_dir=decision_dir / "judgment", stage="judgment",
        prompt=prompt, card=card,
    )
    judged = validate_structured_judgment(
        judgment_raw, artifact_digest,
        sorted(materials["agent_payloads"]["producer"]["source_files"] | materials["agent_payloads"]["recipient"]["source_files"]),
    )
    _save(decision_dir / "judgment.json", judged)
    boundary.ledger.record_judgment(RecipientJudgment(
        judgment_id, delivery_id, "peer-a", judged["decision"], artifact_digest,
        repair_note=judged.get("repair_plan", ""),
    ))
    action_name = {"accept": "use", "accept_with_rework": "repair", "reject_redo": "independent_redo"}[judged["decision"]]
    action_payload = prepare_pipe3_action(materials, source, action_name, allow_producer_rewrite=False)
    consumed, action_meta = _call_actor(
        arm_dir=arm_dir, decision_dir=decision_dir / "action", stage="action",
        prompt=_action_prompt(action_payload, judged), card=card,
    )
    final_sources = extract_consumer_sources(consumed, sorted(action_payload["source_files"]))
    action_result = validate_pipe3_action_result(action_payload, final_sources)
    action_wall_seconds = float(action_meta.get("elapsed_seconds", 0.0))
    repair_cost = action_wall_seconds if action_name != "use" else 0.0
    action_result = {
        **action_result,
        "action_wall_seconds": action_wall_seconds,
        "repair_cost": repair_cost,
        "repair_cost_unit": "full action call seconds when repair/redo; zero for use",
    }
    _save(decision_dir / "action.json", action_result)
    boundary.ledger.record_action(ConsumerAction(
        action_id, delivery_id, "peer-a", action_name != "independent_redo", artifact_digest,
        action_result["output_source_sha256"], repair_cost, action_name,
    ))
    qr, adoption, outcome = _score_outcome(
        materials, final_sources, interfaces(materials), task_seed, decision_dir / "outcome", raw,
    )
    _save(decision_dir / "recipient_score.json", qr)
    _save(decision_dir / "adoption_score.json", adoption)
    outcome["outcome_id"] = outcome_id
    if outcome["status"] in {"PASS", "FAIL"}:
        boundary.ledger.record_outcome(TerminalOutcome(
            outcome_id, delivery_id, outcome["status"] == "PASS", "pipe3-adoption-v1",
            None if outcome["quality_score"] is None else float(outcome["quality_score"]), _digest(outcome),
        ))
    else:
        _log(raw, "unknown_outcome", outcome)
    # The defect registration is operator-side and comes from the immutable
    # candidate registry; it is never accepted from the model's self-report.
    registered = card.get("responsibility_gate", {}).get("registered_producer_candidates", ["peer-b@v1"])
    gate_judgment = {**judged, "producer_defect_registered": selected_key in registered}
    gate = evaluate_source_gate(
        materials, qp, gate_judgment,
        {**action_result, "used_artifact": action_name == "use"}, outcome, None,
    )
    _save(decision_dir / "source_gate.json", gate.payload())
    return {
        "decision_index": decision_index, "selection_id": selection_id,
        "selected_key": selected_key, "delivery_id": delivery_id,
        "artifact_digest": artifact_digest, "producer_score": qp,
        "judgment": judged, "judgment_api": judgment_meta,
        "action": action_result, "action_api": action_meta,
        "recipient_score": qr, "adoption_score": adoption, "outcome": outcome,
        "source_gate": gate.payload(), "final_sources": final_sources,
    }


def _source_state_offer(boundary: Pipe3SelectionBoundary, source: Mapping[str, Any],
                        seal: Any, arm: str) -> tuple[Any, dict[str, Any]]:
    return _source_offer(
        boundary, control=arm, source={
            "delivery_id": source["delivery_id"],
            "delivery_digest": source["artifact_digest"],
            "eligibility": {"producer_feedback_eligible": source["source_gate"]["evidence_publish_allowed"]},
            "producer": source["producer_score"], "action": source["action"],
            "outcome": source["outcome"],
        }, selection=seal.decision_sidecar, selected_peer=source["selected_key"].split("@", 1)[0],
        target_task_index=1,
    )


def _select_source(boundary: Pipe3SelectionBoundary, arm: str, features: Mapping[str, Any], seed: int) -> Any:
    offer = make_offer(
        offer_id=f"offer-{arm}-0", task_id=TASK_ID, task_index=0, role="producer",
        context_key="PIPE3:0", candidate_keys=CANDIDATE_KEYS, public_rows=(),
        evidence_version=VERSION, available_index=0,
    )
    return boundary.choose_and_seal(
        offer=offer, native_selection_id=f"selection-{arm}-0", selector_id="peer-a", role="producer",
        base_scores=(0.0, 0.0), rng=FixedIndexRNG(0), state_version="source-state-v1",
        encoder_version=PUBLIC_ENCODER, feature_schema=PUBLIC_SCHEMA,
        policy_version=_policy_contract(arm)["version"], base_score_version="c1-base-v1",
        rng_algorithm="fixed-index-0", rng_draw=0, selected_at=0.0, read_cut=0,
        decision_index=0, consume_evidence=False, captured_features=features,
    )


class FixedIndexRNG:
    """Pre-registered source bootstrap draw; exposes no hidden randomness."""

    def __init__(self, index: int) -> None:
        self.index = int(index)

    def choice(self, count: int, p: Any = None) -> int:
        if not 0 <= self.index < int(count):
            raise ValueError("fixed index outside choice menu")
        return self.index


def _select_no_update(boundary: Pipe3SelectionBoundary, arm: str, index: int,
                      features: Mapping[str, Any], seed: int) -> Any:
    offer = make_offer(
        offer_id=f"offer-{arm}-{index}", task_id=TASK_ID, task_index=index, role="producer",
        context_key=f"PIPE3:{index}", candidate_keys=CANDIDATE_KEYS, public_rows=(),
        evidence_version=VERSION, available_index=index,
    )
    return boundary.choose_and_seal(
        offer=offer, native_selection_id=f"selection-{arm}-{index}", selector_id="peer-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(seed + index), state_version=f"state-v{index}",
        encoder_version=PUBLIC_ENCODER, feature_schema=PUBLIC_SCHEMA,
        policy_version=_policy_contract(arm)["version"], base_score_version="c1-base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=index, selected_at=float(index), read_cut=index,
        decision_index=index, consume_evidence=False, captured_features=features,
    )


def _select_post_update(boundary: Pipe3SelectionBoundary, arm: str, features: Mapping[str, Any], seed: int) -> Any:
    # This is a pre-execution policy preview.  It must not enter the causal
    # execution ledger until a task is actually started and a delivery is
    # recorded; otherwise the replay checker correctly reports an orphan
    # selection.  Clone the post-update policy state so the preview observes
    # the learned state without mutating the completed execution history.
    preview = Pipe3SelectionBoundary(deepcopy(boundary.policy), boundary.registry)
    return _select_no_update(preview, arm, 2, features, seed)


def _selection_binding(seal: Any, boundary: Pipe3SelectionBoundary) -> dict[str, Any]:
    """Bind a committed policy decision to its native ledger selection.

    The preview returned by ``_select_post_update`` never enters this helper:
    only a committed ``SelectionSeal`` with a native ledger record is eligible.
    """
    if seal.decision_sidecar.ledger_record_hash != boundary.ledger.events[-1]["record_hash"]:
        raise ValueError("selection sidecar is not bound to the latest native ledger record")
    native = seal.native_selection
    policy = seal.policy_selection
    if native.chosen_peer_id != policy.chosen.candidate_id:
        raise ValueError("policy and native chosen candidates disagree")
    native_menu = tuple(native.candidate_ids)
    policy_menu = tuple(candidate.candidate_id for candidate in policy.candidates)
    if native_menu != policy_menu:
        raise ValueError("policy and native candidate menus disagree")
    if not np.isclose(float(native.propensity), float(policy.propensity), atol=1e-12):
        raise ValueError("policy and native propensities disagree")
    binding = {
        "policy_decision_id": policy.event_id,
        "native_selection_id": native.selection_id,
        "decision_digest": seal.decision_sidecar.sidecar_digest,
        "native_record_digest": seal.decision_sidecar.ledger_record_hash,
        "candidate_registry_digest": seal.decision_sidecar.candidate_registry_digest,
        "policy_input_digest": seal.attestation.policy_input_digest,
        "state_before_digest": seal.attestation.policy_state_digest_before,
        "chosen_candidate": policy.chosen.key,
        "candidate_menu": [candidate.key for candidate in policy.candidates],
        "propensity": float(policy.propensity),
    }
    binding["binding_digest"] = _digest({key: value for key, value in binding.items()})
    validate_selection_binding(binding)
    return binding


def _run_arm(arm: str, out_dir: Path, card: Mapping[str, Any]) -> dict[str, Any]:
    arm_dir = out_dir / arm
    arm_dir.mkdir(parents=False, exist_ok=False)
    raw = arm_dir / "raw.jsonl"
    raw.write_text("", encoding="utf-8")
    generated = load_pipe3(0)
    materials = build_materials(generated)
    # Keep the recipient's own integration baseline fixed while varying only
    # the immutable producer snapshot selected by the policy.
    materials = deepcopy(materials)
    merged = dict(materials["agent_payloads"]["producer"]["source_files"])
    merged.update(materials["agent_payloads"]["recipient"]["source_files"])
    fixed_recipient = _patch_recipient(merged)
    for name in ("processor.py",):
        materials["agent_payloads"]["recipient"]["source_files"][name] = fixed_recipient[name]
    candidates = _candidate_materials(materials)
    registry = _registry(materials, candidates)
    features = _features()
    policy = _policy(arm)
    boundary = Pipe3SelectionBoundary(policy, registry)
    _save(arm_dir / "material_manifest.json", materials["manifest"])
    _save(arm_dir / "candidate_registry.json", {"digest": registry_digest(registry), "entries": [x.payload() for x in registry]})
    _log(raw, "arm_config", {
        "version": VERSION, "arm": arm, "task_id": TASK_ID, "seed": 0,
        "policy": _policy_contract(arm), "candidate_registry_digest": registry_digest(registry),
        "feature_digest": _digest(features), "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    })
    seal0 = _select_source(boundary, arm, features, 0)
    selection_bindings = [_selection_binding(seal0, boundary)]
    selected0 = seal0.native_selection.chosen_peer_id + "@v1"
    if selected0 != "peer-b@v1":
        raise AssertionError("fixed source bootstrap did not select peer-b@v1")
    source = _run_episode(
        arm=arm, decision_index=0, arm_dir=arm_dir, decision_dir=arm_dir / "decision_0",
        boundary=boundary, materials=materials, candidates=candidates, selected_key=selected0,
        card=card, raw=raw, task_seed=0,
    )
    _log(raw, "source_episode_complete", {"selected_key": selected0, "gate": source["source_gate"]})
    source_eligible = source["source_gate"]["evidence_publish_allowed"] is True
    role_offer = None
    offer_meta = None
    if source_eligible:
        if arm == "no_update":
            # The frozen control does not consume evidence, but its complete
            # execution still needs an immutable provenance record so the
            # strict ledger replay can distinguish a finished control from a
            # truncated one.  This bookkeeping event never touches policy.
            boundary.ledger.record_evidence_update(RoleEvidenceUpdate(
                "no_update-source-observation", "no_update-judgment-0",
                "no_update-action-0", "no_update-outcome-0", "c1-control-observation-v1", 1.0,
            ))
            _log(raw, "control_evidence_recorded", {"evidence_id": "no_update-source-observation"})
        else:
            role_offer, offer_meta = _source_state_offer(boundary, source, seal0, arm)
            _log(raw, "source_evidence_published", {"offer_id": role_offer.offer_id, "bundle_digest": role_offer.bundle_digest})
    else:
        _log(raw, "promotion_blocked", {"reason": source["source_gate"]["reason"]})

    target = None
    update = {"status": "NOT_RUN", "updates": boundary.policy.updates}
    post = None
    if arm == "no_update":
        seal1 = _select_no_update(boundary, arm, 1, features, 1)
    elif source_eligible:
        from peerrolebench_assignment_attestation import AssignmentEvidenceOffer
        feedback_offer = make_offer(
            offer_id=f"feedback-offer-{arm}", task_id=TASK_ID, task_index=1, role="producer",
            context_key="PIPE3:1", candidate_keys=CANDIDATE_KEYS, public_rows=(),
            evidence_version=VERSION, available_index=1,
            previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
        )
        # The native assignment/update seam expects AssignmentEvidenceOffer,
        # while make_offer returns the compatible typed offer object.
        plan, overlay = preview_role_evidence_selection_with_public_judgment(
            boundary, role_offer=role_offer, feedback_offer=feedback_offer,
            base_scores=(0.0, 0.0), read_cut=1,
            scorer_config=RoleEvidenceScoreConfig(),
            assignment_id=f"assignment-{arm}", native_selection_id=f"selection-{arm}-1",
            selector_id="peer-a", rng=np.random.default_rng(1), state_version="target-state-v1",
            encoder_version=PUBLIC_ENCODER, feature_schema=PUBLIC_SCHEMA,
            policy_version=_policy_contract(arm)["version"], base_score_version="c1-public-overlay-v1",
            rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0, decision_index=1,
            captured_features=features,
        )
        seal1 = commit_role_evidence_selection(boundary, plan=plan, role_offer=role_offer, feedback_offer=feedback_offer)
        _save(arm_dir / "assignment_overlay.json", overlay.payload())
    else:
        return {
            "arm": arm, "status": "UNKNOWN", "passed": False,
            "stop_reason": "source evidence was not eligible; learning-arm target not started",
            "source": source, "source_eligible": False, "policy_updates": boundary.policy.updates,
            "scientific_claim_allowed": False, "selection_bindings": selection_bindings,
            "manifest_roots": {
                "native": boundary.validate_selection_manifests()[0],
                "auxiliary": boundary.validate_selection_manifests()[1],
            },
            "ledger": boundary.ledger.events,
        }
    if arm == "no_update":
        # no_update deliberately has no evidence assignment; it is the frozen
        # execution control and still uses the same menu/read-cut/cost envelope.
        pass
    target_key = seal1.native_selection.chosen_peer_id + "@v1"
    selection_bindings.append(_selection_binding(seal1, boundary))
    target = _run_episode(
        arm=arm, decision_index=1, arm_dir=arm_dir, decision_dir=arm_dir / "decision_1",
        boundary=boundary, materials=materials, candidates=candidates, selected_key=target_key,
        card=card, raw=raw, task_seed=1,
    )
    if target["outcome"]["status"] in {"PASS", "FAIL"}:
        boundary.ledger.record_evidence_update(RoleEvidenceUpdate(
            f"{arm}-target-completion-evidence", f"{arm}-judgment-1", f"{arm}-action-1",
            f"{arm}-outcome-1", "c1-control-observation-v1" if arm == "no_update" else "c1-target-completion-v1", 2.0,
        ))
        replay = replay_ledger_events(boundary.ledger.events)
        if arm == "no_update":
            _log(raw, "control_evidence_recorded", {"evidence_id": f"{arm}-target-completion-evidence"})
        if arm != "no_update":
            credit = derive_later_credit_from_ledger(
                ledger=boundary.ledger, source_gate=evaluate_source_gate(
                    materials, source["producer_score"],
                    {**source["judgment"], "producer_defect_registered": source["selected_key"] in card.get("responsibility_gate", {}).get("registered_producer_candidates", ["peer-b@v1"])},
                    {**source["action"], "used_artifact": source["action"]["consumer_action"] == "use"}, source["outcome"], None,
                ), assignment_id=f"assignment-{arm}", source_evidence_id=offer_meta["evidence_id"],
                evidence_candidate_id=selected0, later_outcome_id=f"{arm}-outcome-1",
            ) if replay.status == "PASS" and replay.complete else None
        else:
            credit = None
        if arm != "no_update" and credit is not None:
            feedback = Feedback(
                feedback_id=f"{arm}-later-feedback", source_event_id=f"policy-selection-{arm}-1",
                source="recipient_judgment", label=JUDGMENT_LABELS[target["judgment"]["decision"]],
                arrived_at=2.0, delay=1.0, action={"accept": "use", "accept_with_rework": "repair", "reject_redo": "redo"}[target["judgment"]["decision"]],
                disposition="eligible", provenance="public", arrival_index=2,
            )
            delayed = DelayedCreditLedger()
            before = deepcopy(boundary.policy.__dict__)
            started = time.perf_counter()
            committed = delayed.apply_once(
                credit, lambda _: boundary.policy.observe_feedback(feedback),
                snapshot=lambda: deepcopy(boundary.policy.__dict__),
                restore=lambda state: (boundary.policy.__dict__.clear(), boundary.policy.__dict__.update(state)),
            )
            update = {"status": "UPDATED" if committed else "NOOP", "updates": boundary.policy.updates,
                      "credit": credit.__dict__, "feedback": feedback.__dict__,
                      "latency_seconds": time.perf_counter() - started,
                      "state_before_digest": _digest(before), "state_after_digest": _digest(boundary.policy.snapshot())}
            _save(arm_dir / "delayed_update.json", update)
            _log(raw, "delayed_update", update)
    post = _select_post_update(boundary, arm, features, 2)
    _save(arm_dir / "post_update_selection.json", {
        "selected_key": post.native_selection.chosen_peer_id + "@v1",
        "propensity": post.native_selection.propensity,
        "probabilities": list(post.policy_selection.probabilities),
        "policy_updates": boundary.policy.updates,
        "preview_only": True,
        "ledger_included": False,
    })
    _log(raw, "post_update_selection", {"selected_key": post.native_selection.chosen_peer_id + "@v1", "updates": boundary.policy.updates})
    result = {
        "arm": arm, "status": "COMPLETE_DEVELOPMENT_ONLY", "passed": True,
        "source": source, "target": target, "source_eligible": source_eligible,
        "update": update, "post_update_selection": {
            "selected_key": post.native_selection.chosen_peer_id + "@v1",
            "propensity": post.native_selection.propensity,
            "probabilities": list(post.policy_selection.probabilities),
            "preview_only": True,
            "ledger_included": False,
        },
        "policy_updates": boundary.policy.updates,
        "ledger_event_count": len(boundary.ledger.events),
        "cost": {
            "scorer_seconds": sum(
                float(value.get("scorer_wall_seconds", 0.0))
                for value in (
                    source["producer_score"], source["outcome"],
                    target["producer_score"], target["outcome"],
                )
            ),
            "update_seconds": float(update.get("latency_seconds", 0.0) or 0.0),
            "action_wall_seconds": (
                float(source["action"].get("action_wall_seconds", 0.0))
                + float(target["action"].get("action_wall_seconds", 0.0))
            ),
            "repair_cost": (
                float(source["action"].get("repair_cost", 0.0))
                + float(target["action"].get("repair_cost", 0.0))
            ),
            "state_bytes": len(json.dumps(
                boundary.policy.snapshot(), sort_keys=True, default=str
            ).encode("utf-8")),
        },
        "scientific_claim_allowed": False,
        "interpretation": "single-root live development evidence only; no benchmark, efficacy, or specialization claim",
        "ledger": boundary.ledger.events,
    }
    _save(arm_dir / "ledger.json", boundary.ledger.events)
    native_root, auxiliary_root = boundary.validate_selection_manifests()
    _save(arm_dir / "selection_bindings.json", selection_bindings)
    _save(arm_dir / "manifest_roots.json", {"native": native_root, "auxiliary": auxiliary_root})
    result["selection_bindings"] = selection_bindings
    result["manifest_roots"] = {"native": native_root, "auxiliary": auxiliary_root}
    _save(arm_dir / "summary.json", result)
    return result


def run(out_dir: Path, *, card_path: Path = CARD) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    card_path = card_path.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    _validate_responsibility_card(card)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    declared_commit = card.get("source_commit")
    if not isinstance(declared_commit, str) or len(declared_commit) < 7:
        raise RuntimeError("card source_commit must be a non-empty git revision")
    ancestor_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", declared_commit, commit],
        cwd=ROOT, check=False,
    )
    if ancestor_check.returncode != 0:
        raise RuntimeError(
            f"card source_commit {declared_commit!r} is not an ancestor of running HEAD {commit!r}; "
            "re-freeze the card before running"
        )
    try:
        card_label = str(card_path.relative_to(ROOT))
    except ValueError:
        card_label = str(card_path)
    top = {
        "version": card.get("runner_version", VERSION), "card": card_label,
        "card_sha256": _sha_file(card_path), "source_commit": commit,
        "task_id": TASK_ID, "arms": list(ARMS), "decisions_per_arm": 3,
        "real_api_calls": "counted_from_raw_request_start", "gpu_jobs": 0,
        "scientific_claim_allowed": False, "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "no_retries": True,
    }
    _save(out_dir / "config.json", top)
    results: list[dict[str, Any]] = []
    for arm in ARMS:
        try:
            results.append(_run_arm(arm, out_dir, card))
        except Exception as exc:
            arm_dir = out_dir / arm
            arm_dir.mkdir(parents=True, exist_ok=True)
            raw = arm_dir / "raw.jsonl"
            if not raw.exists():
                raw.write_text("", encoding="utf-8")
            _log(raw, "arm_failure", {"error_type": type(exc).__name__, "error": str(exc)})
            failure = {"arm": arm, "status": "UNKNOWN", "passed": False,
                       "error_type": type(exc).__name__, "error": str(exc),
                       "scientific_claim_allowed": False, "failure_preserved": True}
            _save(arm_dir / "failure.json", failure)
            results.append(failure)
    request_count = 0
    for path in out_dir.glob("*/raw.jsonl"):
        request_count += sum(1 for line in path.read_text(encoding="utf-8").splitlines()
                             if json.loads(line).get("event_type") == "request_start")
    result = {**top, "results": results, "real_api_calls": request_count,
              "ended_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "COMPLETE_DEVELOPMENT_ONLY" if results and all(r.get("passed") is True for r in results) else "UNKNOWN",
              "passed": bool(results) and all(r.get("passed") is True for r in results),
              "interpretation": "C1 is a bounded single-root live development card; scientific confirmation remains closed"}
    _save(out_dir / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--card", type=Path, default=CARD)
    args = parser.parse_args()
    result = run(args.output, card_path=args.card)
    print(json.dumps({k: result.get(k) for k in ("status", "passed", "real_api_calls", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
