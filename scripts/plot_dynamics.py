"""
scripts/plot_dynamics.py
========================
Plot per-node competence convergence dynamics from a single run directory.

Usage
-----
# Simplest: auto-detect the fixed_peer_calibrated sub-directory in a run dir
    python scripts/plot_dynamics.py --run-dir artifacts/round1/run_20260411_091922

# Explicit snapshot file + output path
    python scripts/plot_dynamics.py \\
        --snapshot artifacts/round1/run_20260411_091922/fixed_peer_calibrated/competence_snapshots.jsonl \\
        --out artifacts/round1_convergence_dynamics.png

# Compare two methods side-by-side (each gets its own axes row)
    python scripts/plot_dynamics.py \\
        --run-dir artifacts/round1/run_20260411_091922 \\
        --methods fixed_peer_calibrated fixed_self_calibrated \\
        --out artifacts/round1_convergence_dynamics.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional-but-expected dependencies — provide a friendly error if missing.
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")  # headless rendering; must be set before pyplot import
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    from matplotlib.lines import Line2D
except ImportError:
    print(
        "[plot_dynamics] ERROR: matplotlib is not installed.\n"
        "  Run:  pip install matplotlib\n",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    np = None  # gracefully fall back to pure-Python smoothing

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NODES = ["decomposer", "evidence_seeker", "verifier", "synthesizer"]

# A carefully chosen palette that reads well in print and on screen.
NODE_COLORS = {
    "decomposer":    "#E06C75",   # rose-red
    "evidence_seeker": "#61AFEF", # sky-blue
    "verifier":      "#98C379",   # sage-green
    "synthesizer":   "#C678DD",   # lavender-purple
}

NODE_LABELS = {
    "decomposer":    "Decomposer",
    "evidence_seeker": "Evidence Seeker",
    "verifier":      "Verifier",
    "synthesizer":   "Synthesizer",
}

METHOD_TITLES = {
    "fixed_peer_calibrated":             "Peer-Calibrated (proposed)",
    "fixed_self_calibrated":             "Self-Calibrated (ablation)",
    "fixed_self_claim":                  "Self-Claim (no calibration)",
    "fixed_static_roles":                "Static Roles (no routing)",
    "central_orchestrator":              "Central Orchestrator",
    "central_orchestrator_with_reflection": "Central Orchestrator + Reflection",
    "single_agent":                      "Single Agent",
    "fixed_random_forward":              "Random Forward",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_snapshots(path: Path) -> list[dict]:
    """Read a competence_snapshots.jsonl file into a list of dicts."""
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def _extract_series(rows: list[dict]) -> dict[str, list[float]]:
    """
    Extract per-node self-competence trajectory from snapshot rows.

    We track only the ``post_sample`` snapshots because those represent
    the stable accumulated state after each full sample has been processed.
    This gives us exactly one data-point per sample per accepted node —
    the time-series we want to plot.

    Returns
    -------
    dict mapping node_name -> [competence_value_after_sample_0, ..., sample_N]
    """
    # Collect post-sample signals per task_id order
    # First pass: unique task_ids (ordered)
    task_order: dict[str, int] = {}
    for row in rows:
        tid = row["task_id"]
        if tid not in task_order:
            task_order[tid] = len(task_order)

    # Second pass: for each post_sample row grab the accepted node's own skill value
    series: dict[str, dict[int, float]] = {n: {} for n in NODES}
    for row in rows:
        if row.get("hop_index") != "post_sample":
            continue
        node = row.get("node_name", "")
        if node not in NODES:
            continue
        comp_after = row.get("competence_after", {})
        # self-competence = the node's own slot in its competence dict
        self_val = comp_after.get(node)
        if self_val is None:
            continue
        idx = task_order.get(row["task_id"], -1)
        if idx >= 0:
            series[node][idx] = float(self_val)

    # Convert to lists aligned to sequential sample indices
    max_idx = len(task_order)
    result: dict[str, list[float]] = {}
    for node in NODES:
        vals: list[float] = []
        last = 0.5  # default initial value
        for i in range(max_idx):
            if i in series[node]:
                last = series[node][i]
            vals.append(last)
        result[node] = vals
    return result


def _smooth(values: list[float], window: int = 8) -> list[float]:
    """Simple causal moving-average smoothing (no numpy required)."""
    if np is not None:
        kernel = np.ones(window) / window
        padded = np.pad(values, (window - 1, 0), mode="edge")
        return list(np.convolve(padded, kernel, mode="valid"))
    # Pure-Python fallback
    out = []
    buf: list[float] = []
    for v in values:
        buf.append(v)
        if len(buf) > window:
            buf.pop(0)
        out.append(sum(buf) / len(buf))
    return out


# ---------------------------------------------------------------------------
# Plotting engine
# ---------------------------------------------------------------------------

def _annotate_phases(ax, n_samples: int) -> None:
    """Add light-grey shaded regions to highlight early turbulence vs. convergence."""
    turbulence_end = min(40, n_samples // 4)
    convergence_start = min(80, n_samples // 2)
    if turbulence_end > 0:
        ax.axvspan(0, turbulence_end, color="#F5A623", alpha=0.07, zorder=0, label=None)
        ax.text(
            turbulence_end / 2, 0.06,
            "Early\nTurbulence",
            ha="center", va="bottom", fontsize=7, color="#B8860B",
            fontstyle="italic",
        )
    if convergence_start < n_samples:
        ax.axvspan(convergence_start, n_samples, color="#50FA7B", alpha=0.05, zorder=0, label=None)
        ax.text(
            convergence_start + (n_samples - convergence_start) / 2, 0.06,
            "Convergence\nZone",
            ha="center", va="bottom", fontsize=7, color="#2E7D32",
            fontstyle="italic",
        )


def plot_method(
    ax: "plt.Axes",
    series: dict[str, list[float]],
    method_name: str,
    smooth_window: int = 8,
) -> None:
    """Draw all node traces onto a single axes."""
    n = max((len(v) for v in series.values()), default=0)
    if n == 0:
        ax.set_title(f"{METHOD_TITLES.get(method_name, method_name)}\n(no data)", fontsize=10)
        return

    x = list(range(n))
    _annotate_phases(ax, n)

    for node in NODES:
        raw = series.get(node, [])
        if not raw:
            continue
        color = NODE_COLORS[node]
        label = NODE_LABELS[node]
        # Raw trace — very faint
        ax.plot(x[: len(raw)], raw, color=color, linewidth=0.6, alpha=0.25, zorder=2)
        # Smoothed trace — prominent
        smoothed = _smooth(raw, window=smooth_window)
        ax.plot(
            x[: len(smoothed)], smoothed,
            color=color, linewidth=2.0, alpha=0.92, label=label, zorder=3,
        )
        # Mark final value
        final_x = len(smoothed) - 1
        final_y = smoothed[-1]
        ax.annotate(
            f"{final_y:.2f}",
            xy=(final_x, final_y),
            xytext=(4, 0), textcoords="offset points",
            fontsize=7, color=color, va="center",
        )

    # Threshold reference line (peer_calibrated threshold)
    ax.axhline(0.62, color="#ABB2BF", linewidth=0.9, linestyle="--", alpha=0.6, zorder=1)
    ax.text(n * 0.02, 0.625, "threshold=0.62", fontsize=6.5, color="#ABB2BF")

    ax.set_xlim(0, n)
    ax.set_ylim(0.0, 1.00)
    ax.set_xlabel("Sample Index", fontsize=9)
    ax.set_ylabel("Self-Competence Estimate", fontsize=9)
    ax.set_title(METHOD_TITLES.get(method_name, method_name), fontsize=10, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
    ax.grid(axis="y", linewidth=0.5, alpha=0.4, color="#3E4451")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)


def build_figure(
    method_data: dict[str, dict[str, list[float]]],
    output_path: Path,
    smooth_window: int = 8,
) -> None:
    """Render and save the final figure."""
    n_methods = len(method_data)
    fig_height = 4.2 * n_methods + 1.0
    fig, axes = plt.subplots(
        n_methods, 1,
        figsize=(10, fig_height),
        squeeze=False,
        facecolor="#282C34",
    )
    fig.subplots_adjust(hspace=0.55, top=0.93, bottom=0.06, left=0.09, right=0.97)

    # Dark background theme — publication-adjacent
    plt.rcParams.update({
        "axes.facecolor":  "#21252B",
        "axes.edgecolor":  "#3E4451",
        "axes.labelcolor": "#ABB2BF",
        "xtick.color":     "#ABB2BF",
        "ytick.color":     "#ABB2BF",
        "text.color":      "#ABB2BF",
        "font.family":     "DejaVu Sans",
        "figure.facecolor":"#282C34",
    })

    for ax_row, (method_name, series) in zip(axes, method_data.items()):
        ax = ax_row[0]
        plot_method(ax, series, method_name, smooth_window=smooth_window)

    # Shared legend at the top of the figure
    legend_handles = [
        Line2D([0], [0], color=NODE_COLORS[n], linewidth=2.5, label=NODE_LABELS[n])
        for n in NODES
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=len(NODES),
        fontsize=9,
        framealpha=0.0,
        labelcolor="#ABB2BF",
        bbox_to_anchor=(0.5, 0.98),
    )

    # Super-title
    fig.suptitle(
        "Competence Convergence Dynamics — Round 1",
        fontsize=13, fontweight="bold", color="#E5C07B", y=1.00,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[plot_dynamics] Saved → {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_snapshot(run_dir: Path, method: str) -> Path | None:
    candidate = run_dir / method / "competence_snapshots.jsonl"
    return candidate if candidate.is_file() else None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Plot competence convergence dynamics from a Round-1 run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--run-dir", type=Path, default=None,
        help="Path to a run directory (e.g. artifacts/round1/run_20260411_091922). "
             "The script will look for method sub-directories inside.",
    )
    p.add_argument(
        "--snapshot", type=Path, default=None,
        help="Explicit path to a single competence_snapshots.jsonl file.",
    )
    p.add_argument(
        "--snapshots", nargs="+", default=None, metavar="PATH[:LABEL]",
        help=(
            "One or more explicit snapshot paths, optionally labeled with :LABEL. "
            "Paths from different run dirs are merged into a single comparison figure. "
            "Example: "
            "--snapshots run_A/fixed_peer_calibrated/competence_snapshots.jsonl:peer "
            "run_B/fixed_self_calibrated/competence_snapshots.jsonl:self"
        ),
    )
    p.add_argument(
        "--methods", nargs="+", default=None,
        help="Which method sub-directories to include when --run-dir is given. "
             "Defaults to all found directories with a competence_snapshots.jsonl.",
    )
    p.add_argument(
        "--out", type=Path,
        default=Path("artifacts/round1_convergence_dynamics.png"),
        help="Output PNG path (default: artifacts/round1_convergence_dynamics.png).",
    )
    p.add_argument(
        "--smooth", type=int, default=8,
        help="Moving-average smoothing window in samples (default: 8).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Resolve repo root (two levels up from scripts/)
    repo_root = Path(__file__).resolve().parent.parent

    def abs_path(p: Path) -> Path:
        return p if p.is_absolute() else repo_root / p

    method_data: dict[str, dict[str, list[float]]] = {}

    if args.snapshots:
        # ── Multi-snapshot mode: load each file, derive label from path or :LABEL suffix ──
        for entry in args.snapshots:
            if ":" in entry and not Path(entry.split(":")[0]).is_file():
                # Windows path safety: only split on last colon that is NOT a drive letter
                parts = entry.rsplit(":", 1)
            else:
                parts = entry.split(":", 1)  # PATH:LABEL (label is optional)
            raw_path = parts[0]
            label_override = parts[1].strip() if len(parts) > 1 else None
            snap_path = abs_path(Path(raw_path))
            if not snap_path.is_file():
                print(f"[plot_dynamics] WARNING: snapshot not found — skipping: {snap_path}", file=sys.stderr)
                continue
            # Determine label: explicit override > parent dir name (method name)
            method_label = label_override if label_override else snap_path.parent.name
            rows = _load_snapshots(snap_path)
            series = _extract_series(rows)
            method_data[method_label] = series
            print(f"[plot_dynamics] Loaded {len(rows):,} rows → label='{method_label}'  ({snap_path.relative_to(repo_root)})")

    elif args.snapshot:
        snap_path = abs_path(args.snapshot)
        if not snap_path.is_file():
            print(f"[plot_dynamics] ERROR: snapshot not found: {snap_path}", file=sys.stderr)
            sys.exit(1)
        method_name = snap_path.parent.name  # derive from directory name
        rows = _load_snapshots(snap_path)
        series = _extract_series(rows)
        method_data[method_name] = series

    elif args.run_dir:
        run_dir = abs_path(args.run_dir)
        if not run_dir.is_dir():
            print(f"[plot_dynamics] ERROR: run_dir not found: {run_dir}", file=sys.stderr)
            sys.exit(1)
        # Discover method sub-directories
        if args.methods:
            candidates = [run_dir / m for m in args.methods]
        else:
            candidates = sorted(
                d for d in run_dir.iterdir()
                if d.is_dir() and (d / "competence_snapshots.jsonl").is_file()
            )
        if not candidates:
            print(
                f"[plot_dynamics] ERROR: no competence_snapshots.jsonl found in {run_dir}",
                file=sys.stderr,
            )
            sys.exit(1)
        for method_dir in candidates:
            snap_path = method_dir / "competence_snapshots.jsonl"
            if not snap_path.is_file():
                print(f"[plot_dynamics] WARNING: skipping {method_dir.name} — no snapshot file.")
                continue
            rows = _load_snapshots(snap_path)
            series = _extract_series(rows)
            method_data[method_dir.name] = series
            print(f"[plot_dynamics] Loaded {len(rows):,} rows from {snap_path.relative_to(repo_root)}")
    else:
        print(
            "[plot_dynamics] ERROR: provide one of --run-dir, --snapshot, or --snapshots.\n"
            "  Example: python scripts/plot_dynamics.py --run-dir artifacts/round1/run_20260411_091922",
            file=sys.stderr,
        )
        sys.exit(1)

    if not method_data:
        print("[plot_dynamics] ERROR: no data to plot.", file=sys.stderr)
        sys.exit(1)

    out_path = abs_path(args.out)
    build_figure(method_data, out_path, smooth_window=args.smooth)


if __name__ == "__main__":
    main()
