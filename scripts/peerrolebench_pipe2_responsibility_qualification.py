"""Zero-call qualification of the PIPE2 responsibility-safe feedback gate.

The cases are authored controls, not model judgments or benchmark labels.  They
exercise only the parent-side distinction between accepted direct use,
recipient-owned repair, mixed edits, rejection, incomplete coverage and an
out-of-contract write.  No candidate code, LLM, native grader or GPU runs.
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

from peerrolebench_pipe2_derived_material_adapter import RECIPE_PATH, build_derived_materials
from peerrolebench_pipe2_responsibility_label import evaluate_pipe2_feedback


ROOT = Path(__file__).resolve().parents[1]
RUNNER_VERSION = "pipe2-responsibility-qualification-v1"
ARTIFACT = "a" * 64


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _case(materials: dict, *, judgment: str, action: str, changed: tuple[str, ...],
          complete: bool = True, score_status: str = "PASS",
          score_label: int | None = 1,
          producer_defect_registered: bool | None = None) -> dict:
    judgment_payload = {
        "decision": judgment, "target_role": "producer",
        "observed_artifact_sha256": ARTIFACT,
        "coverage_complete": complete, "decision_complete": complete,
    }
    if producer_defect_registered is not None:
        judgment_payload["producer_defect_registered"] = producer_defect_registered
    return evaluate_pipe2_feedback(
        materials,
        artifact_sha256=ARTIFACT,
        producer_score={
            "status": score_status, "label": score_label,
            "coverage_complete": complete, "decision_complete": complete,
            "artifact_sha256": ARTIFACT,
        },
        judgment=judgment_payload,
        action={
            "consumer_action": action, "changed_paths": list(changed),
            "delivery_sha256": ARTIFACT,
            "used_artifact": action != "independent_redo",
        },
        outcome={
            "status": "PASS", "artifact_sha256": ARTIFACT,
            "coverage_complete": complete, "decision_complete": complete,
        },
    )


def run(out_dir: Path, seeds: list[int]) -> dict:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    raw = out_dir / "raw.jsonl"
    recipe = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    config = {
        "runner_version": RUNNER_VERSION,
        "task_id": "PIPE2_data_pipeline",
        "seeds": seeds,
        "material_root_digest": recipe["root_digest"],
        "material_adapter": "peerrolebench_pipe2_derived_material_adapter",
        "fixture_mode": "authored-responsibility-controls-only",
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")

    cases = []
    controls = (
        ("accepted_direct_use_without_defect", {"judgment": "accept", "action": "use", "changed": ()}, "PENDING_ATTRIBUTION"),
        ("registered_defect_direct_use", {"judgment": "accept", "action": "use", "changed": (),
                                            "score_status": "FAIL", "score_label": 0,
                                            "producer_defect_registered": True}, "ELIGIBLE"),
        ("recipient_repair", {"judgment": "accept_with_rework", "action": "repair",
                               "changed": ("pipeline/transform.py",)}, "PENDING_ATTRIBUTION"),
        ("mixed_edit", {"judgment": "accept_with_rework", "action": "repair",
                         "changed": ("pipeline/extract.py", "pipeline/transform.py")}, "UNKNOWN"),
        ("rejection_redo", {"judgment": "reject_redo", "action": "independent_redo",
                             "changed": ("pipeline/transform.py",)}, "PENDING_ATTRIBUTION"),
        ("incomplete", {"judgment": "accept", "action": "use", "changed": (),
                         "complete": False, "score_status": "UNKNOWN", "score_label": None}, "UNKNOWN"),
    )
    for seed in seeds:
        materials = build_derived_materials(seed)
        for control_name, kwargs, expected_status in controls:
            result = _case(materials, **kwargs)
            row = {
                "seed": seed,
                "control": control_name,
                "expected_status": expected_status,
                "observed_status": result["feedback_status"],
                "observed_label": result["label"],
                "policy_update_allowed": result["policy_update_allowed"],
                "result_digest": _digest(result),
                "passed": result["feedback_status"] == expected_status
                         and result["policy_update_allowed"] is False,
            }
            cases.append(row)
            with raw.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                         "event_type": "responsibility_control", "payload": row},
                                        ensure_ascii=False) + "\n")
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if all(row["passed"] for row in cases) else "FAILED_OFFLINE",
        "control_count": len(cases),
        "passed_count": sum(row["passed"] for row in cases),
        "cases": cases,
        "benchmark_qualified": False,
        "scientific_claim_allowed": False,
        "interpretation": "Authored parent-side responsibility controls only; no model judgment, candidate execution, API, GPU, benchmark label, or efficacy claim.",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event_type": "summary", "payload": summary},
                                ensure_ascii=False) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = parser.parse_args()
    result = run(args.output, args.seeds)
    print(json.dumps({key: result[key] for key in ("status", "control_count", "passed_count",
                                                    "scientific_claim_allowed")}, indent=2))
