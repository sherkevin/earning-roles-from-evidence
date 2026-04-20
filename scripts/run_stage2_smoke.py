"""Stage-2 (E-005) sanity-probe runner.

Runs the new ``edo_stage2_chain`` method against N samples drawn from a
canonical ``raw_inputs.jsonl``, routing through the **newapi** primary endpoint
(per pinned C-1 + USER_TODO §A U-EXEC-006). Confirms the integration emits the
3 new jsonl files, the dual-track competence schema, and a sane F1 / token
cost — without committing to a fullval-scale batch.

Usage::

    python scripts/run_stage2_smoke.py --n 1
    python scripts/run_stage2_smoke.py --n 200 --workers 8 \
        --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl

The script writes its run_dir under ``artifacts/round2_gpt41mini_stage2/run_<TS>/edo_stage2_chain/``
and finishes by invoking ``scripts/validate_logs.py`` on the new dir.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

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


def load_samples(path: Path, n: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
            if n is not None and len(rows) >= n:
                break
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run Stage-2 (edo_stage2_chain) sanity smoke.")
    p.add_argument("--n", type=int, default=1, help="number of samples to run (default 1)")
    p.add_argument(
        "--samples-jsonl",
        default=str(DEFAULT_SAMPLES_JSONL),
        help="raw_inputs.jsonl source (default: fullval canonical sample set)",
    )
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--workers", type=int, default=1)
    p.add_argument(
        "--artifacts-root",
        default="artifacts/round2_gpt41mini_stage2",
        help="parent dir for the new run_<TS>/ tree",
    )
    p.add_argument("--no-validate", action="store_true")
    args = p.parse_args(argv)

    # Force newapi backend (per U-EXEC-006). Equivalent to LLM_BACKEND=oversea
    # with the newapi base_url; llm_providers.py routes via the configured
    # newapi block automatically when LLM_BACKEND is unset and newapi is PRIMARY.
    # We do NOT override LLM_BASE_URL/LLM_API_KEY: we want llm_providers.py to
    # read them straight from configs/llm.json so resolved_model() is faithful.
    os.environ.pop("LLM_BACKEND", None)  # let auto-routing pick newapi
    os.environ.pop("LLM_BASE_URL", None)
    os.environ.pop("LLM_API_KEY", None)

    samples = load_samples(Path(args.samples_jsonl), args.n)
    if not samples:
        print(f"ERROR: no samples loaded from {args.samples_jsonl}", file=sys.stderr)
        return 2
    print(f"[stage2_smoke] loaded {len(samples)} samples from {Path(args.samples_jsonl).name}")

    config = idea04_paths.merge_experiment_config(Path(args.config))
    config["method_name"] = "edo_stage2_chain"
    config["sample_size"] = len(samples)
    config["n_workers"] = args.workers
    config["progress_every"] = max(1, args.n // 10) if args.n >= 10 else 1

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
    run_root = _REPO_ROOT / args.artifacts_root / run_id
    method_dir = run_root / "edo_stage2_chain"
    method_dir.mkdir(parents=True, exist_ok=True)
    print(f"[stage2_smoke] run_dir = {method_dir}")

    runner = RoundRunner(
        topology=config.get("topology", "chain"),
        max_handoff=int(config.get("max_handoff", 4)),
    )
    metrics = runner.run(
        method_name="edo_stage2_chain",
        samples=samples,
        run_config=config,
        run_dir=method_dir,
    )
    print(json.dumps(metrics, indent=2))

    # Spot-check the 3 new Stage-2 jsonls
    for fname in ("task_tree.jsonl", "audit_events.jsonl", "neighbor_belief_snapshots.jsonl"):
        fpath = method_dir / fname
        nlines = sum(1 for _ in fpath.open(encoding="utf-8")) if fpath.exists() else 0
        print(f"[stage2_smoke] {fname}: exists={fpath.exists()}, lines={nlines}")

    if args.no_validate:
        return 0

    print("\n[stage2_smoke] running validate_logs.py on the new run_dir...")
    rc = subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts/validate_logs.py"), str(method_dir)],
        cwd=str(_REPO_ROOT),
    ).returncode
    print(f"[stage2_smoke] validate_logs exit_code={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
