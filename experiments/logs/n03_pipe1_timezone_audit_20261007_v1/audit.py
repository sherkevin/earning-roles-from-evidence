#!/usr/bin/env python3
"""Static timezone portability check over saved PIPE1 material; no generator."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CAPTURE = ROOT / "experiments/logs/n03_pipe1_native_material_audit_20261007_v1"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not (OUT / "config.json").is_file():
        raise RuntimeError("frozen config must exist before date conversion")
    raw = OUT / "raw.jsonl"
    rows = []
    for seed, timestamp_field, output_field, scale in (
        (1, "encounter_dt", "visit_date", 1),
        (2, "posted_timestamp", "txn_date", 1000),
    ):
        case = CAPTURE / f"seed_{seed}"
        executor = read(case / "executor_view.json")
        parent = read(case / "parent_only.json")
        records = json.loads(executor["workspace_files"]["source_sample.json"])
        expected = parent["expected"]["records"]
        if len(records) != 10 or len(expected) != 10:
            raise ValueError("captured record count changed")
        for index, (source, target) in enumerate(zip(records, expected)):
            timestamp = int(source[timestamp_field]) / scale
            utc_value = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d")
            shanghai_value = datetime.fromtimestamp(timestamp, ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
            parent_value = target[output_field]
            row = {
                "seed": seed, "domain": parent["expected"]["domain"], "record_index": index,
                "source_field": timestamp_field, "source_timestamp": source[timestamp_field],
                "timestamp_scale": scale, "target_field": output_field,
                "utc_date": utc_value, "asia_shanghai_date": shanghai_value,
                "parent_expected_date": parent_value,
                "utc_equals_shanghai": utc_value == shanghai_value,
                "parent_matches_utc": parent_value == utc_value,
                "parent_matches_asia_shanghai": parent_value == shanghai_value,
            }
            rows.append(row)
            with raw.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    result = {"status": "STATIC_DATE_COMPARISON_COMPLETE", "record_count": len(rows),
              "generator_calls": 0, "candidate_executions": 0, "grader_calls": 0, "llm_api_calls": 0,
              "runtime_timezone_observation": {"TZ": os.environ.get("TZ"), "time_tzname": list(time.tzname)},
              "capture_timezone_inference": "UNKNOWN: current environment does not prove the timezone used during earlier capture",
              "by_seed": {}}
    for seed in (1, 2):
        subset = [row for row in rows if row["seed"] == seed]
        result["by_seed"][str(seed)] = {
            "domain": subset[0]["domain"], "records": len(subset),
            "utc_vs_shanghai_different": sum(not row["utc_equals_shanghai"] for row in subset),
            "parent_matches_utc": sum(row["parent_matches_utc"] for row in subset),
            "parent_matches_asia_shanghai": sum(row["parent_matches_asia_shanghai"] for row in subset),
            "parent_matches_neither": sum(not row["parent_matches_utc"] and not row["parent_matches_asia_shanghai"] for row in subset),
        }
    result["portable_label_note"] = (
        "Native generator calls datetime.fromtimestamp without tz; if the saved raw timestamps "
        "cross calendar dates between UTC and Asia/Shanghai, expected dates depend on process TZ. "
        "A future cross-machine comparison should pin TZ before generation/scoring or explicitly "
        "report its timezone; native rules are unchanged here."
    )
    write(OUT / "summary.json", result)


if __name__ == "__main__":
    main()
