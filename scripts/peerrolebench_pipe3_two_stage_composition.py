"""CPU PIPE3 two-stage composition for method v1.1 scheme A.

This is a small qualification composition, not a benchmark.  The default
path calls the pinned PIPE3 sandbox scorers directly.  Source publication is
kept separate from delayed policy credit: a source evidence update never
calls ``observe_feedback``; only a replay-valid later assignment can do so.
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
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, ProducerScore,
    RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import BaselinePolicy, Feedback, TerminalOnlyPolicy  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2 import run_producer_scorer  # noqa: E402
from peerrolebench_pipe3_recipient_scorer_v2 import run_scorer  # noqa: E402
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_pipe3_runner_adapter import prepare_pipe3_action, validate_pipe3_action_result  # noqa: E402
from peerrolebench_pipe3_runner_v1 import auxiliary_manifest_root, Pipe3SelectionBoundary, make_offer  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_role_evidence_offer import (  # noqa: E402
    build_role_evidence_from_ledger, make_role_evidence_offer,
)
from peerrolebench_role_evidence_selection import (  # noqa: E402
    commit_role_evidence_selection, preview_role_evidence_selection,
    preview_role_evidence_selection_with_public_judgment,
)
from peerrolebench_role_evidence_scorer import RoleEvidenceScoreConfig  # noqa: E402
from peerrolebench_isolated_policy_read import read_role_evidence_offer_isolated  # noqa: E402
from peerrolebench_two_stage_gate import (  # noqa: E402
    DelayedCreditLedger, derive_later_credit_from_ledger, evaluate_source_gate,
)


TASK_ID = "PIPE3_stream_processing"
VERSION = "pipe3-two-stage-composition-v1.4"
CONTROLS = ("producer_owned", "recipient_owned", "mixed")
CandidateScorer = Callable[[str, Mapping[str, str], Mapping[str, str], Path, Path, int], dict[str, Any]]
PolicyFactory = Callable[[str], BaselinePolicy]


def default_policy_factory(name: str) -> BaselinePolicy:
    """Construct a registered policy for a future parity run.

    The qualification default remains terminal-only; callers must inject a
    factory explicitly to compare another arm.  Keeping construction outside
    the composition prevents a policy name from silently changing the
    historical v1.2 receipts.
    """

    if name != "terminal_only":
        raise ValueError("default qualification policy is terminal_only; inject a factory for another arm")
    return TerminalOnlyPolicy()


def _candidate_registry(materials: Mapping[str, Any]) -> list[CandidateRegistryEntry]:
    """Bind each menu key to a concrete producer snapshot for this run."""
    base = dict(materials["agent_payloads"]["producer"]["source_files"])
    fixed = _patch_producer(base, interfaces(materials)["timestamp_field"])
    model_config = hashlib.sha256(b"pipe3-qualification-model-config-v2").hexdigest()
    return [
        CandidateRegistryEntry("peer-b", "v1", digest_files({"producer.py": base["producer.py"]}),
                               "fixture-model", model_config),
        CandidateRegistryEntry("peer-c", "v1", digest_files({"producer.py": fixed["producer.py"]}),
                               "fixture-model", model_config),
    ]


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _log(path: Path, event: str, payload: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": event, "payload": payload,
        }, sort_keys=True, ensure_ascii=False, default=str) + "\n")
        handle.flush()


def _patch_producer(sources: Mapping[str, str], timestamp_field: str) -> dict[str, str]:
    text = sources["producer.py"]
    anchor = "    return json.dumps(data, default=str)"
    if anchor not in text:
        raise RuntimeError("producer correction anchor not found")
    if not timestamp_field.isidentifier() or f"event.{timestamp_field}" not in text:
        raise RuntimeError("timestamp field is absent from producer source")
    return {**dict(sources), "producer.py": text.replace(
        anchor, f'    data["{timestamp_field}"] = event.{timestamp_field}.isoformat()\n    return json.dumps(data)', 1,
    )}


def _patch_recipient(sources: Mapping[str, str]) -> dict[str, str]:
    text = sources["processor.py"].replace(
        'open(output_path, "w", encoding="latin-1")',
        'open(output_path, "w", encoding="utf-8")', 1,
    )
    anchor = '            envelope = {"data": processed}\n            fout.write(json.dumps(envelope, ensure_ascii=False) + "\\n")'
    if anchor not in text:
        raise RuntimeError("processor correction anchor not found")
    return {**dict(sources), "processor.py": text.replace(
        anchor, '            fout.write(json.dumps(processed, ensure_ascii=False) + "\\n")', 1,
    )}


def _unknown(reason: str, *, stage: str, error: Exception | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "status": "UNKNOWN", "label": None, "quality_score": None,
        "coverage_complete": False, "decision_complete": False,
        "unknown_reason": reason, "stage": stage,
    }
    if error is not None:
        row.update(error_type=type(error).__name__, error=str(error))
    return row


def _default_scorer(kind: str, sources: Mapping[str, str], info: Mapping[str, str],
                    stage_dir: Path, log: Path, seed: int) -> dict[str, Any]:
    """Call one real v2 sandbox scorer; failures remain UNKNOWN."""
    stage_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        if kind == "producer":
            return run_producer_scorer(
                dict(sources), info, TASK_ID, seed, stage_dir, lambda event, payload: _log(log, event, payload),
            )
        return run_scorer(
            dict(sources), info, kind, TASK_ID, seed, stage_dir, lambda event, payload: _log(log, event, payload),
        )
    except Exception as exc:  # sandbox transport failure is a preserved UNKNOWN
        _log(log, "scorer_failure", {"kind": kind, "stage": str(stage_dir), "error_type": type(exc).__name__, "error": str(exc)})
        return _unknown("scorer_execution_failed", stage=kind, error=exc)


def _score_triplet(sources: Mapping[str, str], info: Mapping[str, str], out: Path,
                   log: Path, seed: int, scorer: CandidateScorer | None) -> dict[str, Any]:
    out.mkdir(parents=False, exist_ok=False)
    producer_sources = {"producer.py": sources["producer.py"], "models.py": sources["models.py"]}
    recipient_sources = {"processor.py": sources["processor.py"], "models.py": sources["models.py"]}
    adoption_sources = {name: sources[name] for name in ("producer.py", "processor.py", "sink.py", "models.py")}
    call = scorer or _default_scorer
    results: dict[str, Any] = {}
    for kind, payload in (("producer", producer_sources), ("recipient", recipient_sources), ("adoption", adoption_sources)):
        try:
            results[kind] = call(kind, payload, info, out / kind, log, seed)
        except Exception as exc:
            results[kind] = _unknown("scorer_injection_failed", stage=kind, error=exc)
            _log(log, "scorer_failure", {"kind": kind, "stage": str(out / kind), "error_type": type(exc).__name__, "error": str(exc)})
    return results


def _event_record(boundary: Pipe3SelectionBoundary, event_type: str, event_id: str) -> dict[str, Any]:
    field = {
        "peer_selection": "selection_id", "producer_delivery": "delivery_id",
        "producer_score": "producer_score_id", "recipient_judgment": "judgment_id",
        "consumer_action": "action_id", "terminal_outcome": "outcome_id",
    }[event_type]
    return next(row for row in boundary.ledger.events if row["event_type"] == event_type and row["payload"].get(field) == event_id)


def _prepare_case(materials: dict[str, Any], control: str) -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
    base = dict(materials["agent_payloads"]["producer"]["source_files"])
    base.update(materials["agent_payloads"]["recipient"]["source_files"])
    producer_fixed = _patch_producer(base, interfaces(materials)["timestamp_field"])
    recipient_fixed = _patch_recipient(base)
    case = deepcopy(materials)
    if control == "producer_owned":
        case["agent_payloads"]["recipient"]["source_files"]["processor.py"] = recipient_fixed["processor.py"]
        delivery = {"producer.py": base["producer.py"]}
        # The source producer snapshot remains immutable during recipient
        # integration.  A producer defect is attributed only from the
        # objective pre-action scorer; recipient repair cannot rewrite it.
        final = {**recipient_fixed, "producer.py": base["producer.py"]}
    elif control == "recipient_owned":
        case["agent_payloads"]["producer"]["source_files"]["producer.py"] = producer_fixed["producer.py"]
        delivery = {"producer.py": producer_fixed["producer.py"]}
        final = {**base, "producer.py": producer_fixed["producer.py"], "processor.py": recipient_fixed["processor.py"]}
    elif control == "mixed":
        delivery = {"producer.py": base["producer.py"]}
        final = {**base, "processor.py": recipient_fixed["processor.py"]}
    else:
        raise ValueError(f"unknown control {control!r}")
    return case, delivery, final


def _record_episode(*, boundary: Pipe3SelectionBoundary, materials: dict[str, Any],
                    control: str, selection_id: str, selected_peer: str,
                    delivery_sources: Mapping[str, str], final_sources: Mapping[str, str],
                    out: Path, raw: Path, seed: int, scorer: CandidateScorer | None) -> dict[str, Any]:
    out.mkdir(parents=False, exist_ok=False)
    info = interfaces(materials)
    delivery_digest = digest_files(delivery_sources)
    index = 0 if selection_id.endswith("-0") else 1
    delivery_id = f"{control}-delivery-{index}"
    registry_entry = next((entry for entry in boundary.registry if entry.candidate_id == selected_peer), None)
    if registry_entry is None:
        raise ValueError(f"selected peer is absent from candidate registry: {selected_peer}")
    if registry_entry.source_digest != delivery_digest:
        _log(raw, "treatment_binding_mismatch", {
            "candidate_key": registry_entry.key,
            "registered_source_digest": registry_entry.source_digest,
            "delivered_source_digest": delivery_digest,
        })
        return {
            "delivery_id": delivery_id, "delivery_digest": delivery_digest,
            "candidate_key": registry_entry.key,
            "candidate_source_digest": registry_entry.source_digest,
            "producer_defect_registered": False,
            "producer": {"status": "UNKNOWN", "label": None, "quality_score": None,
                          "coverage_complete": False, "decision_complete": False,
                          "unknown_reason": "candidate_treatment_binding_mismatch"},
            "scores_before": {}, "scores_after": {},
            "action": {"changed_paths": [], "output_source_sha256": delivery_digest,
                       "consumer_action": "repair"},
            "outcome": {"status": "UNKNOWN", "quality_score": None,
                        "coverage_complete": False, "decision_complete": False},
            "eligibility": {"producer_feedback_eligible": False,
                             "policy_update_allowed": False,
                             "reason": "candidate artifact does not match registered treatment"},
            "index": index,
        }
    # The task start is sealed before actor/scorer execution by contract.
    boundary.ledger.record_task_start(TASK_ID, 0 if selection_id.endswith("-0") else 1)
    _log(raw, "task_start_sealed", {"selection_id": selection_id, "task_index": 0 if selection_id.endswith("-0") else 1})
    before = dict(materials["agent_payloads"]["recipient"]["source_files"])
    before["producer.py"] = delivery_sources["producer.py"]
    scores_before = _score_triplet(before, info, out / "before_action", raw, seed, scorer)
    _log(raw, "scorer_before", scores_before)
    _log(raw, "scorer_input_manifest", {
        "candidate_key": registry_entry.key,
        "candidate_source_digest": registry_entry.source_digest,
        "candidate_registry_digest": boundary.registry_digest,
        "artifact_sha256": delivery_digest,
        "stage": "before_action",
    })
    complete = all(scores_before[k].get("status") in {"PASS", "FAIL"}
                   and scores_before[k].get("coverage_complete") is True
                   and scores_before[k].get("decision_complete") is True
                   for k in ("producer", "recipient", "adoption"))
    if not complete:
        unknown_action = {"changed_paths": [], "output_source_sha256": delivery_digest,
                          "consumer_action": "repair"}
        outcome_payload = {"status": "UNKNOWN", "quality_score": None,
                           "coverage_complete": False, "decision_complete": False}
        return {"delivery_id": delivery_id, "delivery_digest": delivery_digest,
                "candidate_key": registry_entry.key,
                "candidate_source_digest": registry_entry.source_digest,
                "producer_defect_registered": False,
                "producer": scores_before["producer"], "scores_before": scores_before,
                "scores_after": {}, "action": unknown_action, "outcome": outcome_payload,
                "eligibility": {"producer_feedback_eligible": False,
                                 "policy_update_allowed": False,
                                 "reason": "source scorer UNKNOWN; stop before delivery/action"},
                "index": index}
    boundary.ledger.record_delivery(Delivery(
        delivery_id, TASK_ID, selected_peer, "peer-a", delivery_digest,
        f"request-{control}-{index}", index, selection_id,
        registry_entry.source_digest,
    ))
    producer = scores_before["producer"]
    boundary.ledger.record_producer_score(ProducerScore(
        f"{control}-producer-score-{index}", delivery_id, delivery_digest,
        producer.get("scorer_version", "pipe3-producer-objective-v2"), producer.get("status", "UNKNOWN"),
        producer.get("label"), producer.get("quality_score"),
        producer.get("response_digest", _digest(producer)), producer.get("coverage_complete") is True,
        producer.get("decision_complete") is True,
    ))
    boundary.ledger.record_judgment(RecipientJudgment(
        f"{control}-judgment-{index}", delivery_id, "peer-a", "accept_with_rework", delivery_digest,
        repair_note=f"{VERSION}:{control}",
    ))
    action_payload = prepare_pipe3_action(
        materials, delivery_sources, "repair", allow_producer_rewrite=False,
    )
    action_result = validate_pipe3_action_result(action_payload, final_sources)
    boundary.ledger.record_action(ConsumerAction(
        f"{control}-action-{index}", delivery_id, "peer-a", True, delivery_digest,
        action_result["output_source_sha256"], 0.0, "repair",
    ))
    _log(raw, "actor_action", {"changed_paths": action_result["changed_paths"], "output_source_sha256": action_result["output_source_sha256"]})
    scores_after = _score_triplet(final_sources, info, out / "after_action", raw, seed, scorer)
    _log(raw, "scorer_after", scores_after)
    _log(raw, "scorer_input_manifest", {
        "candidate_key": registry_entry.key,
        "candidate_source_digest": registry_entry.source_digest,
        "candidate_registry_digest": boundary.registry_digest,
        "artifact_sha256": delivery_digest,
        "stage": "after_action",
        "changed_paths": action_result["changed_paths"],
    })
    recipient_after, adoption_after = scores_after["recipient"], scores_after["adoption"]
    outcome_payload = {
        "status": "PASS" if recipient_after.get("status") == "PASS" and adoption_after.get("status") == "PASS" else (
            "FAIL" if recipient_after.get("status") in {"PASS", "FAIL"} and adoption_after.get("status") in {"PASS", "FAIL"} else "UNKNOWN"),
        "quality_score": adoption_after.get("quality_score"),
        "coverage_complete": recipient_after.get("coverage_complete") is True and adoption_after.get("coverage_complete") is True,
        "decision_complete": recipient_after.get("decision_complete") is True and adoption_after.get("decision_complete") is True,
    }
    if outcome_payload["status"] in {"PASS", "FAIL"}:
        boundary.ledger.record_outcome(TerminalOutcome(
            f"{control}-outcome-{index}", delivery_id, outcome_payload["status"] == "PASS",
            "pipe3-recipient-objective-v2", None if outcome_payload["quality_score"] is None else float(outcome_payload["quality_score"]),
            _digest(outcome_payload),
        ))
    _log(raw, "terminal_outcome", outcome_payload)
    eligibility = producer_feedback_eligibility(
        materials, producer,
        {"observed_artifact_sha256": delivery_digest, "target_role": "producer" if control == "producer_owned" else "recipient"},
        action_result, outcome_payload,
    )
    return {"delivery_id": delivery_id, "delivery_digest": delivery_digest,
            "candidate_key": registry_entry.key,
            "candidate_source_digest": registry_entry.source_digest,
            "producer_defect_registered": producer.get("status") == "FAIL" and producer.get("label") == 0,
            "producer": producer,
            "scores_before": scores_before, "scores_after": scores_after,
            "action": action_result, "outcome": outcome_payload, "eligibility": eligibility,
            "index": index}


def _source_offer(boundary: Pipe3SelectionBoundary, *, control: str, source: Mapping[str, Any],
                  selection: Any, selected_peer: str, target_task_index: int) -> tuple[Any, Any]:
    records = {name: _event_record(boundary, name, ident) for name, ident in (
        ("peer_selection", f"selection-{control}-0"), ("producer_delivery", source["delivery_id"]),
        ("recipient_judgment", f"{control}-judgment-0"), ("consumer_action", f"{control}-action-0"),
    )}
    eligible = bool(source["eligibility"].get("producer_feedback_eligible"))
    sidecar_payload = {
        "feedback_id": f"feedback-{control}", "source_event_id": selection.event_id,
        "selection_event_id": f"selection-{control}-0", "delivery_id": source["delivery_id"],
        "producer_id": selected_peer, "eligible": eligible,
    }
    evidence_id = f"evidence-{control}-source"
    if not eligible:
        return None, {"records": records, "evidence_id": evidence_id, "eligible": False, "sidecar": sidecar_payload}
    # Native publication is immutable and does not touch policy state.
    boundary.ledger.record_evidence_update(RoleEvidenceUpdate(
        evidence_id, f"{control}-judgment-0", f"{control}-action-0", f"{control}-outcome-0", VERSION, 1.0,
    ))
    evidence = build_role_evidence_from_ledger(
        ledger=boundary.ledger, evidence_id=evidence_id, candidate_key=f"{selected_peer}@v1", role="producer",
        target_task_index=target_task_index, evidence_version=VERSION, available_index=1,
    )
    previous_aux_hash = auxiliary_manifest_root(boundary.auxiliary_manifest_rows)
    role_offer = make_role_evidence_offer(
        offer_id=f"role-offer-{control}", task_id=TASK_ID, task_index=target_task_index, role="producer",
        context_key=f"PIPE3:{target_task_index}", candidate_keys=("peer-b@v1", "peer-c@v1"), evidence=(evidence,),
        evidence_version=VERSION, available_index=1,
        previous_aux_hash=previous_aux_hash,
        candidate_registry_digest=boundary.registry_digest,
    )
    boundary.auxiliary_manifest_rows.append({
        "event_type": "role_evidence_offer", "event_id": role_offer.offer_id,
        "offer_id": role_offer.offer_id, "decision_event_id": "",
        "record_hash": role_offer.offer_record_hash,
        "attestation_digest": role_offer.bundle_digest,
    })
    return role_offer, {"records": records, "evidence_id": evidence_id, "eligible": True,
                        "sidecar": sidecar_payload, "previous_aux_hash": previous_aux_hash}


def _run_control(control: str, *, out: Path, source_seed: int, target_seed: int,
                 scorer: CandidateScorer | None = None,
                 policy_factory: PolicyFactory | None = None,
                 policy_name: str = "terminal_only",
                 assignment_mode: str = "hand_authored") -> dict[str, Any]:
    if assignment_mode not in {"hand_authored", "public_judgment"}:
        raise ValueError("unsupported assignment_mode")
    out.mkdir(parents=False, exist_ok=False)
    raw = out / "raw.jsonl"
    raw.write_text("", encoding="utf-8")
    config = {
        "version": VERSION, "control": control, "task_id": TASK_ID,
        "source_seed": source_seed, "target_seed": target_seed, "root": "PIPE3_stream_processing",
        "same_root_qualification": True, "independent_benchmark": False,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(), "python_executable": sys.executable,
        "platform": platform.platform(),
        "component_sha256": {name: _sha_file(ROOT / name) for name in (
            "scripts/peerrolebench_pipe3_two_stage_composition.py", "scripts/peerrolebench_two_stage_gate.py",
            "scripts/peerrolebench_role_evidence_selection.py", "scripts/peerrolebench_role_evidence_offer.py",
            "scripts/peerrolebench_role_evidence_scorer.py",
        )},
        "policy": policy_name, "assignment_mode": assignment_mode,
        "overlay_values": "qualification_control_only",
        "authored_controls": {"source_judgment": "parent-authored", "action": "parent-authored", "patched_actor": "parent-authored"},
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _log(raw, "config", config)
    # Freeze the run configuration before loading or executing any generated
    # actor/scorer material.  The hashes and seeds above are the audit anchor.
    generated_source = load_pipe3(source_seed)
    # This qualification intentionally keeps one structural root so the
    # treatment-binding and lineage seam can be isolated.  Independent roots
    # remain a live benchmark gate and are not claimed here.
    generated_target = generated_source
    source_materials = build_materials(generated_source)
    target_materials = build_materials(generated_target)
    source_case, source_delivery, source_final = _prepare_case(source_materials, control)
    target_case, target_delivery, target_final = _prepare_case(target_materials, control)
    candidate_registry = _candidate_registry(source_materials)
    make_policy = policy_factory or default_policy_factory
    policy = make_policy(policy_name)
    if not isinstance(policy, BaselinePolicy):
        raise TypeError("policy factory must return a BaselinePolicy")
    boundary = Pipe3SelectionBoundary(policy, candidate_registry)
    offer0 = make_offer(offer_id=f"offer-{control}-0", task_id=TASK_ID, task_index=0, role="producer",
                        context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=(),
                        evidence_version=VERSION, available_index=0)
    seal0 = boundary.choose_and_seal(
        offer=offer0, native_selection_id=f"selection-{control}-0", selector_id="peer-a", role="producer",
        base_scores=(100.0, -100.0), rng=__import__("numpy").random.default_rng(source_seed),
        state_version="source-state-v1", encoder_version="pipe3-v1", feature_schema="pipe3",
        policy_version="contextual-v1", base_score_version="qualification-overlay-v1", rng_algorithm="numpy-pcg64",
        rng_draw=0, selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=False,
    )
    source = _record_episode(boundary=boundary, materials=source_case, control=control,
                             selection_id=f"selection-{control}-0", selected_peer=seal0.native_selection.chosen_peer_id,
                             delivery_sources=source_delivery, final_sources=source_final,
                             out=out / "source", raw=raw, seed=source_seed, scorer=scorer)
    gate = evaluate_source_gate(
        source_case, source["producer"], {"target_role": "producer" if control == "producer_owned" else "recipient",
        "observed_artifact_sha256": source["delivery_digest"],
        "producer_defect_registered": source.get("producer_defect_registered") is True},
        source["action"], source["outcome"], None,
    )
    source["source_gate"] = gate.payload()
    # The source gate is the sole attribution authority.  The legacy helper
    # remains diagnostic only and must not suppress a producer defect that was
    # independently scored while the recipient kept producer.py read-only.
    source["eligibility"] = {
        **source.get("eligibility", {}),
        "producer_feedback_eligible": gate.evidence_publish_allowed,
        "policy_update_allowed": gate.policy_update_allowed,
    }
    _log(raw, "source_gate", gate.payload())
    if not gate.evidence_publish_allowed:
        expected_rejection = (control in {"recipient_owned", "mixed"}
                              and source["outcome"]["status"] in {"PASS", "FAIL", "UNKNOWN"}
                              and gate.status in {"UNKNOWN", "PENDING_ATTRIBUTION"}
                              and boundary.policy.updates == 0)
        summary = {**config, "status": "UNKNOWN", "passed": False,
                   "contract_passed": expected_rejection, "stop_reason": gate.reason,
                   "source": source, "target": {"status": "NOT_RUN_UNKNOWN"}, "policy_updates": boundary.policy.updates,
                   "unknown_denominator": {"source_rows": 1, "unknown_rows": 1}, "ledger": boundary.ledger.events,
                   "scientific_claim_allowed": False}
        (out / "ledger.json").write_text(json.dumps(boundary.ledger.events, indent=2, default=str) + "\n", encoding="utf-8")
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        return summary
    if boundary.policy.updates != 0:
        raise AssertionError("source publication changed persistent policy")
    role_offer, meta = _source_offer(boundary, control=control, source=source, selection=seal0.decision_sidecar,
                                     selected_peer=seal0.native_selection.chosen_peer_id, target_task_index=1)
    if role_offer is None:
        raise AssertionError("eligible source must publish role evidence")
    feedback_offer = make_offer(
        offer_id=f"feedback-offer-{control}", task_id=TASK_ID, task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version=VERSION, available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    _log(raw, "source_publication", {"evidence_id": meta["evidence_id"], "offer_id": role_offer.offer_id,
                                      "bundle_digest": role_offer.bundle_digest, "policy_updates": boundary.policy.updates,
                                      "read_cut": 1})
    isolated_read = read_role_evidence_offer_isolated(
        role_offer, read_cut=1, previous_aux_hash=meta["previous_aux_hash"],
    )
    boundary.auxiliary_manifest_rows.append({
        "event_type": "role_evidence_read", "event_id": f"read-{role_offer.offer_id}",
        "offer_id": role_offer.offer_id, "decision_event_id": f"read-{role_offer.offer_id}",
        "record_hash": role_offer.offer_record_hash,
        "attestation_digest": isolated_read.policy_input_digest,
    })
    _log(raw, "isolated_role_evidence_read", {"offer_id": isolated_read.offer_id,
                                               "policy_input_digest": isolated_read.policy_input_digest,
                                               "read_cut": isolated_read.read_cut})
    target_base_scores = (1.0, 0.0) if seal0.native_selection.chosen_peer_id == "peer-b" else (0.0, 1.0)
    target_kwargs = dict(
        boundary=boundary, role_offer=role_offer, feedback_offer=feedback_offer,
        assignment_id=f"assignment-{control}", native_selection_id=f"selection-{control}-1",
        selector_id="peer-a", rng=__import__("numpy").random.default_rng(target_seed),
        state_version="target-state-v1", encoder_version="pipe3-v1", feature_schema="pipe3",
        policy_version="contextual-v1", base_score_version="qualification-overlay-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0,
        decision_index=1,
    )
    assignment_score = None
    if assignment_mode == "public_judgment":
        plan, assignment_score = preview_role_evidence_selection_with_public_judgment(
            **target_kwargs, base_scores=target_base_scores, read_cut=1,
            scorer_config=RoleEvidenceScoreConfig(),
        )
    else:
        plan = preview_role_evidence_selection(
            **target_kwargs, base_scores=target_base_scores, read_cut=1,
        )
    _log(raw, "target_selection_preview", {"assignment_id": plan.assignment_id,
                                             "selected_peer": plan.assigned_agent_id,
                                             "propensity": plan.selection.propensity,
                                             "read_cut": plan.read_cut,
                                             "persistent_state_digest": plan.persistent_state_digest,
                                             "assignment_mode": assignment_mode,
                                             "assignment_score": None if assignment_score is None else assignment_score.payload()})
    target_seal = commit_role_evidence_selection(boundary, plan=plan, role_offer=role_offer, feedback_offer=feedback_offer)
    _log(raw, "assignment_committed_before_selection", {"assignment_id": plan.assignment_id, "selection_id": target_seal.native_selection.selection_id})
    target = _record_episode(boundary=boundary, materials=target_case, control=control,
                             selection_id=f"selection-{control}-1", selected_peer=target_seal.native_selection.chosen_peer_id,
                             delivery_sources=target_delivery, final_sources=target_final,
                             out=out / "target", raw=raw, seed=target_seed, scorer=scorer)
    if target["outcome"]["status"] == "UNKNOWN":
        _log(raw, "target_unknown_no_update", {"assignment_id": plan.assignment_id,
                                                 "outcome": target["outcome"],
                                                 "policy_updates": boundary.policy.updates})
        summary = {**config, "status": "UNKNOWN", "passed": False, "contract_passed": False,
                   "stop_reason": "target scorer/outcome UNKNOWN; complete replay and delayed credit skipped",
                   "source": source, "target": target, "source_gate": gate.payload(),
                   "role_offer": role_offer.payload(), "assignment_id": plan.assignment_id,
                   "replay": {"status": "NOT_RUN_INCOMPLETE"}, "credit": None,
                   "policy_updates": boundary.policy.updates, "delayed_credit_count": 0,
                   "unknown_denominator": {"source_rows": 1, "unknown_rows": 1},
                   "ledger": boundary.ledger.events, "scientific_claim_allowed": False}
        (out / "ledger.json").write_text(json.dumps(boundary.ledger.events, indent=2, default=str) + "\n", encoding="utf-8")
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        return summary
    # The strict replay contract requires a terminal evidence row for every
    # delivery.  This target completion row is auxiliary lineage for replay;
    # it is never added to the public role-evidence offer and never updates
    # policy.
    if target["outcome"]["status"] in {"PASS", "FAIL"}:
        boundary.ledger.record_evidence_update(RoleEvidenceUpdate(
            f"target-completion-evidence-{control}", f"{control}-judgment-1",
            f"{control}-action-1", f"{control}-outcome-1", "target-completion-v1", 2.0,
        ))
        _log(raw, "target_completion_evidence", {"evidence_id": f"target-completion-evidence-{control}", "public": False})
    replay = replay_ledger_events(boundary.ledger.events)
    credit = derive_later_credit_from_ledger(
        ledger=boundary.ledger, source_gate=gate, assignment_id=plan.assignment_id,
        source_evidence_id=meta["evidence_id"], evidence_candidate_id=f"{seal0.native_selection.chosen_peer_id}@v1",
        later_outcome_id=f"{control}-outcome-1",
    ) if replay.status == "PASS" and replay.complete and target["outcome"]["status"] in {"PASS", "FAIL"} else None
    delayed = DelayedCreditLedger()
    credit_committed = False
    policy_update_applied = False
    # Any non-empty declared source set means this arm expects its own public
    # channel to change policy state.  The runner currently constructs only a
    # terminal_outcome event, so non-terminal arms must remain UNKNOWN rather
    # than silently inheriting the terminal channel.
    policy_update_expected = bool(boundary.policy.accepted_sources)
    if credit is not None:
        selected = boundary.selections[f"policy-{plan.native_selection_id}"]
        quality = target["outcome"].get("quality_score")
        feedback = Feedback(
            feedback_id=f"later-feedback-{control}", source_event_id=selected.event_id,
            source="terminal_outcome", label=None if quality is None else float(quality),
            arrived_at=2.0, delay=1.0, action="repair", disposition="eligible", provenance="public", arrival_index=2,
        )
        before = deepcopy(boundary.policy.__dict__)
        before_updates = boundary.policy.updates
        credit_committed = delayed.apply_once(credit, lambda _: boundary.policy.observe_feedback(feedback),
                                              snapshot=lambda: deepcopy(boundary.policy.__dict__),
                                              restore=lambda state: (boundary.policy.__dict__.clear(), boundary.policy.__dict__.update(state)))
        policy_update_applied = boundary.policy.updates > before_updates
        _log(raw, "delayed_update", {"credit_committed": credit_committed,
                                      "policy_update_applied": policy_update_applied,
                                      "policy_update_expected": policy_update_expected,
                                      "credit": credit.__dict__, "source_event_id": selected.event_id,
                                      "feedback_source": feedback.source,
                                      "policy_updates": boundary.policy.updates, "before_state_digest": _digest(before),
                                      "after_state_digest": _digest(boundary.policy.__dict__)})
    native_root, auxiliary_root = boundary.validate_selection_manifests()
    _log(raw, "manifest_validation", {
        "native_root": native_root, "auxiliary_root": auxiliary_root,
        "native_rows": len(boundary.native_manifest_rows),
        "auxiliary_rows": len(boundary.auxiliary_manifest_rows),
    })
    # A delayed credit commit alone is not sufficient for an arm whose
    # declared feedback channel should update policy state.  In particular,
    # passing a recipient_judgment/raw_acceptance arm while constructing a
    # terminal_outcome event would be a silent channel substitution.  Keep the
    # receipt explicit and fail qualification until the adapter constructs the
    # arm's declared public event.
    feedback_contract_ok = (
        credit is not None
        and credit_committed
        and (not policy_update_expected or policy_update_applied)
    )
    summary = {**config, "status": "QUALIFIED_OFFLINE" if feedback_contract_ok else "UNKNOWN",
               "passed": feedback_contract_ok,
               "contract_passed": feedback_contract_ok, "source": source, "target": target,
               "source_gate": gate.payload(), "role_offer": role_offer.payload(), "assignment_id": plan.assignment_id,
               "replay": replay.as_dict(), "credit": None if credit is None else credit.__dict__,
               "policy_updates": boundary.policy.updates, "policy_update_expected": policy_update_expected,
               "policy_update_applied": policy_update_applied,
               "delayed_credit_count": len(delayed.credits),
               "unknown_denominator": {"source_rows": 1, "unknown_rows": 0}, "ledger": boundary.ledger.events,
               "native_manifest_root": native_root, "auxiliary_manifest_root": auxiliary_root,
               "feedback_contract_ok": feedback_contract_ok,
               "scientific_claim_allowed": False, "interpretation": "engineering comparator; overlay controls are hand-authored qualification values"}
    (out / "ledger.json").write_text(json.dumps(boundary.ledger.events, indent=2, default=str) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return summary


def run(out_dir: Path, *, source_seed: int = 0, target_seed: int = 1,
        scorer: CandidateScorer | None = None,
        policy_factory: PolicyFactory | None = None,
        policy_name: str = "terminal_only",
        assignment_mode: str = "hand_authored") -> dict[str, Any]:
    if assignment_mode not in {"hand_authored", "public_judgment"}:
        raise ValueError("unsupported assignment_mode")
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    top = {"version": VERSION, "task_id": TASK_ID, "source_seed": source_seed, "target_seed": target_seed,
           "controls": list(CONTROLS), "real_api_calls": 0, "gpu_jobs": 0,
           "scientific_claim_allowed": False, "started_at_utc": started,
           "execution_injection": scorer is not None, "policy": policy_name,
           "assignment_mode": assignment_mode}
    (out_dir / "config.json").write_text(json.dumps(top, indent=2) + "\n", encoding="utf-8")
    cases = []
    for control in CONTROLS:
        try:
            cases.append(_run_control(control, out=out_dir / control, source_seed=source_seed,
                                      target_seed=target_seed, scorer=scorer,
                                      policy_factory=policy_factory, policy_name=policy_name,
                                      assignment_mode=assignment_mode))
        except Exception as exc:
            case_dir = out_dir / control
            if not case_dir.exists():
                case_dir.mkdir(parents=False)
            raw = case_dir / "raw.jsonl"
            if raw.exists():
                _log(raw, "composition_failure", {"error_type": type(exc).__name__, "error": str(exc)})
            failure = {**top, "control": control, "status": "FAILED_OFFLINE", "passed": False,
                       "error_type": type(exc).__name__, "error": str(exc), "failure_preserved": True}
            (case_dir / "failure.json").write_text(json.dumps(failure, indent=2, default=str) + "\n", encoding="utf-8")
            cases.append(failure)
    contract_passed = len(cases) == len(CONTROLS) and all(c.get("contract_passed") is True for c in cases)
    result = {**top, "status": "QUALIFIED_OFFLINE" if contract_passed else "UNKNOWN",
              "passed": contract_passed, "contract_passed": contract_passed, "cases": cases,
              "ended_at_utc": datetime.now(timezone.utc).isoformat(),
              "interpretation": "CPU engineering composition only; no LLM efficacy, RARE or benchmark claim"}
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--source-seed", type=int, default=0)
    parser.add_argument("--target-seed", type=int, default=1)
    args = parser.parse_args()
    result = run(args.out_dir, source_seed=args.source_seed, target_seed=args.target_seed)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
