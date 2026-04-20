"""Paired bootstrap CI for E-017 Stage-2 vs Stage-1 fullval.

Reads ``parsed_predictions.jsonl`` from each (seed, method) run dir, joins
on ``task_id`` (per-pair sample), and computes:

  - per-sample ΔF1 (method_b − method_a) and Δtokens
  - mean ΔF1, ΔEM, Δtokens (point estimate)
  - 95% percentile bootstrap CI on the mean (B = 10000 by default)
  - paired sign-test p-value on per-sample ΔF1

Usage::

    python scripts/paired_bootstrap_ci.py \\
        --root artifacts/round2_gpt41mini_stage2_fullval \\
        --method-a fixed_peer_calibrated \\
        --method-b edo_stage2_chain \\
        --seeds 42,43,44 \\
        --B 10000 \\
        --out artifacts/round2_gpt41mini_stage2_fullval/paired_stats_3seed.csv

For each seed, expects a sub-dir ``run_*_seed{N}/{method}/parsed_predictions.jsonl``;
finds the latest one matching that pattern.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_predictions(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rows[row["task_id"]] = row
    return rows


def _find_run_dir(root: Path, seed: int, method: str) -> Path:
    matches = sorted(
        root.glob(f"run_*_seed{seed}/{method}/parsed_predictions.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError(
            f"no parsed_predictions.jsonl for seed={seed} method={method} under {root}"
        )
    return matches[0].parent


def _percentile(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * q
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def _bootstrap_ci(
    deltas: list[float], B: int, alpha: float = 0.05, rng_seed: int = 0
) -> tuple[float, float, float]:
    """Return (point_mean, ci_low, ci_high) via percentile bootstrap on the mean."""
    if not deltas:
        return 0.0, 0.0, 0.0
    rng = random.Random(rng_seed)
    n = len(deltas)
    means: list[float] = []
    for _ in range(B):
        sample_sum = 0.0
        for _ in range(n):
            sample_sum += deltas[rng.randint(0, n - 1)]
        means.append(sample_sum / n)
    point = sum(deltas) / n
    return point, _percentile(means, alpha / 2), _percentile(means, 1 - alpha / 2)


def _sign_test_p(deltas: list[float]) -> float:
    """Two-sided sign test p-value (binomial, ties dropped)."""
    plus = sum(1 for d in deltas if d > 0)
    minus = sum(1 for d in deltas if d < 0)
    n = plus + minus
    if n == 0:
        return 1.0
    k = max(plus, minus)
    # two-sided p = 2 * Pr(X >= k under H0=0.5); use CDF
    # ln-stable computation via lgamma
    log_p = -n * math.log(2.0)
    cumulative = 0.0
    for i in range(k, n + 1):
        # binomial coefficient C(n, i)
        log_binom = (
            math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
        )
        cumulative += math.exp(log_binom + log_p)
    return min(1.0, 2.0 * cumulative)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, help="parent dir containing run_*_seed*/")
    p.add_argument("--method-a", required=True)
    p.add_argument("--method-b", required=True)
    p.add_argument("--seeds", required=True, help="comma-separated seed ints, e.g., 42,43,44")
    p.add_argument("--B", type=int, default=10000)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    root = Path(args.root)
    if not root.is_absolute():
        root = _REPO_ROOT / root
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    out_rows: list[dict] = []
    for seed in seeds:
        try:
            dir_a = _find_run_dir(root, seed, args.method_a)
            dir_b = _find_run_dir(root, seed, args.method_b)
        except FileNotFoundError as e:
            print(f"[paired_bootstrap_ci] WARN seed={seed}: {e}", file=sys.stderr)
            continue
        preds_a = _load_predictions(dir_a / "parsed_predictions.jsonl")
        preds_b = _load_predictions(dir_b / "parsed_predictions.jsonl")
        common_ids = sorted(set(preds_a.keys()) & set(preds_b.keys()))
        if not common_ids:
            print(f"[paired_bootstrap_ci] WARN seed={seed}: no overlapping task_ids", file=sys.stderr)
            continue

        deltas_f1 = [preds_b[tid]["answer_f1"] - preds_a[tid]["answer_f1"] for tid in common_ids]
        deltas_em = [preds_b[tid]["answer_em"] - preds_a[tid]["answer_em"] for tid in common_ids]
        deltas_token = [
            preds_b[tid].get("token_cost", 0) - preds_a[tid].get("token_cost", 0)
            for tid in common_ids
        ]
        f1_mean = sum(preds_a[tid]["answer_f1"] for tid in common_ids) / len(common_ids)
        f1_b_mean = sum(preds_b[tid]["answer_f1"] for tid in common_ids) / len(common_ids)
        token_a_mean = sum(preds_a[tid].get("token_cost", 0) for tid in common_ids) / len(common_ids)
        token_b_mean = sum(preds_b[tid].get("token_cost", 0) for tid in common_ids) / len(common_ids)

        p_f1, lo_f1, hi_f1 = _bootstrap_ci(deltas_f1, args.B, rng_seed=seed)
        p_em, lo_em, hi_em = _bootstrap_ci(deltas_em, args.B, rng_seed=seed + 1000)
        p_tok, lo_tok, hi_tok = _bootstrap_ci(deltas_token, args.B, rng_seed=seed + 2000)
        sign_p = _sign_test_p(deltas_f1)

        out_rows.append({
            "seed": seed,
            "method_a": args.method_a,
            "method_b": args.method_b,
            "n": len(common_ids),
            "f1_a_mean": round(f1_mean, 4),
            "f1_b_mean": round(f1_b_mean, 4),
            "delta_f1_mean": round(p_f1, 4),
            "delta_f1_ci95_low": round(lo_f1, 4),
            "delta_f1_ci95_high": round(hi_f1, 4),
            "delta_f1_sign_p": round(sign_p, 6),
            "delta_em_mean": round(p_em, 4),
            "delta_em_ci95_low": round(lo_em, 4),
            "delta_em_ci95_high": round(hi_em, 4),
            "token_a_mean": round(token_a_mean, 1),
            "token_b_mean": round(token_b_mean, 1),
            "delta_token_mean": round(p_tok, 1),
            "delta_token_ci95_low": round(lo_tok, 1),
            "delta_token_ci95_high": round(hi_tok, 1),
        })
        print(f"[paired_bootstrap_ci] seed={seed} ΔF1 = {p_f1:+.4f} "
              f"[{lo_f1:+.4f}, {hi_f1:+.4f}] sign-p={sign_p:.4g} (n={len(common_ids)})")

    if not out_rows:
        print("[paired_bootstrap_ci] no usable data found", file=sys.stderr)
        return 2

    # summary across seeds (mean of per-seed point estimates)
    mean_delta_f1 = sum(r["delta_f1_mean"] for r in out_rows) / len(out_rows)
    print(f"\n=== AGGREGATE ACROSS {len(out_rows)} SEEDS ===")
    print(f"Mean ΔF1 = {mean_delta_f1:+.4f}")
    if len(out_rows) > 1:
        var = sum((r["delta_f1_mean"] - mean_delta_f1) ** 2 for r in out_rows) / (len(out_rows) - 1)
        print(f"Std ΔF1  = {math.sqrt(var):.4f}")

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = _REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
