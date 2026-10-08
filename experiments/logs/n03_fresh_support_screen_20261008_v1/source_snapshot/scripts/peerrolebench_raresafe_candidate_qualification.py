"""Run zero-call invariants for the RARE-Anchor candidate state."""

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
from peerrolebench_raresafe_candidate import RareAnchorState, RoleFeedback  # noqa: E402


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _event(key: str, index: int, label: float | None, *, weight: float = 1.0,
           status: str = "eligible", supersedes: str | None = None,
           features: tuple[float, ...] = (1.0, 0.0, 0.0, 0.0)) -> RoleFeedback:
    return RoleFeedback(key=key, source_index=index, features=features, label=label,
                        weight=weight, status=status, supersedes=supersedes,
                        encoder_version="hash64-v1")


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "experiment_id": "n03_raresafe_candidate_invariants_20260928",
        "kind": "zero_llm_candidate_method_invariant_qualification",
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "state_source_sha256": _hash(ROOT / "scripts/peerrolebench_raresafe_candidate.py"),
        },
        "dimension": 4,
        "window_size": 2,
        "radius": 2.0,
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    state = RareAnchorState(dimension=4, window_size=2, radius=2.0)
    events = [
        _event("e0", 0, 1.0, features=(1.0, 0.0, 0.0, 0.0)),
        _event("e0", 0, 1.0, features=(1.0, 0.0, 0.0, 0.0)),  # duplicate
        _event("unknown", 1, None, status="unknown"),
        _event("e1", 1, 0.0, features=(0.0, 1.0, 0.0, 0.0)),
        _event("e0-correction", 2, 0.0, supersedes="e0", features=(1.0, 0.0, 0.0, 0.0)),
        _event("late", 1, 1.0, features=(0.0, 0.0, 1.0, 0.0)),
    ]
    outcomes = []
    for event in events:
        before = state.semantic_digest()
        disposition = state.ingest(event)
        after = state.semantic_digest()
        outcomes.append({"key": event.key, "disposition": disposition,
                         "digest_changed": before != after, "watermark": state.watermark,
                         "updates": state.updates, "unknowns": state.unknowns,
                         "duplicates": state.duplicates})

    snapshot = state.snapshot()
    restored = RareAnchorState.restore(snapshot)
    restore_equal = restored.digest() == state.digest()
    norm_bound = math_norm = max(
        (sum((state.theta[i] - state.anchor[i]) ** 2 for i in range(state.dimension)) ** 0.5,),
        default=0.0,
    ) <= state.radius + 1e-9
    results = {
        "outcomes": outcomes,
        "restore_equal": restore_equal,
        "anchor_radius_bound": norm_bound,
        "final_digest": state.digest(),
        "final_snapshot": snapshot,
        "scientific_claim_allowed": False,
    }
    # Event-time interleaving: only feedback sealed before the next decision
    # may affect that decision's probabilities.  A late event is queued and
    # cannot mutate the already captured probability vector.
    candidates = ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0))
    empty = RareAnchorState(dimension=4, window_size=2)
    p_without_feedback = empty.probabilities(candidates)
    early = RareAnchorState(dimension=4, window_size=2)
    early.ingest(_event("before-decision", 0, 1.0, features=candidates[0]))
    p_early = early.probabilities(candidates)
    late = RareAnchorState(dimension=4, window_size=2)
    p_late_captured = late.probabilities(candidates)
    late_disposition = late.ingest(_event("after-decision", 0, 1.0, features=candidates[0]))
    event_time = {
        "without_feedback": p_without_feedback,
        "early_feedback": p_early,
        "late_captured": p_late_captured,
        "late_after_state": late.probabilities(candidates),
        "late_disposition": late_disposition,
        "early_changes_next_decision": p_early != p_without_feedback,
        "late_does_not_rewrite_captured_decision": p_late_captured == p_without_feedback,
    }
    results["event_time_interleaving"] = event_time
    (out_dir / "raw.jsonl").write_text(json.dumps({"event_type": "candidate_invariant_trace", "payload": results}) + "\n")
    passed = (
        [item["disposition"] for item in outcomes]
        == ["UPDATE", "DUPLICATE", "UNKNOWN", "UPDATE", "UPDATE", "QUEUED_CORRECTION"]
        and all(item["digest_changed"] for item in outcomes if item["disposition"] == "UPDATE")
        and outcomes[1]["digest_changed"] is False
        and outcomes[2]["digest_changed"] is False
        and outcomes[5]["digest_changed"] is False
        and restore_equal and norm_bound
        and event_time["early_changes_next_decision"]
        and event_time["late_does_not_rewrite_captured_decision"]
    )
    summary = {
        "experiment_id": config["experiment_id"], "passed": passed,
        "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "results": results, "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"passed": result["passed"], "status": result["status"],
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
