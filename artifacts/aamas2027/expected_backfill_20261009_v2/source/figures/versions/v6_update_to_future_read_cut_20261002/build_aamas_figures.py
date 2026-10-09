"""Draw the internal AAMAS paper's architecture and event-time figures.

The figures are protocol schematics, not empirical results.  They are kept in a
small reproducible script so that labels and dimensions can be edited without
changing the official AAMAS class or layout parameters.
"""
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Keep all labels as embedded TrueType text in the final vector PDFs.
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "article/aamas2027/figures"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#276091"
ORANGE = "#BE6923"
GREEN = "#37784E"
GREY = "#5C6670"
PALE = "#F7F8FA"
TEXT = "#17212B"


def box(ax, x, y, w, h, title, body, artifact, color):
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.2, edgecolor=color, facecolor=PALE,
    )
    ax.add_patch(patch)
    ax.text(x + 0.018, y + h - 0.055, title, fontsize=8.5, weight="bold",
            color=color, va="top", ha="left")
    wrapped = "\n".join(textwrap.wrap(body, width=31))
    ax.text(x + 0.018, y + h - 0.105, wrapped, fontsize=6.7, color=TEXT,
            va="top", ha="left", linespacing=1.12)
    pill_h = 0.052
    ax.add_patch(Rectangle((x + 0.015, y + 0.014), w - 0.03, pill_h,
                           linewidth=0.6, edgecolor="#A7ADB4", facecolor="white"))
    ax.text(x + w / 2, y + 0.040, artifact, fontsize=6.2, family="monospace",
            color=TEXT, va="center", ha="center")


def arrow(ax, start, end, color, dashed=False, rad=0.0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=9, linewidth=1.0,
        linestyle="--" if dashed else "-", color=color,
        connectionstyle=f"arc3,rad={rad}",
    ))


