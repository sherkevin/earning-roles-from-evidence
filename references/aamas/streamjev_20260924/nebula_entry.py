"""Nebula entry point for the first A800 Stream-JEV throughput probe.

The probe measures the actual cached-embedding scorer and event update on the
selected GPU.  It is deliberately separate from the scientific replay runner:
no benchmark labels or hidden data are bundled into the job.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from neural_fast_state import StreamJEVCore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=20000)
    parser.add_argument("--state-dim", type=int, default=32)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--output-dir", default=os.environ.get("NEBULA_OUTPUT_DIR", "./streamjev_a800_results"))
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("The A800 probe requires CUDA; refusing to report a CPU result as GPU evidence")
    device = torch.device("cuda")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    config = {
        "experiment_id": "streamjev_a800_runtime_probe_20260924",
        "event_type": "cached_scorer_and_fast_update_throughput",
        "steps": args.steps,
        "state_dim": args.state_dim,
        "hidden_dim": args.hidden_dim,
        "device": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "git_commit": os.environ.get("GIT_COMMIT", "unknown"),
        "claims_allowed": ["GPU_runtime_latency", "GPU_update_throughput"],
        "claims_forbidden": ["real_data_gain", "benchmark_accuracy", "cross_seed_generalization"],
    }
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    model = StreamJEVCore(32, 32, state_dim=args.state_dim, hidden_dim=args.hidden_dim).to(device).eval()
    context = torch.randn(32, device=device)
    candidates = torch.randn(8, 32, device=device)
    candidate_ids = [f"c{i}" for i in range(8)]
    state = model.initial_state(device=device)
    # Warm-up kernels before measuring.  No gradients are needed in serving.
    with torch.no_grad():
        for i in range(100):
            logits = model.score(context, candidate_ids, candidates, state)
            action = int(torch.argmax(logits).item())
            state = model.update(context, candidate_ids[action], candidates[action], state,
                                 label=float(i % 2), delay=float(i % 4), propensity=0.25)
        torch.cuda.synchronize()
        score_start = time.perf_counter()
        for _ in range(args.steps):
            model.score(context, candidate_ids, candidates, state)
        torch.cuda.synchronize()
        score_elapsed = time.perf_counter() - score_start
        update_start = time.perf_counter()
        for i in range(args.steps):
            action = i % len(candidate_ids)
            state = model.update(context, candidate_ids[action], candidates[action], state,
                                 label=float(i % 2), delay=float(i % 4), propensity=0.25)
        torch.cuda.synchronize()
        update_elapsed = time.perf_counter() - update_start
    result = {
        "experiment_id": config["experiment_id"],
        "device": config["device"],
        "steps": args.steps,
        "score_total_seconds": score_elapsed,
        "score_us_per_call": score_elapsed * 1e6 / args.steps,
        "update_total_seconds": update_elapsed,
        "update_us_per_event": update_elapsed * 1e6 / args.steps,
        "score_events_per_second": args.steps / score_elapsed,
        "update_events_per_second": args.steps / update_elapsed,
        "state_global_norm": float(state.global_state.norm().item()),
        "claims": "Runtime probe only; no data quality or scientific gain claim.",
    }
    with (out / "raw.jsonl").open("w", encoding="utf-8") as handle:
        handle.write(json.dumps({"event_type": "probe_complete", **result}) + "\n")
    (out / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

