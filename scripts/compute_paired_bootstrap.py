"""
Paired per-task F1 (or EM) differences vs a baseline method: bootstrap 95% CI for the
mean paired difference over **all** aligned tasks (zeros included) + exact two-sided
sign test (binomial p=0.5, **ties excluded**).

Example:
  python scripts/compute_paired_bootstrap.py \\
    --run-dir artifacts/round1/run_20260411_102202 \\
    --baseline fixed_peer_calibrated \\
    --compare central_orchestrator central_orchestrator_with_reflection fixed_self_calibrated \\
    --metric answer_f1 \\
    --n-bootstrap 10000 \\
    --out-csv artifacts/round1_v3_paired_stats.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from math import comb
from pathlib import Path


def load_scores(path: Path, metric: str) -> dict[str, float]:
    out: dict[str, float] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            tid = row["task_id"]
            out[tid] = float(row[metric])
    return out


def binom_two_sided_p(k: int, n: int) -> float:
    """Two-sided exact p-value for Binomial(n, 0.5), counting k 'successes'."""
    if n <= 0:
        return 1.0
    lo = sum(comb(n, i) for i in range(k + 1)) / (2**n)
    hi = sum(comb(n, i) for i in range(k, n + 1)) / (2**n)
    return min(1.0, 2 * min(lo, hi))


def bootstrap_mean_ci(
    diffs: list[float],
    n_boot: int,
    alpha: float,
    seed: int,
) -> tuple[float, float, float]:
    if not diffs:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    n = len(diffs)
    means: list[float] = []
    for _ in range(n_boot):
        sample = [diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo_i = max(0, int((alpha / 2) * n_boot))
    hi_i = min(n_boot - 1, int((1 - alpha / 2) * n_boot))
    return sum(diffs) / n, means[lo_i], means[hi_i]


def main() -> None:
    p = argparse.ArgumentParser(description="Paired bootstrap CI vs baseline (per-task F1/EM).")
    p.add_argument("--run-dir", type=Path, required=True, help="Run directory containing method subdirs.")
    p.add_argument("--baseline", required=True, help="Subdir name for baseline method.")
    p.add_argument(
        "--compare",
        nargs="+",
        required=True,
        help="Subdir names to compare against baseline.",
    )
    p.add_argument(
        "--metric",
        default="answer_f1",
        choices=("answer_f1", "answer_em"),
        help="Score column in parsed_predictions.jsonl.",
    )
    p.add_argument("--n-bootstrap", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--out-csv", type=Path, required=True)
    args = p.parse_args()

    run_dir = args.run_dir.resolve()
    base_path = run_dir / args.baseline / "parsed_predictions.jsonl"
    if not base_path.is_file():
        sys.exit(f"[compute_paired_bootstrap] missing {base_path}")

    base_scores = load_scores(base_path, args.metric)
    rows_out: list[dict[str, object]] = []

    for other in args.compare:
        op = run_dir / other / "parsed_predictions.jsonl"
        if not op.is_file():
            print(f"[compute_paired_bootstrap] skip {other}: no {op}", file=sys.stderr)
            continue
        o_scores = load_scores(op, args.metric)
        common = sorted(set(base_scores) & set(o_scores))
        diffs_all: list[float] = []
        ties = 0
        wins_b = 0
        wins_o = 0
        for tid in common:
            d = base_scores[tid] - o_scores[tid]
            diffs_all.append(d)
            if d == 0.0:
                ties += 1
            elif d > 0:
                wins_b += 1
            else:
                wins_o += 1
        n_nt = wins_b + wins_o
        mean_d, lo, hi = bootstrap_mean_ci(diffs_all, args.n_bootstrap, args.alpha, args.seed)
        p_sign = binom_two_sided_p(wins_b, n_nt)
        rows_out.append(
            {
                "baseline": args.baseline,
                "compare": other,
                "metric": args.metric,
                "n_tasks": len(common),
                "n_ties": ties,
                "n_non_tie": n_nt,
                "mean_baseline_minus_compare": round(mean_d, 6),
                "bootstrap_ci_low": round(lo, 6),
                "bootstrap_ci_high": round(hi, 6),
                "sign_test_p_two_sided": round(p_sign, 6),
                "wins_baseline": wins_b,
                "wins_compare": wins_o,
            }
        )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    if not rows_out:
        sys.exit("[compute_paired_bootstrap] no rows written")
    fieldnames = list(rows_out[0].keys())
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    print(f"[compute_paired_bootstrap] wrote {args.out_csv} ({len(rows_out)} rows)")


if __name__ == "__main__":
    main()
