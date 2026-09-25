"""Feature ablation for shared context dilution in associative memory."""
from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.linear_associative_smoke import AssociativeKernelUpdater
from experiments.stationary_estimator_isolation_20260925 import stationary_world


def run(seed: int, feature_mode: str, horizon: int = 2000) -> dict:
    world = stationary_world(seed, horizon=horizon)
    full_dim = int(world["feature_dim"])
    dim = full_dim if feature_mode == "full" else 4
    memory = AssociativeKernelUpdater(
        feature_dim=dim,
        forgetting=1.0,
        ridge=0.1,
        prior=0.5,
        max_weight=8.0,
        uncertainty_scale=0.0,
        temperature=1.0,
    )
    rng = np.random.default_rng(seed + 100003)
    pending: dict[int, list[dict]] = defaultdict(list)
    rewards, regrets, rank_hits, entropies = [], [], [], []

    def select_feature(feature):
        x = np.asarray(feature, dtype=float)
        return x if feature_mode == "full" else x[3:]

    for t, event in enumerate(world["events"]):
        for fb in pending.pop(t, []):
            memory.update_batch(t, [fb])
        menu = event["menu"]
        features = event["features"]
        predictions = []
        for cid in menu:
            x = select_feature(features[cid])
            q = memory.phi(x)
            predictions.append(float(np.clip(q @ memory.S / max(float(q @ memory.Z), 1e-12), 0.0, 1.0)))
        predictions = np.asarray(predictions)
        truth = np.asarray([event["truth"][cid] for cid in menu], dtype=float)
        best = np.flatnonzero(np.isclose(predictions, np.max(predictions), atol=1e-12))
        probs = np.full(len(menu), 0.1 / len(menu), dtype=float)
        probs[best] += 0.9 / len(best)
        idx = int(rng.choice(len(menu), p=probs))
        cid = menu[idx]
        rewards.append(float(truth[idx]))
        regrets.append(float(np.max(truth) - truth[idx]))
        true_best = set(np.flatnonzero(np.isclose(truth, np.max(truth), atol=1e-12)))
        rank_hits.append(float(len(set(best) & true_best) / max(1, len(best))))
        entropies.append(float(-np.sum(probs * np.log(np.maximum(probs, 1e-12)))))
        x = select_feature(features[cid])
        pending[t + 1].append(
            {
                "feedback_id": f"{feature_mode}:{seed}:{t}",
                "feature": list(x),
                "label": int(event["labels"][cid]),
                "propensity": float(probs[idx]),
            }
        )
    for t in sorted(pending):
        for fb in pending[t]:
            memory.update_batch(t, [fb])
    return {
        "seed": seed,
        "feature_mode": feature_mode,
        "horizon": horizon,
        "mean_expected_reward": float(np.mean(rewards)),
        "mean_regret": float(np.mean(regrets)),
        "rank_hit_fraction": float(np.mean(rank_hits)),
        "mean_policy_entropy": float(np.mean(entropies)),
        "updates": int(memory.observed),
    }


def main() -> None:
    out = ROOT / "experiments" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    eid = "feature_ablation_20260925"
    seeds = [20260925 + i * 17 for i in range(5)]
    modes = ["full", "candidate_only"]
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": eid,
        "seeds": seeds,
        "horizon": 2000,
        "world": "stationary_estimator_isolation.stationary_world",
        "feature_modes": {"full": "[1, context, candidate_vector]", "candidate_only": "candidate_vector"},
        "policy": "epsilon-greedy epsilon=0.1",
        "selected_only": True,
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "git_commit": commit,
        },
        "interpretation": "Feature ablation only; no paper claim.",
    }
    (out / f"{eid}_config.json").write_text(json.dumps(config, indent=2) + "\n")
    results = []
    raw_path = out / f"{eid}_raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for seed in seeds:
            for mode in modes:
                result = run(seed, mode)
                results.append(result)
                raw_file.write(json.dumps(result, sort_keys=True) + "\n")
                raw_file.flush()
    summary = {}
    for mode in modes:
        entries = [r for r in results if r["feature_mode"] == mode]
        summary[mode] = {}
        for key in ("mean_expected_reward", "mean_regret", "rank_hit_fraction", "mean_policy_entropy"):
            values = np.asarray([r[key] for r in entries], dtype=float)
            summary[mode][key] = {
                "mean": float(np.mean(values)),
                "sd": float(np.std(values, ddof=1)),
                "n": len(values),
            }
    payload = {
        "experiment_id": eid,
        "config_file": str(out / f"{eid}_config.json"),
        "raw_file": str(raw_path),
        "per_seed": results,
        "summary": summary,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / f"{eid}_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = [
        "# Feature ablation (2026-09-25)",
        "",
        "Same stationary selected-only world and epsilon-greedy policy; only the long-lived feature changes.",
        "",
        "| feature mode | expected reward | regret | rank hit | entropy |",
        "|---|---:|---:|---:|---:|",
    ]
    for mode in modes:
        s = summary[mode]
        lines.append(
            f"| {mode} | {s['mean_expected_reward']['mean']:.6f} | "
            f"{s['mean_regret']['mean']:.6f} | {s['rank_hit_fraction']['mean']:.6f} | "
            f"{s['mean_policy_entropy']['mean']:.6f} |"
        )
    lines += ["", "This tests shared-context dilution only; it does not test delayed regime switches."]
    (out / f"{eid}_summary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
