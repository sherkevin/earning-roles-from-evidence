"""Read-only replay of the real PIPE2 runtime qualification receipts.

The runtime qualification measured producer correctness and recipient adoption,
but it did not record a recipient judgment, consumer action, or an independent
terminal outcome.  This adapter maps only fields that are actually present into
the responsibility gate and fails closed on the missing fields.  It never
fills those fields from the runtime score and never executes candidate code.
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
from typing import Any, Iterable

from peerrolebench_pipe2_derived_material_adapter import (
    RECIPE_PATH,
    build_derived_materials,
    load_derived_pipe2,
)
from peerrolebench_pipe2_responsibility_label import evaluate_pipe2_feedback


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = ROOT / "experiments/logs/n03_pipe2_derived_root_runtime_qualification_20261003_v3/summary.json"
RUNNER_VERSION = "pipe2-runtime-replay-v1"
MISSING_FIELDS = (
    "recipient_judgment",
    "consumer_action",
    "terminal_outcome",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _producer_score(payload: dict[str, Any]) -> dict[str, Any]:
    status = payload.get("status")
    complete = status in {"PASS", "FAIL"} and payload.get("label") in {0, 1}
    return {
        "status": status if status in {"PASS", "FAIL", "UNKNOWN"} else "UNKNOWN",
        "label": payload.get("label") if complete else None,
        "coverage_complete": complete,
        "decision_complete": complete,
        "artifact_sha256": payload.get("artifact_sha256"),
    }


def _iter_cases(summary: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for case in summary.get("cases", []):
        seed = int(case["seed"])
        for producer_name, producer in case.get("producer", {}).items():
            for recipient_name, recipient in case.get("recipient", {}).get(producer_name, {}).items():
                adoption = recipient.get("artifact_adoption", {})
                yield {
                    "seed": seed,
                    "producer_control": producer_name,
                    "recipient_control": recipient_name,
                    "fixture_status": case.get("fixture_status"),
                    "producer": producer,
                    "recipient": recipient,
                    "adoption": adoption,
                }


def replay_case(summary: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    if summary.get("material_root_digest") != recipe.get("root_digest"):
        raise ValueError("runtime summary root digest does not match current recipe")
    seed = int(row["seed"])
    generated = load_derived_pipe2(seed)
    if generated.metadata.get("derived_root_digest") != recipe["root_digest"]:
        raise ValueError("runtime replay material root does not match current recipe")
    materials = build_derived_materials(seed)
    producer = row["producer"]
    producer_score = _producer_score(producer)
    artifact_sha256 = producer.get("artifact_sha256")
    if not isinstance(artifact_sha256, str) or len(artifact_sha256) != 64:
        raise ValueError("runtime producer receipt has no artifact digest")
    # These mappings are deliberately empty: the source receipt does not have
    # the fields, and a score/adoption result cannot be promoted to a judgment,
    # action, or terminal outcome.
    judgment: dict[str, Any] = {}
    action: dict[str, Any] = {}
    outcome: dict[str, Any] = {}
    gate = evaluate_pipe2_feedback(
        materials,
        artifact_sha256=artifact_sha256,
        producer_score=producer_score,
        judgment=judgment,
        action=action,
        outcome=outcome,
    )
    return {
        "seed": seed,
        "producer_control": row["producer_control"],
        "recipient_control": row["recipient_control"],
        "fixture_status": row["fixture_status"],
        "producer_status": producer.get("status"),
        "producer_label_observed": producer.get("label"),
        "producer_artifact_sha256": artifact_sha256,
        "recipient_adoption_status_observed": row["adoption"].get("status"),
        "recipient_adoption_artifact_sha256": row["recipient"].get("artifact_sha256"),
        "missing_fields": list(MISSING_FIELDS),
        "gate": gate,
        "label_emitted": gate.get("label"),
        "policy_update_allowed": gate.get("policy_update_allowed"),
        "scientific_claim_allowed": False,
    }


def run(summary_path: Path, out_dir: Path) -> dict[str, Any]:
    summary_path = summary_path.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    config = {
        "runner_version": RUNNER_VERSION,
        "source_summary": str(summary_path.relative_to(ROOT)),
        "source_summary_sha256": _sha256(summary_path),
        "material_root_digest": recipe["root_digest"],
        "material_adapter": "peerrolebench_pipe2_derived_material_adapter",
        "fixture_mode": "read-only-real-runtime-receipt-replay",
        "argv": sys.argv,
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "benchmark_qualified": False,
        "scientific_claim_allowed": False,
        "started_at_utc": _now(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    rows: list[dict[str, Any]] = []
    raw_path = out_dir / "raw.jsonl"
    for source_row in _iter_cases(summary):
        result = replay_case(summary, source_row)
        result["passed"] = (
            result["label_emitted"] is None
            and result["policy_update_allowed"] is False
            and result["gate"]["feedback_status"] in {"UNKNOWN", "PENDING_ATTRIBUTION"}
            and result["missing_fields"] == list(MISSING_FIELDS)
        )
        rows.append(result)
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "timestamp_utc": _now(),
                "event_type": "pipe2_runtime_replay",
                "payload": result,
            }, ensure_ascii=False) + "\n")
    output = {
        **config,
        "status": "REPLAY_QUALIFIED_UNKNOWN" if all(row["passed"] for row in rows) else "REPLAY_FAILED",
        "case_count": len(rows),
        "passed_count": sum(row["passed"] for row in rows),
        "label_count": sum(row["label_emitted"] is not None for row in rows),
        "gate_status_counts": {
            status: sum(row["gate"]["feedback_status"] == status for row in rows)
            for status in ("ELIGIBLE", "PENDING_ATTRIBUTION", "UNKNOWN")
        },
        "cases": rows,
        "interpretation": (
            "Real runtime receipts prove producer/adoption dimensions only. Missing recipient "
            "judgment, consumer action and independent terminal outcome remain explicit; no "
            "producer label or policy update is emitted. This is evidence of an identification "
            "gap, not a benchmark, method or efficacy result."
        ),
        "ended_at_utc": _now(),
    }
    (out_dir / "summary.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    with raw_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": _now(), "event_type": "summary", "payload": output}, ensure_ascii=False) + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.summary, args.output)
    print(json.dumps({key: result[key] for key in ("status", "case_count", "passed_count", "label_count", "gate_status_counts")}, indent=2))
