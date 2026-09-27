"""Run a zero-LLM PIPE3 material-to-sidecar integration qualification."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import CandidateRef, TerminalOnlyPolicy
from peerrolebench_pipe3_material_adapter import build_materials, digest_files
from peerrolebench_pipe3_runner_adapter import (
    attach_pipe3_delivery, prepare_pipe3_action, validate_pipe3_action_result,
)
from peerrolebench_pipe3_task_qualification import load_pipe3
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar
from peerrolebench_policy_sidecar_manifest import build_manifest
from peerrolebench_policy_sidecar_replay import SidecarRow, replay_policy_sidecars

DIGEST = "a" * 64


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    materials = build_materials(load_pipe3(0))
    producer_files = {"producer.py": materials["agent_payloads"]["producer"]["source_files"]["producer.py"]}
    recipient_payload = attach_pipe3_delivery(materials["agent_payloads"]["recipient"], producer_files)
    action_payload = prepare_pipe3_action(materials, producer_files, "use")
    validated = validate_pipe3_action_result(action_payload, action_payload["source_files"])
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
        input_artifact_sha256=artifact_hash, output_artifact_sha256=validated["output_source_sha256"],
        action="use",
    ))
    ledger.record_outcome(TerminalOutcome(
        outcome_id="outcome-0", delivery_id="delivery-0", success=True,
        scorer_version="fixture-not-scorer-v1", partial_score=1.0,
    ))
    ledger.record_evidence_update(RoleEvidenceUpdate(
        evidence_id="evidence-0", judgment_id="judgment-0", action_id="action-0",
        outcome_id="outcome-0", update_version="fixture-v1", arrived_at=13.0,
    ))
    events = ledger.events
    records = {row["event_type"]: row for row in events}

    selection = DecisionSidecar(
        ledger_record_hash=records["peer_selection"]["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id="selection-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", event_id="policy-selection-0", selector_id="peer-a", context_key="PIPE3:0",
        candidates=(CandidateRef("peer-b", "fixture-v1"), CandidateRef("peer-c", "fixture-v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="fixture-state-0", encoder_version="fixture-encoder-0", feature_schema="fixture-phi-0",
        policy_name="terminal_only", policy_version="v1", base_score_version="fixture-base-v1",
        rng_algorithm="fixture-rng", rng_draw=0, selected_at=10.0,
    )
    judgment = FeedbackSidecar(
        ledger_record_hash=records["recipient_judgment"]["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id="judgment-0", feedback_id="feedback-judgment-0", source_event_id="policy-selection-0",
        selection_event_id="selection-0", delivery_id="delivery-0", producer_id="peer-b",
        producer_version="fixture-v1", recipient_id="peer-a", source="recipient_judgment",
        arrived_at=12.0, delay=2.0, action="use", disposition="unknown", provenance="unknown",
        label_mapping_version="", mapping_digest="", responsibility_status="unknown", attribution_basis="",
        raw_value="accept", label=None,
    )
    outcome = FeedbackSidecar(
        ledger_record_hash=records["terminal_outcome"]["record_hash"], protocol_event_type="terminal_outcome",
        protocol_event_id="outcome-0", feedback_id="feedback-outcome-0", source_event_id="policy-selection-0",
        selection_event_id="selection-0", delivery_id="delivery-0", producer_id="peer-b",
        producer_version="fixture-v1", recipient_id="peer-a", source="terminal_outcome",
        arrived_at=13.0, delay=3.0, action="use", disposition="eligible", provenance="public",
        label_mapping_version="fixture-terminal-v1", mapping_digest=DIGEST,
        responsibility_status="attributed", attribution_basis="fixture-terminal-v1", raw_value=True, label=1.0,
    )
    sidecar_rows = [
        SidecarRow(selection, records["peer_selection"], selection.sidecar_digest),
        SidecarRow(judgment, records["recipient_judgment"], judgment.sidecar_digest),
        SidecarRow(outcome, records["terminal_outcome"], outcome.sidecar_digest),
    ]
    manifest = build_manifest([
        {"ledger_record_hash": row.sidecar.payload()["ledger_record_hash"],
         "protocol_event_type": row.sidecar.protocol_event_type,
         "protocol_event_id": row.sidecar.protocol_event_id,
         "sidecar_digest": row.sidecar.sidecar_digest}
        for row in sidecar_rows
    ])
    result = replay_policy_sidecars(events, sidecar_rows, TerminalOnlyPolicy, manifest)

    config = {
        "experiment_id": "n03_pipe3_policy_sidecar_fixture_20260928",
        "kind": "zero_llm_pipe3_material_sidecar_qualification_not_scientific_benchmark",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        },
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "material_adapter": "pipe3 pinned task adapter",
        "source_files": sorted(recipient_payload["source_files"]),
        "artifact_sha256": artifact_hash, "manifest_root": result.get("manifest_root"),
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (out_dir / "raw.jsonl").write_text(json.dumps({"event_type": "fixture_result", "payload": result}, indent=2) + "\n")
    summary = {
        "experiment_id": config["experiment_id"],
        "passed": result["status"] == "PASS" and result["update_count"] == 1,
        "replay_result": result, "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"passed": result["passed"], "real_api_calls": 0, "gpu_jobs": 0,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
