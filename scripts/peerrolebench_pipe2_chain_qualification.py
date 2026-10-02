"""Zero-call qualification for the typed PIPE2 responsibility chain.

This runner composes only authored controls.  It verifies that a candidate
receipt can move through selection, delivery, independent producer scoring,
recipient judgment, action, terminal outcome, responsibility gating, evidence,
later assignment, and the next task start.  It does not call an LLM, execute
candidate code, invoke TeamBench, or submit a GPU job.
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

from peerrolebench_pipe2_chain_composition import CHAIN_VERSION, compose_pipe2_chain
from peerrolebench_pipe2_derived_material_adapter import RECIPE_PATH


ROOT = Path(__file__).resolve().parents[1]
RUNNER_VERSION = "pipe2-chain-qualification-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out_dir: Path, seeds: list[int]) -> dict:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    raw = out_dir / "raw.jsonl"
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    source_files = {
        "scripts/peerrolebench_pipe2_chain_composition.py": ROOT / "scripts/peerrolebench_pipe2_chain_composition.py",
        "scripts/peerrolebench_pipe2_chain_qualification.py": ROOT / "scripts/peerrolebench_pipe2_chain_qualification.py",
        "scripts/peerrolebench_pipe2_derived_material_adapter.py": ROOT / "scripts/peerrolebench_pipe2_derived_material_adapter.py",
        "scripts/peerrolebench_pipe2_responsibility_label.py": ROOT / "scripts/peerrolebench_pipe2_responsibility_label.py",
        "references/aamas/peer_role_protocol_20260925.py": ROOT / "references/aamas/peer_role_protocol_20260925.py",
    }
    config = {
        "runner_version": RUNNER_VERSION,
        "chain_version": CHAIN_VERSION,
        "task_id": "PIPE2_data_pipeline",
        "seeds": seeds,
        "variants": ["eligible", "repair", "mixed"],
        "material_root_digest": recipe["root_digest"],
        "material_adapter": "peerrolebench_pipe2_derived_material_adapter",
        "source_sha256": {name: _sha256(path) for name, path in source_files.items()},
        "fixture_mode": "authored-chain-controls-only",
        "argv": sys.argv,
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "benchmark_qualified": False,
        "scientific_claim_allowed": False,
        "started_at_utc": _now(),
    }
    (out_dir / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    expected = {
        "eligible": {
            "feedback_status": "ELIGIBLE",
            "evidence_recorded": True,
            "assignment_recorded": True,
            "next_selection_recorded": True,
            "event_count": 11,
            "event_types": [
                "peer_selection", "task_start", "producer_delivery", "producer_score",
                "recipient_judgment", "consumer_action", "terminal_outcome",
                "role_evidence_update", "later_assignment", "selection", "task_start",
            ],
        },
        "repair": {
            "feedback_status": "PENDING_ATTRIBUTION",
            "evidence_recorded": False,
            "assignment_recorded": False,
            "next_selection_recorded": False,
            "event_count": 7,
            "event_types": [
                "peer_selection", "task_start", "producer_delivery", "producer_score",
                "recipient_judgment", "consumer_action", "terminal_outcome",
            ],
        },
        "mixed": {
            "feedback_status": "UNKNOWN",
            "evidence_recorded": False,
            "assignment_recorded": False,
            "next_selection_recorded": False,
            "event_count": 7,
        },
    }
    rows: list[dict] = []
    for seed in seeds:
        for variant, contract in expected.items():
            result = compose_pipe2_chain(seed, variant=variant)
            snapshot = result["ledger_snapshot"]
            observed = {
                "feedback_status": result["gate"]["feedback_status"],
                "evidence_recorded": result["evidence_recorded"],
                "assignment_recorded": result["assignment_recorded"],
                "next_selection_recorded": result["next_selection_recorded"],
                "event_count": snapshot["event_count"],
                "event_types": result["ledger_event_types"],
            }
            passed = observed == contract and result["material_root_digest"] == recipe["root_digest"]
            row = {
                "seed": seed,
                "variant": variant,
                "expected": contract,
                "observed": observed,
                "material_root_digest": result["material_root_digest"],
                "ledger_event_digest": result["ledger_event_digest"],
                "passed": passed,
            }
            rows.append(row)
            with raw.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({
                    "timestamp_utc": _now(),
                    "event_type": "pipe2_chain_control",
                    "payload": row,
                }, ensure_ascii=False) + "\n")

    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if all(row["passed"] for row in rows) else "FAILED_OFFLINE",
        "control_count": len(rows),
        "passed_count": sum(row["passed"] for row in rows),
        "failed_count": sum(not row["passed"] for row in rows),
        "cases": rows,
        "interpretation": (
            "Authored typed-ledger composition only.  This validates ordering, "
            "digest binding, responsibility gating and future-assignment plumbing; "
            "it supplies no model judgment, benchmark label, efficacy or training evidence."
        ),
        "ended_at_utc": _now(),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "timestamp_utc": _now(), "event_type": "summary", "payload": summary
        }, ensure_ascii=False) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = parser.parse_args()
    result = run(args.output, args.seeds)
    print(json.dumps({
        key: result[key]
        for key in ("status", "control_count", "passed_count", "failed_count", "scientific_claim_allowed")
    }, indent=2))
