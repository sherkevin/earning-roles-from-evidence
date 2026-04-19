from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def collect_metrics(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metrics_path in sorted(root.glob("*/metrics.json")):
        method = metrics_path.parent.name
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        rows.append({"method": method, **metrics})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect per-method metrics from a run directory.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    rows = collect_metrics(run_dir)
    if not rows:
        raise SystemExit(f"No metrics.json found under {run_dir}")

    fieldnames = list(rows[0].keys())
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    if args.out_md is not None:
        cols = [
            "method",
            "answer_f1",
            "answer_em",
            "premature_accept_rate",
            "mean_handoff_count",
            "api_total_tokens_per_sample",
            "cost_normalized_f1_api",
            "sample_count",
        ]
        lines = ["# Run Metrics", "", "| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for row in rows:
            vals = [str(row.get(col, "")) for col in cols]
            lines.append("| " + " | ".join(vals) + " |")
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    print(args.out_csv)
    if args.out_md is not None:
        print(args.out_md)


if __name__ == "__main__":
    main()
