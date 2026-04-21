"""Render Figure 3: Stage-2 prototype vs Stage-1 peer_calibrated paired F1 on HotpotQA fullval.

Two-panel layout (same ACL 2-column width = 3.3 in):

  Panel A (left): Bar chart of F1 mean ± cross-seed std for method=edo_stage2_chain
                  vs method=fixed_peer_calibrated on HotpotQA fullval n=7405, 3 seeds
                  (42/43/44). Overlay: paired-bootstrap 95% CI as thin whisker on
                  the rightmost bar (ΔF1 direction).

  Panel B (right): Token cost bar (same methods, same scale) with Δ token% annotation
                   in the title. Cross-seed σ overlay.

Data sources (single source of truth):
- artifacts/round2_gpt41mini_stage2_fullval/paired_stats_3seed.csv
  columns: seed, method_a, method_b, n, mean_f1_a, mean_f1_b, std_f1_a, std_f1_b,
           mean_delta_f1, ci_low, ci_high, paired_p,
           mean_token_a, mean_token_b, mean_delta_token_pct

- (interim) artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/
  fixed_peer_calibrated/metrics.json + edo_stage2_chain/metrics.json
  Used ONLY while the 3-seed paired_stats_3seed.csv is not yet written (E-017
  in flight). If --interim flag passed, plots a single-seed point estimate
  with a honest "interim; 3-seed CI pending" annotation on the figure.

Usage:
    # Full 3-seed (after E-017 complete and paired_bootstrap_ci.py has run):
    python scripts/plot_fig3_stage2_vs_stage1_paired.py

    # Interim single-seed (after seed=42 resume completes, before seed 43/44):
    python scripts/plot_fig3_stage2_vs_stage1_paired.py --interim

Output:
    artifacts/figures/fig3_stage2_vs_stage1_paired.{pdf,png}
    artifacts/figures/fig3_stage2_vs_stage1_paired_data.md  (data provenance)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO_ROOT / "artifacts"
FIG_DIR = ARTIFACTS / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

FULLVAL_ROOT = ARTIFACTS / "round2_gpt41mini_stage2_fullval"
PAIRED_CSV = FULLVAL_ROOT / "paired_stats_3seed.csv"

METHODS = ["fixed_peer_calibrated", "edo_stage2_chain"]
METHOD_LABELS = {
    "fixed_peer_calibrated": "Stage-1 (peer_calibrated)",
    "edo_stage2_chain":      "Stage-2 (edo_stage2_chain)",
}
METHOD_COLORS = {
    "fixed_peer_calibrated": "#7d8da6",
    "edo_stage2_chain":      "#2c5fab",
}


def load_3seed_stats() -> pd.DataFrame:
    """Load the canonical 3-seed paired stats table (E-017 output)."""
    if not PAIRED_CSV.exists():
        raise FileNotFoundError(
            f"paired_stats_3seed.csv not found at {PAIRED_CSV}. "
            "Run scripts/paired_bootstrap_ci.py after all 3 seeds of E-017 complete, "
            "or pass --interim to use single-seed estimate."
        )
    return pd.read_csv(PAIRED_CSV)


def load_interim_single_seed() -> pd.DataFrame:
    """Fallback: single-seed (seed=42) point estimate from metrics.json.

    Returns a dataframe mimicking paired_stats_3seed.csv schema but with n_seeds=1.
    """
    stage1_m = (
        FULLVAL_ROOT
        / "run_20260419_124130_seed42"
        / "fixed_peer_calibrated"
        / "metrics.json"
    )
    stage2_m = (
        FULLVAL_ROOT
        / "run_20260419_124129_seed42"
        / "edo_stage2_chain"
        / "metrics.json"
    )
    if not stage1_m.exists() or not stage2_m.exists():
        raise FileNotFoundError(
            "Interim single-seed metrics.json not found. "
            f"Expected: {stage1_m} and {stage2_m}. "
            "Wait for E-017 seed=42 resume to complete (runner writes metrics.json at end)."
        )
    s1 = json.loads(stage1_m.read_text(encoding="utf-8"))
    s2 = json.loads(stage2_m.read_text(encoding="utf-8"))
    # Construct single-row stats mimicking 3-seed schema
    return pd.DataFrame([{
        "seed": 42,
        "method_a": "fixed_peer_calibrated",
        "method_b": "edo_stage2_chain",
        "n": int(s1.get("sample_count", s1.get("n", 0))),
        "mean_f1_a": s1["answer_f1"],
        "mean_f1_b": s2["answer_f1"],
        "std_f1_a": 0.0,
        "std_f1_b": 0.0,
        "mean_delta_f1": s2["answer_f1"] - s1["answer_f1"],
        "ci_low": float("nan"),
        "ci_high": float("nan"),
        "paired_p": float("nan"),
        "mean_token_a": s1.get("api_total_tokens_per_sample", s1.get("avg_tokens_per_sample", float("nan"))),
        "mean_token_b": s2.get("api_total_tokens_per_sample", s2.get("avg_tokens_per_sample", float("nan"))),
        "mean_delta_token_pct": (
            (s2.get("api_total_tokens_per_sample", 0) - s1.get("api_total_tokens_per_sample", 0))
            / s1.get("api_total_tokens_per_sample", 1) * 100.0
            if s1.get("api_total_tokens_per_sample") else float("nan")
        ),
    }])


def render(df: pd.DataFrame, interim: bool, out_basename: str = "fig3_stage2_vs_stage1_paired") -> tuple[Path, Path]:
    """Render 2-panel figure from the paired stats dataframe."""
    n_seeds = len(df) if not interim else 1
    # Aggregate across seeds for mean ± cross-seed std
    agg = {
        "f1_stage1_mean": df["mean_f1_a"].mean(),
        "f1_stage1_std": df["mean_f1_a"].std(ddof=0) if n_seeds > 1 else 0.0,
        "f1_stage2_mean": df["mean_f1_b"].mean(),
        "f1_stage2_std": df["mean_f1_b"].std(ddof=0) if n_seeds > 1 else 0.0,
        "delta_f1_mean": df["mean_delta_f1"].mean(),
        "ci_low": df["ci_low"].iloc[0] if "ci_low" in df.columns else float("nan"),
        "ci_high": df["ci_high"].iloc[0] if "ci_high" in df.columns else float("nan"),
        "paired_p": df["paired_p"].iloc[0] if "paired_p" in df.columns else float("nan"),
        "tok_stage1_mean": df["mean_token_a"].mean(),
        "tok_stage2_mean": df["mean_token_b"].mean(),
        "delta_token_pct": df["mean_delta_token_pct"].mean(),
        "n_samples": int(df["n"].iloc[0]) if "n" in df.columns else 0,
    }

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(3.4, 3.0), sharey=False)

    # ---- Panel A: F1 bars ----
    method_indices = np.arange(len(METHODS))
    f1_vals = [agg["f1_stage1_mean"], agg["f1_stage2_mean"]]
    f1_stds = [agg["f1_stage1_std"], agg["f1_stage2_std"]]
    for i, (m, val, std) in enumerate(zip(METHODS, f1_vals, f1_stds)):
        axA.bar(
            i, val, width=0.55,
            color=METHOD_COLORS[m],
            edgecolor="black", linewidth=0.5, zorder=3,
            yerr=(std if n_seeds > 1 else None),
            error_kw={"ecolor": "black", "capsize": 3, "elinewidth": 0.7},
        )
        axA.text(i, val + 0.008, f"{val:.3f}",
                 ha="center", va="bottom", fontsize=6.8, zorder=4)
    axA.set_xticks(method_indices)
    axA.set_xticklabels([METHOD_LABELS[m].split(" ")[0] for m in METHODS], fontsize=7.5)
    axA.set_ylabel("HotpotQA F1", fontsize=8.5)
    axA.tick_params(axis="y", labelsize=7.5)
    axA.set_ylim(max(0.0, min(f1_vals) - 0.05), max(f1_vals) + 0.04)
    axA.yaxis.grid(True, color="#cccccc", linewidth=0.5, zorder=0)
    axA.set_axisbelow(True)
    for spine in ("top", "right"):
        axA.spines[spine].set_visible(False)

    # CI whisker annotation on stage2 bar
    if not np.isnan(agg["ci_low"]) and not np.isnan(agg["ci_high"]):
        ci_text = f"ΔF1={agg['delta_f1_mean']*100:+.2f} pp\n[{agg['ci_low']*100:+.2f}, {agg['ci_high']*100:+.2f}]"
    else:
        ci_text = f"ΔF1={agg['delta_f1_mean']*100:+.2f} pp\n(CI pending)"
    axA.text(0.5, max(f1_vals) + 0.025, ci_text,
             ha="center", va="bottom",
             fontsize=6.5, color="#444",
             transform=axA.transData, zorder=5)
    axA.set_title(f"(A) F1 (n={agg['n_samples']})", fontsize=8.8, pad=6)

    # ---- Panel B: token cost ----
    tok_vals = [agg["tok_stage1_mean"], agg["tok_stage2_mean"]]
    for i, (m, val) in enumerate(zip(METHODS, tok_vals)):
        axB.bar(
            i, val, width=0.55,
            color=METHOD_COLORS[m],
            edgecolor="black", linewidth=0.5, zorder=3,
        )
        if not np.isnan(val):
            axB.text(i, val + max(tok_vals) * 0.015,
                     f"{int(val):,}", ha="center", va="bottom",
                     fontsize=6.8, zorder=4)
    axB.set_xticks(method_indices)
    axB.set_xticklabels([METHOD_LABELS[m].split(" ")[0] for m in METHODS], fontsize=7.5)
    axB.set_ylabel("API tokens / sample", fontsize=8.5)
    axB.tick_params(axis="y", labelsize=7.5)
    axB.yaxis.grid(True, color="#cccccc", linewidth=0.5, zorder=0)
    axB.set_axisbelow(True)
    for spine in ("top", "right"):
        axB.spines[spine].set_visible(False)
    axB.set_title(f"(B) Token ({agg['delta_token_pct']:+.1f}%)",
                  fontsize=8.8, pad=6)

    if interim:
        fig.text(0.5, -0.02,
                 f"interim single-seed; n_seeds=1; cross-seed CI pending E-017 seed 43+44",
                 ha="center", fontsize=6.5, color="#a04020")

    fig.suptitle("Stage-2 vs Stage-1 paired, HotpotQA fullval", fontsize=9.2, y=1.00)
    fig.tight_layout()

    png_path = FIG_DIR / f"{out_basename}.png"
    pdf_path = FIG_DIR / f"{out_basename}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def write_data_provenance(df: pd.DataFrame, interim: bool, out_basename: str = "fig3_stage2_vs_stage1_paired") -> Path:
    note = FIG_DIR / f"{out_basename}_data.md"
    with note.open("w", encoding="utf-8") as fh:
        fh.write("# Figure 3 — Data provenance\n\n")
        fh.write("Single source of truth for the bars rendered by `scripts/plot_fig3_stage2_vs_stage1_paired.py`.\n\n")
        fh.write(f"Generation mode: **{'interim single-seed' if interim else '3-seed full'}**\n\n")
        fh.write("| Seed | Method | mean_f1 | mean_token | n |\n")
        fh.write("|---|---|---:|---:|---:|\n")
        for _, row in df.iterrows():
            fh.write(f"| {row.get('seed', 'agg')} | {row['method_a']} | {row['mean_f1_a']:.4f} | {row['mean_token_a']:.0f} | {int(row['n'])} |\n")
            fh.write(f"| {row.get('seed', 'agg')} | {row['method_b']} | {row['mean_f1_b']:.4f} | {row['mean_token_b']:.0f} | {int(row['n'])} |\n")
        fh.write("\n")
        if not interim:
            ci_low = df["ci_low"].iloc[0] if "ci_low" in df.columns else float("nan")
            ci_high = df["ci_high"].iloc[0] if "ci_high" in df.columns else float("nan")
            p = df["paired_p"].iloc[0] if "paired_p" in df.columns else float("nan")
            fh.write(f"Paired bootstrap 95% CI (B=10000) on ΔF1: [{ci_low:+.4f}, {ci_high:+.4f}]; paired p={p:.4g}.\n")
        else:
            fh.write("Interim mode: CI not available from single seed; will be computed once E-017 seed=43 + seed=44 complete and scripts/paired_bootstrap_ci.py runs.\n")
        fh.write("\nCanonical source when full 3-seed complete: `artifacts/round2_gpt41mini_stage2_fullval/paired_stats_3seed.csv` (output of scripts/paired_bootstrap_ci.py).\n")
    return note


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interim", action="store_true",
        help="Use single-seed point estimate (seed=42 metrics.json) instead of 3-seed CSV. "
             "Only appropriate when E-017 is in flight and paired_stats_3seed.csv not yet written."
    )
    args = parser.parse_args()

    try:
        if args.interim:
            df = load_interim_single_seed()
        else:
            df = load_3seed_stats()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    png, pdf = render(df, interim=args.interim)
    note = write_data_provenance(df, interim=args.interim)
    print(f"Wrote: {png.relative_to(REPO_ROOT)}")
    print(f"Wrote: {pdf.relative_to(REPO_ROOT)}")
    print(f"Wrote: {note.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
