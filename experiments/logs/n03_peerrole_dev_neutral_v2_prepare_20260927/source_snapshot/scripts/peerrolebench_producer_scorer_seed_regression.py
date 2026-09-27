"""Zero-LLM producer scorer source-shape regression for DIST1 seeds 1 and 2."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from peerrolebench_producer_scorer import run_producer_scorer  # noqa: E402
from peerrolebench_task_contract import export_task_materials, load_generated_task  # noqa: E402


ALLOWLIST = [
    "__future__", "collections", "dataclasses", "functools", "heapq", "itertools",
    "math", "mqueue", "queue", "threading", "time", "typing", "uuid",
]


def interfaces(source):
    import ast
    queue_tree = ast.parse(source["mqueue/queue.py"])
    priority_tree = ast.parse(source["mqueue/priority.py"])
    queue = [n.name for n in queue_tree.body if isinstance(n, ast.ClassDef)
             and n.name not in {"QueueFull", "QueueEmpty"}]
    priority = [n.name for n in priority_tree.body if isinstance(n, ast.ClassDef)
                and "priority" in n.name.lower()]
    if len(queue) != 1 or len(priority) != 1:
        raise ValueError("seed regression interface inventory is ambiguous")
    return {"queue": queue[0], "priority": priority[0]}


def main():
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

    config = {"qualification_version": "dist1-producer-scorer-seed-regression-v1",
              "task_id": "DIST1_queue_race", "seeds": [1, 2], "llm_calls": 0,
              "gpu_jobs": 0, "native_grader_invoked": False,
              "scientific_claim_allowed": False,
              "expected": "original generated source must not be PASS; FAIL or resource UNKNOWN are retained"}
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    results = []
    for seed in config["seeds"]:
        generated = load_generated_task("DIST1_queue_race", seed)
        materials = export_task_materials(generated)
        source = {path: text for path, text in materials["agent_payloads"]["producer"]["source_files"].items()
                  if path.startswith("mqueue/")}
        case_dir = out / f"seed_{seed}"
        case_dir.mkdir()
        result = run_producer_scorer(source, interfaces(source), "DIST1_queue_race", seed,
                                     case_dir / "scorer", log)
        row = {"seed": seed, "interfaces": interfaces(source),
               "status": result.get("status"), "label": result.get("label"),
               "quality_score": result.get("quality_score"),
               "response_digest": result.get("response_digest"),
               "transport": result.get("transport")}
        results.append(row)
        log("seed_result", row)
    passed = all(row["status"] in {"FAIL", "UNKNOWN"} for row in results)
    summary = {"qualification_version": config["qualification_version"], "passed": passed,
               "results": results, "scorer_is_qualified": False,
               "scientific_claim_allowed": False,
               "remaining_gates": ["second structural root", "matched baseline matrix",
                                   "non-adversarial worker boundary limitation"]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": passed, "scorer_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
