"""Zero-call qualification for the canonical PIPE3 history append boundary.

The injected scorer is a deliberately named fixture.  This script checks that
history append is downstream of a committed delayed credit and that enabling
the append seam does not change the canonical selection/ledger trace.  It is
an engineering qualification, never a benchmark or efficacy result.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from peerrolebench_pipe3_two_stage_composition import run  # noqa: E402


VERSION = "peer-history-integration-qualification-v2"


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _fixture_scorer(kind, sources, info, out, log, seed):
    """Complete deterministic CPU fixture; no candidate/API execution."""
    out.mkdir(parents=True, exist_ok=True)
    return {
        "status": "FAIL" if kind == "producer" else "PASS",
        "label": 0 if kind == "producer" else 1,
        "quality_score": 0.0 if kind == "producer" else 0.8,
        "coverage_complete": True,
        "decision_complete": True,
        "scorer_version": "peer-history-integration-fixture-v1",
        "response_digest": "a" * 64,
    }


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_qualification(out: Path) -> dict[str, Any]:
    out = out.resolve()
    out.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    config = {
        "qualification_version": VERSION,
        "git_commit": commit,
        "python": sys.version,
        "platform": platform.platform(),
        "seed": {"source": 0, "target": 1},
        "modes": ["off", "append"],
        "scorer": "peer-history-integration-fixture-v1",
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "components": [
            "scripts/peerrolebench_pipe3_two_stage_composition.py",
            "scripts/peerrolebench_peer_history_adapter.py",
            "scripts/peerrolebench_peer_history_binding.py",
            "scripts/peerrolebench_peer_history.py",
        ],
    }
    config["component_sha256"] = {
        name: _sha_file(ROOT / name) for name in config["components"]
    }
    config["git_worktree_status_before"] = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True,
    )
    _json(out / "config.json", config)
    results: dict[str, dict[str, Any]] = {}
    for mode in ("off", "append"):
        results[mode] = run(
            out / mode, source_seed=0, target_seed=1,
            scorer=_fixture_scorer, history_mode=mode,
        )
    off = results["off"]
    append = results["append"]
    matched: list[dict[str, Any]] = []
    for left, right in zip(off["cases"], append["cases"]):
        if left.get("control") != right.get("control"):
            raise AssertionError("mode cases are not aligned")
        left_ledger = left.get("ledger", [])
        right_ledger = right.get("ledger", [])
        matched.append({
            "control": left["control"],
            "ledger_equal": left_ledger == right_ledger,
            "ledger_digest_off": _digest(left_ledger),
            "ledger_digest_append": _digest(right_ledger),
            "selection_trace_equal": [
                row for row in left_ledger if row["event_type"] == "peer_selection"
            ] == [
                row for row in right_ledger if row["event_type"] == "peer_selection"
            ],
            "off_history": left.get("history", {}).get("status", "DISABLED"),
            "append_history": (
                "APPENDED" if "entry" in right.get("history", {})
                else right.get("history", {}).get("status", "UNKNOWN")
            ),
            "policy_updates_equal": left.get("policy_updates") == right.get("policy_updates"),
        })
    producer = next(row for row in matched if row["control"] == "producer_owned")
    controls = [row for row in matched if row["control"] != "producer_owned"]
    passed = bool(
        off.get("status") == "QUALIFIED_OFFLINE"
        and append.get("status") == "QUALIFIED_OFFLINE"
        and producer["ledger_equal"]
        and producer["selection_trace_equal"]
        and producer["append_history"] == "APPENDED"
        and all(row["ledger_equal"] and row["append_history"] == "NOT_RUN_UNKNOWN" for row in controls)
    )
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed,
        "matched_modes": matched,
        "mode_status": {mode: results[mode]["status"] for mode in results},
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "interpretation": (
            "The append mode adds one canonical history row only after delayed credit; "
            "selection/ledger traces remain matched. This does not establish peer suitability, "
            "role specialization, baseline parity, or online efficacy."
        ),
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _json(out / "summary.json", summary)
    (out / "raw.jsonl").write_text(
        json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "event_type": "matched_mode_summary", "payload": summary},
                   ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_qualification(args.output)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
