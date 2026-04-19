"""Render Figure 2: Backbone-sensitivity bar chart for the EMNLP submission.

Renders a single ACL-2-column-width (3.3 in) figure that contrasts the three
fixed Stage-1 methods (peer_calibrated, static_roles, self_claim) under two
backbones (glm-4-flash, gpt-4.1-mini) on the chain-200 HotpotQA slice. Marks
the validated fullval F1 for peer_calibrated as an overlay. Produces both
PNG (for in-doc preview) and PDF (for ACL camera-ready).

Data sources (single source of truth):
- artifacts/round1/round1_v3_main_table.csv          (GLM chain-200)
- artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv  (gpt-4.1-mini chain-200)
- artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/metrics.json (peer fullval)

Usage:
    python scripts/plot_fig2_backbone_sensitivity.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO_ROOT / "artifacts"
FIG_DIR = ARTIFACTS / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

GLM_CSV = ARTIFACTS / "round1" / "round1_v3_main_table.csv"
GPT_CSV = ARTIFACTS / "round2_gpt41mini" / "round2_gpt41mini_main_table.csv"
PEER_FULLVAL_JSON = (
    ARTIFACTS
    / "round2_gpt41mini_fullval"
    / "run_20260414_135408"
    / "fixed_peer_calibrated"
    / "metrics.json"
)

METHODS = ["fixed_peer_calibrated", "fixed_static_roles", "fixed_self_claim"]
METHOD_LABELS = {
    "fixed_peer_calibrated": "peer_calibrated",
    "fixed_static_roles":    "static_roles",
    "fixed_self_claim":      "self_claim",
}
BACKBONES = ["glm-4-flash", "gpt-4.1-mini"]
BACKBONE_COLORS = {"glm-4-flash": "#7d8da6", "gpt-4.1-mini": "#2c5fab"}


def load_f1_table() -> pd.DataFrame:
    glm = pd.read_csv(GLM_CSV)
    glm = glm.set_index("method").loc[METHODS, ["answer_f1"]].rename(columns={"answer_f1": "glm-4-flash"})
    gpt = pd.read_csv(GPT_CSV)
    gpt = gpt.set_index("method").loc[METHODS, ["answer_f1"]].rename(columns={"answer_f1": "gpt-4.1-mini"})
    return glm.join(gpt)


def load_peer_fullval() -> float:
    with PEER_FULLVAL_JSON.open() as fh:
        return float(json.load(fh)["answer_f1"])


def render(out_basename: str = "fig2_backbone_sensitivity") -> tuple[Path, Path]:
    df = load_f1_table()
    peer_fullval = load_peer_fullval()

    fig, ax = plt.subplots(figsize=(3.4, 3.0))

    method_indices = np.arange(len(METHODS))
    bar_w = 0.36
    for offset, backbone in zip([-bar_w / 2, +bar_w / 2], BACKBONES):
        ys = df[backbone].values
        ax.bar(
            method_indices + offset,
            ys,
            width=bar_w,
            color=BACKBONE_COLORS[backbone],
            label=f"{backbone} (chain-200)",
            edgecolor="black",
            linewidth=0.5,
            zorder=3,
        )
        for x, y in zip(method_indices + offset, ys):
            ax.text(
                x, y + 0.008, f"{y:.3f}",
                ha="center", va="bottom",
                fontsize=6.8, color="black", zorder=4,
            )

    peer_idx = METHODS.index("fixed_peer_calibrated")
    gpt_offset = +bar_w / 2
    star_x = peer_idx + gpt_offset - 0.08
    ax.scatter(
        star_x,
        peer_fullval,
        marker="*",
        s=110,
        color="#d8332e",
        edgecolor="white",
        linewidth=0.8,
        zorder=6,
        label=f"peer fullval n=7405: {peer_fullval:.3f}",
    )
    ax.text(
        star_x + 0.02, peer_fullval + 0.005, f"{peer_fullval:.3f}",
        ha="left", va="bottom",
        fontsize=6.8, color="#d8332e", fontweight="bold", zorder=7,
    )

    ax.set_ylabel("HotpotQA F1", fontsize=8.5)
    ax.set_xticks(method_indices)
    ax.set_xticklabels([METHOD_LABELS[m] for m in METHODS], fontsize=8)
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_ylim(0.50, 0.85)
    ax.yaxis.grid(True, color="#cccccc", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax.set_title(
        "Backbone-sensitive Stage-1 ordering (chain-200, n=200)",
        fontsize=8.8, pad=6,
    )

    ax.legend(
        fontsize=6.8, frameon=False, loc="upper center",
        bbox_to_anchor=(0.5, -0.13), ncol=1, handletextpad=0.4, borderaxespad=0.0,
    )

    fig.tight_layout()

    png_path = FIG_DIR / f"{out_basename}.png"
    pdf_path = FIG_DIR / f"{out_basename}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    return png_path, pdf_path


def write_data_provenance(out_basename: str = "fig2_backbone_sensitivity") -> Path:
    df = load_f1_table()
    peer_fullval = load_peer_fullval()
    note = FIG_DIR / f"{out_basename}_data.md"
    with note.open("w", encoding="utf-8") as fh:
        fh.write("# Figure 2 — Data provenance\n\n")
        fh.write("Single source of truth for the bars rendered by `scripts/plot_fig2_backbone_sensitivity.py`.\n\n")
        fh.write("| Method | GLM-4-flash chain-200 (n=200) | gpt-4.1-mini chain-200 (n=200) |\n")
        fh.write("|---|---:|---:|\n")
        for m in METHODS:
            fh.write(f"| `{METHOD_LABELS[m]}` | {df.loc[m, 'glm-4-flash']:.4f} | {df.loc[m, 'gpt-4.1-mini']:.4f} |\n")
        fh.write("\n")
        fh.write(f"Overlay marker: `peer_calibrated` fullval F1 = **{peer_fullval:.4f}** (n=7405). ")
        fh.write("Source: `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/metrics.json`.\n\n")
        fh.write("`static_roles` and `self_claim` fullval are corrupted by upstream provider model drift and are pending rerun (U-006-decide). ")
        fh.write("This figure therefore intentionally compares only chain-200 numbers across backbones, with fullval shown only where it is validated.\n")
    return note


if __name__ == "__main__":
    png, pdf = render()
    note = write_data_provenance()
    print(f"Wrote: {png.relative_to(REPO_ROOT)}")
    print(f"Wrote: {pdf.relative_to(REPO_ROOT)}")
    print(f"Wrote: {note.relative_to(REPO_ROOT)}")
