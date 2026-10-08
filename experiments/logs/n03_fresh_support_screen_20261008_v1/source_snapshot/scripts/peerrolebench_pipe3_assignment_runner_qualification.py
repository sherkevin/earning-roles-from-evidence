"""Run the zero-API PIPE3 assignment runner boundary qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_metateam_profile_qualification import profile, digest
from peerrolebench_pipe3_assignment_runner import Pipe3AssignmentRunner
from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer
from peer_role_protocol_20260925 import PeerRoleLedger, PeerSelection


def fixture_offer() -> MetaTeamAssignmentOffer:
    p = profile(profile_id="pipe3-profile-0", source_decision_index=0, source_arrival_index=1, available_index=1)
    return MetaTeamAssignmentOffer.build(
        offer_id="pipe3-offer-0", task_id="PIPE3_stream_processing", decision_index=3,
        read_cut=2, candidate_keys=("agent-a@v1", "agent-b@v1"), profiles=(p,)
    )


def selection(menu=("agent-a@v1", "agent-b@v1"), task_index=3, selected_at=3.0):
    return SimpleNamespace(candidates=tuple(SimpleNamespace(key=k) for k in menu), task_index=task_index, selected_at=selected_at)


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Persist attempt metadata before constructing or exercising the runner so
    # a failed qualification still has an auditable configuration record.
    config = {
        "qualification": "pipe3-assignment-runner-boundary-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).with_name("peerrolebench_pipe3_assignment_runner.py").read_bytes()).hexdigest(),
        "python": platform.python_version(), "platform": platform.platform(),
        "fixture_mode": "hand-authored-offer-profile",
        "source": "offline fixture; not a real PIPE3 episode",
        "real_api_calls": 0, "gpu_jobs": 0,
        "policy_read_trace_mode": "recorded_public_input_digest",
        "isolated_policy_trace": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    runner = Pipe3AssignmentRunner(fixture_offer())
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=False)
    ledger.record_selection(PeerSelection(
        selection_id="native-selection-3", task_id="PIPE3_stream_processing", task_index=3,
        selector_id="agent-recipient", role="producer",
        candidate_ids=("agent-a", "agent-b"), chosen_peer_id="agent-a", propensity=0.5,
    ))
    runner.emit_offer()
    att = runner.consume_profiles(("pipe3-profile-0",))
    runner.seal_selection(selection(), att)
    runner.start_task(ledger)
    checks = [{"name": "happy_path", "status": "PASS"},
              {"name": "ledger_task_start", "status": "PASS"
               if ledger.events[-1]["event_type"] == "task_start"
               and ledger.events[-1]["payload"]["task_index"] == fixture_offer().decision_index
               else "FAIL"}]

    def rejected(name, fn):
        try:
            fn()
        except ValueError as exc:
            checks.append({"name": name, "status": "PASS", "error": str(exc)})
        else:
            checks.append({"name": name, "status": "FAIL"})

    rejected("no_attestation", lambda: Pipe3AssignmentRunner(fixture_offer()).seal_selection(selection()))
    def before_consumption():
        r = Pipe3AssignmentRunner(fixture_offer()); r.emit_offer(); r.seal_selection(selection(), None)
    rejected("selection_before_consumption", before_consumption)
    rejected("wrong_menu", lambda: (lambda r: (r.emit_offer(), r.consume_profiles(("pipe3-profile-0",)), r.seal_selection(selection(("agent-b@v1", "agent-a@v1")), r.attestation)))(Pipe3AssignmentRunner(fixture_offer())))
    rejected("duplicate_consumption", lambda: (lambda r: (r.emit_offer(), r.consume_profiles(("pipe3-profile-0",)), r.consume_profiles(("pipe3-profile-0",))))(Pipe3AssignmentRunner(fixture_offer())))
    # A pre-watermark offer is rejected by the underlying frozen contract.
    rejected("pre_watermark", lambda: MetaTeamAssignmentOffer.build(
        offer_id="early", task_id="PIPE3_stream_processing", decision_index=3, read_cut=0,
        candidate_keys=("agent-a@v1",), profiles=(profile(profile_id="early-p", available_index=1),)))
    # Mutation is represented by replacing a profile in the offer after emit.
    def mutate():
        r = Pipe3AssignmentRunner(fixture_offer()); r.emit_offer()
        object.__setattr__(r.offer, "profiles", (profile(profile_id="pipe3-profile-0", profile_revision=2, supersedes_profile_id="old", source_arrival_index=1, available_index=1),))
        r.consume_profiles(("pipe3-profile-0",))
    rejected("profile_mutation", mutate)

    (out_dir / "trace.jsonl").write_text("\n".join(json.dumps(x, sort_keys=True) for x in runner.trace) + "\n")
    result = {
        "qualification": "pipe3-assignment-runner-boundary-v1",
        "status": "QUALIFIED_OFFLINE" if all(c["status"] == "PASS" for c in checks) else "FAILED_OFFLINE",
        "real_api_calls": 0, "gpu_jobs": 0,
        "fixture_mode": config["fixture_mode"], "source": config["source"],
        "policy_read_trace_mode": runner.policy_read_trace_mode,
        "isolated_policy_trace": runner.isolated_policy_trace,
        "trace_events": [e["event"] for e in runner.trace], "checks": checks,
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out-dir", type=Path, required=True)
    result = run(ap.parse_args().out_dir); print(json.dumps(result, indent=2)); raise SystemExit(result["status"] != "QUALIFIED_OFFLINE")
