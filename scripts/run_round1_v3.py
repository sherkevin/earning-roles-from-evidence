"""
scripts/run_round1_v3.py
========================
Run new Engineer-2 baselines (fixed_self_calibrated, central_orchestrator_with_reflection)
that were added in Session 1.  Reuses the existing sample set from a prior run to ensure
apples-to-apples comparison with fixed_peer_calibrated.

Usage
-----
# Run fixed_self_calibrated against the same 200 samples used in run_20260411_102202:
    python scripts/run_round1_v3.py \
        --config configs/round1_hotpotqa.yaml \
        --samples-jsonl artifacts/round1/run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl \
        --methods fixed_self_calibrated \
        --artifacts-root artifacts/round1

# Add more methods in one shot:
    python scripts/run_round1_v3.py \
        --config configs/round1_hotpotqa.yaml \
        --samples-jsonl artifacts/round1/run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl \
        --methods fixed_self_calibrated,central_orchestrator_with_reflection \
        --artifacts-root artifacts/round1

# Resume into an existing run dir (avoids creating a new timestamp dir):
    python scripts/run_round1_v3.py \
        --config configs/round1_hotpotqa.yaml \
        --samples-jsonl artifacts/round1/run_20260411_102202/fixed_peer_calibrated/raw_inputs.jsonl \
        --methods fixed_self_calibrated \
        --resume-run-dir artifacts/round1/run_20260411_XXXXXX \
        --artifacts-root artifacts/round1

# Merge metrics only (7405 / fullval table), no LLM calls:
    python scripts/run_round1_v3.py \
        --merge-summary-only \
        --resume-run-dir artifacts/round1/run_YYYYMMDD_HHMMSS \
        --methods fixed_peer_calibrated,fixed_static_roles,fixed_self_claim \
        --artifacts-root artifacts/round1 \
        --summary-csv-name round1_v3_main_table_fullval.csv \
        --no-canonical-self-override
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Path bootstrap (mirrors run_round0_smoke setup)
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
sys.path.insert(0, str(_REPO_ROOT / "workspace"))

import idea04_paths  # noqa: E402  (from scripts/)
from idea04_core.runner import RoundRunner  # noqa: E402  (from workspace/)
from idea04_core.methods import METHOD_NAMES  # noqa: E402

# ---------------------------------------------------------------------------
# Allowed methods for this script (Engineer-2 additions)
# ---------------------------------------------------------------------------
V3_METHODS = [
    "fixed_self_calibrated",
    "central_orchestrator_with_reflection",
    # also allow re-running these for same-run comparison
    "fixed_peer_calibrated",
    "fixed_static_roles",
    "fixed_self_claim",
    "central_orchestrator",
    "single_agent",
    "fixed_random_forward",
]


def load_samples_from_jsonl(path: Path, sample_size: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if sample_size is not None:
        rows = rows[:sample_size]
    return rows


V3_MAIN_TABLE_FIELDS = [
    "method",
    "answer_em",
    "answer_f1",
    "mean_handoff_count",
    "dead_end_rate",
    "premature_accept_rate",
    "forward_after_correction_rate",
    "token_cost_per_sample",
    "api_prompt_tokens_per_sample",
    "api_completion_tokens_per_sample",
    "api_total_tokens_per_sample",
    "cost_normalized_f1",
    "cost_normalized_f1_api",
    "first_accept_success_rate",
    "sample_count",
]

V3_MAIN_TABLE_METHOD_ORDER = [
    "single_agent",
    "central_orchestrator",
    "central_orchestrator_with_reflection",
    "fixed_static_roles",
    "fixed_self_claim",
    "fixed_random_forward",
    "fixed_peer_calibrated",
    "fixed_self_calibrated",
]

# Peer–self 同批 jsonl 的权威 self 跑次；合并主表时覆盖 run_* 内旧副本（如 102202 目录）。
_CANONICAL_SELF_CALIBRATED_METRICS = (
    _REPO_ROOT / "artifacts/round1/run_20260411_132631/fixed_self_calibrated/metrics.json"
)


def write_summary(
    output_root: Path,
    run_root: Path,
    run_id: str,
    methods: list[str],
    *,
    summary_csv_basename: str = "round1_v3_main_table.csv",
    apply_canonical_self: bool = True,
) -> None:
    """Merge metrics for `methods` from `run_root/<name>/metrics.json` into `output_root / summary_csv_basename`."""
    summary_csv = output_root / summary_csv_basename
    by_method: dict[str, dict[str, Any]] = {}
    if summary_csv.is_file():
        with summary_csv.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                name = row.get("method")
                if name:
                    by_method[name] = row

    for method_name in methods:
        mp = run_root / method_name / "metrics.json"
        if not mp.is_file():
            continue
        m = json.loads(mp.read_text(encoding="utf-8"))
        row: dict[str, Any] = {"method": method_name, **{k: m[k] for k in V3_MAIN_TABLE_FIELDS[1:] if k in m}}
        by_method[method_name] = row

    if apply_canonical_self and _CANONICAL_SELF_CALIBRATED_METRICS.is_file():
        m = json.loads(_CANONICAL_SELF_CALIBRATED_METRICS.read_text(encoding="utf-8"))
        by_method["fixed_self_calibrated"] = {
            "method": "fixed_self_calibrated",
            **{k: m[k] for k in V3_MAIN_TABLE_FIELDS[1:] if k in m},
        }
    elif apply_canonical_self and "fixed_self_calibrated" in by_method:
        print(
            f"[run_round1_v3] WARN: canonical self_calibrated missing {_CANONICAL_SELF_CALIBRATED_METRICS}; "
            "table row may reflect run_dir only."
        )

    ordered = [n for n in V3_MAIN_TABLE_METHOD_ORDER if n in by_method]

    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=V3_MAIN_TABLE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for name in ordered:
            src = by_method[name]
            out = {k: src.get(k, "") for k in V3_MAIN_TABLE_FIELDS}
            out["method"] = name
            writer.writerow(out)
    print(f"[run_round1_v3] Summary merged → {summary_csv}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run Round-1 v3 Engineer-2 baselines for idea04.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", default="configs/round1_hotpotqa.yaml")
    parser.add_argument(
        "--topology",
        choices=["chain", "star"],
        default=None,
        help="Override merged config topology (use with star yaml or to force star on chain config).",
    )
    parser.add_argument(
        "--samples-jsonl", required=False, default=None,
        help="Path to raw_inputs.jsonl (required unless --merge-summary-only).",
    )
    parser.add_argument(
        "--sample-size", type=int, default=None,
        help="Cap number of samples (default: use all rows from jsonl).",
    )
    parser.add_argument(
        "--artifacts-root", default="artifacts/round1",
        help="Parent directory for this round's run dirs.",
    )
    parser.add_argument(
        "--methods", default="fixed_self_calibrated",
        help=(
            "Comma-separated methods to run.  "
            f"Allowed: {', '.join(V3_METHODS)}"
        ),
    )
    parser.add_argument(
        "--resume-run-dir", default=None,
        help="Existing run_* dir; new methods are added as sub-directories.  "
             "If omitted, a new timestamped dir is created.",
    )
    parser.add_argument(
        "--no-write-summary",
        action="store_true",
        help="Do not merge into artifacts/round1/round1_v3_main_table.csv (e.g. star or ablation runs).",
    )
    parser.add_argument(
        "--summary-csv-name",
        default="round1_v3_main_table.csv",
        help="Output CSV basename under --artifacts-root (e.g. round1_v3_main_table_fullval.csv).",
    )
    parser.add_argument(
        "--no-canonical-self-override",
        action="store_true",
        help="Do not inject run_20260411_132631 fixed_self_calibrated into merged table (use for fullval-only CSV).",
    )
    parser.add_argument(
        "--merge-summary-only",
        action="store_true",
        help="Skip model runs; merge metrics from --resume-run-dir into summary CSV.",
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help=(
            "Number of parallel worker threads per method (default 1 = sequential). "
            "Set to 8–16 for large runs; note fixed_peer_calibrated competence updates "
            "are approximate under parallelism (ordering not guaranteed)."
        ),
    )
    args = parser.parse_args(argv)

    output_root = _REPO_ROOT / args.artifacts_root

    if args.merge_summary_only:
        if not args.resume_run_dir:
            sys.exit("[run_round1_v3] ERROR: --merge-summary-only requires --resume-run-dir")
        run_root = Path(args.resume_run_dir)
        if not run_root.is_absolute():
            run_root = _REPO_ROOT / run_root
        if not run_root.is_dir():
            sys.exit(f"[run_round1_v3] ERROR: --resume-run-dir is not a directory: {run_root}")
        methods_to_run = [m.strip() for m in args.methods.split(",") if m.strip()]
        for m in methods_to_run:
            if m not in V3_METHODS:
                sys.exit(f"[run_round1_v3] Unknown method {m!r}.  Allowed: {V3_METHODS}")
        write_summary(
            output_root,
            run_root,
            run_root.name,
            methods_to_run,
            summary_csv_basename=args.summary_csv_name,
            apply_canonical_self=not args.no_canonical_self_override,
        )
        return

    # -- Config ---------------------------------------------------------------
    config_path = _REPO_ROOT / args.config
    config = idea04_paths.merge_experiment_config(config_path)
    if args.topology:
        config["topology"] = args.topology

    # -- Samples --------------------------------------------------------------
    if not args.samples_jsonl:
        sys.exit("[run_round1_v3] ERROR: --samples-jsonl is required (unless --merge-summary-only).")
    jsonl_path = _REPO_ROOT / Path(args.samples_jsonl)
    if not jsonl_path.is_file():
        sys.exit(f"[run_round1_v3] ERROR: samples jsonl not found: {jsonl_path}")
    samples = load_samples_from_jsonl(jsonl_path, sample_size=args.sample_size)
    print(f"[run_round1_v3] Loaded {len(samples)} samples from {jsonl_path.name}")

    # -- Methods --------------------------------------------------------------
    methods_to_run = [m.strip() for m in args.methods.split(",") if m.strip()]
    for m in methods_to_run:
        if m not in V3_METHODS:
            sys.exit(f"[run_round1_v3] Unknown method {m!r}.  Allowed: {V3_METHODS}")
        if m not in METHOD_NAMES:
            sys.exit(
                f"[run_round1_v3] Method {m!r} is not registered in methods.METHOD_NAMES. "
                "Check workspace/idea04_core/methods.py."
            )

    # -- Run dir --------------------------------------------------------------
    if args.resume_run_dir:
        run_root = Path(args.resume_run_dir)
        if not run_root.is_absolute():
            run_root = _REPO_ROOT / run_root
        if not run_root.is_dir():
            sys.exit(f"[run_round1_v3] --resume-run-dir is not a directory: {run_root}")
        run_id = run_root.name
        print(f"[run_round1_v3] Resuming into existing run dir: {run_root}")
    else:
        run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
        run_root = output_root / run_id
        run_root.mkdir(parents=True, exist_ok=True)
        print(f"[run_round1_v3] New run dir: {run_root}")

    # -- Execute --------------------------------------------------------------
    for method_name in methods_to_run:
        method_dir = run_root / method_name
        if method_dir.exists() and (method_dir / "metrics.json").is_file():
            print(f"[run_round1_v3] Skipping {method_name} — metrics.json already exists.")
            continue

        print(f"\n[run_round1_v3] {'='*60}")
        print(f"[run_round1_v3] Running method: {method_name}  ({len(samples)} samples)")
        print(f"[run_round1_v3] {'='*60}")

        method_config = dict(config)
        method_config["method_name"] = method_name
        method_config["n_workers"] = args.workers
        runner = RoundRunner(
            topology=config["topology"],
            max_handoff=config["max_handoff"],
        )
        metrics = runner.run(
            method_name=method_name,
            samples=samples,
            run_config=method_config,
            run_dir=method_dir,
        )
        print(
            f"[run_round1_v3] {method_name} → "
            f"F1={metrics['answer_f1']:.4f}  EM={metrics['answer_em']:.4f}  "
            f"PAR={metrics['premature_accept_rate']:.4f}"
        )

    if not args.no_write_summary:
        write_summary(
            output_root,
            run_root,
            run_id,
            methods_to_run,
            summary_csv_basename=args.summary_csv_name,
            apply_canonical_self=not args.no_canonical_self_override,
        )
    else:
        print("[run_round1_v3] Skipped write_summary (--no-write-summary).")
    print(f"\n[run_round1_v3] All done.  Run dir: {run_root}")


if __name__ == "__main__":
    main()
