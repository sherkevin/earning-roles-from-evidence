"""Offline isolated PIPE3 live-trace qualification.

This is a deliberately small composition check.  It reuses the pinned PIPE3
CPU scorers and action validator, then sends only a public profile through the
existing separate-process policy reader before the source-bound selection on
the same canonical boundary.  The responsibility gate is intentionally
closed in this qualification, so the public feedback is UNKNOWN and no
policy update may occur.  It makes no API or GPU call and is not a benchmark
result.
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
from types import SimpleNamespace
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    ProducerScore,
    RecipientJudgment,
    TerminalOutcome,
)
from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_metateam_profile_qualification import profile  # noqa: E402
from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_profile_episode_qualification import (  # noqa: E402
    _log,
    _patch_producer,
    _patch_recipient,
    _run_scorers,
)
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    prepare_pipe3_action,
    validate_pipe3_action_result,
)
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary,
    auxiliary_manifest_root,
    make_offer,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest  # noqa: E402
from peerrolebench_policy_sidecar import FeedbackSidecar  # noqa: E402
from peerrolebench_isolated_policy_read import read_profiles_isolated  # noqa: E402
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402


TASK_ID = "PIPE3_stream_processing"
TRACE_SCHEMA = "pipe3-isolated-live-trace-v1"
PUBLIC_EVENT_KEYS = {
    "actor_output": {"actor_role", "artifact_sha256", "public_paths"},
    "scorer_before": {"scorer", "status", "label", "quality_score", "artifact_sha256", "decision_complete", "coverage_complete"},
    "action": {"consumer_action", "changed_paths", "input_source_sha256", "output_source_sha256", "public_writable_paths"},
    "scorer_after": {"scorer", "status", "label", "quality_score", "artifact_sha256", "decision_complete", "coverage_complete"},
    "outcome": {"status", "quality_score", "coverage_complete", "decision_complete", "artifact_sha256"},
    "policy_read": {"offer_id", "offer_digest", "profile_ids", "read_cut", "policy_input_digest", "public_profiles_digest", "worker_sha256"},
}


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _event_record(boundary: Pipe3SelectionBoundary, event_type: str, event_id: str) -> dict[str, Any]:
    id_fields = {
        "peer_selection": "selection_id",
        "recipient_judgment": "judgment_id",
        "consumer_action": "action_id",
    }
    field = id_fields[event_type]
    return next(
        row for row in boundary.ledger.events
        if row["event_type"] == event_type and row["payload"].get(field) == event_id
    )


def _public_score(name: str, result: Mapping[str, Any], artifact: str) -> dict[str, Any]:
    return {
        "scorer": name,
        "status": result.get("status"),
        "label": result.get("label"),
        "quality_score": result.get("quality_score"),
        "artifact_sha256": artifact,
        "decision_complete": result.get("decision_complete"),
        "coverage_complete": result.get("coverage_complete"),
    }


def _append_trace(trace: list[dict[str, Any]], event: str, payload: Mapping[str, Any]) -> None:
    expected = PUBLIC_EVENT_KEYS[event]
    if set(payload) != expected:
        raise AssertionError(f"public payload key mismatch for {event}: {sorted(payload)}")
    trace.append({"seq": len(trace), "event": event, "payload": dict(payload)})


def run(out_dir: Path, *, seed: int = 0) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    raw_log = out_dir / "events.jsonl"
    generated = load_pipe3(seed)
    materials = build_materials(generated)
    base = dict(materials["agent_payloads"]["producer"]["source_files"])
    base.update(materials["agent_payloads"]["recipient"]["source_files"])
    producer_correct = _patch_producer(base)
    producer_final = _patch_recipient(producer_correct)
    case_materials = deepcopy(materials)
    case_materials["agent_payloads"]["recipient"]["source_files"]["processor.py"] = _patch_recipient(base)["processor.py"]
    delivery_sources = {"producer.py": producer_correct["producer.py"]}
    final_sources = producer_final
    info = interfaces(case_materials)
    delivery_digest = digest_files(delivery_sources)
    config = {
        "qualification": TRACE_SCHEMA,
        "task_id": TASK_ID,
        "seed": seed,
        "case": "recipient_owned_gate_closed",
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "fixture_mode": "pinned-pipe3-cpu-scorer-action-isolated-public-profile-read",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    _log(raw_log, "config", config)
    trace: list[dict[str, Any]] = []

    # The first selection is the actor's assignment context.  The source text
    # itself is kept in the scorer workspace; the public trace carries only a
    # digest and paths.
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    offer0 = make_offer(
        offer_id="isolated-live-offer-0", task_id=TASK_ID, task_index=0,
        role="producer", context_key="PIPE3:0",
        candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=(),
        evidence_version="pipe3-cpu-v1", available_index=0,
    )
    seal0 = boundary.choose_and_seal(
        offer=offer0, native_selection_id="isolated-live-selection-0", selector_id="peer-a",
        role="producer", base_scores=(100.0, -100.0), rng=np.random.default_rng(seed),
        state_version="isolated-live-state-0", encoder_version="isolated-live-encoder-0",
        feature_schema="pipe3", policy_version="contextual-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0, read_cut=0,
        decision_index=0, consume_evidence=False,
    )

    _append_trace(trace, "actor_output", {
        "actor_role": "producer",
        "artifact_sha256": delivery_digest,
        "public_paths": ["producer.py"],
    })
    before_dir = out_dir / "before_action"
    producer, recipient_before, adoption_before = _run_scorers(
        {**case_materials["agent_payloads"]["recipient"]["source_files"], "producer.py": delivery_sources["producer.py"]},
        info, before_dir, raw_log, seed,
    )
    _append_trace(trace, "scorer_before", _public_score("pipe3-producer-recipient-adoption-v2", producer, delivery_digest))

    boundary.ledger.record_task_start(TASK_ID, 0)
    boundary.ledger.record_delivery(Delivery(
        "isolated-live-delivery", TASK_ID, "peer-b", "peer-a", delivery_digest,
        "isolated-live-selection-0", 0, "isolated-live-selection-0",
    ))
    boundary.ledger.record_producer_score(ProducerScore(
        "isolated-live-producer-score", "isolated-live-delivery", delivery_digest,
        producer.get("scorer_version", "pipe3-producer-objective-v2"), producer.get("status", "UNKNOWN"),
        producer.get("label"), producer.get("quality_score"), producer.get("response_digest", _sha_text(json.dumps(producer, sort_keys=True, default=str))),
        producer.get("coverage_complete") is True, producer.get("decision_complete") is True,
    ))
    boundary.ledger.record_judgment(RecipientJudgment(
        "isolated-live-judgment", "isolated-live-delivery", "peer-a", "accept_with_rework",
        delivery_digest, repair_note="isolated live trace qualification",
    ))

    action_payload = prepare_pipe3_action(case_materials, delivery_sources, "repair")
    action_snapshot = dict(action_payload["source_files"])
    action_snapshot.update({"producer.py": final_sources["producer.py"], "processor.py": final_sources["processor.py"]})
    action_result = validate_pipe3_action_result(action_payload, action_snapshot)
    boundary.ledger.record_action(ConsumerAction(
        "isolated-live-action", "isolated-live-delivery", "peer-a", True, delivery_digest,
        action_result["output_source_sha256"], 0.0, "repair",
    ))
    _append_trace(trace, "action", {
        "consumer_action": action_result["consumer_action"],
        "changed_paths": action_result["changed_paths"],
        "input_source_sha256": action_result["input_source_sha256"],
        "output_source_sha256": action_result["output_source_sha256"],
        "public_writable_paths": sorted(action_payload["writable_paths"]),
    })

    _, recipient_after, adoption_after = _run_scorers(
        action_snapshot, info, out_dir / "after_action", raw_log, seed,
    )
    _append_trace(trace, "scorer_after", _public_score("pipe3-recipient-adoption-v2", recipient_after, delivery_digest))
    outcome_payload = {
        "status": "PASS" if recipient_after.get("status") == "PASS" and adoption_after.get("status") == "PASS" else "FAIL",
        "quality_score": float(adoption_after.get("quality_score") or 0.0),
        "coverage_complete": recipient_after.get("coverage_complete") is True and adoption_after.get("coverage_complete") is True,
        "decision_complete": recipient_after.get("decision_complete") is True and adoption_after.get("decision_complete") is True,
        "artifact_sha256": delivery_digest,
    }
    boundary.ledger.record_outcome(TerminalOutcome(
        "isolated-live-outcome", "isolated-live-delivery", outcome_payload["status"] == "PASS" and outcome_payload["coverage_complete"] and outcome_payload["decision_complete"],
        "pipe3-recipient-objective-v2", outcome_payload["quality_score"], _sha_text(json.dumps(outcome_payload, sort_keys=True)),
    ))
    _append_trace(trace, "outcome", outcome_payload)

    eligibility = producer_feedback_eligibility(
        case_materials, producer,
        {"observed_artifact_sha256": delivery_digest, "target_role": "recipient"},
        action_result, outcome_payload,
    )
    # Responsibility is intentionally closed in this qualification.  Keep the
    # candidate's diagnostic eligibility separate from public update permission.
    policy_update_allowed = bool(eligibility["policy_update_allowed"])
    if policy_update_allowed:
        raise AssertionError("qualification fixture unexpectedly opened policy update gate")

    records = {
        event_type: _event_record(boundary, event_type, event_id)
        for event_type, event_id in (
            ("peer_selection", "isolated-live-selection-0"),
            ("recipient_judgment", "isolated-live-judgment"),
            ("consumer_action", "isolated-live-action"),
        )
    }
    sidecar = FeedbackSidecar(
        ledger_record_hash=records["recipient_judgment"]["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id="isolated-live-judgment", feedback_id="isolated-live-feedback",
        source_event_id=seal0.policy_selection.event_id, selection_event_id="isolated-live-selection-0",
        delivery_id="isolated-live-delivery", producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        source="recipient_judgment", arrived_at=1.0, delay=1.0, action="repair", disposition="unknown",
        provenance="unknown", label_mapping_version="pipe3-label-v1", mapping_digest="d" * 64,
        responsibility_status="pending_attribution", attribution_basis=eligibility["reason"], artifact_sha256=delivery_digest,
        delivery_record_hash=boundary.ledger.events[2]["record_hash"], action_id="isolated-live-action",
        action_record_hash=records["consumer_action"]["record_hash"], raw_value="accept_with_rework", label=None,
        arrival_index=1, sidecar_version="peerrole-policy-sidecar-v4",
    )
    gate_payload = {
        "gate_version": "producer-feedback-eligibility-v1", "ledger_record_hash": sidecar.ledger_record_hash,
        "sidecar_digest": sidecar.sidecar_digest, "protocol_event_type": sidecar.protocol_event_type,
        "protocol_event_id": sidecar.protocol_event_id, "source_event_id": sidecar.source_event_id,
        "delivery_id": sidecar.delivery_id, "producer_id": sidecar.producer_id, "producer_version": sidecar.producer_version,
        "recipient_id": sidecar.recipient_id, "selection_event_id": sidecar.selection_event_id,
        "eligible": False, "weight": None, "label": None, "label_mapping_version": sidecar.label_mapping_version,
        "evidence_version": "pipe3-cpu-v1", "source_index": 0,
    }
    gate = AttributionGate(**gate_payload, gate_digest=_digest(gate_payload))
    schedule = (ArrivalAssignment(sidecar.feedback_id, sidecar.protocol_event_type, sidecar.protocol_event_id, sidecar.source_event_id, 1),)
    source_offer = build_source_bound_offer(
        selection=seal0.decision_sidecar, selection_record=records["peer_selection"],
        feedback_inputs=((sidecar, records["recipient_judgment"], gate, "recipient-owned-or-unattributed"),),
        ledger=boundary.ledger, arrival_schedule=schedule, offer_id="isolated-live-source-offer",
        context_key="PIPE3:1", target_task_index=1, previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )

    # Exercise the existing isolated assignment runner with a public profile.
    # It is a read-only profile fixture here: no hidden scorer output or source
    # text crosses the process boundary.
    assignment_offer = MetaTeamAssignmentOffer.build(
        offer_id="isolated-live-assignment-offer", task_id=TASK_ID, decision_index=1, read_cut=1,
        candidate_keys=("peer-b@v1", "peer-c@v1"),
        profiles=(profile(
            profile_id="isolated-live-profile-r1", candidate_key="peer-b@v1", producer_id="peer-b",
            selected_candidate_key="peer-b@v1", source_decision_index=0,
            source_arrival_index=1, available_index=1,
        ),),
    )
    from peerrolebench_pipe3_assignment_runner import Pipe3AssignmentRunner  # noqa: E402
    isolated_runner = Pipe3AssignmentRunner(assignment_offer)
    isolated_runner.emit_offer()
    read_attestation = isolated_runner.consume_profiles(("isolated-live-profile-r1",), isolated_policy_read=True)
    isolated_runner.seal_selection(
        SimpleNamespace(candidates=(SimpleNamespace(key="peer-b@v1"), SimpleNamespace(key="peer-c@v1")), task_index=1, selected_at=1.0),
        read_attestation,
    )
    read = read_profiles_isolated(assignment_offer, ("isolated-live-profile-r1",), read_cut=1)
    _append_trace(trace, "policy_read", {
        "offer_id": assignment_offer.offer_id,
        "offer_digest": assignment_offer.offer_digest,
        "profile_ids": list(read.profile_ids),
        "read_cut": read.read_cut,
        "policy_input_digest": read.policy_input_digest,
        "public_profiles_digest": read.public_profiles_digest,
        "worker_sha256": read.worker_sha256,
    })

    seal1 = boundary.choose_and_seal_source_bound(
        source_offer=source_offer, native_selection_id="isolated-live-selection-1", selector_id="peer-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(1), state_version="isolated-live-state-1",
        encoder_version="isolated-live-encoder-1", feature_schema="pipe3", policy_version="contextual-v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=2.0,
        read_cut=1, decision_index=1, consume_evidence=True,
    )
    checks = {
        "ordered_actor_scorer_action_outcome_policy_read": [e["event"] for e in trace] == ["actor_output", "scorer_before", "action", "scorer_after", "outcome", "policy_read"],
        "public_payload_only": all(set(e["payload"]) == PUBLIC_EVENT_KEYS[e["event"]] for e in trace),
        "isolated_policy_read": bool(read_attestation and isolated_runner.isolated_policy_trace),
        "source_bound_selection_after_read": seal1.native_selection.task_index == 1 and trace[-1]["event"] == "policy_read",
        "responsibility_gate_closed": not policy_update_allowed,
        "unknown_no_update": sidecar.label is None and boundary.policy.updates == 0,
        "manifests_validate": all(boundary.validate_selection_manifests()),
    }
    result = {
        **config,
        "status": "QUALIFIED_OFFLINE" if all(checks.values()) else "FAILED_OFFLINE",
        "passed": all(checks.values()),
        "trace": trace,
        "isolated_runner_trace": isolated_runner.trace,
        "checks": checks,
        "policy_update_allowed": policy_update_allowed,
        "policy_updates": boundary.policy.updates,
        "source_offer": source_offer.offer.payload(),
        "selection_id_after_policy_read": seal1.native_selection.selection_id,
        "ledger_event_count": len(boundary.ledger.events),
        "elapsed_cpu_seconds": time.perf_counter() - started,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "offline composition qualification only; no live API/GPU or efficacy claim",
        "remaining_gates": ["real actor/scorer IPC runner", "independent histories", "same-information baseline parity", "later-use outcome"],
    }
    (out_dir / "trace.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in trace) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir.resolve())
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed", "policy_updates")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
