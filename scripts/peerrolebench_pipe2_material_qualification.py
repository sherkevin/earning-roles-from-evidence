"""Zero-call qualification for the PIPE2 second-root material boundary."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from peerrolebench_pipe2_material_adapter import (
    attach_extracted_rows, build_materials, load_pipe2, validate_extracted_rows,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER_VERSION = "pipe2-material-qualification-v1"


def run(out_dir: Path, *, seeds: tuple[int, ...] = (0, 1, 2)) -> dict:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    config = {
        "runner_version": RUNNER_VERSION, "task_id": "PIPE2_data_pipeline", "seeds": list(seeds),
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows = []
    for seed in seeds:
        generated = load_pipe2(seed)
        materials = build_materials(generated)
        manifest = materials["manifest"]
        columns = generated.expected["columns"]
        # A schema-valid handoff is enough for this qualification. It is not a
        # producer correctness label and intentionally does not use expected output.
        artifact = validate_extracted_rows([
            {column: f"fixture-{seed}-{index}-{column}" for column in columns}
            for index in range(1)
        ], columns=columns)
        recipient = attach_extracted_rows(materials["agent_payloads"]["recipient"], artifact)
        row = {
            "seed": seed, "task_id": generated.task_id,
            "scientific_task_text_qualified": manifest["scientific_task_text_qualified"],
            "producer_paths": manifest["producer_writable_paths"],
            "recipient_paths": manifest["recipient_writable_paths"],
            "required_delivery_paths_before": materials["agent_payloads"]["recipient"]["required_delivery_paths"],
            "required_delivery_paths_after": recipient["required_delivery_paths"],
            "delivery_schema": artifact["schema"], "delivery_row_count": artifact["row_count"],
            "correctness_label": artifact["correctness_label"],
            "passed": bool(manifest["scientific_task_text_qualified"] and
                           recipient["required_delivery_paths"] == [] and
                           recipient["source_files"]),
        }
        rows.append(row)
    (out_dir / "raw.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    summary = {
        **config, "status": "QUALIFIED_OFFLINE" if all(row["passed"] for row in rows) else "FAILED_OFFLINE",
        "passed": all(row["passed"] for row in rows), "cases": rows,
        "interpretation": "PIPE2 material/ownership/delivery shape only; no scorer, adoption, API, GPU, or efficacy claim",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs")}, indent=2))
