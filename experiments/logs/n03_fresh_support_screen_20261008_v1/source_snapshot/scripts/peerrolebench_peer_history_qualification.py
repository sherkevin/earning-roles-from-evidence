"""Run a zero-call qualification receipt for PeerHistoryV1."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess

from peerrolebench_peer_history import AssignmentSealV1, HistoryCostV1, HistoryEntryV1, PeerHistoryV1


ROOT = Path(__file__).resolve().parents[1]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def entry(status: str, arrival: int) -> HistoryEntryV1:
    return HistoryEntryV1(
        f"entry-{arrival}", "peer-a", "peer-a", sha("role"), sha("state"), sha("delivery"),
        f"judgment-{arrival}", None if status == "UNKNOWN" else 1.0,
        f"outcome-{arrival}", None if status == "UNKNOWN" else 1.0,
        sha("metric"), HistoryCostV1(input_tokens=2, output_tokens=3, wall_ms=4.0),
        arrival, "assignment-0", status,
    )


def qualify(out_dir: Path) -> dict:
    out_dir = out_dir.resolve(); out_dir.mkdir(parents=False, exist_ok=False)
    config = {
        "qualification_version": "peer-history-v1-qualification",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": platform.python_version(), "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    checks = []
    left, right = PeerHistoryV1.empty("peer-a"), PeerHistoryV1.empty("peer-b")
    checks.append({"case": "empty_histories_same_content_digest", "passed": left.content_digest() == right.content_digest()})
    history = PeerHistoryV1.empty("peer-a")
    try:
        history.append(entry("PASS", 4)); premature = False
    except ValueError:
        premature = True
    checks.append({"case": "append_before_seal_rejected", "passed": premature})
    history.seal_assignment(AssignmentSealV1("assignment-0", "peer-a", sha("role"), sha("state"), 3, sha("registry")))
    history.append(entry("PASS", 4)); history.append(entry("UNKNOWN", 5))
    projection = history.selector_projection()
    checks.append({"case": "unknown_counted_without_positive_support", "passed": projection["scopes"][0]["n_unknown"] == 1 and abs(projection["scopes"][0]["smoothed_rate"] - (2.0 / 3.0)) < 1e-12})
    restored = PeerHistoryV1.replay(history.snapshot())
    checks.append({"case": "snapshot_replay_digest", "passed": restored.state_digest() == history.state_digest()})
    public_text = json.dumps(projection, ensure_ascii=False).lower()
    forbidden = ("artifact_sha256", "task_id", "gold", "private_text", "raw_text")
    checks.append({"case": "public_projection_hides_private_fields", "passed": not any(key in public_text for key in forbidden)})
    summary = {**config, "status": "QUALIFIED_OFFLINE" if all(row["passed"] for row in checks) else "FAILED_OFFLINE",
               "passed": all(row["passed"] for row in checks), "case_count": len(checks), "checks": checks,
               "ended_at_utc": datetime.now(timezone.utc).isoformat(),
               "interpretation": "append-only history seam only; no API/GPU/benchmark/efficacy claim"}
    (out_dir / "raw.jsonl").write_text("".join(json.dumps({"event_type": "check", "payload": row}) + "\n" for row in checks))
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = qualify(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "passed", "case_count", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
