"""3-shard × 200-sample paired Stage-1 vs Stage-2 driver (E-006 partial).

For each shard k ∈ {0, 1, 2}, runs:
  - Stage-1 ``fixed_peer_calibrated``
  - Stage-2 ``edo_stage2_chain``

on samples ``[k*200 : (k+1)*200]`` of fullval. Then prints the per-shard
ΔF1 + cross-shard mean ± std so we have a 3-replicate paired CI without
spending fullval-scale tokens.

Total runs: 6 × ~200 samples × ~5000 tokens = ~6M tokens ≈ $2-3 (gpt-4.1-mini).
Wall time: 6 × 5 min = 30 min serial; we use serial to avoid newapi rate-limits.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
sys.path.insert(0, str(_REPO_ROOT / "workspace"))

import idea04_paths  # noqa: E402
from idea04_core.runner import RoundRunner  # noqa: E402

DEFAULT_SAMPLES_JSONL = (
    _REPO_ROOT
    / "artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl"
)


def _load_shard(path: Path, start: int, n: int) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i < start:
                continue
            if i >= start + n:
                break
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _run_one(method_name: str, samples: list[dict], shard_idx: int, run_root: Path,
             config: dict, workers: int) -> dict:
    method_dir = run_root / f"shard{shard_idx}" / method_name
    method_dir.mkdir(parents=True, exist_ok=True)
    cfg = dict(config)
    cfg["method_name"] = method_name
    cfg["sample_size"] = len(samples)
    cfg["n_workers"] = workers
    cfg["progress_every"] = max(1, len(samples) // 5)
    runner = RoundRunner(
        topology=cfg.get("topology", "chain"),
        max_handoff=int(cfg.get("max_handoff", 4)),
    )
    metrics = runner.run(method_name, samples, cfg, method_dir)
    return metrics


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n-per-shard", type=int, default=200)
    p.add_argument("--n-shards", type=int, default=3)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--config", default="configs/round2_gpt41mini_chain200.yaml")
    p.add_argument("--artifacts-root", default="artifacts/round2_gpt41mini_3shard_paired")
    args = p.parse_args()

    os.environ.pop("LLM_BACKEND", None)
    os.environ.pop("LLM_BASE_URL", None)
    os.environ.pop("LLM_API_KEY", None)

    cfg = idea04_paths.merge_experiment_config(_REPO_ROOT / args.config)

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
    run_root = _REPO_ROOT / args.artifacts_root / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    print(f"[3shard] run_root = {run_root}")

    methods = ["fixed_peer_calibrated", "edo_stage2_chain"]
    rows = []
    for k in range(args.n_shards):
        start = k * args.n_per_shard
        samples = _load_shard(DEFAULT_SAMPLES_JSONL, start, args.n_per_shard)
        print(f"\n[3shard] shard {k}: samples [{start}:{start + args.n_per_shard}] = {len(samples)} loaded")
        per_shard: dict[str, dict] = {}
        for method in methods:
            print(f"[3shard] shard {k}: running {method}...")
            metrics = _run_one(method, samples, k, run_root, cfg, args.workers)
            per_shard[method] = metrics
            print(f"[3shard] shard {k} {method}: F1={metrics['answer_f1']:.4f} "
                  f"EM={metrics['answer_em']:.4f} tokens={metrics['api_total_tokens_per_sample']:.0f}")
        rows.append({
            "shard": k,
            "n": len(samples),
            "stage1_f1": per_shard["fixed_peer_calibrated"]["answer_f1"],
            "stage2_f1": per_shard["edo_stage2_chain"]["answer_f1"],
            "stage1_em": per_shard["fixed_peer_calibrated"]["answer_em"],
            "stage2_em": per_shard["edo_stage2_chain"]["answer_em"],
            "stage1_tokens": per_shard["fixed_peer_calibrated"]["api_total_tokens_per_sample"],
            "stage2_tokens": per_shard["edo_stage2_chain"]["api_total_tokens_per_sample"],
            "delta_f1": per_shard["edo_stage2_chain"]["answer_f1"] - per_shard["fixed_peer_calibrated"]["answer_f1"],
            "delta_em": per_shard["edo_stage2_chain"]["answer_em"] - per_shard["fixed_peer_calibrated"]["answer_em"],
            "delta_tokens_pct": (
                per_shard["edo_stage2_chain"]["api_total_tokens_per_sample"]
                - per_shard["fixed_peer_calibrated"]["api_total_tokens_per_sample"]
            ) / per_shard["fixed_peer_calibrated"]["api_total_tokens_per_sample"] * 100.0,
        })

    # ── Summary ──
    delta_f1s = [r["delta_f1"] for r in rows]
    delta_ems = [r["delta_em"] for r in rows]
    delta_tokens_pcts = [r["delta_tokens_pct"] for r in rows]
    summary = {
        "n_shards": len(rows),
        "n_per_shard": args.n_per_shard,
        "delta_f1_per_shard": delta_f1s,
        "delta_em_per_shard": delta_ems,
        "delta_tokens_pct_per_shard": delta_tokens_pcts,
        "delta_f1_mean": statistics.mean(delta_f1s),
        "delta_f1_std": statistics.stdev(delta_f1s) if len(delta_f1s) > 1 else 0.0,
        "delta_em_mean": statistics.mean(delta_ems),
        "delta_em_std": statistics.stdev(delta_ems) if len(delta_ems) > 1 else 0.0,
        "delta_tokens_pct_mean": statistics.mean(delta_tokens_pcts),
        "delta_tokens_pct_std": statistics.stdev(delta_tokens_pcts) if len(delta_tokens_pcts) > 1 else 0.0,
        "per_shard_rows": rows,
    }
    summary_path = run_root / "shard_paired_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n=== 3-SHARD PAIRED SUMMARY ===")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_shard_rows"}, indent=2))
    print(f"\nSaved → {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
