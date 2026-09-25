"""Policy calibration control for the associative estimator.

The estimator and fixed stationary worlds are unchanged. Only the behavior
policy differs: temperature-1 softmax versus epsilon-greedy. This separates
weak ranking from failure to exploit the ranking.
"""
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


def probs_from_policy(predictions: np.ndarray, policy: str) -> np.ndarray:
    if policy == "epsilon":
        best = np.flatnonzero(np.isclose(predictions, np.max(predictions), atol=1e-12))
        p = np.full(len(predictions), 0.1 / len(predictions), dtype=float)
        p[best] += 0.9 / len(best)
        return p
    if policy == "softmax":
        z = (predictions - np.max(predictions)) / 1.0
        p = np.exp(np.clip(z, -60.0, 0.0))
        return p / np.sum(p)
    raise ValueError(policy)


def run(seed: int, policy: str, horizon: int = 2000) -> dict:
    world = stationary_world(seed, horizon=horizon)
    d = int(world["feature_dim"])
    assoc = AssociativeKernelUpdater(
        feature_dim=d,
        forgetting=1.0,
        ridge=0.1,
        prior=0.5,
        max_weight=8.0,
        uncertainty_scale=0.0,
        temperature=1.0,
    )
    rng = np.random.default_rng(seed + 100003)
    pending: dict[int, list[dict]] = defaultdict(list)
    rewards, regrets, entropies, rank_hits = [], [], [], []
    for t, event in enumerate(world["events"]):
        for fb in pending.pop(t, []):
            assoc.update_batch(t, [fb])
        menu = event["menu"]
        features = event["features"]
        predictions = np.asarray(
            [
                float(
                    np.clip(
                        assoc.phi(features[cid]) @ assoc.S
                        / max(float(assoc.phi(features[cid]) @ assoc.Z), 1e-12),
                        0.0,
                        1.0,
                    )
                )
                for cid in menu
            ]
        )
        truth = np.asarray([event["truth"][cid] for cid in menu], dtype=float)
        probs = probs_from_policy(predictions, policy)
        idx = int(rng.choice(len(menu), p=probs))
        cid = menu[idx]
        rewards.append(float(truth[idx]))
        regrets.append(float(np.max(truth) - truth[idx]))
        entropies.append(float(-np.sum(probs * np.log(np.maximum(probs, 1e-12)))))
        pred_best = set(np.flatnonzero(np.isclose(predictions, np.max(predictions), atol=1e-12)))
        true_best = set(np.flatnonzero(np.isclose(truth, np.max(truth), atol=1e-12)))
        rank_hits.append(float(len(pred_best & true_best) / max(1, len(pred_best))))
        pending[t + 1].append(
            {
                "feedback_id": f"{policy}:{seed}:{t}",
                "feature": list(features[cid]),
                "label": int(event["labels"][cid]),
                "propensity": float(probs[idx]),
            }
        )
    for t in sorted(pending):
        for fb in pending[t]:
            assoc.update_batch(t, [fb])
    return {
        "seed": seed,
        "policy": policy,
        "horizon": horizon,
        "mean_expected_reward": float(np.mean(rewards)),
        "mean_regret": float(np.mean(regrets)),
        "mean_entropy": float(np.mean(entropies)),
        "rank_hit_fraction": float(np.mean(rank_hits)),
        "updates": int(assoc.observed),
    }


def main() -> None:
    out = ROOT / "experiments" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    eid = "policy_calibration_isolation_20260925"
    seeds = [20260925 + i * 17 for i in range(5)]
    methods = ["softmax", "epsilon"]
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": eid,
        "seeds": seeds,
        "horizon": 2000,
        "estimator": "AssociativeKernelUpdater with fixed theta stationary world",
        "policies": {"softmax": "temperature=1", "epsilon": "epsilon=0.1"},
        "selected_only": True,
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "git_commit": commit,
        },
        "interpretation": "Policy calibration control only; no paper claim.",
    }
    (out / f"{eid}_config.json").write_text(json.dumps(config, indent=2) + "\n")
    results = []
    raw_path = out / f"{eid}_raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for seed in seeds:
            for policy in methods:
                result = run(seed, policy)
                results.append(result)
                raw_file.write(json.dumps(result, sort_keys=True) + "\n")
                raw_file.flush()
    summary = {}
    for policy in methods:
        entries = [r for r in results if r["policy"] == policy]
        summary[policy] = {}
        for key in ("mean_expected_reward", "mean_regret", "mean_entropy", "rank_hit_fraction"):
            values = np.asarray([r[key] for r in entries], dtype=float)
            summary[policy][key] = {
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
        "# Policy calibration isolation (2026-09-25)",
        "",
        "Same associative estimator and stationary selected-only worlds; only behavior policy changes.",
        "",
        "| policy | expected reward | regret | rank hit | entropy |",
        "|---|---:|---:|---:|---:|",
    ]
    for policy in methods:
        s = summary[policy]
        lines.append(
            f"| {policy} | {s['mean_expected_reward']['mean']:.6f} | "
            f"{s['mean_regret']['mean']:.6f} | {s['rank_hit_fraction']['mean']:.6f} | "
            f"{s['mean_entropy']['mean']:.6f} |"
        )
    lines += ["", "This isolates policy calibration; it does not improve the estimator representation."]
    (out / f"{eid}_summary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
