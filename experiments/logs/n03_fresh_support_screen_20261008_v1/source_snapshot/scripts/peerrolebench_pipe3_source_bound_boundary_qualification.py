"""Zero-call qualification of source-bound feedback on the live selection boundary.

This composes an existing canonical ``Pipe3SelectionBoundary`` with the
source-bound v4 offer adapter.  The first selection, delivery, judgment,
action, outcome, and responsibility lineage are recorded on one ledger; the
next selection consumes the sealed public offer on that same boundary.  It is
an engineering qualification only: no candidate source, LLM, GPU, or
scientific effect is evaluated.
"""

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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import (  # noqa: E402
    _append_episode, _make_feedback, registry,
)
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary, auxiliary_manifest_root, make_offer,
)
from peerrolebench_policy_projection import AttributionGate, _digest  # noqa: E402
from peerrolebench_policy_sidecar import EVENT_TIME_SIDECAR_VERSION  # noqa: E402
from peerrolebench_source_bound_feedback_adapter import build_source_bound_offer  # noqa: E402


TASK_ID = "PIPE3_stream_processing"


def _selection_record(boundary, selection_id: str):
    return next(
        row for row in boundary.ledger.events
        if row["event_type"] == "peer_selection"
        and row["payload"]["selection_id"] == selection_id
    )


def _gate_for(sidecar, ledger_record, *, evidence_version="pipe3-source-bound-v1"):
    payload = {
        "gate_version": "source-bound-boundary-gate-v1",
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
        "evidence_version": evidence_version,
        "source_index": 0,
    }
    if sidecar.label is None:
        raise ValueError("qualification sidecar must carry an eligible label")
    if ledger_record["record_hash"] != sidecar.ledger_record_hash:
        raise ValueError("gate ledger record mismatch")
    return AttributionGate(**payload, gate_digest=_digest(payload))


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=False)
    config = {
        "experiment_id": "n03_pipe3_source_bound_boundary_qualification_20260930",
        "qualification": "pipe3-source-bound-boundary-v1",
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in (
                "scripts/peerrolebench_pipe3_runner_v1.py",
                "scripts/peerrolebench_source_bound_feedback_adapter.py",
                "scripts/peerrolebench_pipe3_full_chain_qualification.py",
            )
        },
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    offer0 = make_offer(
        offer_id="offer-0", task_id=TASK_ID, task_index=0, role="producer",
        context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version="pipe3-source-bound-v1", available_index=0,
    )
    seal0 = boundary.choose_and_seal(
        offer=offer0, native_selection_id="selection-0", selector_id="peer-a", role="producer",
        base_scores=(100.0, -100.0), rng=np.random.default_rng(0), state_version="state-0",
        encoder_version="enc-0", feature_schema="pipe3", policy_version="contextual-v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=False,
    )
    episode = _append_episode(
        boundary, task_index=0, selection=seal0, producer_id="peer-b",
        artifact="b" * 64, suffix="source-bound", selected_at=0.0,
    )
    row = _make_feedback(
        episode, boundary, source="recipient_judgment", feedback_id="feedback-source-bound",
        arrived_at=5.0, label=1.0,
    )
    sidecar = replace(row.sidecar, sidecar_version=EVENT_TIME_SIDECAR_VERSION, arrival_index=1)
    judgment_record = row.ledger_record
    gate = _gate_for(sidecar, judgment_record)
    schedule = (ArrivalAssignment(
        sidecar.feedback_id, sidecar.protocol_event_type, sidecar.protocol_event_id,
        sidecar.source_event_id, 1,
    ),)
    source_offer = build_source_bound_offer(
        selection=seal0.decision_sidecar,
        selection_record=_selection_record(boundary, "selection-0"),
        feedback_inputs=((sidecar, judgment_record, gate, None),),
        ledger=boundary.ledger,
        arrival_schedule=schedule,
        offer_id="offer-1",
        context_key="PIPE3:1",
        target_task_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    seal1 = boundary.choose_and_seal_source_bound(
        source_offer=source_offer, native_selection_id="selection-1", selector_id="peer-a",
        role="producer", base_scores=(0.0, 0.0), rng=np.random.default_rng(1),
        state_version="state-1", encoder_version="enc-1", feature_schema="pipe3",
        policy_version="contextual-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=10.0,
        read_cut=1, decision_index=1, consume_evidence=True,
    )
    native_root, auxiliary_root = boundary.validate_selection_manifests()
    checks = {
        "same_boundary_ledger": len(boundary.ledger.events) == 9,
        "future_task_index": source_offer.offer.task_index == 1 and seal1.native_selection.task_index == 1,
        "source_feedback_consumed": boundary.policy.updates == 1 and seal1.attestation.consumed,
        "auxiliary_chain_continues": len(boundary.auxiliary_manifest_rows) == 4,
        "native_manifest_valid": bool(native_root) and native_root != "GENESIS",
        "auxiliary_manifest_valid": bool(auxiliary_root) and auxiliary_root != "GENESIS",
        "source_offer_sidecar_v4": sidecar.sidecar_version == EVENT_TIME_SIDECAR_VERSION,
    }
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if all(checks.values()) else "FAILED_OFFLINE",
        "checks": checks,
        "source_offer": source_offer.offer.payload(),
        "selection0": seal0.native_selection.selection_id,
        "selection1": seal1.native_selection.selection_id,
        "policy_updates": boundary.policy.updates,
        "native_manifest_root": native_root,
        "auxiliary_manifest_root": auxiliary_root,
        "ledger_event_count": len(boundary.ledger.events),
        "auxiliary_manifest_rows": len(boundary.auxiliary_manifest_rows),
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "same-boundary source-bound offer to future selection only; no scorer/API/GPU/effect claim",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "ledger.json").write_text(json.dumps(boundary.ledger.events, indent=2) + "\n", encoding="utf-8")
    (out_dir / "raw.json").write_text(json.dumps({"checks": checks, "offer": source_offer.offer.payload()}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir.resolve())
    print(json.dumps({key: result[key] for key in ("status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
