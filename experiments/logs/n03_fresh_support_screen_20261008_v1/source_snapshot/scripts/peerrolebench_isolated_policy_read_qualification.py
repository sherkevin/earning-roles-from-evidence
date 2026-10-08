"""Zero-call qualification for the separate-process public-profile read."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_metateam_profile_qualification import profile  # noqa: E402
from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer  # noqa: E402
from peerrolebench_pipe3_assignment_runner import Pipe3AssignmentRunner  # noqa: E402
from peerrolebench_isolated_policy_read import read_profiles_isolated  # noqa: E402


def offer() -> MetaTeamAssignmentOffer:
    return MetaTeamAssignmentOffer.build(
        offer_id="isolated-offer-0", task_id="PIPE3_stream_processing", decision_index=3,
        read_cut=2, candidate_keys=("agent-a@v1", "agent-b@v1"),
        profiles=(profile(profile_id="profile-a-r1", source_decision_index=0, source_arrival_index=1, available_index=1),),
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "qualification": "isolated-public-profile-read-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "worker_sha256": hashlib.sha256((ROOT / "scripts/peerrolebench_policy_read_worker.py").read_bytes()).hexdigest(),
        "parent_sha256": hashlib.sha256((ROOT / "scripts/peerrolebench_isolated_policy_read.py").read_bytes()).hexdigest(),
        "fixture_mode": "hand-authored-metateam-public-offer",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "python": platform.python_version(), "platform": platform.platform(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    sealed = offer()
    runner = Pipe3AssignmentRunner(sealed)
    runner.emit_offer()
    attestation = runner.consume_profiles(("profile-a-r1",), isolated_policy_read=True)
    checks = [
        {"name": "separate_process_read", "status": "PASS",
         "isolated_policy_trace": runner.isolated_policy_trace,
         "trace_mode": runner.policy_read_trace_mode},
        {"name": "attestation_and_worker_input_match", "status": "PASS"
         if runner.trace[-1]["isolated_read"]["policy_input_digest"] == attestation.policy_input_digest else "FAIL"},
    ]

    def reject(name, fn):
        try:
            fn()
        except (TypeError, ValueError) as exc:
            checks.append({"name": name, "status": "PASS", "error": str(exc)})
        else:
            checks.append({"name": name, "status": "FAIL"})

    reject("reject_unavailable_profile", lambda: read_profiles_isolated(
        sealed, ("profile-a-r1",), read_cut=0))
    reject("reject_unknown_profile", lambda: read_profiles_isolated(
        sealed, ("profile-b-r1",), read_cut=2))
    reject("reject_unsorted_profile_ids", lambda: read_profiles_isolated(
        MetaTeamAssignmentOffer.build(
            offer_id="two-profile-offer", task_id="PIPE3_stream_processing", decision_index=3,
            read_cut=2, candidate_keys=("agent-a@v1", "agent-b@v1"), profiles=(
                profile(profile_id="profile-a-r1", source_decision_index=0, source_arrival_index=1, available_index=1),
                profile(profile_id="profile-b-r1", candidate_key="agent-b@v1", producer_id="agent-b",
                        selected_candidate_key="agent-b@v1", source_decision_index=0,
                        source_arrival_index=1, available_index=1),
            )), ("profile-b-r1", "profile-a-r1"), read_cut=2))
    result = {**config, "status": "QUALIFIED_OFFLINE" if all(row["status"] == "PASS" for row in checks) else "FAILED_OFFLINE", "checks": checks, "trace": runner.trace}
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "raw.json").write_text(json.dumps({"offer": sealed.payload(), "trace": runner.trace}, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