def overview():
    fig, ax = plt.subplots(figsize=(7.0, 2.72))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    w, h = 0.27, 0.31
    xs = [0.025, 0.365, 0.705]
    top, bottom = 0.55, 0.10
    box(ax, xs[0], top, w, h, "1  Situated delivery",
        "Only the selected producer runs and returns a versioned artifact.",
        "id | version | digest", ORANGE)
    box(ax, xs[1], top, w, h, "2  Recipient judgment",
        "The real consumer reads, uses, revises, or rejects the artifact.",
        "judgment | action | owner", ORANGE)
    box(ax, xs[2], top, w, h, "3  Public role evidence",
        "A responsibility gate admits attributable, complete, non-duplicate evidence.",
        "evidence | reason | watermark", GREEN)
    box(ax, xs[2], bottom, w, h, "4  Future assignment",
        "A local selector reads the sealed snapshot before target execution.",
        "assignment | p(a) | read-cut", BLUE)
    box(ax, xs[1], bottom, w, h, "5  Target outcome",
        "Quality, adoption, rework, and complete cost are scored independently.",
        "quality | cost | UNKNOWN", BLUE)
    box(ax, xs[0], bottom, w, h, "6  Delayed credit",
        "Only the matching future responsibility opportunity receives credit.",
        "state' | digest' | lag", GREEN)
    cy_top, cy_bottom = top + h / 2, bottom + h / 2
    arrow(ax, (xs[0] + w, cy_top), (xs[1], cy_top), ORANGE)
    arrow(ax, (xs[1] + w, cy_top), (xs[2], cy_top), GREEN)
    arrow(ax, (xs[2] + w / 2, top), (xs[2] + w / 2, bottom + h), BLUE)
    arrow(ax, (xs[2], cy_bottom), (xs[1] + w, cy_bottom), BLUE)
    arrow(ax, (xs[1], cy_bottom), (xs[0] + w, cy_bottom), GREEN)
    # Route delayed feedback around the stages so it cannot be mistaken for a
    # synchronous edge or obscure the labels.
    x0, x1 = 0.008, xs[2] + w + 0.012
    # Leave stage 6 at its outside edge and enter stage 4 from its outside right edge;
    # the delayed path never crosses a node or the public-evidence box.
    arrow(ax, (xs[0], bottom + h / 2), (x0, bottom + h / 2), GREY, dashed=True)
    arrow(ax, (x0, bottom + h / 2), (x0, 0.94), GREY, dashed=True)
    arrow(ax, (x0, 0.94), (x1, 0.94), GREY, dashed=True)
    # Delayed credit returns to the later assignment/read-cut (stage 4),
    # never to the public-evidence box (stage 3).
    arrow(ax, (x1, 0.94), (x1, bottom + h / 2), GREY, dashed=True)
    arrow(ax, (x1, bottom + h / 2), (xs[2] + w, bottom + h / 2), GREY, dashed=True)
    ax.text(0.51, 0.02, "dashed edge: delayed feedback changes a later read cut only",
            fontsize=6.5, color=GREY, ha="center", va="bottom")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.02)
    fig.savefig(OUT / "overview.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def timeline():
    fig, ax = plt.subplots(figsize=(3.35, 1.82))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    w, h = 0.285, 0.24
    xs = [0.02, 0.357, 0.694]
    ytop, ybot = 0.61, 0.20
    items = [
        (xs[0], ytop, "$t$: select + execute", "source delivery", ORANGE),
        (xs[1], ytop, "$t+d$: inspect + act", "recipient judgment", ORANGE),
        (xs[2], ytop, "$w$: publish", "evidence / UNKNOWN", GREEN),
        (xs[2], ybot, "$t+1$: read cut", "seal assignment", BLUE),
        (xs[1], ybot, "$t+1$: execute", "target outcome", BLUE),
        (xs[0], ybot, "$t+1+d$: validate", "delayed credit", GREEN),
    ]
    for x, y, a, b, c in items:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                    linewidth=1.0, edgecolor=c, facecolor=PALE))
        ax.text(x + w / 2, y + h * .62, a, fontsize=5.9, ha="center", va="center", color=TEXT)
        ax.text(x + w / 2, y + h * .33, b, fontsize=6.7, weight="bold", ha="center", va="center", color=c)
    arrow_y_top = ytop + h * .91
    arrow_y_bottom = ybot + h * .91
    arrow(ax, (xs[0] + w, arrow_y_top), (xs[1], arrow_y_top), ORANGE)
    arrow(ax, (xs[1] + w, arrow_y_top), (xs[2], arrow_y_top), GREEN)
    arrow(ax, (xs[2] + w / 2, ytop), (xs[2] + w / 2, ybot + h), BLUE)
    arrow(ax, (xs[2], arrow_y_bottom), (xs[1] + w, arrow_y_bottom), BLUE)
    arrow(ax, (xs[1], arrow_y_bottom), (xs[0] + w, arrow_y_bottom), GREEN)
    x0, x1 = 0.006, xs[2] + w + 0.008
    # Route outside both rows so the delayed path does not cross a node.
    arrow(ax, (xs[0], ybot + h / 2), (x0, ybot + h / 2), GREY, dashed=True)
    arrow(ax, (x0, ybot + h / 2), (x0, 0.93), GREY, dashed=True)
    arrow(ax, (x0, 0.93), (x1, 0.93), GREY, dashed=True)
    # Delayed credit changes the later read cut, not the already published row.
    arrow(ax, (x1, 0.93), (x1, ybot + h / 2), GREY, dashed=True)
    arrow(ax, (x1, ybot + h / 2), (xs[2] + w, ybot + h / 2), GREY, dashed=True)
    ax.text(0.5, 0.04, "future outcome is unavailable at the sealed assignment",
            fontsize=6.1, color=GREY, ha="center", va="center")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.02)
    fig.savefig(OUT / "timeline.pdf", bbox_inches="tight", pad_inches=0.015)
    plt.close(fig)



