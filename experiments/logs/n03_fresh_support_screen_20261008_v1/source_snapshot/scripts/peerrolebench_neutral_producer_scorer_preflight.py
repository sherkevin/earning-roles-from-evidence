"""Run the unqualified producer scorer on the versioned neutral DIST1 material."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_manifest_provenance import load_materials  # noqa: E402
from peerrolebench_producer_scorer import run_producer_scorer  # noqa: E402
from peerrolebench_real_closed_loop import producer_interface_names  # noqa: E402


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--material-adapter", default="dist1-neutral-v1",
                        choices=("dist1-neutral-v1", "dist1-neutral-v2"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw = output / "raw.jsonl"

    def log(event_type: str, payload: object) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    config = {
        "experiment_id": output.name,
        "purpose": "neutral DIST1 material producer scorer transport preflight",
        "task_id": "DIST1_queue_race", "seed": 0,
        "material_adapter": args.material_adapter,
        "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
        "controller_update_allowed": False,
        "scorer_is_qualified": False, "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    try:
        materials, _ = load_materials(config["task_id"], config["seed"],
                                      config["material_adapter"])
        producer = materials["agent_payloads"]["producer"]
        source = {path: producer["source_files"][path]
                  for path in (*producer["writable_paths"], "mqueue/__init__.py", "mqueue/config.py")
                  if path in producer["source_files"]}
        card = {"source_import_allowlist": [
            "__future__", "collections", "dataclasses", "functools", "heapq", "itertools",
            "math", "mqueue", "queue", "threading", "time", "typing", "uuid",
        ]}
        interfaces = producer_interface_names(source, card)
        result = run_producer_scorer(source, interfaces, config["task_id"], config["seed"],
                                     output / "scorer", log)
        summary = {"config": config, "interfaces": interfaces, "result": result,
                   "scorer_is_qualified": False, "controller_update_allowed": False,
                   "scientific_claim_allowed": False,
                   "interpretation": "diagnostic transport/adapter evidence only"}
    except Exception as exc:
        summary = {"config": config, "error": {"type": type(exc).__name__, "message": str(exc)},
                   "scorer_is_qualified": False, "controller_update_allowed": False,
                   "scientific_claim_allowed": False}
        log("preflight_error", summary["error"])
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"status": summary.get("result", {}).get("status", "UNKNOWN"),
                      "scorer_is_qualified": False,
                      "controller_update_allowed": False}, indent=2))
    return 0 if "result" in summary else 1


if __name__ == "__main__":
    raise SystemExit(main())
