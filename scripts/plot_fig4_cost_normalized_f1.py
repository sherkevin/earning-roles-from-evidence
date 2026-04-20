"""Render Figure 4: Token-cost-normalised F1 for Stage-1 methods on HotpotQA chain-200.

This figure visualises the Pareto-cost story that §4.3 Finding 4 articulates
numerically: on the canonical strong backbone (`gpt-4.1-mini`), the three
Stage-1 fixed methods have nearly-identical F1 (~0.73–0.77) but very different
per-sample API token cost (~4,663–6,415 tokens). Cost-normalised F1
(F1 per 1k tokens) puts `static_roles` well ahead of the TCPB prototype
`peer_calibrated` and of `self_claim` — directly visualising why TCPB is
Pareto-dominated in the delivered Stage-1 regime (the paper's §Limitations
item (6) admission).

Two panels:
  Panel A: F1 bars with API-tokens-per-sample annotation
  Panel B: Cost-normalised F1 (F1 / (api_tokens_per_sample / 1000)) bars

Data sources (single source of truth, already committed):
- artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv
  (chain-200 HotpotQA × 3 fixed methods × gpt-4.1-mini, seed=42)

Usage:
    python scripts/plot_fig4_cost_normalized_f1.py

Output:
    artifacts/figures/fig4_cost_normalized_f1.{pdf,png}
    artifacts/figures/fig4_cost_normalized_f1_data.md

Note on paper integration:
    This figure is OPTIONAL for the ARR May 25 sprint submission; it is
    provided mainly to (a) make Finding 4 Pareto-domination visually
    undeniable and (b) pre-satisfy `demand.md §11.5 #12` "no null-effect
    ablation tables" should a reviewer ask for "F1 at equal cost" framing.
    If the 8-page budget is tight after E-017 fullval table inflow, this
    figure can be held in Appendix D or omitted.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO_ROOT / "artifacts"
FIG_DIR = ARTIFACTS / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

GPT_CSV = ARTIFACTS / "round2_gpt41mini" / "round2_gpt41mini_main_table.csv"

METHODS = ["fixed_peer_calibrated", "fixed_static_roles", "fixed_self_claim"]
METHOD_LABELS = {
    "fixed_peer_calibrated": "peer_calibrated",
    "fixed_static_roles":    "static_roles",
    "fixed_self_claim":      "self_claim",
}
METHOD_COLORS = {
    "fixed_peer_calibrated": "#2c5fab",
    "fixed_static_roles":    "#5ba870",
    "fixed_self_claim":      "#d8732e",
}


def load_gpt41mini_chain200() -> pd.DataFrame:
    df = pd.read_csv(GPT_CSV)
    df = df.set_index("method").loc[METHODS].copy()
    return df


def render(df: pd.DataFrame, out_basename: str = "fig4_cost_normalized_f1") -> tuple[Path, Path]:
    # Single-panel design: cost-normalised F1 bars with F1/Tok annotations
    fig, ax = plt.subplots(figsize=(3.4, 3.0))

    method_indices = np.arange(len(METHODS))
    cn_f1 = [df.loc[m, "cost_normalized_f1_api"] for m in METHODS]
    f1_vals = [df.loc[m, "answer_f1"] for m in METHODS]
    tok_vals = [df.loc[m, "api_total_tokens_per_sample"] for m in METHODS]

    for i, (m, v, f1, tok) in enumerate(zip(METHODS, cn_f1, f1_vals, tok_vals)):
        ax.bar(
            i, v, width=0.55,
            color=METHOD_COLORS[m],
            edgecolor="black", linewidth=0.5, zorder=3,
        )
        ax.text(i, v + v * 0.02, f"{v:.4f}",
                ha="center", va="bottom", fontsize=7.5, zorder=4)
        ax.text(
            i, v * 0.55,
            f"F1={f1:.3f}\nTok={int(tok):,}",
            ha="center", va="center",
            fontsize=7.0, color="white", fontweight="bold", zorder=5,
        )

    ax.set_xticks(method_indices)
    ax.set_xticklabels([METHOD_LABELS[m] for m in METHODS], fontsize=8.0)
    ax.set_ylabel("HotpotQA F1 per 1,000 API tokens", fontsize=8.8)
    ax.tick_params(axis="y", labelsize=7.8)
    ax.set_ylim(0, max(cn_f1) * 1.18)
    ax.yaxis.grid(True, color="#cccccc", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    best_cn_method = max(METHODS, key=lambda m: df.loc[m, "cost_normalized_f1_api"])
    best_cn_label = METHOD_LABELS[best_cn_method]
    ax.set_title(
        f"Cost-normalised Stage-1 F1 (chain-200, gpt-4.1-mini)\n"
        f"Pareto-best: {best_cn_label} — TCPB dominated on both axes",
        fontsize=8.7, pad=6,
    )
    fig.tight_layout()

    png_path = FIG_DIR / f"{out_basename}.png"
    pdf_path = FIG_DIR / f"{out_basename}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def write_data_provenance(df: pd.DataFrame, out_basename: str = "fig4_cost_normalized_f1") -> Path:
    note = FIG_DIR / f"{out_basename}_data.md"
    with note.open("w", encoding="utf-8") as fh:
        fh.write("# Figure 4 — Data provenance\n\n")
        fh.write("Single source of truth for the bars rendered by "
                 "`scripts/plot_fig4_cost_normalized_f1.py`.\n\n")
        fh.write("Source: `artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv` "
                 "(chain-200 HotpotQA × 3 fixed methods × gpt-4.1-mini, seed=42).\n\n")
        fh.write("| Method | F1 | API tokens per sample | F1 per 1k API tokens |\n")
        fh.write("|---|---:|---:|---:|\n")
        for m in METHODS:
            row = df.loc[m]
            fh.write(f"| `{METHOD_LABELS[m].split(chr(10))[0].strip()}` "
                     f"| {row['answer_f1']:.4f} "
                     f"| {int(row['api_total_tokens_per_sample']):,} "
                     f"| {row['cost_normalized_f1_api']:.4f} |\n")
        fh.write("\n")
        best = max(METHODS, key=lambda m: df.loc[m, 'cost_normalized_f1_api'])
        fh.write(f"Pareto-best cost-normalised F1: `{METHOD_LABELS[best].split(chr(10))[0]}` "
                 f"= {df.loc[best, 'cost_normalized_f1_api']:.4f} F1/kTok. "
                 "This visualisation makes §4.3 Finding 4 ('peer_calibrated is Pareto-"
                 "dominated by a trivial baseline') numerically undeniable.\n")
    return note


def main() -> int:
    df = load_gpt41mini_chain200()
    png, pdf = render(df)
    note = write_data_provenance(df)
    print(f"Wrote: {png.relative_to(REPO_ROOT)}")
    print(f"Wrote: {pdf.relative_to(REPO_ROOT)}")
    print(f"Wrote: {note.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
