#!/usr/bin/env python3
"""Run the non-oracular PIPE3 material adapter preflight without LLM calls."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import platform
import sys


ROOT = Path(__file__).resolve().parents[1]
SEEDS = (0, 1, 2)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


QUAL = load("pipe3_qualification", ROOT / "scripts/peerrolebench_pipe3_task_qualification.py")
ADAPTER = load("pipe3_material_adapter", ROOT / "scripts/peerrolebench_pipe3_material_adapter.py")


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "--output":
        raise SystemExit("usage: peerrolebench_pipe3_material_preflight.py --output DIR")
    output = Path(sys.argv[2]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw = output / "raw.jsonl"

    def record(event_type: str, payload: object) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    config = {
        "experiment_id": output.name,
        "purpose": "N03 PIPE3 non-oracular material adapter preflight",
        "source_commit": QUAL.PIN,
        "seeds": list(SEEDS),
        "llm_calls": 0,
        "gpu_jobs": 0,
        "network": False,
        "candidate_code_executed": False,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    record("config", config)
    results = {}
    try:
        pin = QUAL.verify_pin()
        record("pin_check", pin)
        if not pin["passed"]:
            raise RuntimeError("TeamBench checkout is not the reviewed clean pin")
        for seed in SEEDS:
            materials = ADAPTER.build_materials(QUAL.load_pipe3(seed))
            manifest = materials["manifest"]
            results[str(seed)] = manifest
            record("material_check", {"seed": seed, "manifest": manifest})
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
        record("preflight_error", error)
        summary = {"config": config, "error": error, "material_preflight_passed": False,
                   "scientific_claim_allowed": False}
        (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
        return 1
    passed = bool(results) and all(item["scientific_task_text_qualified"] for item in results.values())
    summary = {
        "config": config,
        "platform": platform.platform(),
        "seeds": results,
        "material_preflight_passed": passed,
        "runtime_dispatch_verified": False,
        "scientific_claim_allowed": False,
        "remaining_gates": [
            "real payload dispatch and candidate-readable workspace boundary",
            "hidden scorer and operator ledger process/IPC isolation",
            "real event-ledger replay with lineage and propensity",
            "multi-event, missing-field, exception, and normal integration coverage",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    record("summary", summary)
    print(json.dumps({key: summary[key] for key in
                      ("material_preflight_passed", "runtime_dispatch_verified",
                       "scientific_claim_allowed")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
