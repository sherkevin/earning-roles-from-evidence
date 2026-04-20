"""E-017 driver: Stage-2 vs Stage-1 paired fullval, **single seed per invocation**.

Per ``[u_020_stage2_fullval_3seed_launch_20260420]`` E-017 task spec,
we need 3 seeds × 2 methods = 6 batches of 7405 samples. This driver runs
ONE (seed, method) batch per invocation so we can launch them as independent
background processes and parallelise.

Usage::

    python scripts/run_e017_fullval_seed.py --seed 42 --method edo_stage2_chain
    python scripts/run_e017_fullval_seed.py --seed 42 --method fixed_peer_calibrated

Each invocation:
  1. Pre-flight: confirm newapi resolvable + RNG seeded
  2. Run RoundRunner on the **full 7405 fullval samples** (deterministic order
     — head-N is paired across seeds because the input file is fixed)
  3. validate_logs.py on the new run_dir; bail with non-zero on FAIL
  4. Append a single-line cost ledger row to
     ``artifacts/round2_gpt41mini_stage2_fullval/cost_ledger.jsonl``

Per pinned C-6: same question-id list across seeds; we do NOT shuffle samples.
The "seed" only varies the Python `random` state used by `fixed_random_forward`
and the `ThreadPoolExecutor` task pickup order.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
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
DEFAULT_CONFIG = _REPO_ROOT / "configs/round2_gpt41mini_chain200.yaml"

ALLOWED_METHODS = ("edo_stage2_chain", "fixed_peer_calibrated")

OUT_ROOT = _REPO_ROOT / "artifacts/round2_gpt41mini_stage2_fullval"
COST_LEDGER = OUT_ROOT / "cost_ledger.jsonl"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--method", required=True, choices=ALLOWED_METHODS)
    p.add_argument("--n", type=int, default=7405,
                   help="number of samples to run (default: full 7405 fullval)")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--samples-jsonl", default=str(DEFAULT_SAMPLES_JSONL))
    p.add_argument(
        "--run-dir",
        default=None,
        help=(
            "Optional path to an EXISTING run_dir to resume from. When set, "
            "skips auto-timestamped dir creation and points runner at this "
            "exact directory; runner.run() detects _ckpt_preds.jsonl and "
            "resumes. Used for cross-machine migration (E-017 R26+ on server). "
            "Path may be absolute, or relative to repo root."
        ),
    )
    args = p.parse_args()

    os.environ.pop("LLM_BACKEND", None)
    os.environ.pop("LLM_BASE_URL", None)
    os.environ.pop("LLM_API_KEY", None)

    random.seed(args.seed)

    rows: list[dict] = []
    with Path(args.samples_jsonl).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
            if len(rows) >= args.n:
                break
    print(f"[e017] seed={args.seed} method={args.method} n={len(rows)}")

    cfg = idea04_paths.merge_experiment_config(Path(args.config))
    cfg["method_name"] = args.method
    cfg["sample_size"] = len(rows)
    cfg["n_workers"] = args.workers
    cfg["progress_every"] = max(50, args.n // 20)

    if args.run_dir:
        method_dir = Path(args.run_dir)
        if not method_dir.is_absolute():
            method_dir = (_REPO_ROOT / method_dir).resolve()
        method_dir.mkdir(parents=True, exist_ok=True)
        print(f"[e017] resuming run_dir = {method_dir}")
    else:
        run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
        run_dir_name = f"{run_id}_seed{args.seed}"
        method_dir = OUT_ROOT / run_dir_name / args.method
        method_dir.mkdir(parents=True, exist_ok=True)
        print(f"[e017] run_dir = {method_dir}")

    runner = RoundRunner(
        topology=cfg.get("topology", "chain"),
        max_handoff=int(cfg.get("max_handoff", 4)),
    )

    t0 = time.time()
    metrics = runner.run(args.method, rows, cfg, method_dir)
    elapsed_s = time.time() - t0

    print("\n=== METRICS ===")
    print(json.dumps(metrics, indent=2))
    print(f"\n[e017] elapsed = {elapsed_s:.1f} s ({elapsed_s/60:.1f} min)")

    # validate
    print("\n[e017] validate_logs...")
    rc = subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts/validate_logs.py"), str(method_dir)],
        cwd=str(_REPO_ROOT),
    ).returncode
    if rc != 0:
        print(f"[e017] FATAL: validate_logs failed exit={rc}", file=sys.stderr)
        return rc

    # cost ledger
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    ledger_row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed,
        "method": args.method,
        "run_dir": str(method_dir.relative_to(_REPO_ROOT)),
        "n_samples": metrics["sample_count"],
        "elapsed_s": round(elapsed_s, 1),
        "answer_f1": metrics["answer_f1"],
        "answer_em": metrics["answer_em"],
        "mean_handoff_count": metrics["mean_handoff_count"],
        "api_total_tokens_per_sample": metrics["api_total_tokens_per_sample"],
        "estimated_cost_usd": round(
            metrics["sample_count"] *
            (
                metrics["api_prompt_tokens_per_sample"] * 0.40e-6
                + metrics["api_completion_tokens_per_sample"] * 1.60e-6
            ),
            3,
        ),
    }
    with COST_LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ledger_row, ensure_ascii=False) + "\n")
    print(f"[e017] cost ledger appended: {COST_LEDGER}")
    print(json.dumps(ledger_row, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
