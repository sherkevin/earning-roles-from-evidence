"""Candidate Figure 1 using a best-paper framework grammar.

This script deliberately writes to a versioned candidate directory.  It does
not overwrite article/aamas2027/figures/overview.pdf.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["font.family"] = "DejaVu Sans"


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "article/aamas2027/figures/versions/v9_vector_production_20261004"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#2E5DA1"
ORANGE = "#C5681D"
GREEN = "#3F7D52"
PURPLE = "#8C5B87"
INK = "#17212B"
MUTED = "#5E6B78"
LINE = "#96A1AC"
PALE_BLUE = "#F1F6FB"
PALE_ORANGE = "#FFF5EA"
PALE_GREEN = "#F0F7F2"
PALE_PURPLE = "#FAF6FA"
WHITE = "#FFFFFF"


def box(ax, xy, wh, title, body, edge, fill=WHITE, title_size=11, body_size=9.4,
        dashed=False, title_color=None, lw=1.8):
    x, y = xy
    w, h = wh
    p = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=lw, edgecolor=edge, facecolor=fill,
        linestyle=(0, (4, 2)) if dashed else "-",
        transform=ax.transAxes, clip_on=False,
    )
    ax.add_patch(p)
    ax.text(x + 0.018, y + h - 0.035, title, transform=ax.transAxes,
            ha="left", va="top", fontsize=title_size, fontweight="bold",
            color=title_color or edge)
    ax.text(x + 0.018, y + h - 0.085, body, transform=ax.transAxes,
            ha="left", va="top", fontsize=body_size, linespacing=1.2,
            color=INK)
    return p


def arrow(ax, start, end, color, label=None, label_xy=None, lw=2.0,
          linestyle="-", mutation_scale=13, connectionstyle="arc3"):
    a = FancyArrowPatch(
        start, end, transform=ax.transAxes, arrowstyle="-|>",
        mutation_scale=mutation_scale, linewidth=lw, color=color,
        linestyle=linestyle, connectionstyle=connectionstyle,
        shrinkA=2, shrinkB=2, clip_on=False,
    )
    ax.add_patch(a)
    if label:
        lx, ly = label_xy or ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        ax.text(lx, ly, label, transform=ax.transAxes, ha="center", va="center",
                fontsize=8.2, color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.16", facecolor=WHITE,
                          edgecolor="none", alpha=0.92))
    return a


def circle_agent(ax, center, label, edge=BLUE):
    c = Circle(center, 0.019, transform=ax.transAxes, facecolor=WHITE,
               edgecolor=edge, linewidth=1.5, clip_on=False)
    ax.add_patch(c)
    ax.text(*center, label, transform=ax.transAxes, ha="center", va="center",
            fontsize=8.0, color=edge, fontweight="bold")


def draw():
    fig, ax = plt.subplots(figsize=(12.2, 3.85))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # One visual sentence: situated episode -> central mechanism -> future assignment.
    # Left: the observable episode, deliberately small so the method dominates.
    box(ax, (0.025, 0.57), (0.205, 0.25), "① Situated episode",
        "task xₜ\nartifact oₜ", ORANGE, PALE_ORANGE)
    ax.text(0.043, 0.595, "producer → recipient", transform=ax.transAxes,
            fontsize=8.2, color=ORANGE, fontweight="bold")

    # Central mechanism: the only large container, following the reference grammar.
    box(ax, (0.275, 0.245), (0.425, 0.575), "EARNING ROLES",
        "public evidence from the recipient's situated use", PURPLE, PALE_PURPLE,
        title_size=12.4, body_size=9.0, dashed=True, title_color=PURPLE, lw=2.0)

    box(ax, (0.292, 0.475), (0.122, 0.205), "② Recipient use",
        "judgment jₜ\nchanged paths", ORANGE, PALE_ORANGE,
        title_size=8.5, body_size=8.0)
    box(ax, (0.426, 0.475), (0.122, 0.205), "③ Ownership gate",
        "producer-owned?\nUNKNOWN if\nambiguous", GREEN, PALE_GREEN,
        title_size=7.6, body_size=7.2)
    box(ax, (0.560, 0.475), (0.122, 0.205), "④ Publish",
        "versioned evidence\n+ watermark", GREEN, PALE_GREEN,
        title_size=8.8, body_size=8.0)
    arrow(ax, (0.414, 0.578), (0.423, 0.578), ORANGE, lw=1.6, mutation_scale=10)
    arrow(ax, (0.548, 0.578), (0.557, 0.578), GREEN, lw=1.6, mutation_scale=10)
    ax.text(0.302, 0.405, "public + attributable + complete → role evidence",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.4,
            color=MUTED)

    # Right: the next decision, with a tiny local peer menu rather than a generic output box.
    box(ax, (0.745, 0.57), (0.225, 0.25), "⑤ Local peer selector",
        "read-cut state → sealed assignment", BLUE, PALE_BLUE,
        title_size=10.5, body_size=9.0)
    circle_agent(ax, (0.785, 0.645), "A")
    circle_agent(ax, (0.835, 0.645), "B")
    circle_agent(ax, (0.885, 0.645), "C")
    ax.text(0.920, 0.645, "local menu", transform=ax.transAxes,
            ha="left", va="center", fontsize=7.6, color=MUTED)

    # Later target outcome is intentionally outside the mechanism and after the seal.
    box(ax, (0.765, 0.205), (0.185, 0.19), "⑥ Later outcome",
        "quality yₜ + complete cost", BLUE, PALE_BLUE,
        title_size=10.2, body_size=8.4)

    # Main path: one direction, labels are the objects rather than vague verbs.
    arrow(ax, (0.230, 0.695), (0.292, 0.695), ORANGE, label="delivery", label_xy=(0.260, 0.735), lw=2.2)
    arrow(ax, (0.700, 0.695), (0.742, 0.695), BLUE, label="evidence → decision", label_xy=(0.721, 0.855), lw=2.2)
    arrow(ax, (0.845, 0.565), (0.845, 0.405), BLUE, label="after seal", label_xy=(0.895, 0.48), lw=1.8, linestyle=(0, (4, 2)))

    # Delayed credit returns only to a future read cut in the selector; it does
    # not touch the sealed assignment or the central evidence row.
    arrow(ax, (0.790, 0.405), (0.790, 0.575), MUTED,
          label="delayed credit", label_xy=(0.730, 0.485),
          lw=1.8, linestyle=(0, (4, 2)), connectionstyle="arc3,rad=0.08")
    ax.text(0.825, 0.585, "future read cut", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=7.2, color=MUTED,
            bbox=dict(boxstyle="round,pad=0.14", facecolor=PALE_BLUE,
                      edgecolor="none", alpha=0.95))

    # Caption-like footer is part of the figure but remains a single contract sentence.
    ax.text(0.025, 0.035,
            "Recipient use becomes public evidence; a later outcome evaluates the sealed assignment.",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=8.8,
            color=MUTED)

    fig.savefig(OUT / "overview.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT / "overview.png", dpi=240, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


if __name__ == "__main__":
    draw()
