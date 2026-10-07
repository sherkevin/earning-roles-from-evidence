"""Zero-call qualification for the versioned independent-Y integration seam."""

from __future__ import annotations

from datetime import datetime, timezone
import argparse
from copy import deepcopy
import json
from pathlib import Path

from peerrolebench_independent_y_contract_v2 import (
    canonical_digest, validate_independent_y,
)


ROOT = Path(__file__).resolve().parents[1]
VERSION = "n03-independent-y-contract-v2-qualification-v1"


def _sha(tag: str) -> str:
    return canonical_digest({"tag": tag})


def _context() -> dict:
    delivery = _sha("delivery")
    return {
        "assignment_id": "assignment-arm", "selection_id": "selection-arm-1",
        "delivery_id": "arm-delivery-1", "candidate_key": "peer-b@v1",
        "assignment_event_index": 10, "selection_event_index": 11,
        "task_start_event_index": 12, "delivery_event_index": 13,
        "action_event_index": 16, "task_start_binding_digest": _sha("task-start-prefix"),
        "delivery_artifact_sha256": delivery, "action_input_sha256": delivery,
        "target_snapshot_sha256": _sha("target-snapshot"),
        "artifact_sha256": _sha("target-snapshot"),
        "worker_input_sha256": _sha("worker-input"), "response_digest": _sha("response"),
        "holdout_digest": _sha("holdout"), "read_cut": 20,
    }


def _receipt(ctx: dict) -> dict:
    return {
        "schema_version": "pipe3-independent-y-contract-v2",
        "source": "independent_terminal_holdout", "scorer_version": "pipe3-terminal-holdout-v1",
        "episode_role": "target", "derived_from": [], "policy_visible": False,
        "feedback_id": "feedback-y-1", "assignment_id": ctx["assignment_id"],
        "selection_id": ctx["selection_id"], "delivery_id": ctx["delivery_id"],
        "task_start_binding_digest": ctx["task_start_binding_digest"],
        "delivery_artifact_sha256": ctx["delivery_artifact_sha256"],
        "action_input_sha256": ctx["action_input_sha256"],
        "target_snapshot_sha256": ctx["target_snapshot_sha256"],
        "artifact_sha256": ctx["artifact_sha256"],
        "worker_input_sha256": ctx["worker_input_sha256"],
        "response_digest": ctx["response_digest"], "holdout_digest": ctx["holdout_digest"],
        "status": "PASS", "label": 1, "quality_score": 1.0,
        "coverage_complete": True, "arrival_index": 18,
    }


def run(out_dir: Path) -> dict:
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    config = {
        "version": VERSION, "contract_version": "pipe3-independent-y-contract-v2",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "cases": ["positive", "source_relabel", "D_relabel", "wrong_target_snapshot",
                   "invalid_event_order", "late_feedback", "duplicate", "incomplete"],
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    ctx = _context()
    cases = {}
    cases["positive"] = validate_independent_y(_receipt(ctx), ctx)
    source = _receipt(ctx); source["episode_role"] = "source"
    cases["source_relabel"] = validate_independent_y(source, ctx)
    derived = _receipt(ctx); derived["derived_from"] = ["D", "recipient"]
    cases["D_relabel"] = validate_independent_y(derived, ctx)
    wrong = _receipt(ctx); wrong["target_snapshot_sha256"] = _sha("other-target")
    cases["wrong_target_snapshot"] = validate_independent_y(wrong, ctx)
    bad_order = deepcopy(ctx); bad_order["selection_event_index"] = 14
    cases["invalid_event_order"] = validate_independent_y(_receipt(bad_order), bad_order)
    late = _receipt(ctx); late["arrival_index"] = 21
    cases["late_feedback"] = validate_independent_y(late, ctx)
    cases["duplicate"] = validate_independent_y(_receipt(ctx), ctx, seen_feedback_ids=["feedback-y-1"])
    incomplete = _receipt(ctx); incomplete["coverage_complete"] = False
    cases["incomplete"] = validate_independent_y(incomplete, ctx)
    positive_ok = cases["positive"].get("valid") is True
    rejects_ok = all(
        cases[name].get("disposition") == "UNKNOWN"
        for name in config["cases"] if name != "positive"
    )
    summary = {
        **config, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "positive_valid": positive_ok, "negative_cases_fail_closed": rejects_ok,
        "passed": bool(positive_ok and rejects_ok), "status": "QUALIFIED_OFFLINE" if positive_ok and rejects_ok else "UNKNOWN",
        "cases": cases, "policy_state_mutated": False,
        "interpretation": "provenance and event-order seam only; no worker execution, API, GPU, policy update, or efficacy claim",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
