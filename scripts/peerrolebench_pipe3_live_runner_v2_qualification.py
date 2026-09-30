"""Zero-call, root-specific PIPE3 live-runner promotion qualification.

This runner is deliberately a small promotion gate, not a benchmark.  It
reuses the pinned PIPE3 material/scorers/action validator and the versioned
source-bound selection boundary.  Each control owns a fresh policy, ledger,
RNG namespace and output directory.  The responsibility gate remains the
source of truth: producer-owned evidence is diagnostic ``ELIGIBLE`` but is
recorded as public ``UNKNOWN`` while ``policy_update_allowed`` is false.
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
import traceback
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
from peerrolebench_isolated_policy_read import read_source_offer_isolated  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_profile_episode_qualification import (  # noqa: E402
    _log, _patch_producer, _patch_recipient, _run_scorers,
)
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    prepare_pipe3_action, validate_pipe3_action_result,
)
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary, auxiliary_manifest_root, make_offer,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest  # noqa: E402
from peerrolebench_policy_sidecar import FeedbackSidecar  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402


TASK_ID = "PIPE3_stream_processing"
RUNNER_VERSION = "pipe3-live-runner-v2-qualification"
CONTROLS = ("producer_owned", "recipient_owned")


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _record(boundary: Pipe3SelectionBoundary, event_type: str, event_id: str) -> dict[str, Any]:
    fields = {
        "peer_selection": "selection_id", "producer_delivery": "delivery_id",
        "producer_score": "producer_score_id", "recipient_judgment": "judgment_id",
        "consumer_action": "action_id", "terminal_outcome": "outcome_id",
    }
    field = fields[event_type]
    return next(row for row in boundary.ledger.events
                if row["event_type"] == event_type and row["payload"].get(field) == event_id)


def _public_score(name: str, result: Mapping[str, Any], artifact: str) -> dict[str, Any]:
    return {
        "scorer": name, "status": result.get("status"), "label": result.get("label"),
        "quality_score": result.get("quality_score"), "artifact_sha256": artifact,
        "decision_complete": result.get("decision_complete"),
        "coverage_complete": result.get("coverage_complete"),
    }


def _cost(elapsed: float, *, scorer_calls: int = 0, repair: int = 0) -> dict[str, Any]:
    # This qualification has no LLM/provider path.  Keep a stable complete
    # schema so an eventual live runner cannot silently omit a cost component.
    return {
        "api_calls": 0, "gpu_jobs": 0, "tokens": 0, "wall_seconds": round(float(elapsed), 6),
        "scorer_calls": int(scorer_calls), "retry_count": 0, "communication_records": 0,
        "repair_count": int(repair), "replay_events": 0,
    }


def _emit(raw: Any, trace: list[dict[str, Any]], *, control: str, stream_id: str,
          event: str, payload: Mapping[str, Any], started: float,
          cost: Mapping[str, Any], unknown_reason: str | None = None) -> None:
    row = {
        "seq": len(trace), "control": control, "stream_id": stream_id, "event": event,
        "payload": dict(payload), "cost": dict(cost),
        "unknown_reason": unknown_reason,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    trace.append(row)
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n")
        handle.flush()


def _episode_materials(materials: dict[str, Any], control: str) -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
    base = dict(materials["agent_payloads"]["producer"]["source_files"])
    base.update(materials["agent_payloads"]["recipient"]["source_files"])
    producer_correct = _patch_producer(base)
    recipient_correct = _patch_recipient(base)
    producer_final = _patch_recipient(producer_correct)
    case_materials = deepcopy(materials)
    if control == "producer_owned":
        # Qp fails on the delivered producer; recipient sources are fixed so a
        # producer-owned repair is the only change in the action stage.
        case_materials["agent_payloads"]["recipient"]["source_files"]["processor.py"] = recipient_correct["processor.py"]
        delivery = {"producer.py": base["producer.py"]}
    elif control == "recipient_owned":
        # Qp passes; action changes recipient-owned processor.py, which must
        # remain UNKNOWN for producer learning.
        delivery = {"producer.py": producer_correct["producer.py"]}
    else:
        raise ValueError(f"unknown control {control!r}")
    return case_materials, delivery, producer_final


def _run_control(control: str, *, out: Path, seed: int, stream_id: str) -> dict[str, Any]:
    started = time.perf_counter()
    out.mkdir(parents=True, exist_ok=False)
    raw = out / "raw.jsonl"
    worker_log = out / "worker_events.jsonl"
    generated = load_pipe3(seed)
    materials = build_materials(generated)
    case_materials, delivery_sources, final_sources = _episode_materials(materials, control)
    info = interfaces(case_materials)
    policy = ContextualTrustPolicy()
    boundary = Pipe3SelectionBoundary(policy, registry())
    rng = np.random.default_rng(seed + (11 if control == "producer_owned" else 29))
    trace: list[dict[str, Any]] = []
    unknown_denominator = {"feedback_rows": 0, "eligible_rows": 0, "unknown_rows": 0}
    stream_config = {
        "runner_version": RUNNER_VERSION, "task_id": TASK_ID, "control": control,
        "stream_id": stream_id, "seed": seed, "rng_namespace": f"{RUNNER_VERSION}:{stream_id}",
        "root": "PIPE3_stream_processing", "split": "qualification_only",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "policy_update_allowed": False, "policy_name": policy.name,
        "baseline_parity_status": "NOT_RUN",
        "independent_live_history_status": "qualification_only",
        "material_adapter": "pipe3-neutral-v1", "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    _json(out / "config.json", {
        **stream_config,
        "candidate_registry_digest": _sha_text(json.dumps([entry.__dict__ for entry in registry()], sort_keys=True, default=str)),
        "schedule_schema": "global-event-index-v1", "schedule_digest": "pending",
        "cost_schema": "pipe3-cost-v1", "unknown_policy": "preserve-reason-no-update",
        "component_sha256": {name: _sha_file(ROOT / name) for name in (
            "scripts/peerrolebench_pipe3_live_runner_v2_qualification.py",
            "scripts/peerrolebench_pipe3_runner_v1.py",
            "scripts/peerrolebench_source_bound_feedback_adapter.py",
            "scripts/peerrolebench_isolated_policy_read.py",
        )},
    })
    with raw.open("w", encoding="utf-8") as handle:
        handle.write("")

    def score_stage(files: Mapping[str, str], stage_dir: Path, stage: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], float]:
        t0 = time.perf_counter()
        stage_dir.mkdir(parents=True, exist_ok=True)
        result = _run_scorers(files, info, stage_dir, worker_log, seed)
        elapsed = time.perf_counter() - t0
        return result[0], result[1], result[2], elapsed

    def record_episode(index: int, *, selection_id: str, selected_peer: str, delivery_sources_i: Mapping[str, str],
                       final_sources_i: Mapping[str, str], context: str) -> dict[str, Any]:
        delivery_digest = digest_files(delivery_sources_i)
        actor_t = time.perf_counter()
        _emit(raw, trace, control=control, stream_id=stream_id, event="actor_output",
              payload={"task_index": index, "actor_role": "producer", "selected_peer": selected_peer,
                       "artifact_sha256": delivery_digest, "public_paths": sorted(delivery_sources_i)},
              started=started, cost=_cost(time.perf_counter() - actor_t))
        before_sources = dict(case_materials["agent_payloads"]["recipient"]["source_files"])
        before_sources["producer.py"] = delivery_sources_i["producer.py"]
        producer, recipient_before, adoption_before, scorer_elapsed = score_stage(
            before_sources, out / f"episode_{index}" / "before_action", "before")
        _emit(raw, trace, control=control, stream_id=stream_id, event="scorer_before",
              payload={"task_index": index, "producer": _public_score("pipe3-producer-objective-v2", producer, delivery_digest),
                       "recipient": _public_score("pipe3-recipient-objective-v2", recipient_before, delivery_digest),
                       "adoption": _public_score("pipe3-recipient-objective-v2", adoption_before, delivery_digest)},
              started=started, cost=_cost(scorer_elapsed, scorer_calls=3))
        boundary.ledger.record_task_start(TASK_ID, index)
        delivery_id = f"{control}-delivery-{index}"
        boundary.ledger.record_delivery(Delivery(
            delivery_id, TASK_ID, selected_peer, "peer-a", delivery_digest,
            f"{control}-selection-{index}", index, f"{control}-selection-{index}",
        ))
        boundary.ledger.record_producer_score(ProducerScore(
            f"{control}-producer-score-{index}", delivery_id, delivery_digest,
            producer.get("scorer_version", "pipe3-producer-objective-v2"), producer.get("status", "UNKNOWN"),
            producer.get("label"), producer.get("quality_score"),
            producer.get("response_digest", _sha_text(json.dumps(producer, sort_keys=True, default=str))),
            producer.get("coverage_complete") is True, producer.get("decision_complete") is True,
        ))
        boundary.ledger.record_judgment(RecipientJudgment(
            f"{control}-judgment-{index}", delivery_id, "peer-a", "accept_with_rework", delivery_digest,
            repair_note=f"{RUNNER_VERSION}:{control}",
        ))
        action_t = time.perf_counter()
        action_payload = prepare_pipe3_action(case_materials, delivery_sources_i, "repair")
        action_snapshot = dict(action_payload["source_files"])
        action_snapshot.update({"producer.py": final_sources_i["producer.py"], "processor.py": final_sources_i["processor.py"]})
        action_result = validate_pipe3_action_result(action_payload, action_snapshot)
        boundary.ledger.record_action(ConsumerAction(
            f"{control}-action-{index}", delivery_id, "peer-a", True, delivery_digest,
            action_result["output_source_sha256"], 0.0, "repair",
        ))
        _emit(raw, trace, control=control, stream_id=stream_id, event="action",
              payload={"task_index": index, "consumer_action": action_result["consumer_action"],
                       "changed_paths": action_result["changed_paths"],
                       "input_source_sha256": action_result["input_source_sha256"],
                       "output_source_sha256": action_result["output_source_sha256"]},
              started=started, cost=_cost(time.perf_counter() - action_t, repair=1))
        _, recipient_after, adoption_after, scorer_after_elapsed = score_stage(
            action_snapshot, out / f"episode_{index}" / "after_action", "after")
        outcome_payload = {
            "task_index": index,
            "status": "PASS" if recipient_after.get("status") == "PASS" and adoption_after.get("status") == "PASS" else "FAIL",
            "quality_score": float(adoption_after.get("quality_score") or 0.0),
            "coverage_complete": recipient_after.get("coverage_complete") is True and adoption_after.get("coverage_complete") is True,
            "decision_complete": recipient_after.get("decision_complete") is True and adoption_after.get("decision_complete") is True,
            "artifact_sha256": delivery_digest,
        }
        outcome_success = outcome_payload["status"] == "PASS" and outcome_payload["coverage_complete"] and outcome_payload["decision_complete"]
        boundary.ledger.record_outcome(TerminalOutcome(
            f"{control}-outcome-{index}", delivery_id, outcome_success,
            "pipe3-recipient-objective-v2", outcome_payload["quality_score"], _sha_text(json.dumps(outcome_payload, sort_keys=True)),
        ))
        _emit(raw, trace, control=control, stream_id=stream_id, event="outcome",
              payload=outcome_payload, started=started, cost=_cost(scorer_after_elapsed, scorer_calls=3))
        eligibility = producer_feedback_eligibility(
            case_materials, producer,
            {"observed_artifact_sha256": delivery_digest, "target_role": "producer" if control == "producer_owned" else "recipient"},
            action_result, outcome_payload,
        )
        # The current gate deliberately blocks policy updates even when the
        # diagnostic responsibility status is ELIGIBLE (later-use is not yet
        # a valid training label).  Public projection therefore remains UNKNOWN.
        if eligibility["policy_update_allowed"]:
            raise AssertionError("promotion qualification unexpectedly opened policy update gate")
        unknown_reason = "policy-update-gate-closed"
        unknown_denominator["feedback_rows"] += 1
        unknown_denominator["unknown_rows"] += 1
        records = {name: _record(boundary, name, ident) for name, ident in (
            ("peer_selection", f"{control}-selection-{index}"),
            ("producer_delivery", delivery_id),
            ("recipient_judgment", f"{control}-judgment-{index}"),
            ("consumer_action", f"{control}-action-{index}"),
        )}
        selection_event = f"policy-{control}-selection-{index}"
        sidecar = FeedbackSidecar(
            ledger_record_hash=records["recipient_judgment"]["record_hash"], protocol_event_type="recipient_judgment",
            protocol_event_id=f"{control}-judgment-{index}", feedback_id=f"{control}-feedback-{index}",
            source_event_id=selection_event, selection_event_id=f"{control}-selection-{index}",
            delivery_id=delivery_id, producer_id=selected_peer, producer_version="v1", recipient_id="peer-a",
            source="recipient_judgment", arrived_at=float(index + 1), delay=1.0, action="repair",
            disposition="unknown", provenance="unknown", label_mapping_version="pipe3-label-v1", mapping_digest="d" * 64,
            responsibility_status="pending_attribution", attribution_basis=eligibility["reason"], artifact_sha256=delivery_digest,
            delivery_record_hash=records["producer_delivery"]["record_hash"], action_id=f"{control}-action-{index}",
            action_record_hash=records["consumer_action"]["record_hash"], raw_value="accept_with_rework", label=None,
            arrival_index=index + 1, sidecar_version="peerrole-policy-sidecar-v4",
        )
        gate_payload = {
            "gate_version": "producer-feedback-eligibility-v1", "ledger_record_hash": sidecar.ledger_record_hash,
            "sidecar_digest": sidecar.sidecar_digest, "protocol_event_type": sidecar.protocol_event_type,
            "protocol_event_id": sidecar.protocol_event_id, "source_event_id": sidecar.source_event_id,
            "delivery_id": sidecar.delivery_id, "producer_id": sidecar.producer_id, "producer_version": sidecar.producer_version,
            "recipient_id": sidecar.recipient_id, "selection_event_id": sidecar.selection_event_id,
            "eligible": False, "weight": None, "label": None, "label_mapping_version": sidecar.label_mapping_version,
            "evidence_version": "pipe3-cpu-v1", "source_index": index,
        }
        gate = AttributionGate(**gate_payload, gate_digest=_digest(gate_payload))
        schedule = (ArrivalAssignment(sidecar.feedback_id, sidecar.protocol_event_type, sidecar.protocol_event_id, sidecar.source_event_id, index + 1),)
        source_offer = build_source_bound_offer(
            selection=seal_by_index[index].decision_sidecar, selection_record=records["peer_selection"],
            feedback_inputs=((sidecar, records["recipient_judgment"], gate, unknown_reason),),
            ledger=boundary.ledger, arrival_schedule=schedule, offer_id=f"{control}-offer-{index}",
            context_key=f"PIPE3:{index + 1}", target_task_index=index + 1,
            previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
        )
        _emit(raw, trace, control=control, stream_id=stream_id, event="source_offer",
              payload={"source_task_index": index, "target_task_index": source_offer.offer.task_index,
                       "offer_id": source_offer.offer.offer_id,
                       "offer_record_hash": source_offer.offer.offer_record_hash,
                       "bundle_digest": source_offer.offer.bundle_digest,
                       "available_index": source_offer.offer.available_index,
                       "candidate_keys": list(source_offer.offer.candidate_keys),
                       "schedule_digest": source_offer.schedule_digest},
              started=started, cost=_cost(0.0), unknown_reason=unknown_reason)
        return {
            "index": index, "delivery_digest": delivery_digest, "eligibility": eligibility,
            "source_offer": source_offer, "sidecar": sidecar, "records": records,
            "outcome": outcome_payload, "action": action_result,
        }

    # First decision is sealed before task 0 starts.  The selection seal is
    # retained so the public sidecar can be bound to its canonical record.
    offer0 = make_offer(
        offer_id=f"{control}-selection-offer-0", task_id=TASK_ID, task_index=0, role="producer",
        context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=(),
        evidence_version="pipe3-cpu-v1", available_index=0,
    )
    seal_by_index: dict[int, Any] = {}
    seal_by_index[0] = boundary.choose_and_seal(
        offer=offer0, native_selection_id=f"{control}-selection-0", selector_id="peer-a", role="producer",
        base_scores=(100.0, -100.0), rng=rng, state_version=f"{stream_id}-state-0",
        encoder_version="pipe3-live-encoder-v2", feature_schema="pipe3", policy_version="contextual-v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0,
        read_cut=0, decision_index=0, consume_evidence=False,
    )
    selected0 = seal_by_index[0].native_selection.chosen_peer_id
    first = record_episode(0, selection_id=f"{control}-selection-0", selected_peer=selected0,
                           delivery_sources_i=delivery_sources, final_sources_i=final_sources, context="first")

    source_offer = first["source_offer"]
    read_t = time.perf_counter()
    read = read_source_offer_isolated(source_offer, read_cut=1, previous_aux_hash=source_offer.previous_aux_hash)
    _emit(raw, trace, control=control, stream_id=stream_id, event="policy_read",
          payload={"task_index": 1, "offer_id": read.offer_id, "offer_record_hash": read.offer_record_hash,
                   "bundle_digest": read.bundle_digest, "candidate_keys": list(read.candidate_keys),
                   "read_cut": read.read_cut, "policy_input_digest": read.policy_input_digest,
                   "public_rows_digest": read.public_rows_digest, "worker_sha256": read.worker_sha256},
          started=started, cost=_cost(time.perf_counter() - read_t), unknown_reason="policy-update-gate-closed")
    seal_by_index[1] = boundary.choose_and_seal_source_bound(
        source_offer=source_offer, native_selection_id=f"{control}-selection-1", selector_id="peer-a", role="producer",
        base_scores=(0.0, 0.0), rng=rng, state_version=f"{stream_id}-state-1",
        encoder_version="pipe3-live-encoder-v2", feature_schema="pipe3", policy_version="contextual-v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=2.0,
        read_cut=1, decision_index=1, consume_evidence=True,
    )
    _emit(raw, trace, control=control, stream_id=stream_id, event="next_selection",
          payload={"task_index": 1, "selection_id": seal_by_index[1].native_selection.selection_id,
                   "chosen_peer_id": seal_by_index[1].native_selection.chosen_peer_id,
                   "candidate_ids": list(seal_by_index[1].native_selection.candidate_ids),
                   "propensity": seal_by_index[1].native_selection.propensity,
                   "offer_id": source_offer.offer.offer_id, "read_cut": 1},
          started=started, cost=_cost(0.0), unknown_reason="policy-update-gate-closed")

    # A native LaterAssignment cannot be recorded here.  The ledger requires
    # non-empty evidence_ids, while this qualification deliberately keeps the
    # responsibility gate closed (including the producer-owned diagnostic
    # ELIGIBLE status).  Stop at the sealed next selection and preserve an
    # explicit blocked receipt instead of fabricating evidence or task_start.
    blocked_reason = "policy_update_gate_closed_no_legal_role_evidence_for_later_assignment"
    _emit(raw, trace, control=control, stream_id=stream_id, event="promotion_blocked",
          payload={"task_id": TASK_ID, "source_task_index": 0, "target_task_index": 1,
                   "selection_id": f"{control}-selection-1", "offer_id": source_offer.offer.offer_id,
                   "reason": blocked_reason},
          started=started, cost=_cost(0.0), unknown_reason=blocked_reason)
    replay = replay_ledger_events(boundary.ledger.events, allow_incomplete=True)
    replay_ok = replay.status == "PASS"
    _json(out / "ledger.json", boundary.ledger.events)
    native_root, auxiliary_root = boundary.validate_selection_manifests()
    result = {
        **stream_config, "status": "BLOCKED_BY_RESPONSIBILITY_GATE", "passed": False,
        "trace": trace, "ledger_event_count": len(boundary.ledger.events),
        "native_manifest_root": native_root, "auxiliary_manifest_root": auxiliary_root,
        "policy_updates": policy.updates, "unknown_denominator": unknown_denominator,
        "diagnostic_eligibility": first["eligibility"], "later_use_effect_status": "BLOCKED_BY_RESPONSIBILITY_GATE",
        "blocked_reason": blocked_reason, "next_task_started": False, "next_outcome_recorded": False,
        "schedule_digest": first["source_offer"].schedule_digest,
        "baseline_parity_status": "NOT_RUN",
        "replay": {"status": replay.status, "complete": replay.complete, "snapshot": replay.snapshot},
        "cost_totals": {"api_calls": 0, "gpu_jobs": 0, "tokens": 0,
                        "event_count": len(trace), "unknown_rows": unknown_denominator["unknown_rows"]},
        "elapsed_cpu_seconds": time.perf_counter() - started,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "scientific_claim_allowed": False,
        "interpretation": "promotion diagnostic stopped before later assignment; no legal role evidence exists while policy update is closed",
    }
    _json(out / "summary.json", result)
    return result


def run(out_dir: Path, *, seed: int = 0) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    top_config = {
        "runner_version": RUNNER_VERSION, "task_id": TASK_ID, "seed": seed,
        "controls": list(CONTROLS), "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "root": "PIPE3_stream_processing",
        "baseline_parity_status": "NOT_RUN",
        "independent_live_history_status": "qualification_only",
        "cost_schema": "pipe3-cost-v1", "unknown_policy": "preserve-reason-no-update",
        "independent_output_dirs": [str(out_dir / control) for control in CONTROLS],
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _json(out_dir / "config.json", top_config)
    results: list[dict[str, Any]] = []
    for control in CONTROLS:
        control_dir = out_dir / control
        try:
            results.append(_run_control(control, out=control_dir, seed=seed, stream_id=f"{control}-stream-{seed}"))
        except Exception as exc:  # Preserve the failed control receipt; do not overwrite it.
            control_dir.mkdir(parents=True, exist_ok=True)
            failure = {
                "runner_version": RUNNER_VERSION, "control": control,
                "status": "FAILED_OFFLINE", "passed": False, "real_api_calls": 0, "gpu_jobs": 0,
                "scientific_claim_allowed": False, "error_type": type(exc).__name__,
                "error": str(exc), "traceback": traceback.format_exc(),
                "failure_preserved": True, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            _json(control_dir / "failure.json", failure)
            _json(control_dir / "summary.json", failure)
            results.append(failure)
    passed = len(results) == len(CONTROLS) and all(row.get("passed") is True for row in results)
    blocked = len(results) == len(CONTROLS) and all(
        row.get("status") == "BLOCKED_BY_RESPONSIBILITY_GATE" for row in results
    )
    summary = {
        **top_config,
        "status": "QUALIFIED_OFFLINE" if passed else ("BLOCKED_BY_RESPONSIBILITY_GATE" if blocked else "FAILED_OFFLINE"),
        "passed": passed, "cases": results,
        "blocked_count": sum(row.get("status") == "BLOCKED_BY_RESPONSIBILITY_GATE" for row in results),
        "failure_count": sum(row.get("status") == "FAILED_OFFLINE" for row in results),
        "later_use_effect_status": "BLOCKED_BY_RESPONSIBILITY_GATE", "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "zero-call promotion qualification; no baseline or efficacy claim",
    }
    _json(out_dir / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    result = run(args.out_dir, seed=args.seed)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
