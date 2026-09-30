"""CPU-only PIPE3 episode composition qualification.

Runs pinned PIPE3 material through the real v2 scorer workers, canonical
ledger/v4 sidecars, the responsibility gate, and (only for eligible
producer-owned evidence) public profile generation, isolated read, versioned
selection, and native task start.  It makes no API/GPU call and cannot support
a scientific efficacy claim.
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
import tempfile
import time
from types import SimpleNamespace
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, RecipientJudgment,
    TerminalOutcome,
)
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer  # noqa: E402
from peerrolebench_pipe3_assignment_runner import Pipe3AssignmentRunner  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2 import (  # noqa: E402
    classify as classify_producer, run_producer_scorer,
)
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_recipient_scorer_v2 import (  # noqa: E402
    classify as classify_recipient, digest_files as scorer_digest_files,
    run_scorer as run_recipient_scorer,
)
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_pipe3_runner_adapter import (  # noqa: E402
    prepare_pipe3_action, validate_pipe3_action_result,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest, project_feedback  # noqa: E402
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar  # noqa: E402
from peerrolebench_profile_generator import (  # noqa: E402
    DeterministicPublicProfileGenerator, PublicProfileGenerationRequest,
)
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402

TASK_ID = "PIPE3_stream_processing"
PROFILE_FIELDS = {
    "reliability": "medium", "strengths": ["public producer feedback"],
    "weaknesses": ["requires later validation"], "communication_style": "concise",
    "notes": ["deterministic qualification fixture"],
}


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _log(path: Path, event: str, payload: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": event, "payload": payload,
        }, sort_keys=True, ensure_ascii=False, default=str) + "\n")
        handle.flush()


def _patch_producer(source: Mapping[str, str]) -> dict[str, str]:
    text = source["producer.py"]
    anchor = "    return json.dumps(data, default=str)"
    if anchor not in text:
        raise RuntimeError("producer correction anchor not found")
    return {**dict(source), "producer.py": text.replace(
        anchor,
        '    data["timestamp"] = event.timestamp.isoformat()\n'
        "    return json.dumps(data)", 1,
    )}


def _patch_recipient(source: Mapping[str, str]) -> dict[str, str]:
    text = source["processor.py"].replace(
        'open(output_path, "w", encoding="latin-1")',
        'open(output_path, "w", encoding="utf-8")', 1,
    )
    envelope = '            envelope = {"data": processed}\n            fout.write(json.dumps(envelope, ensure_ascii=False) + "\\n")'
    if envelope not in text:
        raise RuntimeError("processor correction anchor not found")
    return {**dict(source), "processor.py": text.replace(
        envelope, '            fout.write(json.dumps(processed, ensure_ascii=False) + "\\n")', 1,
    )}


def _score_directly(kind: str, mode: str | None, files: Mapping[str, str], info: Mapping[str, str],
                    artifact_digest: str, seed: int, log: Path) -> dict[str, Any]:
    """Development fallback for the nested macOS transport; never hard-codes a score."""
    worker_name = (
        "peerrolebench_pipe3_producer_scorer_worker_v2.py"
        if kind == "producer" else "peerrolebench_pipe3_recipient_scorer_worker_v2.py"
    )
    import importlib.util
    spec = importlib.util.spec_from_file_location("pipe3_direct_worker", ROOT / "scripts" / worker_name)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {worker_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="pipe3-direct-score-") as temp:
        root = Path(temp) / "public"
        root.mkdir(parents=True)
        (root.parent / "scratch").mkdir()
        for name, text in files.items():
            (root / name).write_text(text, encoding="utf-8")
        # The worker imports public modules by their short names.  Clear the
        # previous case's modules so a direct fallback cannot score stale
        # source from another temporary workspace.
        for module_name in ("models", "producer", "processor", "sink"):
            sys.modules.pop(module_name, None)
        sys.path.insert(0, str(root))
        scorer = (module.Scorer(root, info["event_class"], info["timestamp_field"], info["id_field"])
                  if kind == "producer" else
                  module.Scorer(root, mode, info["event_class"], info["timestamp_field"], info["id_field"]))
        try:
            value = scorer.run(artifact_digest)
        finally:
            if sys.path and sys.path[0] == str(root):
                sys.path.pop(0)
            for module_name in ("models", "producer", "processor", "sink"):
                sys.modules.pop(module_name, None)
    value.update(task_id=TASK_ID, seed=seed)
    result = (classify_producer({"ok": True, "value": value}, artifact_digest, TASK_ID, seed)
              if kind == "producer" else
              classify_recipient({"ok": True, "value": value}, artifact_digest, TASK_ID, seed, mode))
    result["transport"] = {"status": "direct_cpu_fallback", "worker": worker_name}
    _log(log, "scorer_direct_cpu_fallback", {"kind": kind, "mode": mode,
                                               "worker": worker_name, "result": result})
    return result


def _run_scorers(files: Mapping[str, str], info: Mapping[str, str], out: Path,
                 log: Path, seed: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    producer_files = {"producer.py": files["producer.py"], "models.py": files["models.py"]}
    recipient_files = {"processor.py": files["processor.py"], "models.py": files["models.py"]}
    adoption_files = {name: files[name] for name in ("producer.py", "processor.py", "sink.py", "models.py")}
    def emit(event: str, payload: Any) -> None:
        _log(log, event, payload)
    calls = [
        ("producer", None, producer_files,
         lambda: run_producer_scorer(producer_files, info, TASK_ID, seed, out / "producer_scorer", emit)),
        ("recipient", "recipient", recipient_files,
         lambda: run_recipient_scorer(recipient_files, info, "recipient", TASK_ID, seed, out / "recipient_scorer", emit)),
        ("recipient", "adoption", adoption_files,
         lambda: run_recipient_scorer(adoption_files, info, "adoption", TASK_ID, seed, out / "adoption_scorer", emit)),
    ]
    results = []
    for kind, mode, scorer_files, call in calls:
        try:
            result = call()
        except (PermissionError, OSError, RuntimeError, ValueError) as exc:
            _log(log, "scorer_transport_failure", {"kind": kind, "mode": mode,
                                                    "error_type": type(exc).__name__, "message": str(exc)})
            result = _score_directly(kind, mode, scorer_files, info,
                                     scorer_digest_files(scorer_files), seed, log)
        results.append(result)
    return results[0], results[1], results[2]


def _ledger_prefix(case: str, artifact_digest: str) -> PeerRoleLedger:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection(
        f"selection-{case}", TASK_ID, 0, "selector", "producer",
        ("peer-b", "peer-c"), "peer-b", 0.5,
    ))
    ledger.record_task_start(TASK_ID, 0)
    ledger.record_delivery(Delivery(
        f"delivery-{case}", TASK_ID, "peer-b", "peer-a", artifact_digest,
        f"request-{case}", 0, f"selection-{case}",
    ))
    return ledger


def _episode(case: str, *, materials: dict[str, Any], final_sources: Mapping[str, str],
             delivery_sources: Mapping[str, str], out: Path, log: Path,
             generator: Any, seed: int) -> dict[str, Any]:
    info = interfaces(materials)
    delivery_digest = digest_files(delivery_sources)
    ledger = _ledger_prefix(case, delivery_digest)
    before_sources = dict(materials["agent_payloads"]["recipient"]["source_files"])
    before_sources["producer.py"] = delivery_sources["producer.py"]
    producer, recipient, adoption = _run_scorers(before_sources, info, out / "before_action", log, seed)

    ledger.record_judgment(RecipientJudgment(
        f"judgment-{case}", f"delivery-{case}", "peer-a", "accept_with_rework", delivery_digest,
        repair_note="CPU qualification control",
    ))
    action_payload = prepare_pipe3_action(materials, delivery_sources, "repair")
    final_snapshot = dict(action_payload["source_files"])
    final_snapshot.update({"producer.py": final_sources["producer.py"], "processor.py": final_sources["processor.py"]})
    action_result = validate_pipe3_action_result(action_payload, final_snapshot)
    ledger.record_action(ConsumerAction(
        f"action-{case}", f"delivery-{case}", "peer-a", True, delivery_digest,
        action_result["output_source_sha256"], 0.0, "repair",
    ))
    _, recipient_after, adoption_after = _run_scorers(final_snapshot, info, out / "after_action", log, seed)
    outcome_payload = {
        "status": "PASS" if recipient_after.get("status") == "PASS" and adoption_after.get("status") == "PASS" else "FAIL",
        "coverage_complete": recipient_after.get("coverage_complete") is True and adoption_after.get("coverage_complete") is True,
        "decision_complete": recipient_after.get("decision_complete") is True and adoption_after.get("decision_complete") is True,
    }
    outcome_success = outcome_payload["status"] == "PASS" and outcome_payload["coverage_complete"] and outcome_payload["decision_complete"]
    outcome = TerminalOutcome(
        f"outcome-{case}", f"delivery-{case}", outcome_success,
        "pipe3-recipient-objective-v2", float(adoption_after.get("quality_score") or 0.0),
        _sha_text(json.dumps(outcome_payload, sort_keys=True)),
    )
    ledger.record_outcome(outcome)
    judgment = {
        "observed_artifact_sha256": delivery_digest,
        "target_role": "producer" if case == "producer_fix" else "recipient",
    }
    eligibility = producer_feedback_eligibility(materials, producer, judgment, action_result, outcome_payload)
    eligible = bool(eligibility["producer_feedback_eligible"])
    records = {row["event_type"]: row for row in ledger.events}
    selection = DecisionSidecar(
        ledger_record_hash=records["peer_selection"]["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id=f"selection-{case}", task_id=TASK_ID, task_index=0, role="producer",
        event_id=f"policy-selection-{case}", selector_id="selector", context_key="PIPE3:0",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="cpu-qualification", encoder_version="cpu-qualification", feature_schema="pipe3",
        policy_name="qualification", policy_version="v1", base_score_version="v1",
        rng_algorithm="fixed", rng_draw=0, selected_at=0.0,
    )
    action_record = records["consumer_action"]
    sidecar = FeedbackSidecar(
        ledger_record_hash=records["recipient_judgment"]["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id=f"judgment-{case}", feedback_id=f"feedback-{case}", source_event_id=f"policy-selection-{case}",
        selection_event_id=f"selection-{case}", delivery_id=f"delivery-{case}", producer_id="peer-b", producer_version="v1",
        recipient_id="peer-a", source="recipient_judgment", arrived_at=1.0, delay=1.0, action="repair",
        disposition="eligible" if eligible else "unknown", provenance="public" if eligible else "unknown",
        label_mapping_version="cpu-v1", mapping_digest="a" * 64,
        responsibility_status="attributed" if eligible else "pending_attribution", attribution_basis=eligibility["reason"],
        artifact_sha256=delivery_digest, delivery_record_hash=records["producer_delivery"]["record_hash"],
        action_id=action_record["payload"]["action_id"], action_record_hash=action_record["record_hash"],
        raw_value="accept_with_rework", label=1.0 if eligible else None, arrival_index=0,
        sidecar_version="peerrole-policy-sidecar-v4",
    )
    gate_payload = {
        "gate_version": "producer-feedback-eligibility-v1", "ledger_record_hash": sidecar.ledger_record_hash,
        "sidecar_digest": sidecar.sidecar_digest, "protocol_event_type": sidecar.protocol_event_type,
        "protocol_event_id": sidecar.protocol_event_id, "source_event_id": sidecar.source_event_id,
        "delivery_id": sidecar.delivery_id, "producer_id": sidecar.producer_id, "producer_version": sidecar.producer_version,
        "recipient_id": sidecar.recipient_id, "selection_event_id": sidecar.selection_event_id,
        "eligible": eligible, "weight": 1.0 if eligible else None, "label": 1.0 if eligible else None,
        "label_mapping_version": sidecar.label_mapping_version, "evidence_version": "pipe3-cpu-v1", "source_index": 0,
    }
    gate = AttributionGate(**gate_payload, gate_digest=_digest(gate_payload))
    schedule = (ArrivalAssignment(sidecar.feedback_id, sidecar.protocol_event_type, sidecar.protocol_event_id, sidecar.source_event_id, 0),)
    source_offer = build_source_bound_offer(
        selection=selection, selection_record=records["peer_selection"],
        feedback_inputs=((sidecar, records["recipient_judgment"], gate, None if eligible else "recipient-owned-or-unattributed"),),
        ledger=ledger, arrival_schedule=schedule, offer_id=f"offer-{case}", context_key="PIPE3:1",
    )
    profile = None
    assignment_trace = None
    if eligible:
        projection = project_feedback(sidecar, gate, selection=selection)
        generated = generator.generate(PublicProfileGenerationRequest(
            selection=selection, feedback_sidecar=sidecar, public_projection=projection, attribution_gate=gate,
            profile_id=f"profile-{case}-r1", profile_revision=1, profile=PROFILE_FIELDS,
            parser_version="cpu-v1", model_config_digest="b" * 64, available_index=0,
        ))
        profile = generated.profile
        assignment_offer = MetaTeamAssignmentOffer.build(
            offer_id=f"assignment-{case}", task_id=TASK_ID, decision_index=1, read_cut=1,
            candidate_keys=("peer-b@v1", "peer-c@v1"), profiles=(profile,),
        )
        runner = Pipe3AssignmentRunner(assignment_offer)
        runner.emit_offer()
        attestation = runner.consume_profiles((profile.profile_id,), isolated_policy_read=True)
        later_selection = SimpleNamespace(
            candidates=(SimpleNamespace(key="peer-b@v1"), SimpleNamespace(key="peer-c@v1")), task_index=1, selected_at=1.0,
        )
        runner.seal_selection(later_selection, attestation)
        ledger.record_selection(PeerSelection(
            f"selection-{case}-1", TASK_ID, 1, "selector", "producer", ("peer-b", "peer-c"), "peer-b", 0.5,
        ))
        runner.start_task(ledger)
        assignment_trace = runner.trace
    return {
        "case": case, "delivery_artifact_sha256": delivery_digest,
        "producer_score": producer, "recipient_before": recipient, "adoption_before": adoption,
        "recipient_after": recipient_after, "adoption_after": adoption_after,
        "action": action_result, "outcome": outcome_payload, "eligibility": eligibility,
        "offer": source_offer.offer.payload(), "profile": profile.payload() if profile else None,
        "assignment_trace": assignment_trace, "ledger": ledger.events,
    }


def run(out_dir: Path, *, profile_generator=None, seed: int = 0) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_log = out_dir / "events.jsonl"
    started = time.perf_counter()
    generated = load_pipe3(seed)
    materials = build_materials(generated)
    base = dict(materials["agent_payloads"]["producer"]["source_files"])
    base.update(materials["agent_payloads"]["recipient"]["source_files"])
    recipient_correct = _patch_recipient(base)
    producer_correct = _patch_producer(base)
    producer_final = _patch_recipient(producer_correct)
    config = {
        "qualification": "pipe3-profile-episode-cpu-v2", "task_id": TASK_ID, "seed": seed,
        "cases": ["producer_fix", "recipient_fix"], "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(), "platform": platform.platform(), "runner_sha256": _sha_file(Path(__file__)),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    _log(raw_log, "config", config)
    generator = profile_generator or DeterministicPublicProfileGenerator()
    producer_materials = deepcopy(materials)
    producer_materials["agent_payloads"]["recipient"]["source_files"]["processor.py"] = recipient_correct["processor.py"]
    recipient_materials = deepcopy(materials)
    records = [
        _episode("producer_fix", materials=producer_materials, final_sources=producer_final,
                 delivery_sources={"producer.py": base["producer.py"]}, out=out_dir / "producer_fix",
                 log=raw_log, generator=generator, seed=seed),
        _episode("recipient_fix", materials=recipient_materials, final_sources=producer_final,
                 delivery_sources={"producer.py": producer_correct["producer.py"]}, out=out_dir / "recipient_fix",
                 log=raw_log, generator=generator, seed=seed),
    ]
    passed = (
        records[0]["eligibility"]["producer_feedback_status"] == "ELIGIBLE"
        and records[0]["profile"] is not None
        and records[0]["assignment_trace"][-1]["event"] == "task_started"
        and records[1]["eligibility"]["producer_feedback_status"] == "PENDING_ATTRIBUTION"
        and records[1]["profile"] is None
    )
    result = {
        **config, "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE", "passed": passed,
        "cases": records, "elapsed_cpu_seconds": time.perf_counter() - started,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "remaining_gates": [
            "replace deterministic profile fixture with a metered public-only generator",
            "execute one bounded real episode only after this composition remains stable",
            "independent roots, live history, baseline parity, and later-use effect remain open",
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir.resolve())
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
