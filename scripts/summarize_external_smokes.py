"""Summarize all external-baseline + TCPB smoke metrics into a single table.

Scientist S-121/S-122/S-123 write-ups can import from here or run this as a
CLI to produce a LaTeX-ready comparison row for `article/latex/edo_paper.tex`
(or the `_pending_data_templates.tex` placeholder being managed by scientist).

Usage::

    python scripts/summarize_external_smokes.py            # human-readable table
    python scripts/summarize_external_smokes.py --tex      # LaTeX tabular rows
    python scripts/summarize_external_smokes.py --json     # machine-readable JSON list

Reads from:
  - artifacts/external_baselines/mad/r41_smoke_*/metrics.json
  - artifacts/external_baselines/marag/r41_smoke_*/metrics.json
  - artifacts/external_baselines/reagent/r41c_w3_n5/metrics.json (R41c result)
  - artifacts/external_baselines/{mad,marag,reagent}/r41b_n50*/metrics.json (n=50 batches; * may be empty)
  - artifacts/round2_gpt41mini_stage2_fullval/run_*_seed42/edo_stage2_chain/metrics.json
  - artifacts/round2_gpt41mini_stage2_fullval/run_*_seed42/fixed_peer_calibrated/metrics.json

Per the R41/R41b/R41c phase-block outputs; no LLM calls; no writes to LaTeX.
Designed for the scientist workflow described in `four-role-todo-workflow.mdc §5`.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class _Row:
    system: str
    path: Path
    sample_count: int = 0
    answer_em: float = 0.0
    answer_f1: float = 0.0
    wall_s: float = 0.0
    model: str = ""
    notes: list[str] = field(default_factory=list)


def _load_metrics(path: Path) -> _Row | None:
    if not path.is_file():
        return None
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[summarize] skip unparseable {path}: {exc}", file=sys.stderr)
        return None
    host = data.get("host") or data.get("method_name") or path.parts[-3]
    row = _Row(
        system=str(host),
        path=path,
        sample_count=int(data.get("sample_count", 0) or 0),
        answer_em=float(data.get("answer_em", 0.0) or 0.0),
        answer_f1=float(data.get("answer_f1", 0.0) or 0.0),
        wall_s=float(data.get("wall_s", 0.0) or 0.0),
        model=str(data.get("model", "unknown")),
        notes=list(data.get("notes", [])),
    )
    return row


def collect_rows() -> list[_Row]:
    """Scan known baseline output locations + TCPB fullval dirs for metrics.json."""
    rows: list[_Row] = []

    # External baselines (current R41/R41b/R41c/R41d outputs)
    baseline_globs = [
        "artifacts/external_baselines/mad/r41_smoke_*/metrics.json",
        "artifacts/external_baselines/marag/r41_smoke_*/metrics.json",
        "artifacts/external_baselines/reagent/r41c_w3_n5/metrics.json",
        "artifacts/external_baselines/mad/r41b_n50*/metrics.json",
        "artifacts/external_baselines/marag/r41b_n50*/metrics.json",
        "artifacts/external_baselines/reagent/r41b_n50*/metrics.json",
        # R41d MuSiQue matrix outputs (5 systems under one timestamped dir)
        "artifacts/matrix/musique_n50_*/tcpb_stage2/metrics.json",
        "artifacts/matrix/musique_n50_*/tcpb_stage1/metrics.json",
        "artifacts/matrix/musique_n50_*/mad/metrics.json",
        "artifacts/matrix/musique_n50_*/marag/metrics.json",
        "artifacts/matrix/musique_n50_*/reagent/metrics.json",
    ]
    for gstr in baseline_globs:
        for p in sorted(_REPO_ROOT.glob(gstr)):
            row = _load_metrics(p)
            if row is not None:
                # Tag matrix rows with dataset suffix
                if "/matrix/musique_n50_" in str(p):
                    row.system = f"{row.system} [MuSiQue]"
                elif "hotpotqa" in str(row.system).lower() or "r41" in str(p):
                    row.system = f"{row.system} [HotpotQA]"
                rows.append(row)

    # TCPB fullval reference (seed=42/43/44 metrics.json when they land)
    tcpb_globs = [
        "artifacts/round2_gpt41mini_stage2_fullval/run_*_seed42/edo_stage2_chain/metrics.json",
        "artifacts/round2_gpt41mini_stage2_fullval/run_*_seed42/fixed_peer_calibrated/metrics.json",
        "artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/edo_stage2_chain/metrics.json",
        "artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/fixed_peer_calibrated/metrics.json",
        "artifacts/round2_gpt41mini_stage2_fullval/run_*_seed44/edo_stage2_chain/metrics.json",
        "artifacts/round2_gpt41mini_stage2_fullval/run_*_seed44/fixed_peer_calibrated/metrics.json",
    ]
    for gstr in tcpb_globs:
        for p in sorted(_REPO_ROOT.glob(gstr)):
            row = _load_metrics(p)
            if row is not None:
                # Mark system with run-dir hint for seed disambiguation
                row.system = f"TCPB {p.parts[-3]} {p.parts[-2]}"
                rows.append(row)

    return rows


def render_table(rows: list[_Row]) -> str:
    """Human-readable table."""
    out = []
    out.append(f"{'SYSTEM':<58} {'N':>6} {'EM':>7} {'F1':>7} {'WALL':>8} {'MODEL':<16}")
    out.append("-" * 110)
    for r in rows:
        out.append(
            f"{r.system[:58]:<58} {r.sample_count:>6d} {r.answer_em:>7.3f} "
            f"{r.answer_f1:>7.3f} {r.wall_s:>7.1f}s {r.model[:16]:<16}"
        )
    return "\n".join(out)


def render_tex(rows: list[_Row]) -> str:
    """LaTeX tabular row per system. Caller embeds inside a \\begin{tabular}."""
    out = [r"% Auto-generated by scripts/summarize_external_smokes.py"]
    out.append(r"% system & n & EM & F1 & wall (s) & model")
    for r in rows:
        sys_short = r.system.split(" (")[0][:40]
        sys_escaped = sys_short.replace("&", r"\&").replace("_", r"\_")
        out.append(
            f"{sys_escaped} & {r.sample_count} & {r.answer_em:.3f} & "
            f"{r.answer_f1:.3f} & {r.wall_s:.1f} & {r.model.replace('_', '-')} \\\\"
        )
    return "\n".join(out)


def render_json(rows: list[_Row]) -> str:
    return json.dumps(
        [
            {
                "system": r.system,
                "sample_count": r.sample_count,
                "answer_em": r.answer_em,
                "answer_f1": r.answer_f1,
                "wall_s": r.wall_s,
                "model": r.model,
                "path": str(r.path.relative_to(_REPO_ROOT)) if r.path else "",
                "notes": r.notes,
            }
            for r in rows
        ],
        indent=2,
        ensure_ascii=False,
    )


def main() -> int:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group()
    group.add_argument("--tex", action="store_true", help="LaTeX tabular rows")
    group.add_argument("--json", action="store_true", help="machine-readable JSON list")
    args = p.parse_args()

    rows = collect_rows()
    if not rows:
        print("[summarize] no metrics.json found in any of the known locations.",
              file=sys.stderr)
        return 1
    rows.sort(key=lambda r: (r.sample_count, r.system))

    if args.tex:
        print(render_tex(rows))
    elif args.json:
        print(render_json(rows))
    else:
        print(render_table(rows))
        print()
        print(f"# found {len(rows)} metrics.json files; sorted by (sample_count, system)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
