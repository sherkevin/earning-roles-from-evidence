"""Zero-LLM PIPE3 public sidecar -> Meta-Team profile replay qualification."""

from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_metateam_profile_sidecar import (  # noqa: E402
    build_public_profile_fixture, replay_public_profile_fixture,
)
from peerrolebench_pipe3_material_adapter import build_materials, digest_files  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, project_feedback  # noqa: E402
from peerrolebench_policy_sidecar import (  # noqa: E402
    DecisionSidecar, FeedbackSidecar, bind_to_ledger_record,
)

DIGEST = "a" * 64
PROFILE = {
    "reliability": "medium",
    "strengths": ["queue integration"],
    "weaknesses": ["priority ordering"],
    "communication_style": "concise",
    "notes": ["public recipient judgment only"],
}


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def make_gate(sidecar: FeedbackSidecar) -> AttributionGate:
    values = {
        "gate_version": "pipe3-metateam-gate-v1",
        "ledger_record_hash": sidecar.ledger_record_hash,
        "sidecar_digest": sidecar.sidecar_digest,
        "protocol_event_type": sidecar.protocol_event_type,
        "protocol_event_id": sidecar.protocol_event_id,
        "source_event_id": sidecar.source_event_id,
        "delivery_id": sidecar.delivery_id,
        "producer_id": sidecar.producer_id,
        "producer_version": sidecar.producer_version,
        "recipient_id": sidecar.recipient_id,
        "selection_event_id": sidecar.selection_event_id,
        "eligible": True,
        "weight": 1.0,
        "label": sidecar.label,
        "label_mapping_version": sidecar.label_mapping_version,
        "evidence_version": "pipe3-evidence-v1",
        "source_index": 5,
    }
    payload = {key: values[key] for key in (
        "gate_version", "ledger_record_hash", "sidecar_digest", "protocol_event_type",
        "protocol_event_id", "source_event_id", "delivery_id", "producer_id",
        "producer_version", "recipient_id", "selection_event_id", "eligible", "weight",
        "label", "label_mapping_version", "evidence_version", "source_index",
    )}
    return AttributionGate(**values, gate_digest=hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest())


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    materials = build_materials(load_pipe3(0))
    producer_files = {"producer.py": materials["agent_payloads"]["producer"]["source_files"]["producer.py"]}
    artifact_hash = digest_files(producer_files)

    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection(
        selection_id="selection-0", task_id="PIPE3_stream_processing", task_index=0,
        selector_id="peer-a", role="producer", candidate_ids=("peer-b", "peer-c"),
        chosen_peer_id="peer-b", propensity=0.5,
    ))
    ledger.record_task_start("PIPE3_stream_processing", 0)
    ledger.record_delivery(Delivery(
        delivery_id="delivery-0", task_id="PIPE3_stream_processing", producer_id="peer-b",
        recipient_id="peer-a", artifact_sha256=artifact_hash, source_event_id="request-0",
        task_index=0, selection_id="selection-0",
    ))
    ledger.record_judgment(RecipientJudgment(
        judgment_id="judgment-0", delivery_id="delivery-0", consumer_id="peer-a",
        decision="accept", observed_artifact_sha256=artifact_hash,
    ))
    ledger.record_action(ConsumerAction(
        action_id="action-0", delivery_id="delivery-0", consumer_id="peer-a", used_artifact=True,
        input_artifact_sha256=artifact_hash, output_artifact_sha256=artifact_hash, action="use",
    ))
    ledger.record_outcome(TerminalOutcome(
        outcome_id="outcome-0", delivery_id="delivery-0", success=True,
        scorer_version="fixture-not-scorer-v1", partial_score=1.0,
    ))
    ledger.record_evidence_update(RoleEvidenceUpdate(
        evidence_id="evidence-0", judgment_id="judgment-0", action_id="action-0",
        outcome_id="outcome-0", update_version="fixture-v1", arrived_at=13.0,
    ))
    records = {row["event_type"]: row for row in ledger.events}

    selection = DecisionSidecar(
        ledger_record_hash=records["peer_selection"]["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id="selection-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", event_id="policy-selection-0", selector_id="peer-a", context_key="PIPE3:0",
        candidates=(CandidateRef("peer-b", "fixture-v1"), CandidateRef("peer-c", "fixture-v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="fixture-state-0", encoder_version="fixture-encoder-0", feature_schema="fixture-phi-0",
        policy_name="metateam_l2_public_fixture", policy_version="v1", base_score_version="fixture-base-v1",
        rng_algorithm="fixture-rng", rng_draw=0, selected_at=10.0,
    )
    judgment = FeedbackSidecar(
        ledger_record_hash=records["recipient_judgment"]["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id="judgment-0", feedback_id="feedback-judgment-0", source_event_id="policy-selection-0",
        selection_event_id="selection-0", delivery_id="delivery-0", producer_id="peer-b",
        producer_version="fixture-v1", recipient_id="peer-a", source="recipient_judgment",
        arrived_at=12.0, delay=2.0, action="use", disposition="eligible", provenance="public",
        label_mapping_version="judgment-v1", mapping_digest=DIGEST,
        responsibility_status="attributed", attribution_basis="fixture-judgment-v1",
        artifact_sha256=artifact_hash, delivery_record_hash=records["producer_delivery"]["record_hash"],
        action_id="action-0", action_record_hash=records["consumer_action"]["record_hash"],
        raw_value="accept", label=1.0, arrival_index=12,
        sidecar_version="peerrole-policy-sidecar-v4",
    )
    bind_to_ledger_record(selection.payload(), records["peer_selection"], expected_event_type="peer_selection", expected_event_id="selection-0")
    bind_to_ledger_record(judgment.payload(), records["recipient_judgment"], expected_event_type="recipient_judgment", expected_event_id="judgment-0")
    projection = project_feedback(judgment, make_gate(judgment), selection=selection)

    profile = build_public_profile_fixture(
        selection=selection, feedback_sidecar=judgment, public_projection=projection,
        profile_id="pipe3-profile-0", profile_revision=1, profile=PROFILE,
        parser_version="fixture-parser-v1", model_config_digest=digest_text("fixture-profile-model-v1"),
    )
    replayed = replay_public_profile_fixture(
        profile, selection=selection, feedback_sidecar=judgment, public_projection=projection,
    )
    if replayed.profile_digest != profile.profile_digest:
        raise AssertionError("PIPE3 profile replay digest mismatch")

    mutation_results = {}
    mutation_results["wrong_candidate"] = "REJECTED" if _reject_wrong_candidate(selection, judgment, projection, profile) else "ACCEPTED"
    mutation_results["wrong_public_payload"] = "REJECTED" if _reject_wrong_payload(selection, judgment, projection, profile) else "ACCEPTED"
    if any(value != "REJECTED" for value in mutation_results.values()):
        raise AssertionError(f"PIPE3 mutation was accepted: {mutation_results}")

    config = {
        "experiment_id": "n03_metateam_pipe3_public_replay_20260930",
        "kind": "zero_llm_pipe3_metateam_public_profile_builder_replay_qualification_not_scientific_benchmark",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        },
        "runner_script": str(Path(__file__).resolve()),
        "runner_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "profile_sidecar_sha256": hashlib.sha256(
            (ROOT / "scripts/peerrolebench_metateam_profile_sidecar.py").read_bytes()
        ).hexdigest(),
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "profile_schema": profile.profile_schema, "profile_digest": profile.profile_digest,
        "source_input_digest": profile.source_input_digest,
        "mutation_results": mutation_results,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    raw = {
        "selection": selection.payload(), "judgment": judgment.payload(),
        "projection": projection.public_payload(), "profile": profile.payload(),
        "replayed_profile_digest": replayed.profile_digest,
    }
    (out_dir / "raw.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n")
    summary = {"status": "QUALIFIED_OFFLINE", "passed": True, **config,
               "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def _reject_wrong_candidate(selection, judgment, projection, profile) -> bool:
    mutated = replace(projection, candidate_key="peer-c@fixture-v1")
    try:
        replay_public_profile_fixture(profile, selection=selection, feedback_sidecar=judgment, public_projection=mutated)
    except ValueError:
        return True
    return False


def _reject_wrong_payload(selection, judgment, projection, profile) -> bool:
    mutated = replace(projection, label=0.0)
    try:
        replay_public_profile_fixture(profile, selection=selection, feedback_sidecar=judgment, public_projection=mutated)
    except ValueError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"status": result["status"], "real_api_calls": 0, "gpu_jobs": 0,
                      "scientific_claim_allowed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
