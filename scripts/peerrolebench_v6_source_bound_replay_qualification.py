"""Replay one frozen real PIPE3 v6 ledger through the source-bound adapter.

No model is called.  The purpose is to check that the adapter can consume a
real previously recorded ledger/artifact lineage and preserve its pending
attribution as UNKNOWN rather than turning it into a learnable label.
"""

from __future__ import annotations

import argparse
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

from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_file  # noqa: E402
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_policy_projection import AttributionGate, _digest  # noqa: E402
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar  # noqa: E402
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402


SOURCE_RUN = ROOT / "experiments/logs/n03_pipe3_real_smoke_20260929_v6"
DIGEST = "a" * 64


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = SOURCE_RUN / "ledger.json"
    ledger_result = replay_ledger_file(ledger_path, allow_incomplete=True)
    ledger = ledger_result.ledger
    records = {row["event_type"]: row for row in ledger.events}
    selection_record = records["peer_selection"]
    delivery_record = records["producer_delivery"]
    judgment_record = records["recipient_judgment"]
    action_record = records["consumer_action"]
    judgment = judgment_record["payload"]
    delivery = delivery_record["payload"]
    selection = DecisionSidecar(
        ledger_record_hash=selection_record["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id=selection_record["payload"]["selection_id"], task_id="PIPE3_stream_processing",
        task_index=0, role="producer", event_id="policy-selection-0", selector_id="peer-a",
        context_key="PIPE3:0", candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="v6-replay-state", encoder_version="v6-replay-encoder", feature_schema="pipe3",
        policy_name="v6-replay", policy_version="v1", base_score_version="v1",
        rng_algorithm="replay", rng_draw=0, selected_at=0.0,
    )
    sidecar = FeedbackSidecar(
        ledger_record_hash=judgment_record["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id=judgment["judgment_id"], feedback_id="v6-feedback-unknown",
        source_event_id=selection.event_id, selection_event_id=selection.protocol_event_id,
        delivery_id=judgment["delivery_id"], producer_id=delivery["producer_id"], producer_version="v1",
        recipient_id=judgment["consumer_id"], source="recipient_judgment",
        arrived_at=1.0, delay=1.0, action=action_record["payload"]["action"],
        disposition="unknown", provenance="unknown", label_mapping_version="v6-label-v1",
        mapping_digest=DIGEST, responsibility_status="pending_attribution",
        attribution_basis="recipient-owned-change", artifact_sha256=delivery["artifact_sha256"],
        delivery_record_hash=delivery_record["record_hash"], action_id=action_record["payload"]["action_id"],
        action_record_hash=action_record["record_hash"], arrival_index=0,
        sidecar_version="peerrole-policy-sidecar-v4",
    )
    gate_values = {
        "gate_version": "v6-replay-gate-v1", "ledger_record_hash": sidecar.ledger_record_hash,
        "sidecar_digest": sidecar.sidecar_digest, "protocol_event_type": sidecar.protocol_event_type,
        "protocol_event_id": sidecar.protocol_event_id, "source_event_id": sidecar.source_event_id,
        "delivery_id": sidecar.delivery_id, "producer_id": sidecar.producer_id,
        "producer_version": sidecar.producer_version, "recipient_id": sidecar.recipient_id,
        "selection_event_id": sidecar.selection_event_id, "eligible": False, "weight": None,
        "label": None, "label_mapping_version": sidecar.label_mapping_version,
        "evidence_version": "v6-evidence-v1", "source_index": 0,
    }
    gate = AttributionGate(**gate_values, gate_digest=_digest(gate_values))
    schedule = (ArrivalAssignment(sidecar.feedback_id, sidecar.protocol_event_type, sidecar.protocol_event_id, sidecar.source_event_id, 0),)
    result = build_source_bound_offer(
        selection=selection, selection_record=selection_record,
        feedback_inputs=((sidecar, judgment_record, gate, "recipient-owned-change"),), ledger=ledger,
        arrival_schedule=schedule, offer_id="v6-offer-0", context_key="PIPE3:1",
    )
    row = dict(result.offer.public_rows[0])
    if result.offer.public_rows[0].get("label") is not None or row.get("unknown_reason") != "recipient-owned-change":
        raise AssertionError("v6 pending attribution leaked a label or lost UNKNOWN reason")
    config = {
        "qualification": "real-v6-ledger-source-bound-replay-v1",
        "source_run": str(SOURCE_RUN.relative_to(ROOT)),
        "source_summary_sha256": hashlib.sha256((SOURCE_RUN / "summary.json").read_bytes()).hexdigest(),
        "source_ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "source_ledger_status": ledger_result.status,
        "source_ledger_complete": ledger_result.complete,
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "python": platform.python_version(), "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    raw = {"selection": selection.payload(), "feedback_sidecar": sidecar.payload(), "public_row": row, "offer": result.offer.payload()}
    (out_dir / "raw.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n")
    summary = {**config, "status": "QUALIFIED_OFFLINE", "pending_attribution_preserved": True, "offer_bundle_digest": result.offer.bundle_digest, "schedule_digest": result.schedule_digest, "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "source_ledger_status", "pending_attribution_preserved", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
