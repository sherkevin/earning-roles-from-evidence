"""Qualify raw-acceptance sidecars in the canonical replay boundary.

The ledger and sidecars are deterministic fixtures.  This is a runner/replay
contract check, not a benchmark or a scientific effect experiment.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, PeerRoleLedger, PeerSelection, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import CandidateRef, RawAcceptancePolicy  # noqa: E402
from peerrolebench_policy_projection import (  # noqa: E402
    RAW_ACCEPTANCE_MAPPING_VERSION, RawAcceptanceSidecar,
)
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar  # noqa: E402
from peerrolebench_policy_sidecar_manifest import build_manifest  # noqa: E402
from peerrolebench_policy_sidecar_replay import SidecarRow, replay_policy_sidecars  # noqa: E402


ARTIFACT = "b" * 64
DIGEST = "a" * 64


def ledger_events() -> list[dict]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection(
        selection_id="selection-0", task_id="task", task_index=0, selector_id="peer-a",
        role="producer", candidate_ids=("peer-b", "peer-c"), chosen_peer_id="peer-b", propensity=0.5,
    ))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery(
        delivery_id="delivery-0", task_id="task", producer_id="peer-b", recipient_id="peer-a",
        artifact_sha256=ARTIFACT, source_event_id="request-0", task_index=0, selection_id="selection-0",
    ))
    ledger.record_judgment(RecipientJudgment(
        judgment_id="judgment-0", delivery_id="delivery-0", consumer_id="peer-a",
        decision="accept", observed_artifact_sha256=ARTIFACT,
    ))
    ledger.record_action(ConsumerAction(
        action_id="action-0", delivery_id="delivery-0", consumer_id="peer-a",
        used_artifact=True, input_artifact_sha256=ARTIFACT, output_artifact_sha256=ARTIFACT,
        action="use",
    ))
    ledger.record_outcome(TerminalOutcome(
        outcome_id="outcome-0", delivery_id="delivery-0", success=True,
        scorer_version="terminal-v1", partial_score=1.0,
    ))
    ledger.record_evidence_update(RoleEvidenceUpdate(
        evidence_id="evidence-0", judgment_id="judgment-0", action_id="action-0",
        outcome_id="outcome-0", update_version="evidence-v1", arrived_at=13.0,
    ))
    return ledger.events


def _event(events: list[dict], event_type: str) -> dict:
    return next(item for item in events if item["event_type"] == event_type)


def sidecar_rows(events: list[dict]) -> list[SidecarRow]:
    selection_record = _event(events, "peer_selection")
    judgment_record = _event(events, "recipient_judgment")
    outcome_record = _event(events, "terminal_outcome")
    selection = DecisionSidecar(
        ledger_record_hash=selection_record["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id="selection-0", task_id="task", task_index=0, role="producer",
        event_id="policy-selection-0", selector_id="peer-a", context_key="ctx",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="state-0", encoder_version="enc-0", feature_schema="phi-0",
        policy_name="raw_acceptance", policy_version="raw-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=10.0,
    )
    raw = RawAcceptanceSidecar(
        ledger_record_hash=judgment_record["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id="judgment-0", feedback_id="raw-feedback-0",
        source_event_id="policy-selection-0", selection_event_id="selection-0",
        delivery_id="delivery-0", producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        decision="accept", label_mapping_version=RAW_ACCEPTANCE_MAPPING_VERSION,
        mapping_digest=DIGEST, source_index=0, arrived_at=12.0, delay=2.0,
    )
    terminal = FeedbackSidecar(
        ledger_record_hash=outcome_record["record_hash"], protocol_event_type="terminal_outcome",
        protocol_event_id="outcome-0", feedback_id="terminal-feedback-0",
        source_event_id="policy-selection-0", selection_event_id="selection-0",
        delivery_id="delivery-0", producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        source="terminal_outcome", arrived_at=13.0, delay=3.0, action="use",
        disposition="eligible", provenance="public", label_mapping_version="terminal-v1",
        mapping_digest=DIGEST, responsibility_status="attributed", attribution_basis="terminal-v1",
        raw_value=True, label=1.0,
    )
    return [
        SidecarRow(selection, selection_record, selection.sidecar_digest),
        SidecarRow(raw, judgment_record, raw.sidecar_digest),
        SidecarRow(terminal, outcome_record, terminal.sidecar_digest),
    ]


def manifest(rows: list[SidecarRow]) -> list[dict[str, str]]:
    return build_manifest([{
        "ledger_record_hash": row.sidecar.payload()["ledger_record_hash"],
        "protocol_event_type": row.sidecar.protocol_event_type,
        "protocol_event_id": row.sidecar.protocol_event_id,
        "sidecar_digest": row.sidecar.sidecar_digest,
    } for row in rows])


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    events = ledger_events()
    rows = sidecar_rows(events)
    config = {
        "experiment_id": "n03_raw_acceptance_replay_20260929_v1",
        "kind": "zero_call_versioned_replay_contract_not_scientific_benchmark",
        "policy": "raw_acceptance",
        "cases": ["canonical", "wrong_canonical_decision", "wrong_producer", "duplicate_sidecar"],
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        },
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    cases: list[dict] = []
    canonical_manifest = manifest(rows)
    canonical = replay_policy_sidecars(events, rows, RawAcceptancePolicy, canonical_manifest)
    cases.append({"case": "canonical", "result": canonical,
                  "expectation_met": canonical["status"] == "PASS"
                  and canonical["update_count"] == 1 and canonical["ignored_channel_count"] == 1})

    raw = rows[1].sidecar
    assert isinstance(raw, RawAcceptanceSidecar)
    wrong_decision = replace(raw, decision="reject")
    wrong_rows = [rows[0], SidecarRow(wrong_decision, rows[1].ledger_record, wrong_decision.sidecar_digest), rows[2]]
    wrong = replay_policy_sidecars(events, wrong_rows, RawAcceptancePolicy, manifest(wrong_rows))
    cases.append({"case": "wrong_canonical_decision", "result": wrong,
                  "expectation_met": wrong["status"] == "INVALID" and wrong["update_count"] == 0})

    wrong_producer = replace(raw, producer_id="peer-c")
    wrong_producer_rows = [rows[0], SidecarRow(wrong_producer, rows[1].ledger_record, wrong_producer.sidecar_digest), rows[2]]
    wrong_producer_result = replay_policy_sidecars(
        events, wrong_producer_rows, RawAcceptancePolicy, manifest(wrong_producer_rows),
    )
    cases.append({"case": "wrong_producer", "result": wrong_producer_result,
                  "expectation_met": wrong_producer_result["status"] == "INVALID"
                  and wrong_producer_result["update_count"] == 0})

    duplicate = replay_policy_sidecars(
        events, rows + [rows[1]], RawAcceptancePolicy, canonical_manifest,
    )
    cases.append({"case": "duplicate_sidecar", "result": duplicate,
                  "expectation_met": duplicate["status"] == "INVALID" and duplicate["update_count"] == 0})

    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps({
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "event_type": "case_result", "payload": {
                    "case": case["case"], "expectation_met": case["expectation_met"],
                    "status": case["result"]["status"], "update_count": case["result"]["update_count"],
                    "unknown_count": case["result"].get("unknown_count", 0),
                    "ignored_channel_count": case["result"].get("ignored_channel_count", 0),
                },
            }, sort_keys=True) + "\n")
    passed = all(case["expectation_met"] for case in cases)
    summary = {
        "experiment_id": config["experiment_id"], "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed, "case_count": len(cases), "cases": cases,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"passed": result["passed"], "status": result["status"], "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
