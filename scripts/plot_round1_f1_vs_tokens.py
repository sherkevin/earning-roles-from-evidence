"""
Plot answer_f1 vs token_cost_per_sample for every method under a single run_* directory.

Example:
  python scripts/plot_round1_f1_vs_tokens.py \\
    --run-dir artifacts/round1/run_20260411_102202 \\
    --out artifacts/round1_v3_f1_vs_tokens_run_20260411_102202.png

  # Only v3 main-table methods (excludes e.g. single_agent under the same run dir):
  python scripts/plot_round1_f1_vs_tokens.py \\
    --run-dir artifacts/round1/run_20260411_102202 \\
    --methods fixed_static_roles,fixed_self_claim,fixed_peer_calibrated,central_orchestrator,central_orchestrator_with_reflection,fixed_self_calibrated \\
    --out artifacts/round1_v3_f1_vs_tokens_run_20260411_102202.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    print("[plot_round1_f1_vs_tokens] ERROR: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument(
        "--methods",
        default=None,
        help="Comma-separated subdir names; default = all dirs that contain metrics.json.",
    )
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(f"[plot_round1_f1_vs_tokens] ERROR: not a directory: {run_dir}", file=sys.stderr)
        sys.exit(1)

    allow = None
    if args.methods:
        allow = {m.strip() for m in args.methods.split(",") if m.strip()}

    points: list[tuple[str, float, float]] = []
    for sub in sorted(run_dir.iterdir()):
        if not sub.is_dir():
            continue
        name = sub.name
        if allow is not None and name not in allow:
            continue
        mj = sub / "metrics.json"
        if not mj.is_file():
            continue
        data = json.loads(mj.read_text(encoding="utf-8"))
        f1 = float(data["answer_f1"])
        tok = float(data["token_cost_per_sample"])
        points.append((name, f1, tok))

    if not points:
        print(f"[plot_round1_f1_vs_tokens] ERROR: no metrics.json under {run_dir}", file=sys.stderr)
        sys.exit(1)

    xs = [t for _, _, t in points]
    ys = [f for _, f, _ in points]
    labels = [n for n, _, _ in points]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.scatter(xs, ys, s=80, alpha=0.85, c="#3B82F6", edgecolors="#1E3A5F", linewidths=0.8)
    for name, f1, tok in points:
        ax.annotate(
            name.replace("_", "\n"),
            (tok, f1),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=7,
            ha="left",
        )
    ax.set_xlabel("token_cost_per_sample (heuristic)")
    ax.set_ylabel("answer_f1")
    ax.set_title(f"F1 vs tokens — {run_dir.name}")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=160)
    plt.close(fig)
    print(f"[plot_round1_f1_vs_tokens] wrote {args.out.resolve()}")


if __name__ == "__main__":
    main()
