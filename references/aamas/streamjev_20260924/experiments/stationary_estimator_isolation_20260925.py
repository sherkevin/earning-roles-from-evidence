"""Stationary long-horizon isolation for selector estimators.

The world has one fixed signed linear reward function and one-step selected-only
feedback delay. A common epsilon-greedy policy separates estimator quality from
the previous temperature-1 softmax collapse. This is an isolation experiment,
not a benchmark claim.
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
from typing import Mapping, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from online_head import OnlineRLSHead
from experiments.linear_associative_smoke import AssociativeKernelUpdater


METHODS = ("static", "associative", "diag_ls", "online_rls")


def sigmoid(x: float) -> float:
    x = max(-12.0, min(12.0, float(x)))
    return 1.0 / (1.0 + math.exp(-x))


def stationary_world(seed: int, horizon: int = 2000) -> Mapping[str, object]:
    rng = np.random.default_rng(seed)
    feature_rng = np.random.default_rng(seed + 9973)
    candidate_ids = [f"c{i}" for i in range(8)]
    candidate_vectors = feature_rng.normal(0.0, 0.8, size=(8, 4))
    candidate_vectors /= np.maximum(
        np.linalg.norm(candidate_vectors, axis=1, keepdims=True), 1e-8
    )
    context_dim = 2
    feature_dim = 1 + context_dim + 4
    theta = rng.normal(0.0, 0.85, size=feature_dim)
    events = []
    for t in range(horizon):
        context = rng.normal(0.0, 0.75, size=context_dim)
        menu = rng.choice(candidate_ids, size=4, replace=False).tolist()
        rng.shuffle(menu)
        features = {
            cid: np.concatenate(
                ([1.0], context, candidate_vectors[int(cid[1:])])
            ).astype(float)
            for cid in menu
        }
        truth = {cid: sigmoid(theta @ features[cid]) for cid in menu}
        labels = {cid: int(rng.random() < truth[cid]) for cid in menu}
        events.append(
            {
                "t": t,
                "menu": menu,
                "features": {cid: features[cid].tolist() for cid in menu},
                "truth": truth,
                "labels": labels,
                "delay": 1,
            }
        )
    return {
        "seed": seed,
        "events": events,
        "feature_dim": feature_dim,
        "menu_size": 4,
        "switch_times": [],
    }


class DiagonalLeastSquares:
    """O(d) diagonal approximation to signed linear ridge regression."""

    def __init__(self, feature_dim: int, ridge: float = 1.0) -> None:
        self.feature_dim = int(feature_dim)
        self.ridge = float(ridge)
        self.b = np.zeros(self.feature_dim, dtype=np.float64)
        self.d = np.full(self.feature_dim, self.ridge, dtype=np.float64)
        self.observed = 0

    def update(self, feature: Sequence[float], label: float, propensity: float) -> None:
        x = np.asarray(feature, dtype=np.float64)
        weight = min(8.0, 1.0 / float(propensity))
        self.b += weight * float(label) * x
        self.d += weight * (x * x)
        self.observed += 1

    def predict(self, feature: Sequence[float]) -> float:
        x = np.asarray(feature, dtype=np.float64)
        return float(np.clip(x @ (self.b / self.d), 0.0, 1.0))


def policy_probs(predictions: Sequence[float], epsilon: float) -> np.ndarray:
    values = np.asarray(predictions, dtype=np.float64)
    best = np.flatnonzero(np.isclose(values, np.max(values), atol=1e-12))
    probs = np.full(len(values), epsilon / len(values), dtype=np.float64)
    for idx in best:
        probs[idx] += (1.0 - epsilon) / len(best)
    return probs


def run_method(world: Mapping[str, object], method: str, seed: int) -> tuple[dict, list[dict]]:
    events = world["events"]
    d = int(world["feature_dim"])
    assoc = (
        AssociativeKernelUpdater(
            feature_dim=d,
            forgetting=1.0,
            ridge=0.1,
            prior=0.5,
            max_weight=8.0,
            uncertainty_scale=0.0,
            temperature=1.0,
        )
        if method == "associative"
        else None
    )
    diag = DiagonalLeastSquares(d) if method == "diag_ls" else None
    rls = (
        OnlineRLSHead(
            feature_dim=d,
            forgetting=1.0,
            ridge=1.0,
            max_parameter_norm=20.0,
            max_weight=8.0,
            residual_scale=1.0,
            uncertainty_scale=0.0,
            temperature=1.0,
        )
        if method == "online_rls"
        else None
    )
    rng = np.random.default_rng(seed + 100003)
    pending: dict[int, list[dict]] = defaultdict(list)
    raw = []
    expected_rewards = []
    regrets = []
    mse_values = []
    rank_hits = []
    oracle_rewards = []
    policy_entropy = []
    for t, event in enumerate(events):
        for fb in pending.pop(t, []):
            if assoc is not None:
                assoc.update_batch(t, [fb])
            elif diag is not None:
                diag.update(fb["feature"], float(fb["label"]), float(fb["propensity"]))
            elif rls is not None:
                rls.update(
                    fb["feature"],
                    float(fb["label"]),
                    float(fb["propensity"]),
                    feedback_id=fb["feedback_id"],
                )
        menu = event["menu"]
        features = event["features"]
        truth = np.asarray([event["truth"][cid] for cid in menu], dtype=float)
        if method == "static":
            predictions = np.full(len(menu), 0.5, dtype=float)
        elif assoc is not None:
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
        elif diag is not None:
            predictions = np.asarray([diag.predict(features[cid]) for cid in menu])
        elif rls is not None:
            predictions = np.asarray(
                [sigmoid(rls.theta @ np.asarray(features[cid])) for cid in menu]
            )
        else:
            raise ValueError(method)
        probs = policy_probs(predictions, epsilon=0.10)
        action_idx = int(rng.choice(len(menu), p=probs))
        cid = menu[action_idx]
        selected_truth = float(truth[action_idx])
        oracle = float(np.max(truth))
        expected_rewards.append(selected_truth)
        regrets.append(oracle - selected_truth)
        oracle_rewards.append(oracle)
        mse_values.append(float(np.mean((predictions - truth) ** 2)))
        pred_best = set(np.flatnonzero(np.isclose(predictions, np.max(predictions), atol=1e-12)))
        truth_best = set(np.flatnonzero(np.isclose(truth, np.max(truth), atol=1e-12)))
        rank_hits.append(float(len(pred_best & truth_best) / max(1, len(pred_best))))
        policy_entropy.append(float(-np.sum(probs * np.log(np.maximum(probs, 1e-12)))))
        arrival = t + 1
        pending[arrival].append(
            {
                "feedback_id": f"{method}:{seed}:{t}",
                "source_t": t,
                "candidate_id": cid,
                "feature": list(features[cid]),
                "label": int(event["labels"][cid]),
                "propensity": float(probs[action_idx]),
            }
        )
        raw.append(
            {
                "event_type": "decision",
                "method": method,
                "seed": seed,
                "t": t,
                "selected_candidate": cid,
                "propensity": float(probs[action_idx]),
                "prediction_evaluation_only": predictions.tolist(),
                "truth_evaluation_only": truth.tolist(),
                "selected_truth_evaluation_only": selected_truth,
                "oracle_truth_evaluation_only": oracle,
                "feedback_arrival": arrival,
                "label_hidden": True,
            }
        )
    for t in sorted(pending):
        for fb in pending[t]:
            if assoc is not None:
                assoc.update_batch(t, [fb])
            elif diag is not None:
                diag.update(fb["feature"], float(fb["label"]), float(fb["propensity"]))
            elif rls is not None:
                rls.update(
                    fb["feature"],
                    float(fb["label"]),
                    float(fb["propensity"]),
                    feedback_id=fb["feedback_id"],
                )
    result = {
        "method": method,
        "seed": seed,
        "horizon": len(events),
        "mean_expected_reward": float(np.mean(expected_rewards)),
        "mean_regret": float(np.mean(regrets)),
        "mean_oracle_reward": float(np.mean(oracle_rewards)),
        "mean_prediction_mse": float(np.mean(mse_values)),
        "rank_hit_fraction": float(np.mean(rank_hits)),
        "mean_policy_entropy": float(np.mean(policy_entropy)),
        "uniform_entropy": float(math.log(4)),
        "updates": int(
            assoc.observed
            if assoc is not None
            else diag.observed
            if diag is not None
            else rls.observed
            if rls is not None
            else 0
        ),
    }
    return result, raw


def main() -> None:
    out = ROOT / "experiments" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    eid = "stationary_estimator_isolation_20260925"
    seeds = [20260925 + i * 17 for i in range(5)]
    horizon = 2000
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": eid,
        "seeds": seeds,
        "horizon": horizon,
        "methods": list(METHODS),
        "world": {
            "fixed_theta": True,
            "regime_switches": False,
            "feedback_delay": 1,
            "unselected_labels_delivered": False,
            "oracle_truth_delivered": False,
        },
        "policy": {"type": "epsilon_greedy", "epsilon": 0.10, "tie_split": True},
        "runtime": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "git_commit": commit,
            "command": "python3 references/aamas/streamjev_20260924/experiments/stationary_estimator_isolation_20260925.py",
        },
        "interpretation": "Estimator isolation only; synthetic data and no paper claim.",
    }
    (out / f"{eid}_config.json").write_text(json.dumps(config, indent=2) + "\n")
    all_results = []
    raw_path = out / f"{eid}_raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for seed in seeds:
            world = stationary_world(seed, horizon=horizon)
            for method in METHODS:
                result, rows = run_method(world, method, seed)
                all_results.append(result)
                for row in rows:
                    raw_file.write(json.dumps(row, sort_keys=True) + "\n")
                raw_file.flush()
    by_method = {m: [r for r in all_results if r["method"] == m] for m in METHODS}
    summary = {}
    for method, entries in by_method.items():
        summary[method] = {}
        for key in (
            "mean_expected_reward",
            "mean_regret",
            "mean_oracle_reward",
            "mean_prediction_mse",
            "rank_hit_fraction",
            "mean_policy_entropy",
        ):
            values = np.asarray([e[key] for e in entries], dtype=float)
            summary[method][key] = {
                "mean": float(np.mean(values)),
                "sd": float(np.std(values, ddof=1)),
                "n": len(values),
            }
    payload = {
        "experiment_id": eid,
        "config_file": str(out / f"{eid}_config.json"),
        "raw_file": str(raw_path),
        "per_seed": all_results,
        "summary": summary,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "Stationary estimator isolation; no real-data quality claim.",
    }
    (out / f"{eid}_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = [
        "# Stationary estimator isolation (2026-09-25)",
        "",
        "Fixed-theta, 2000-step synthetic selected-only stream with one-step feedback delay. All methods use the same epsilon-greedy policy form; truth and unselected labels are evaluation-only.",
        "",
        "| method | expected reward | regret | prediction MSE | rank hit | policy entropy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        s = summary[method]
        lines.append(
            f"| {method} | {s['mean_expected_reward']['mean']:.6f} | "
            f"{s['mean_regret']['mean']:.6f} | {s['mean_prediction_mse']['mean']:.6f} | "
            f"{s['rank_hit_fraction']['mean']:.6f} | {s['mean_policy_entropy']['mean']:.6f} |"
        )
    lines += [
        "",
        "This experiment isolates estimator/statistic mismatch from regime switching. It does not test real benchmark quality or A800 latency.",
    ]
    (out / f"{eid}_summary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
