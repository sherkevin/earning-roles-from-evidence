"""One-method preflight for the two-time-scale residual candidate."""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from experiments.bounded_residual_fast_weight_isolation_20260925 import run_method, world


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "experiments" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    eid = "dual_residual_fast_weight_preflight_20260925"
    seeds = [20260925 + i * 17 for i in range(5)]
    config = {
        "experiment_id": eid,
        "seeds": seeds,
        "horizon": 2000,
        "method": "dual_rfw",
        "parameters": {"alpha_s": 0.999, "eta_s": 0.05, "alpha_f": 0.80,
                        "eta_f": 0.50, "epsilon": 0.05, "omega_max": 4.0,
                        "rho_s": 0.50, "rho_f": 1.0, "m": 7},
        "feedback": {"selected_only": True, "delay": 1},
        "policy": {"type": "epsilon_greedy", "epsilon": 0.10},
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "numpy": np.__version__,
                    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()},
        "interpretation": "Synthetic preflight only; compare with prior isolation logs."}
    (out / f"{eid}_config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows, raw = [], out / f"{eid}_raw.jsonl"
    with raw.open("w", encoding="utf-8") as stream:
        for scenario in ("stationary", "switch"):
            for seed in seeds:
                result, events = run_method(world(seed, 2000, scenario == "switch"), "dual_rfw", seed)
                result["scenario"] = scenario
                rows.append(result)
                for event in events:
                    event["scenario"] = scenario
                    stream.write(json.dumps(event, sort_keys=True) + "\n")
    summary = {}
    for scenario in ("stationary", "switch"):
        subset = [r for r in rows if r["scenario"] == scenario]
        summary[scenario] = {key: {"mean": float(np.mean([r[key] for r in subset])),
                                   "sd": float(np.std([r[key] for r in subset], ddof=1)), "n": len(subset)}
                             for key in ("mean_expected_reward", "mean_regret", "mean_prediction_mse",
                                         "rank_hit_fraction", "decision_p95_us", "update_p95_us")}
    payload = {"experiment_id": eid, "config_file": str(out / f"{eid}_config.json"),
               "raw_file": str(raw), "per_seed": rows, "summary": summary,
               "finished_at_utc": datetime.now(timezone.utc).isoformat(),
               "interpretation": "Synthetic preflight only; no real-data quality claim."}
    (out / f"{eid}_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out / f"{eid}_summary.md").write_text("\n".join([
        "# Dual residual fast-weight preflight (2026-09-25)", "",
        "| scenario | reward | regret | MSE | rank hit | decision p95 us | update p95 us |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *[f"| {s} | {v['mean_expected_reward']['mean']:.6f} | {v['mean_regret']['mean']:.6f} | {v['mean_prediction_mse']['mean']:.6f} | {v['rank_hit_fraction']['mean']:.6f} | {v['decision_p95_us']['mean']:.3f} | {v['update_p95_us']['mean']:.3f} |" for s, v in summary.items()],
        "", "Synthetic preflight only; no real-data or A800 claim.",
    ]) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
