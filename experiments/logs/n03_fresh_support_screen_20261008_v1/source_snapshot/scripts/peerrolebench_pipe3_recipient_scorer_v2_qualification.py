"""Zero-call qualification for the versioned PIPE3 recipient/adoption scorer.

The v1 real smoke exposed the same illegal ``probe`` action in the adoption
fixture.  This matrix verifies that the v2 worker uses the public action
domain and returns determinate scores for both scorer views on the two
same-root seed variants.  It is an engineering contract check, not a
benchmark result or a role-learning experiment.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_recipient_scorer_v2 import run_scorer  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    raw = out / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    config = {
        "qualification_version": "pipe3-recipient-scorer-qualification-v2",
        "scorer_version": "pipe3-recipient-objective-v2",
        "task_id": "PIPE3_stream_processing", "seeds": [0, 1],
        "modes": ["recipient", "adoption"], "llm_calls": 0, "gpu_jobs": 0,
        "native_grader_invoked": False, "scientific_claim_allowed": False,
        "root_status": "CONDITIONAL_NOT_FROZEN",
        "repeat_count_frozen_before_execution": True,
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    results = []
    for seed in [0, 1]:
        materials = build_materials(load_pipe3(seed))
        info = interfaces(materials)
        producer = materials["agent_payloads"]["producer"]["source_files"]
        recipient = materials["agent_payloads"]["recipient"]["source_files"]
        source_by_mode = {
            "recipient": {name: recipient[name] for name in ("processor.py", "models.py")},
            "adoption": {"producer.py": producer["producer.py"],
                         "processor.py": recipient["processor.py"],
                         "sink.py": recipient["sink.py"], "models.py": recipient["models.py"]},
        }
        for mode, sources in source_by_mode.items():
            evidence = out / f"seed_{seed}" / mode
            evidence.parent.mkdir(parents=True, exist_ok=True)
            result = run_scorer(sources, info, mode, config["task_id"], seed, evidence, log)
            item = {"seed": seed, "mode": mode, "status": result.get("status"),
                    "label": result.get("label"), "quality_score": result.get("quality_score"),
                    "coverage_complete": result.get("coverage_complete"),
                    "decision_complete": result.get("decision_complete"),
                    "reason": result.get("reason"), "checks": result.get("checks"),
                    "scorer_version": result.get("scorer_version"),
                    "response_digest": result.get("response_digest")}
            results.append(item)
            log("case_result", item)

    passed = all(item["status"] in {"PASS", "FAIL"}
                 and item["label"] in {0, 1}
                 and item["coverage_complete"] is True
                 and item["decision_complete"] is True
                 and item["scorer_version"] == "pipe3-recipient-objective-v2"
                 and not (item["reason"] and "Invalid action: probe" in item["reason"])
                 for item in results)
    summary = {**config, "passed": passed, "results": results,
               "scorer_is_qualified": False,
               "remaining_gates": [
                   "author independent correct and near-miss recipient artifacts",
                   "validate responsibility-aware judgment and sink adoption semantics",
                   "complete PIPE3 runner chain and independent roots",
                   "compare same-information baselines before any efficacy claim",
               ]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": passed, "scorer_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
