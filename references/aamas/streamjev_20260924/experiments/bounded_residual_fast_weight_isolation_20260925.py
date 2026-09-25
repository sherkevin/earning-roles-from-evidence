"""Low-cost preflight for the bounded residual fast-weight candidate.

This is a synthetic, selected-only replay.  It is deliberately run before any
Nebula job: the candidate must beat a static baseline and expose a measurable
adaptation/stability trade-off under the same policy and feedback trace.
"""
from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from online_head import OnlineRLSHead
from experiments.linear_associative_smoke import AssociativeKernelUpdater

METHODS = ("static", "associative", "online_rls", "rfw_tr")


def sigmoid(x: float) -> float:
    x = max(-12.0, min(12.0, float(x)))
    return 1.0 / (1.0 + math.exp(-x))


def world(seed: int, horizon: int, switch: bool) -> Mapping[str, object]:
    rng = np.random.default_rng(seed)
    feature_rng = np.random.default_rng(seed + 9973)
    candidate_ids = [f"c{i}" for i in range(8)]
    candidate_vectors = feature_rng.normal(0.0, 0.8, size=(8, 4))
    candidate_vectors /= np.maximum(np.linalg.norm(candidate_vectors, axis=1, keepdims=True), 1e-8)
    feature_dim = 7
    theta_a = rng.normal(0.0, 0.85, size=feature_dim)
    theta_b = -theta_a if switch else theta_a.copy()
    events = []
    switch_at = horizon // 2 if switch else None
    for t in range(horizon):
        context = rng.normal(0.0, 0.75, size=2)
        menu = rng.choice(candidate_ids, size=4, replace=False).tolist()
        rng.shuffle(menu)
        features = {
            cid: np.concatenate(([1.0], context, candidate_vectors[int(cid[1:])])).astype(float)
            for cid in menu
        }
        theta = theta_b if switch_at is not None and t >= switch_at else theta_a
        truth = {cid: sigmoid(theta @ features[cid]) for cid in menu}
        labels = {cid: int(rng.random() < truth[cid]) for cid in menu}
        events.append({"t": t, "menu": menu, "features": {c: features[c].tolist() for c in menu},
                       "truth": truth, "labels": labels, "delay": 1})
    return {"seed": seed, "events": events, "feature_dim": feature_dim,
            "switch_at": switch_at, "menu_size": 4}


