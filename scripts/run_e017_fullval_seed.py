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

ALLOWED_METHODS = ("edo_stage2_chain", "fixed_peer_calibrated", "single_agent")

OUT_ROOT = _REPO_ROOT / "artifacts/round2_gpt41mini_stage2_fullval"
COST_LEDGER = OUT_ROOT / "cost_ledger.jsonl"

# E-020.3: canonical newapi pre-flight quota probe script. If present, run
# it before launching the RoundRunner; abort on non-ACTIVE status to prevent
# `quota_exhaustion_incident_20260419_2338`-class silent corruption.
_QUOTA_PROBE = _REPO_ROOT / "workspace/tmp/newapi_quota_probe.sh"


def _run_quota_preflight(timeout_s: int = 30) -> None:
    """Run the newapi quota probe and abort if quota is not ACTIVE.

    Per ``four-role-todo-workflow.mdc §6.1.3`` (pre-flight quota / balance
    probe is STRONGLY RECOMMENDED for any script issuing > 100 LLM calls).

    Exits the process with status 2 on probe failure. Raises no exception.

    Allowed short-circuit: set ``SKIP_QUOTA_PREFLIGHT=1`` for unit tests
    / smoke probes that will issue < 20 LLM calls.
    """
    if os.environ.get("SKIP_QUOTA_PREFLIGHT", "").strip().lower() in (
        "1", "true", "yes",
    ):
        print(
            "[run_e017_fullval_seed] WARNING: SKIP_QUOTA_PREFLIGHT set; "
            "skipping newapi quota probe. Use only for smoke / tests.",
            flush=True,
        )
        return
    if not _QUOTA_PROBE.is_file():
        print(
            f"[run_e017_fullval_seed] WARNING: quota probe not found at "
            f"{_QUOTA_PROBE}; skipping pre-flight (install the probe script "
            "per four-role-todo-workflow.mdc §6.1.3).",
            flush=True,
        )
        return
    print(
        f"[run_e017_fullval_seed] pre-flight: running {_QUOTA_PROBE.name} ...",
        flush=True,
    )
    try:
        result = subprocess.run(
            ["bash", str(_QUOTA_PROBE)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        print(
            f"[run_e017_fullval_seed] FATAL: quota probe timed out after "
            f"{timeout_s}s — server unreachable?",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(2)

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if "newapi ACTIVE" in stdout:
        # Log the probe tail so the scheduler log captures the evidence.
        tail = "\n".join(stdout.strip().splitlines()[-5:])
        print(
            "[run_e017_fullval_seed] pre-flight OK: newapi ACTIVE.\n"
            f"  probe tail: {tail}",
            flush=True,
        )
        return
    print(
        "[run_e017_fullval_seed] FATAL PRE-FLIGHT: newapi quota not ACTIVE. "
        "Aborting before runner launch to prevent F1=0 garbage accumulation.",
        file=sys.stderr,
        flush=True,
    )
    print(f"  probe stdout:\n{stdout}", file=sys.stderr, flush=True)
    if stderr:
        print(f"  probe stderr:\n{stderr}", file=sys.stderr, flush=True)
    print(
        "  Remediation: top up balance (see USER_TODO §B.1 U-EXEC-007) "
        "or verify `configs/llm.json` newapi key is not rotated. Re-launch "
        "after `bash workspace/tmp/newapi_quota_probe.sh` prints "
        "'STATUS: newapi ACTIVE'.",
        file=sys.stderr,
        flush=True,
    )
    sys.exit(2)


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
    p.add_argument(
        "--skip-preflight",
        action="store_true",
        help=(
            "Skip the newapi quota pre-flight probe. Intended for smoke / "
            "tests; production fullval batches should always run the probe. "
            "Equivalent to setting SKIP_QUOTA_PREFLIGHT=1."
        ),
    )
    p.add_argument(
        "--consec-zero-halt",
        type=int,
        default=None,
        help=(
            "Override ``consecutive_zero_halt_threshold`` passed to the "
            "RoundRunner (E-020.2 silent-corruption guard). Default (when "
            "not set) inherits from yaml config or runner default (50). "
            "Set to 0 to disable (only recommended for unit tests that "
            "deliberately produce all-F1=0 samples). Production fullval "
            "batches should leave this unset."
        ),
    )
    args = p.parse_args()

    # E-020.3 pre-flight guard (after argparse so --skip-preflight works).
    if not args.skip_preflight:
        _run_quota_preflight()

    # Default E-017 fullval runs must use the repository's canonical provider
    # routing, but local open-weight smoke runs intentionally override the
    # backend with LLM_BACKEND=local_vllm. Preserve that explicit route so
    # server-only GPU experiments do not accidentally fall back to newapi.
    explicit_backend = os.environ.get("LLM_BACKEND", "").strip().lower()
    if explicit_backend != "local_vllm":
        os.environ.pop("LLM_BACKEND", None)
        os.environ.pop("LLM_BASE_URL", None)
        os.environ.pop("LLM_API_KEY", None)
    else:
        print(
            "[e017] preserving explicit LLM_BACKEND=local_vllm route "
            f"(base={os.environ.get('LLM_BASE_URL', '')})",
            flush=True,
        )

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
    if args.consec_zero_halt is not None:
        cfg["consecutive_zero_halt_threshold"] = int(args.consec_zero_halt)
        print(
            f"[e017] consecutive_zero_halt_threshold = "
            f"{cfg['consecutive_zero_halt_threshold']} (CLI override)",
            flush=True,
        )

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
