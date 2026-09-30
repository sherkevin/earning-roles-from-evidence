"""Zero-call qualification for the source-bound PIPE3 feedback adapter."""

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
    TerminalOutcome,
)
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest  # noqa: E402
from peerrolebench_policy_sidecar import (  # noqa: E402
    DecisionSidecar, FeedbackSidecar, bind_to_ledger_record,
)
from peerrolebench_source_bound_feedback_adapter import (  # noqa: E402
    SourceBoundOffer, build_source_bound_offer,
)


DIGEST = "a" * 64


def fixture() -> tuple[PeerRoleLedger, DecisionSidecar, dict, FeedbackSidecar, dict, AttributionGate, tuple[ArrivalAssignment, ...]]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    native = PeerSelection("selection-0", "PIPE3_stream_processing", 0, "peer-a", "producer", ("peer-b", "peer-c"), "peer-b", 0.5)
    ledger.record_selection(native)
    ledger.record_task_start("PIPE3_stream_processing", 0)
    ledger.record_delivery(Delivery("delivery-0", "PIPE3_stream_processing", "peer-b", "peer-a", DIGEST, "request-0", 0, "selection-0"))
    ledger.record_judgment(RecipientJudgment("judgment-0", "delivery-0", "peer-a", "accept", DIGEST))
    ledger.record_action(ConsumerAction("action-0", "delivery-0", "peer-a", True, DIGEST, DIGEST, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("outcome-0", "delivery-0", True, "fixture-outcome-v1", 1.0))
    records = {(row["event_type"], row["payload"].get("selection_id") or row["payload"].get("judgment_id")): row for row in ledger.events}
    selection_record = next(row for row in ledger.events if row["event_type"] == "peer_selection")
    delivery_record = next(row for row in ledger.events if row["event_type"] == "producer_delivery")
    action_record = next(row for row in ledger.events if row["event_type"] == "consumer_action")
    selection = DecisionSidecar(
        ledger_record_hash=selection_record["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id="selection-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", event_id="policy-selection-0", selector_id="peer-a", context_key="PIPE3:0",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="state-0", encoder_version="enc-0", feature_schema="pipe3",
        policy_name="fixture", policy_version="v1", base_score_version="base-v1",
        rng_algorithm="fixture-rng", rng_draw=0, selected_at=0.0,
    )
    judgment_record = next(row for row in ledger.events if row["event_type"] == "recipient_judgment")
    sidecar = FeedbackSidecar(
        ledger_record_hash=judgment_record["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id="judgment-0", feedback_id="feedback-0", source_event_id="policy-selection-0",
        selection_event_id="selection-0", delivery_id="delivery-0", producer_id="peer-b", producer_version="v1",
        recipient_id="peer-a", source="recipient_judgment", arrived_at=1.0, delay=1.0, action="use",
        disposition="eligible", provenance="public", label_mapping_version="fixture-label-v1",
        mapping_digest=DIGEST, responsibility_status="attributed", attribution_basis="fixture-v1",
        artifact_sha256=DIGEST, delivery_record_hash=delivery_record["record_hash"],
        action_id="action-0", action_record_hash=action_record["record_hash"], raw_value="accept", label=1.0,
        arrival_index=0, sidecar_version="peerrole-policy-sidecar-v4",
    )
    gate_values = {
        "gate_version": "fixture-gate-v1", "ledger_record_hash": sidecar.ledger_record_hash,
        "sidecar_digest": sidecar.sidecar_digest, "protocol_event_type": sidecar.protocol_event_type,
        "protocol_event_id": sidecar.protocol_event_id, "source_event_id": sidecar.source_event_id,
        "delivery_id": sidecar.delivery_id, "producer_id": sidecar.producer_id,
        "producer_version": sidecar.producer_version, "recipient_id": sidecar.recipient_id,
        "selection_event_id": sidecar.selection_event_id, "eligible": True, "weight": 1.0,
        "label": 1.0, "label_mapping_version": sidecar.label_mapping_version,
        "evidence_version": "fixture-evidence-v1", "source_index": 0,
    }
    gate = AttributionGate(**gate_values, gate_digest=_digest(gate_values))
    schedule = (ArrivalAssignment("feedback-0", "recipient_judgment", "judgment-0", "policy-selection-0", 0),)
    return ledger, selection, selection_record, sidecar, judgment_record, gate, schedule


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "qualification": "source-bound-pipe3-feedback-adapter-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256((ROOT / "scripts/peerrolebench_source_bound_feedback_adapter.py").read_bytes()).hexdigest(),
        "fixture_mode": "canonical-ledger-v4-sidecar-frozen-schedule",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "python": platform.python_version(), "platform": platform.platform(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    ledger, selection, selection_record, sidecar, judgment_record, gate, schedule = fixture()
    result = build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=ledger,
        arrival_schedule=schedule, offer_id="offer-0", context_key="PIPE3:1",
    )
    checks = [{
        "name": "canonical_v4_sidecar_to_offer", "status": "PASS",
        "offer_id": result.offer.offer_id, "candidate_keys": list(result.offer.candidate_keys),
        "schedule_digest": result.schedule_digest,
    }]

    def reject(name, fn):
        try:
            fn()
        except (TypeError, ValueError) as exc:
            checks.append({"name": name, "status": "PASS", "error": str(exc)})
        else:
            checks.append({"name": name, "status": "FAIL"})

    reject("reject_schedule_protocol_mutation", lambda: build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=ledger,
        arrival_schedule=(ArrivalAssignment("feedback-0", "terminal_outcome", "judgment-0", "policy-selection-0", 0),),
        offer_id="offer-bad-schedule", context_key="PIPE3:1",
    ))
    reject("reject_sidecar_record_hash_mutation", lambda: build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((replace(sidecar, ledger_record_hash="b" * 64), judgment_record, gate, None),), ledger=ledger,
        arrival_schedule=schedule, offer_id="offer-bad-hash", context_key="PIPE3:1",
    ))
    reject("reject_non_v4_online_sidecar", lambda: build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((replace(sidecar, sidecar_version="peerrole-policy-sidecar-v3", arrival_index=None, supersedes=None), judgment_record, gate, None),), ledger=ledger,
        arrival_schedule=schedule, offer_id="offer-old", context_key="PIPE3:1",
    ))
    reject("reject_schedule_index_mutation", lambda: build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((sidecar, judgment_record, gate, None),), ledger=ledger,
        arrival_schedule=(ArrivalAssignment("feedback-0", "recipient_judgment", "judgment-0", "policy-selection-0", 1),),
        offer_id="offer-bad-index", context_key="PIPE3:1",
    ))
    summary = {**config, "status": "QUALIFIED_OFFLINE" if all(row["status"] == "PASS" for row in checks) else "FAILED_OFFLINE", "checks": checks, "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "raw.json").write_text(json.dumps({"selection": selection.payload(), "feedback": sidecar.payload(), "offer": result.offer.payload()}, indent=2, ensure_ascii=False) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