def method_state():
    """Draw the evidence-to-role state schematic (method figure, no results)."""
    fig, ax = plt.subplots(figsize=(7.0, 2.72))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    lanes = [
        (0.70, 0.22, "EPISODE", ORANGE),
        (0.39, 0.22, "PUBLIC EVIDENCE", GREEN),
        (0.08, 0.22, "LOCAL DECISION", BLUE),
    ]
    for y, h, title, color in lanes:
        ax.add_patch(FancyBboxPatch(
            (0.115, y), 0.865, h, boxstyle="round,pad=0.008,rounding_size=0.012",
            linewidth=0.7, edgecolor="#D4D9DE", facecolor="#FBFCFD"))
        ax.text(0.018, y + h / 2, title, fontsize=7.0, weight="bold", color=color,
                va="center", ha="left", rotation=90)

    def lane_node(x, y, w, title, body, color, dashed=False):
        style = "round,pad=0.008,rounding_size=0.012"
        ax.add_patch(FancyBboxPatch((x, y), w, 0.15, boxstyle=style,
                                    linewidth=1.0, linestyle="--" if dashed else "-",
                                    edgecolor=color, facecolor="white"))
        ax.text(x + 0.012, y + 0.112, title, fontsize=7.2, weight="bold",
                color=color, va="top", ha="left")
        ax.text(x + 0.012, y + 0.058, body, fontsize=6.45, color=TEXT,
                va="center", ha="left", linespacing=1.04)

    # Three lanes share aligned interfaces but retain their legal boundaries.
    lane_node(0.145, 0.735, 0.18, "producer artifact", "version | digest", ORANGE)
    lane_node(0.385, 0.735, 0.205, "recipient judgment", "action | owner | changed paths", ORANGE)
    lane_node(0.665, 0.735, 0.235, "target outcome", "after seal: quality | adoption | cost", BLUE)
    arrow(ax, (0.325, 0.81), (0.385, 0.81), ORANGE)
    arrow(ax, (0.590, 0.81), (0.665, 0.81), ORANGE)

    lane_node(0.385, 0.425, 0.15, "typed projection", "public fields only", GREEN)
    lane_node(0.565, 0.425, 0.19, "ownership / UNKNOWN", "producer defect? recipient work?", GREEN, dashed=True)
    lane_node(0.785, 0.425, 0.17, "versioned row", "evidence | watermark", GREEN)
    arrow(ax, (0.535, 0.50), (0.565, 0.50), GREEN)
    arrow(ax, (0.755, 0.50), (0.785, 0.50), GREEN)

    lane_node(0.145, 0.115, 0.18, "local peers (k)", "candidate menu | graph", BLUE)
    lane_node(0.385, 0.115, 0.18, "read-cut state", "local state | representation", BLUE)
    lane_node(0.61, 0.115, 0.17, "sealed assignment", "p(a) | task start", BLUE)
    lane_node(0.805, 0.115, 0.15, "selected-only", "update state'", BLUE)
    arrow(ax, (0.325, 0.19), (0.385, 0.19), BLUE)
    arrow(ax, (0.565, 0.19), (0.61, 0.19), BLUE)
    arrow(ax, (0.78, 0.19), (0.825, 0.19), BLUE)

    # Cross-lane relationships are explicitly labelled and delayed where needed.
    arrow(ax, (0.485, 0.735), (0.46, 0.575), ORANGE)
    ax.text(0.488, 0.635, "project", fontsize=5.7, color=ORANGE, ha="left", va="center")
    arrow(ax, (0.87, 0.425), (0.475, 0.265), GREEN, dashed=True, rad=0.12)
    ax.text(0.65, 0.335, "eligible rows at read cut", fontsize=5.7, color=GREEN,
            ha="center", va="center", rotation=-8)
    arrow(ax, (0.78, 0.735), (0.89, 0.265), GREY, dashed=True, rad=-0.12)
    # The update writes a future read-cut state; it never rewrites the sealed assignment.
    y_next = 0.055
    arrow(ax, (0.88, 0.115), (0.88, y_next), BLUE, dashed=True)
    arrow(ax, (0.88, y_next), (0.475, y_next), BLUE, dashed=True)
    arrow(ax, (0.475, y_next), (0.475, 0.115), BLUE, dashed=True)
    ax.text(0.68, 0.074, "future read cut", fontsize=5.7, color=BLUE, ha="center", va="center")
    ax.text(0.56, 0.025,
            "only public rows before the read cut can affect selection; target outcomes arrive after the seal",
            fontsize=6.2, color=GREY, ha="center", va="bottom")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.025)
    fig.savefig(OUT / "method_state.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

def experiment_map():
    fig, ax = plt.subplots(figsize=(7.0, 2.30))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    # Three compact panels follow the left-to-right grammar used by the gallery:
    # inputs, matched alternatives, and the estimands they can falsify.
    panels = [(0.02, 0.12, 0.25, 0.76, "TRACKS", GREEN),
              (0.37, 0.12, 0.27, 0.76, "MATCHED POLICIES", BLUE),
              (0.74, 0.12, 0.24, 0.76, "RQ / ENDPOINT", ORANGE)]
    for x, y, w, h, title, c in panels:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
                                    linewidth=1.1, edgecolor=c, facecolor=PALE))
        ax.text(x + 0.018, y + h - 0.055, title, fontsize=8.0, weight="bold", color=c,
                ha="left", va="top")
    tracks = [
        (0.055, 0.59, "ArtifactRole", "producer → recipient → later duty"),
        (0.055, 0.34, "PeerSelect", "local graph, drift, service cost"),
    ]
    for x, y, title, body in tracks:
        ax.add_patch(Rectangle((x, y), 0.18, 0.14, facecolor="white", edgecolor="#A7ADB4", linewidth=.7))
        ax.text(x + .09, y + .09, title, fontsize=7.0, weight="bold", color=GREEN, ha="center")
        ax.text(x + .09, y + .042, body, fontsize=5.8, color=TEXT, ha="center", va="center")
    arms = ["uniform", "no update", "raw acceptance", "terminal only", "trust / bandit", "pooled", "RARE"]
    for i, arm in enumerate(arms):
        yy = 0.70 - i * 0.078
        c = BLUE if arm == "RARE" else "#A7ADB4"
        ax.add_patch(Rectangle((0.405, yy), 0.20, 0.052, facecolor="white", edgecolor=c, linewidth=.8))
        ax.text(0.505, yy + .026, arm, fontsize=6.2, weight="bold" if arm == "RARE" else "normal",
                color=BLUE if arm == "RARE" else TEXT, ha="center", va="center")
    rqs = [(0.775, 0.67, "RQ1", "information"), (0.775, 0.51, "RQ2", "assignment"),
           (0.775, 0.35, "RQ3", "latency / cost"), (0.775, 0.19, "RQ4", "safety / drift")]
    for x, y, rq, text in rqs:
        ax.add_patch(Rectangle((x, y), 0.17, 0.09, facecolor="white", edgecolor="#A7ADB4", linewidth=.7))
        ax.text(x + .03, y + .045, rq, fontsize=6.5, weight="bold", color=ORANGE, ha="left", va="center")
        ax.text(x + .105, y + .045, text, fontsize=6.0, color=TEXT, ha="center", va="center")
    arrow(ax, (0.27, 0.50), (0.37, 0.50), GREEN)
    arrow(ax, (0.64, 0.50), (0.74, 0.50), BLUE)
    ax.text(0.5, 0.035, "every arm receives the same menu, lawful feedback schedule, opportunity, and complete-cost budget",
            fontsize=6.2, color=GREY, ha="center", va="center")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.02)
    fig.savefig(OUT / "experiment_map.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    overview()
    timeline()
    experiment_map()
    method_state()
    print(f"wrote protocol figures under {OUT}")
