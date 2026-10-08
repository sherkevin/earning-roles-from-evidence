"""CPU-only composition of the pinned PIPE3 episode with the versioned boundary.

This qualification keeps the existing v2 producer/recipient/adoption scorers and
the PIPE3 action validator, then routes their canonical judgment through one
``Pipe3SelectionBoundary``.  The boundary writes the first selection, delivery,
judgment, action and outcome; the v4 source-bound adapter seals that judgment as
public evidence for a later selection on the same boundary.  It uses two
ownership controls and makes no API/GPU call or scientific claim.
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

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, ProducerScore, RecipientJudgment, TerminalOutcome,
)
from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_profile_episode_qualification import (  # noqa: E402
    _log, _patch_producer, _patch_recipient, _run_scorers, PROFILE_FIELDS,
)
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    prepare_pipe3_action, validate_pipe3_action_result,
)
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary, auxiliary_manifest_root, make_offer,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest  # noqa: E402
from peerrolebench_policy_sidecar import FeedbackSidecar  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402


TASK_ID = "PIPE3_stream_processing"


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _event_record(boundary: Pipe3SelectionBoundary, event_type: str, event_id: str) -> dict[str, Any]:
    id_fields = {
        "peer_selection": "selection_id", "producer_delivery": "delivery_id",
        "recipient_judgment": "judgment_id", "consumer_action": "action_id",
        "terminal_outcome": "outcome_id",
    }
    field = id_fields[event_type]
    return next(
        row for row in boundary.ledger.events
        if row["event_type"] == event_type and row["payload"].get(field) == event_id
    )


def _run_case(*, case: str, boundary: Pipe3SelectionBoundary,
              selection_sidecar: Any,
              materials: dict[str, Any], delivery_sources: Mapping[str, str],
              final_sources: Mapping[str, str], out: Path, log: Path, seed: int) -> dict[str, Any]:
    info = interfaces(materials)
    delivery_digest = digest_files(delivery_sources)
    before_sources = dict(materials["agent_payloads"]["recipient"]["source_files"])
    before_sources["producer.py"] = delivery_sources["producer.py"]
    (out / "before_action").mkdir(parents=True, exist_ok=True)
    producer, recipient, adoption = _run_scorers(before_sources, info, out / "before_action", log, seed)

    boundary.ledger.record_task_start(TASK_ID, 0)
    boundary.ledger.record_delivery(Delivery(
        f"delivery-{case}", TASK_ID, "peer-b", "peer-a", delivery_digest,
        f"produce-{case}", 0, f"selection-{case}",
    ))
    delivery_record = _event_record(boundary, "producer_delivery", f"delivery-{case}")
    producer_score_digest = producer.get("response_digest") or _sha_text(
        json.dumps(producer, sort_keys=True, ensure_ascii=False, default=str)
    )
    boundary.ledger.record_producer_score(ProducerScore(
        f"producer-score-{case}", f"delivery-{case}", delivery_digest,
        producer.get("scorer_version", "pipe3-producer-objective-v2"),
        producer.get("status", "UNKNOWN"), producer.get("label"),
        producer.get("quality_score"), producer_score_digest,
        producer.get("coverage_complete") is True, producer.get("decision_complete") is True,
    ))
    boundary.ledger.record_judgment(RecipientJudgment(
        f"judgment-{case}", f"delivery-{case}", "peer-a", "accept_with_rework", delivery_digest,
        repair_note="CPU versioned-boundary qualification",
    ))
    action_payload = prepare_pipe3_action(materials, delivery_sources, "repair")
    final_snapshot = dict(action_payload["source_files"])
    final_snapshot.update({"producer.py": final_sources["producer.py"], "processor.py": final_sources["processor.py"]})
    action_result = validate_pipe3_action_result(action_payload, final_snapshot)
    boundary.ledger.record_action(ConsumerAction(
        f"action-{case}", f"delivery-{case}", "peer-a", True, delivery_digest,
        action_result["output_source_sha256"], 0.0, "repair",
    ))
    (out / "after_action").mkdir(parents=True, exist_ok=True)
    _, recipient_after, adoption_after = _run_scorers(final_snapshot, info, out / "after_action", log, seed)
    outcome_payload = {
        "status": "PASS" if recipient_after.get("status") == "PASS" and adoption_after.get("status") == "PASS" else "FAIL",
        "coverage_complete": recipient_after.get("coverage_complete") is True and adoption_after.get("coverage_complete") is True,
        "decision_complete": recipient_after.get("decision_complete") is True and adoption_after.get("decision_complete") is True,
    }
    outcome = TerminalOutcome(
        f"outcome-{case}", f"delivery-{case}", outcome_payload["status"] == "PASS" and outcome_payload["coverage_complete"] and outcome_payload["decision_complete"],
        "pipe3-recipient-objective-v2", float(adoption_after.get("quality_score") or 0.0),
        _sha_text(json.dumps(outcome_payload, sort_keys=True)),
    )
    boundary.ledger.record_outcome(outcome)
    judgment = {"observed_artifact_sha256": delivery_digest,
                "target_role": "producer" if case == "producer_fix" else "recipient"}
    eligibility = producer_feedback_eligibility(materials, producer, judgment, action_result, outcome_payload)
    eligible = bool(eligibility["producer_feedback_eligible"])
    policy_update_allowed = bool(eligibility["policy_update_allowed"])
    # The current responsibility contract intentionally keeps policy updates
    # closed until the later-use gate is implemented.  Preserve that boundary:
    # an ELIGIBLE diagnostic status is not itself a public learning label.
    public_label = 1.0 if policy_update_allowed else None
    public_disposition = "eligible" if policy_update_allowed else "unknown"
    public_provenance = "public" if policy_update_allowed else "unknown"
    unknown_reason = None if policy_update_allowed else "policy-update-gate-closed"

    selection = boundary.selections[f"policy-selection-{case}"]
    selection_record = _event_record(boundary, "peer_selection", f"selection-{case}")
    judgment_record = _event_record(boundary, "recipient_judgment", f"judgment-{case}")
    action_record = _event_record(boundary, "consumer_action", f"action-{case}")
    sidecar = FeedbackSidecar(
        ledger_record_hash=judgment_record["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id=f"judgment-{case}", feedback_id=f"feedback-{case}",
        source_event_id=selection.event_id, selection_event_id=f"selection-{case}",
        delivery_id=f"delivery-{case}", producer_id="peer-b", producer_version="v1",
        recipient_id="peer-a", source="recipient_judgment", arrived_at=1.0, delay=1.0,
        action="repair", disposition=public_disposition,
        provenance=public_provenance, label_mapping_version="pipe3-label-v1",
        mapping_digest="d" * 64, responsibility_status="attributed" if policy_update_allowed else "pending_attribution",
        attribution_basis=eligibility["reason"], artifact_sha256=delivery_digest,
        delivery_record_hash=delivery_record["record_hash"], action_id=f"action-{case}",
        action_record_hash=action_record["record_hash"], raw_value="accept_with_rework",
        label=public_label, arrival_index=1,
        sidecar_version="peerrole-policy-sidecar-v4",
    )
    gate_payload = {
        "gate_version": "producer-feedback-eligibility-v1", "ledger_record_hash": sidecar.ledger_record_hash,
        "sidecar_digest": sidecar.sidecar_digest, "protocol_event_type": sidecar.protocol_event_type,
        "protocol_event_id": sidecar.protocol_event_id, "source_event_id": sidecar.source_event_id,
        "delivery_id": sidecar.delivery_id, "producer_id": sidecar.producer_id,
        "producer_version": sidecar.producer_version, "recipient_id": sidecar.recipient_id,
        "selection_event_id": sidecar.selection_event_id, "eligible": policy_update_allowed,
        "weight": 1.0 if policy_update_allowed else None, "label": public_label,
        "label_mapping_version": sidecar.label_mapping_version, "evidence_version": "pipe3-cpu-v1", "source_index": 0,
    }
    gate = AttributionGate(**gate_payload, gate_digest=_digest(gate_payload))
    schedule = (ArrivalAssignment(sidecar.feedback_id, sidecar.protocol_event_type,
                                  sidecar.protocol_event_id, sidecar.source_event_id, 1),)
    source_offer = build_source_bound_offer(
        selection=selection_sidecar,
        selection_record=selection_record,
        feedback_inputs=((sidecar, judgment_record, gate, unknown_reason),),
        ledger=boundary.ledger, arrival_schedule=schedule, offer_id=f"offer-{case}",
        context_key="PIPE3:1", target_task_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    seal1 = boundary.choose_and_seal_source_bound(
        source_offer=source_offer, native_selection_id=f"selection-{case}-1", selector_id="peer-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(1), state_version="cpu-state-1",
        encoder_version="cpu-encoder-1", feature_schema="pipe3", policy_version="contextual-v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=1,
        selected_at=2.0, read_cut=1, decision_index=1, consume_evidence=True,
    )
    checks = {
        "scorer_outcome_complete": eligibility["q_complete"] and eligibility["outcome_complete"],
        "same_canonical_boundary": source_offer.offer.task_index == 1 and seal1.native_selection.task_index == 1,
        "responsibility_gate_blocks_update": (not policy_update_allowed) and boundary.policy.updates == 0,
        "unknown_has_no_update": (not policy_update_allowed) and boundary.policy.updates == 0,
        "selection_manifests_validate": all(boundary.validate_selection_manifests()),
    }
    return {
        "case": case, "checks": checks, "eligibility": eligibility,
        "public_feedback": {"disposition": public_disposition, "provenance": public_provenance,
                             "unknown_reason": unknown_reason, "label": public_label},
        "producer_score": producer, "recipient_before": recipient, "recipient_after": recipient_after,
        "adoption_after": adoption_after, "source_offer": source_offer.offer.payload(),
        "selection1": seal1.native_selection.selection_id, "policy_updates": boundary.policy.updates,
        "ledger_event_count": len(boundary.ledger.events), "auxiliary_manifest_rows": len(boundary.auxiliary_manifest_rows),
    }


def run(out_dir: Path, *, seed: int = 0) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    generated = load_pipe3(seed)
    materials = build_materials(generated)
    base = dict(materials["agent_payloads"]["producer"]["source_files"])
    base.update(materials["agent_payloads"]["recipient"]["source_files"])
    recipient_correct = _patch_recipient(base)
    producer_correct = _patch_producer(base)
    producer_final = _patch_recipient(producer_correct)
    config = {
    "qualification": "pipe3-versioned-source-bound-composition-v3", "task_id": TASK_ID, "seed": seed,
        "cases": ["producer_fix", "recipient_fix"], "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "runner": "Pipe3SelectionBoundary+source-bound-v2",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(), "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw = out_dir / "events.jsonl"
    _log(raw, "config", config)
    cases = []
    for case in ("producer_fix", "recipient_fix"):
        case_materials = deepcopy(materials)
        if case == "producer_fix":
            case_materials["agent_payloads"]["recipient"]["source_files"]["processor.py"] = recipient_correct["processor.py"]
            delivery_sources = {"producer.py": base["producer.py"]}
        else:
            delivery_sources = {"producer.py": producer_correct["producer.py"]}
        boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
        offer0 = make_offer(offer_id=f"offer-{case}-0", task_id=TASK_ID, task_index=0, role="producer",
                            context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=(),
                            evidence_version="pipe3-cpu-v1", available_index=0)
        seal0 = boundary.choose_and_seal(offer=offer0, native_selection_id=f"selection-{case}", selector_id="peer-a",
                                         role="producer", base_scores=(100.0, -100.0), rng=np.random.default_rng(0),
                                         state_version="cpu-state-0", encoder_version="cpu-encoder-0", feature_schema="pipe3",
                                         policy_version="contextual-v1", base_score_version="base-v1", rng_algorithm="numpy-pcg64",
                                         rng_draw=0, selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=False)
        cases.append(_run_case(case=case, boundary=boundary, selection_sidecar=seal0.decision_sidecar, materials=case_materials,
                               delivery_sources=delivery_sources, final_sources=producer_final,
                               out=out_dir / case, log=raw, seed=seed))
    passed = all(all(case["checks"].values()) for case in cases)
    result = {**config, "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE", "passed": passed,
              "cases": cases, "elapsed_cpu_seconds": time.perf_counter() - started,
              "ended_at_utc": datetime.now(timezone.utc).isoformat(),
              "interpretation": "real pinned CPU scorer/action/outcome composed with canonical source-bound next selection; no efficacy claim",
              "remaining_gates": ["isolated live runner with real actor and scorer IPC", "independent histories", "same-information baseline parity", "later-use outcome"]}
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir.resolve())
    print(json.dumps({k: result[k] for k in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
