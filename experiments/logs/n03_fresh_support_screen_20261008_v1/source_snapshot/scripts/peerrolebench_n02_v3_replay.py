"""Reconcile the historical N02 real-API ledger with the strict attribution gate.

N02 contains real recipient judgments, consumer actions and terminal outcomes,
but its card explicitly says producer correctness was not independently
measured.  This replay therefore supplies an UNKNOWN producer score and checks
that the current gate rejects the historical role-evidence path instead of
silently treating the old ledger entry as a valid label.
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
from typing import Any

from peerrolebench_pipe2_responsibility_label import evaluate_pipe2_feedback


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926"
RUNNER_VERSION = "n02-v3-strict-gate-replay-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _by_type(events: list[dict[str, Any]], event_type: str, index: int) -> dict[str, Any]:
    if event_type == "producer_delivery":
        rows = [row["payload"] for row in events
                if row.get("event_type") == event_type
                and int(row.get("payload", {}).get("task_index", -1)) == index]
    else:
        delivery_id = f"delivery-{index}"
        rows = [row["payload"] for row in events
                if row.get("event_type") == event_type
                and row.get("payload", {}).get("delivery_id") == delivery_id]
    if len(rows) != 1:
        raise ValueError(f"expected one {event_type} for episode {index}, found {len(rows)}")
    return rows[0]


def replay_episode(root: Path, index: int) -> dict[str, Any]:
    materials = json.loads((root / f"materials_{index}.json").read_text(encoding="utf-8"))
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    episode_summary = next(row for row in summary["episodes"] if int(row["index"]) == index)
    events = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
    delivery = _by_type(events, "producer_delivery", index)
    judgment = _by_type(events, "recipient_judgment", index)
    action_event = _by_type(events, "consumer_action", index)
    outcome_event = _by_type(events, "terminal_outcome", index)
    evidence = [row for row in events
                if row.get("event_type") == "role_evidence_update"
                and row.get("payload", {}).get("outcome_id") == outcome_event["outcome_id"]]
    assignment = [row for row in events
                  if row.get("event_type") == "later_assignment"
                  and int(row.get("payload", {}).get("task_index", -1)) > index]

    artifact = delivery["artifact_sha256"]
    producer_score = {
        "status": "UNKNOWN",
        "label": None,
        "coverage_complete": False,
        "decision_complete": False,
        "artifact_sha256": artifact,
    }
    judgment_input = {
        "decision": judgment["decision"],
        "target_role": "producer",
        "observed_artifact_sha256": judgment["observed_artifact_sha256"],
        "coverage_complete": True,
        "decision_complete": True,
        "producer_defect_registered": False,
    }
    action_input = {
        "consumer_action": action_event["action"],
        "changed_paths": episode_summary.get("changed_paths", []),
        "delivery_sha256": action_event["input_artifact_sha256"],
        "used_artifact": action_event["used_artifact"],
    }
    outcome_input = {
        "status": "PASS" if outcome_event["success"] else "FAIL",
        "artifact_sha256": artifact,
        "coverage_complete": True,
        "decision_complete": True,
    }
    gate = evaluate_pipe2_feedback(
        materials,
        artifact_sha256=artifact,
        producer_score=producer_score,
        judgment=judgment_input,
        action=action_input,
        outcome=outcome_input,
    )
    return {
        "index": index,
        "producer": delivery["producer_id"],
        "recipient": delivery["recipient_id"],
        "artifact_sha256": artifact,
        "historical_judgment": judgment["decision"],
        "historical_action": action_event["action"],
        "historical_terminal_success": outcome_event["success"],
        "historical_role_evidence_present": bool(evidence),
        "historical_assignment_present": bool(assignment),
        "producer_score_observed": False,
        "gate": gate,
        "label_emitted": gate["label"],
        "policy_update_allowed": gate["policy_update_allowed"],
        "historical_evidence_rejected_by_current_gate": bool(evidence) and not gate["feedback_eligible"],
        "scientific_claim_allowed": False,
    }


def run(root: Path, out_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    config = {
        "runner_version": RUNNER_VERSION,
        "source_root": str(root.relative_to(ROOT)),
        "source_summary_sha256": _sha256(root / "summary.json"),
        "source_ledger_sha256": _sha256(root / "ledger.json"),
        "task_id": "DIST1_queue_race",
        "episode_indices": [0, 1],
        "fixture_mode": "read-only-real-api-ledger-replay",
        "argv": sys.argv,
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "started_at_utc": _now(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    raw_path = out_dir / "raw.jsonl"
    rows = []
    for index in config["episode_indices"]:
        row = replay_episode(root, index)
        row["passed"] = (
            row["gate"]["feedback_status"] in {"UNKNOWN", "PENDING_ATTRIBUTION"}
            and row["label_emitted"] is None
            and row["policy_update_allowed"] is False
            and row["historical_evidence_rejected_by_current_gate"] is True
        )
        rows.append(row)
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": _now(), "event_type": "n02_strict_gate_replay", "payload": row}, ensure_ascii=False) + "\n")
    output = {
        **config,
        "status": "REPLAY_QUALIFIED_UNKNOWN" if all(row["passed"] for row in rows) else "REPLAY_FAILED",
        "episode_count": len(rows),
        "passed_count": sum(row["passed"] for row in rows),
        "label_count": sum(row["label_emitted"] is not None for row in rows),
        "gate_status_counts": {
            status: sum(row["gate"]["feedback_status"] == status for row in rows)
            for status in ("ELIGIBLE", "PENDING_ATTRIBUTION", "UNKNOWN")
        },
        "historical_role_evidence_count": sum(row["historical_role_evidence_present"] for row in rows),
        "historical_evidence_rejected_count": sum(row["historical_evidence_rejected_by_current_gate"] for row in rows),
        "episodes": rows,
        "interpretation": (
            "The real N02 ledger contains judgment/action/terminal events and historical role evidence, "
            "but no independent producer score or registered producer defect. The current strict gate "
            "therefore emits no label and rejects the historical evidence path for attribution."
        ),
        "ended_at_utc": _now(),
    }
    (out_dir / "summary.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    with raw_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": _now(), "event_type": "summary", "payload": output}, ensure_ascii=False) + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root, args.output)
    print(json.dumps({key: result[key] for key in ("status", "episode_count", "passed_count", "label_count", "gate_status_counts", "historical_role_evidence_count", "historical_evidence_rejected_count")}, indent=2))
