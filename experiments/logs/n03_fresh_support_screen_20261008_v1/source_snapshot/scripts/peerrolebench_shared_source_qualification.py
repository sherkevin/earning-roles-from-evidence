"""Zero-call qualification for shared-source arm projections."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_shared_source import (  # noqa: E402
    ARM_NAMES, freeze_source_receipt, project_source_to_arms,
    validate_arm_projections,
)


def _source(gate_status: str = "ELIGIBLE", inclusion: str = "ITT_AND_ELIGIBLE") -> dict:
    return {
        "source_event_id": "pipe3-source-0",
        "task_id": "PIPE3_stream_processing",
        "root": "PIPE3_stream_processing",
        "seed": 0,
        "delivery_digest": "a" * 64,
        "judgment": {"decision": "accept", "target_role": "producer"},
        "action": {"consumer_action": "use", "changed_paths": []},
        "producer_score": {"status": "FAIL", "label": 0},
        "outcome": {"status": "PASS", "quality_score": 1.0},
        "gate": {"status": gate_status, "structural_owner_role": "producer"},
        "cost": {"api_attempts": 2, "input_tokens": 10, "output_tokens": 5},
        "episode_status": "SOURCE_COMPLETE" if gate_status == "ELIGIBLE" else "STOPPED_PRE_TARGET",
        "gate_status": gate_status,
        "estimand_inclusion": inclusion if gate_status == "ELIGIBLE" else "ITT_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    config = {
        "qualification_version": "shared-source-projection-qualification-v1",
        "projection_version": "shared-source-projection-v1",
        "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "python": platform.python_version(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    results = []

    valid = project_source_to_arms(_source(), ARM_NAMES)
    results.append({"case": "S1_valid_shared_source", "result": validate_arm_projections(valid), "passed": True})

    for name, mutate in [
        ("S2_delivery_digest_mutation", lambda row: row.__setitem__("delivery_digest", "b" * 64)),
        ("S3_gate_mutation", lambda row: row["gate"].__setitem__("status", "PENDING_ATTRIBUTION")),
        ("S4_action_mutation", lambda row: row["action"].__setitem__("changed_paths", ["processor.py"])),
        ("S5_cost_mutation", lambda row: row["cost"].__setitem__("output_tokens", 99)),
    ]:
        rows = project_source_to_arms(_source(), ARM_NAMES)
        mutate(rows[1])
        try:
            validate_arm_projections(rows)
        except ValueError as exc:
            results.append({"case": name, "status": "REJECTED", "error": str(exc), "passed": True})
        else:
            results.append({"case": name, "status": "ACCEPTED", "passed": False})

    pending = project_source_to_arms(_source("PENDING_ATTRIBUTION", "ITT_ONLY"), ARM_NAMES)
    pending_result = validate_arm_projections(pending)
    results.append({"case": "S6_pending_attribution_is_itt_only", "result": pending_result,
                    "passed": pending_result["gate_status"] == "PENDING_ATTRIBUTION"
                    and pending_result["estimand_inclusion"] == "ITT_ONLY"})
    summary = {**config, "status": "QUALIFIED_OFFLINE" if all(r["passed"] for r in results) else "FAILED_OFFLINE",
               "passed": all(r["passed"] for r in results), "case_count": len(results), "results": results}
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    with (output / "raw.jsonl").open("w") as handle:
        for row in results:
            handle.write(json.dumps({"event_type": "shared_source_case", "payload": row}, ensure_ascii=False) + "\n")
    print(json.dumps({"passed": summary["passed"], "case_count": len(results), "llm_calls": 0,
                      "gpu_jobs": 0, "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