def qk(feature: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Map [bias, context(2), candidate(4)] into normalized query/address."""
    x = np.asarray(feature, dtype=np.float64)
    q = np.zeros(7, dtype=np.float64)
    k = np.zeros(7, dtype=np.float64)
    q[:3] = x[:3]
    k[0] = x[0]
    k[3:] = x[3:]
    q /= max(float(np.linalg.norm(q)), 1e-12)
    k /= max(float(np.linalg.norm(k)), 1e-12)
    return q, k


class ResidualFastWeight:
    """Projected residual outer-product update from the math candidate."""

    def __init__(self, dim: int = 7, alpha: float = 0.995, eta: float = 0.25,
                 epsilon: float = 0.05, omega_max: float = 4.0, rho: float = 1.0):
        self.dim = dim
        self.alpha = float(alpha)
        self.eta = float(eta)
        self.epsilon = float(epsilon)
        self.omega_max = float(omega_max)
        self.rho = float(rho)
        self.R = np.zeros((dim, dim), dtype=np.float64)
        self.observed = 0
        self.update_times_us: list[float] = []

    def advance(self, feedbacks: Sequence[Mapping[str, object]]) -> None:
        start = time.perf_counter_ns()
        self.R *= self.alpha
        if feedbacks:
            delta = np.zeros_like(self.R)
            for fb in feedbacks:
                q = np.asarray(fb["q"], dtype=np.float64)
                k = np.asarray(fb["k"], dtype=np.float64)
                p = max(float(fb["propensity"]), 1e-12)
                weight = min(self.omega_max, 1.0 / p)
                pred = float(np.clip(0.5 + q @ self.R @ k, 0.0, 1.0))
                residual = float(fb["label"]) - pred
                delta += (self.eta * weight * residual / (1.0 + self.epsilon)) * np.outer(q, k)
                self.observed += 1
            self.R += delta
            norm = float(np.linalg.norm(self.R))
            if norm > self.rho:
                self.R *= self.rho / norm
        self.update_times_us.append((time.perf_counter_ns() - start) / 1e3)

    def predict(self, feature: Sequence[float]) -> float:
        q, k = qk(feature)
        return float(np.clip(0.5 + q @ self.R @ k, 0.0, 1.0))


class DualResidualFastWeight:
    """Two time-scales: a slow protected residual and a fast decaying residual."""

    def __init__(self, dim: int = 7, alpha_s: float = 0.999, eta_s: float = 0.05,
                 alpha_f: float = 0.80, eta_f: float = 0.50, epsilon: float = 0.05,
                 omega_max: float = 4.0, rho_s: float = 0.50, rho_f: float = 1.0):
        self.alpha_s, self.eta_s = float(alpha_s), float(eta_s)
        self.alpha_f, self.eta_f = float(alpha_f), float(eta_f)
        self.epsilon, self.omega_max = float(epsilon), float(omega_max)
        self.rho_s, self.rho_f = float(rho_s), float(rho_f)
        self.Rs = np.zeros((dim, dim), dtype=np.float64)
        self.Rf = np.zeros((dim, dim), dtype=np.float64)
        self.observed = 0
        self.update_times_us: list[float] = []

    def advance(self, feedbacks: Sequence[Mapping[str, object]]) -> None:
        start = time.perf_counter_ns()
        self.Rs *= self.alpha_s
        self.Rf *= self.alpha_f
        ds = np.zeros_like(self.Rs)
        df = np.zeros_like(self.Rf)
        for fb in feedbacks:
            q = np.asarray(fb["q"], dtype=np.float64)
            k = np.asarray(fb["k"], dtype=np.float64)
            p = max(float(fb["propensity"]), 1e-12)
            weight = min(self.omega_max, 1.0 / p)
            pred = float(np.clip(0.5 + q @ (self.Rs + self.Rf) @ k, 0.0, 1.0))
            residual = float(fb["label"]) - pred
            outer = np.outer(q, k)
            ds += (self.eta_s * weight * residual / (1.0 + self.epsilon)) * outer
            df += (self.eta_f * weight * residual / (1.0 + self.epsilon)) * outer
            self.observed += 1
        self.Rs += ds
        self.Rf += df
        for name, radius in (("Rs", self.rho_s), ("Rf", self.rho_f)):
            value = getattr(self, name)
            norm = float(np.linalg.norm(value))
            if norm > radius:
                setattr(self, name, value * (radius / norm))
        self.update_times_us.append((time.perf_counter_ns() - start) / 1e3)

    def predict(self, feature: Sequence[float]) -> float:
        q, k = qk(feature)
        return float(np.clip(0.5 + q @ (self.Rs + self.Rf) @ k, 0.0, 1.0))


def policy_probs(predictions: Sequence[float], epsilon: float = 0.10) -> np.ndarray:
    values = np.asarray(predictions, dtype=np.float64)
    best = np.flatnonzero(np.isclose(values, np.max(values), atol=1e-12))
    probs = np.full(len(values), epsilon / len(values), dtype=np.float64)
    for idx in best:
        probs[idx] += (1.0 - epsilon) / len(best)
    return probs


def run_method(world_data: Mapping[str, object], method: str, seed: int) -> tuple[dict, list[dict]]:
    events = world_data["events"]
    d = int(world_data["feature_dim"])
    assoc = AssociativeKernelUpdater(feature_dim=d, forgetting=1.0, ridge=0.1,
                                     prior=0.5, max_weight=8.0,
                                     uncertainty_scale=0.0, temperature=1.0) if method == "associative" else None
    rls = OnlineRLSHead(feature_dim=d, forgetting=1.0, ridge=1.0,
                        max_parameter_norm=20.0, max_weight=8.0,
                        residual_scale=1.0, uncertainty_scale=0.0,
                        temperature=1.0) if method == "online_rls" else None
    rfw = ResidualFastWeight() if method == "rfw_tr" else None
    dual = DualResidualFastWeight() if method == "dual_rfw" else None
    rng = np.random.default_rng(seed + 100003)
    pending: dict[int, list[dict]] = defaultdict(list)
    raw: list[dict] = []
    rewards, regrets, mses, ranks, entropies = [], [], [], [], []
    decision_us: list[float] = []
    for t, event in enumerate(events):
        feedbacks = pending.pop(t, [])
        if rfw is not None or dual is not None:
            (rfw if rfw is not None else dual).advance(feedbacks)
        elif assoc is not None:
            assoc.update_batch(t, feedbacks)
        elif rls is not None:
            for fb in feedbacks:
                rls.update(fb["feature"], float(fb["label"]), float(fb["propensity"]), feedback_id=fb["feedback_id"])
        menu = event["menu"]
        features = event["features"]
        truth = np.asarray([event["truth"][cid] for cid in menu], dtype=float)
        start = time.perf_counter_ns()
        if method == "static":
            predictions = np.full(len(menu), 0.5, dtype=float)
        elif assoc is not None:
            predictions = np.asarray([float(np.clip(assoc.phi(features[cid]) @ assoc.S /
                max(float(assoc.phi(features[cid]) @ assoc.Z), 1e-12), 0.0, 1.0)) for cid in menu])
        elif rls is not None:
            predictions = np.asarray([sigmoid(rls.theta @ np.asarray(features[cid])) for cid in menu])
        elif rfw is not None:
            predictions = np.asarray([rfw.predict(features[cid]) for cid in menu])
        else:
            predictions = np.asarray([dual.predict(features[cid]) for cid in menu])
        probs = policy_probs(predictions)
        action_idx = int(rng.choice(len(menu), p=probs))
        decision_us.append((time.perf_counter_ns() - start) / 1e3)
        cid = menu[action_idx]
        selected_truth = float(truth[action_idx])
        rewards.append(selected_truth)
        regrets.append(float(np.max(truth) - selected_truth))
        mses.append(float(np.mean((predictions - truth) ** 2)))
        pred_best = set(np.flatnonzero(np.isclose(predictions, np.max(predictions), atol=1e-12)))
        truth_best = set(np.flatnonzero(np.isclose(truth, np.max(truth), atol=1e-12)))
        ranks.append(float(len(pred_best & truth_best) / max(1, len(pred_best))))
        entropies.append(float(-np.sum(probs * np.log(np.maximum(probs, 1e-12)))))
        fb = {"feedback_id": f"{method}:{seed}:{t}", "feature": list(features[cid]),
              "q": qk(features[cid])[0].tolist(), "k": qk(features[cid])[1].tolist(),
              "label": int(event["labels"][cid]), "propensity": float(probs[action_idx])}
        pending[t + 1].append(fb)
        raw.append({"event_type": "decision", "method": method, "seed": seed, "t": t,
                    "selected_candidate": cid, "propensity": float(probs[action_idx]),
                    "prediction_evaluation_only": predictions.tolist(),
                    "truth_evaluation_only": truth.tolist(), "selected_truth_evaluation_only": selected_truth,
                    "oracle_truth_evaluation_only": float(np.max(truth)), "label_hidden": True})
    for t in sorted(pending):
        feedbacks = pending[t]
        if rfw is not None or dual is not None:
            (rfw if rfw is not None else dual).advance(feedbacks)
        elif assoc is not None:
            assoc.update_batch(t, feedbacks)
        elif rls is not None:
            for fb in feedbacks:
                rls.update(fb["feature"], float(fb["label"]), float(fb["propensity"]), feedback_id=fb["feedback_id"])
    updates = rfw.observed if rfw is not None else dual.observed if dual is not None else assoc.observed if assoc is not None else rls.observed if rls is not None else 0
    update_times = (rfw.update_times_us if rfw is not None else dual.update_times_us if dual is not None else [])
    return ({"method": method, "seed": seed, "horizon": len(events),
             "switch_at": world_data["switch_at"], "mean_expected_reward": float(np.mean(rewards)),
             "mean_regret": float(np.mean(regrets)), "mean_prediction_mse": float(np.mean(mses)),
             "rank_hit_fraction": float(np.mean(ranks)), "mean_policy_entropy": float(np.mean(entropies)),
             "decision_p50_us": float(np.percentile(decision_us, 50)),
             "decision_p95_us": float(np.percentile(decision_us, 95)),
             "update_p50_us": float(np.percentile(update_times, 50)) if update_times else 0.0,
             "update_p95_us": float(np.percentile(update_times, 95)) if update_times else 0.0,
             "state_bytes": int(rfw.R.nbytes) if rfw is not None else int(dual.Rs.nbytes + dual.Rf.nbytes) if dual is not None else 0, "updates": int(updates)}, raw)


def main() -> None:
    out = ROOT / "experiments" / "logs"
    out.mkdir(parents=True, exist_ok=True)
    eid = "bounded_residual_fast_weight_isolation_20260925"
    seeds = [20260925 + i * 17 for i in range(5)]
    config = {"experiment_id": eid, "seeds": seeds, "horizon": 2000, "methods": list(METHODS),
              "scenarios": ["stationary", "switch"],
              "candidate": {"m": 7, "alpha": 0.995, "eta": 0.25, "epsilon": 0.05, "omega_max": 4.0, "rho": 1.0},
              "feedback": {"selected_only": True, "delay": 1, "propensity_clip": 4.0},
              "policy": {"type": "epsilon_greedy", "epsilon": 0.10},
              "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                          "python": platform.python_version(), "numpy": np.__version__,
                          "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                          "command": "python3 references/aamas/streamjev_20260924/experiments/bounded_residual_fast_weight_isolation_20260925.py"},
              "interpretation": "Synthetic preflight only; no real-data claim."}
    (out / f"{eid}_config.json").write_text(json.dumps(config, indent=2) + "\n")
    all_results: list[dict] = []
    raw_path = out / f"{eid}_raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for scenario in ("stationary", "switch"):
            for seed in seeds:
                data = world(seed, 2000, scenario == "switch")
                for method in METHODS:
                    result, rows = run_method(data, method, seed)
                    result["scenario"] = scenario
                    all_results.append(result)
                    for row in rows:
                        row["scenario"] = scenario
                        raw_file.write(json.dumps(row, sort_keys=True) + "\n")
                    raw_file.flush()
    summary: dict[str, dict] = {}
    for scenario in ("stationary", "switch"):
        for method in METHODS:
            rows = [r for r in all_results if r["scenario"] == scenario and r["method"] == method]
            summary[f"{scenario}/{method}"] = {key: {"mean": float(np.mean([r[key] for r in rows])),
                                                     "sd": float(np.std([r[key] for r in rows], ddof=1)), "n": len(rows)}
                                                for key in ("mean_expected_reward", "mean_regret", "mean_prediction_mse",
                                                            "rank_hit_fraction", "mean_policy_entropy", "decision_p95_us", "update_p95_us")}
    payload = {"experiment_id": eid, "config_file": str(out / f"{eid}_config.json"),
               "raw_file": str(raw_path), "per_seed": all_results, "summary": summary,
               "finished_at_utc": datetime.now(timezone.utc).isoformat(),
               "interpretation": "Synthetic preflight only; no real-data quality claim."}
    (out / f"{eid}_results.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = ["# Bounded residual fast-weight isolation (2026-09-25)", "",
             "Synthetic selected-only stream, five seeds, 2000 decisions per scenario, one-step feedback delay; truth is evaluation-only.", "",
             "| scenario/method | reward | regret | MSE | rank hit | decision p95 us | update p95 us |", "|---|---:|---:|---:|---:|---:|---:|"]
    for key, values in summary.items():
        lines.append(f"| {key} | {values['mean_expected_reward']['mean']:.6f} | {values['mean_regret']['mean']:.6f} | {values['mean_prediction_mse']['mean']:.6f} | {values['rank_hit_fraction']['mean']:.6f} | {values['decision_p95_us']['mean']:.3f} | {values['update_p95_us']['mean']:.3f} |")
    lines += ["", "This is a falsification preflight. It does not establish real benchmark quality or A800 performance."]
    (out / f"{eid}_summary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
