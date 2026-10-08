"""Compose isolated profile read with selection -> native task start."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import PeerRoleLedger, PeerSelection  # noqa: E402
from peerrolebench_metateam_profile_qualification import profile  # noqa: E402
from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer  # noqa: E402
from peerrolebench_pipe3_assignment_runner import Pipe3AssignmentRunner  # noqa: E402


def selection():
    return SimpleNamespace(
        candidates=(SimpleNamespace(key="agent-a@v1"), SimpleNamespace(key="agent-b@v1")),
        task_index=3, selected_at=3.0,
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "qualification": "isolated-assignment-to-task-start-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256((ROOT / "scripts/peerrolebench_pipe3_assignment_runner.py").read_bytes()).hexdigest(),
        "fixture_mode": "hand-authored-offer-isolated-read-native-ledger",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "python": platform.python_version(), "platform": platform.platform(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    offer = MetaTeamAssignmentOffer.build(
        offer_id="isolated-task-start-offer", task_id="PIPE3_stream_processing", decision_index=3,
        read_cut=2, candidate_keys=("agent-a@v1", "agent-b@v1"),
        profiles=(profile(profile_id="profile-a-r1", source_decision_index=0, source_arrival_index=1, available_index=1),),
    )
    runner = Pipe3AssignmentRunner(offer)
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=False)
    ledger.record_selection(PeerSelection(
        "isolated-native-selection", "PIPE3_stream_processing", 3, "agent-recipient", "producer",
        ("agent-a", "agent-b"), "agent-a", 0.5,
    ))
    runner.emit_offer()
    attestation = runner.consume_profiles(("profile-a-r1",), isolated_policy_read=True)
    runner.seal_selection(selection(), attestation)
    runner.start_task(ledger)
    trace = runner.trace
    checks = [
        {"name": "isolated_profile_read", "status": "PASS" if runner.isolated_policy_trace else "FAIL"},
        {"name": "selection_after_read", "status": "PASS" if runner.state == "task_started" and trace[2]["event"] == "selection_sealed" else "FAIL"},
        {"name": "native_task_start_same_decision", "status": "PASS" if ledger.events[-1]["event_type"] == "task_start" and ledger.events[-1]["payload"]["task_index"] == offer.decision_index else "FAIL"},
        {"name": "trace_keeps_worker_digest", "status": "PASS" if trace[1]["isolated_read"]["policy_input_digest"] == attestation.policy_input_digest else "FAIL"},
    ]
    result = {**config, "status": "QUALIFIED_OFFLINE" if all(c["status"] == "PASS" for c in checks) else "FAILED_OFFLINE", "trace": trace, "ledger": ledger.events, "checks": checks}
    (out_dir / "trace.json").write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "raw.json").write_text(json.dumps({"offer": offer.payload(), "attestation": attestation.payload(), "ledger": ledger.events}, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
