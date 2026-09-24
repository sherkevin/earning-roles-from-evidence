#!/usr/bin/env python3
"""CPU-only native integration check for the frozen v3 guard implementation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

from appworld import AppWorld
import aamas_peer_judgment_smoke_v3 as smoke


def main() -> None:
    here = Path(__file__).resolve().parent
    cfg = json.loads((here / "config.json").read_text())
    script = ROOT / "scripts/aamas_peer_judgment_smoke_v3.py"
    if hashlib.sha256(script.read_bytes()).hexdigest() != cfg["runner_sha256"]:
        raise RuntimeError("v3 runner changed after CPU fixture config was frozen")
    raw = here / "raw.jsonl"
    deferred: list[tuple[str, dict]] = []
    result = {"task_id": cfg["task_id"], "experiment_name": cfg["experiment_name"],
              "native_guard_enabled": True, "llm_api_calls": 0,
              "docs_ok": False, "task_data_get_ok": False, "audit_events": 0,
              "persisted_api_events": 0, "error": None}
    try:
        with AppWorld(task_id=cfg["task_id"], experiment_name=cfg["experiment_name"],
                      load_ground_truth=False, random_seed=cfg["seed"],
                      raise_on_extra_parameters=True) as world:
            if world.task.ground_truth is not None or not world.raise_on_unsafe_execution:
                raise RuntimeError("Unsafe native fixture setup")
            audit = smoke.api_guard(world, "producer", smoke.Secrets(), raw, deferred)
            docs = world.execute("print(apis.api_docs.show_app_descriptions())")
            smoke.flush_guard_events(raw, deferred)
            datum = world.execute("print(apis.phone.get_current_date_and_time())")
            smoke.flush_guard_events(raw, deferred)
            result["docs_ok"] = ("Execution failed" not in docs and "api_docs" in docs)
            result["task_data_get_ok"] = ("Execution failed" not in datum and
                                          any(row.get("public_read_observation")
                                              for row in audit))
            result["audit_events"] = len(audit)
            result["ground_truth_unloaded"] = world.task.ground_truth is None
            world.save()
        result["persisted_api_events"] = sum(
            json.loads(line)["event"] == "public_api_call" for line in raw.read_text().splitlines())
        if not (result["docs_ok"] and result["task_data_get_ok"] and
                result["audit_events"] == 2 and result["persisted_api_events"] == 2):
            raise AssertionError("Native public API/deferred-audit assertions failed")
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc),
                           "traceback": traceback.format_exc()}
    (here / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))
    if result["error"] is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
