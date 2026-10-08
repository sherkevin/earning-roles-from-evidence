"""Zero-call five-case qualification for the responsibility label gate."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    materials = build_materials(load_pipe3(0))
    info = interfaces(materials)
    digest = "a" * 64
    q = {"status": "PASS", "coverage_complete": True, "decision_complete": True}
    y = {"status": "PASS", "coverage_complete": True, "decision_complete": True}
    cases = [
        ("producer_defect", ["producer.py"], "producer", "ELIGIBLE"),
        ("recipient_only", ["processor.py"], "producer", "PENDING_ATTRIBUTION"),
        ("sink_only", [], "sink", "PENDING_ATTRIBUTION"),
        ("mixed_edit", ["producer.py", "processor.py"], "producer", "UNKNOWN"),
        ("no_attribution", [], "producer", "PENDING_ATTRIBUTION"),
    ]
    results = []
    for name, changed_paths, target_role, expected in cases:
        action = {"changed_paths": changed_paths}
        judgment = {"target_role": target_role, "observed_artifact_sha256": digest}
        result = producer_feedback_eligibility(materials, q, judgment, action, y)
        observed = {"case": name, "expected": expected, **result}
        results.append(observed)
    summary = {
        "qualification_version": "pipe3-responsibility-label-qualification-v1",
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "event_class": info["event_class"], "llm_calls": 0, "gpu_jobs": 0,
        "native_grader_invoked": False, "scientific_claim_allowed": False,
        "passed": all(item["producer_feedback_status"] == item["expected"] for item in results),
        "results": results,
        "scorer_is_qualified": False,
        "remaining_gates": [
            "replace synthetic sidecars with operator-validated producer/recipient/sink artifacts",
            "add structured judgment target_paths and evidence references to the real runner",
            "register a mixed-edit counterfactual before any eligible update",
        ],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "config.json").write_text(json.dumps({key: summary[key] for key in
                                                   ("qualification_version", "task_id", "seed",
                                                    "event_class", "llm_calls", "gpu_jobs",
                                                    "native_grader_invoked", "scientific_claim_allowed")},
                                                  indent=2, ensure_ascii=False) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    with (out / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps({"timestamp_utc": summary["created_at_utc"],
                                     "event_type": "responsibility_case", "payload": result},
                                    ensure_ascii=False) + "\n")
        handle.write(json.dumps({"timestamp_utc": summary["created_at_utc"],
                                 "event_type": "summary", "payload": summary},
                                ensure_ascii=False) + "\n")
    print(json.dumps({"passed": summary["passed"], "scorer_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
