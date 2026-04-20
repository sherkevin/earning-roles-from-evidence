"""Run Stage-1 ``fixed_peer_calibrated`` on the EXACT same first-200 fullval
samples that the Stage-2 200-sample batch used, so we can compute a paired
ΔF1 between Stage-2 (`edo_stage2_chain`) and the Stage-1 backbone-equal control.

Both use gpt-4.1-mini via newapi; same chain topology; same max_handoff=4.
"""

from __future__ import annotations

import argparse
import json
import os
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


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--method", default="fixed_peer_calibrated")
    p.add_argument("--config", default="configs/round2_gpt41mini_chain200.yaml")
    p.add_argument(
        "--artifacts-root",
        default="artifacts/round2_gpt41mini_stage1_pair_for_stage2",
    )
    args = p.parse_args()

    os.environ.pop("LLM_BACKEND", None)
    os.environ.pop("LLM_BASE_URL", None)
    os.environ.pop("LLM_API_KEY", None)

    rows = []
    with DEFAULT_SAMPLES_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
            if len(rows) >= args.n:
                break
    print(f"[stage1_pair] {len(rows)} samples loaded")

    cfg = idea04_paths.merge_experiment_config(_REPO_ROOT / args.config)
    cfg["method_name"] = args.method
    cfg["sample_size"] = len(rows)
    cfg["n_workers"] = args.workers
    cfg["progress_every"] = max(1, args.n // 10) if args.n >= 10 else 1

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
    run_root = _REPO_ROOT / args.artifacts_root / run_id / args.method
    run_root.mkdir(parents=True, exist_ok=True)
    print(f"[stage1_pair] run_dir = {run_root}")

    runner = RoundRunner(
        topology=cfg.get("topology", "chain"),
        max_handoff=int(cfg.get("max_handoff", 4)),
    )
    metrics = runner.run(args.method, rows, cfg, run_root)
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
