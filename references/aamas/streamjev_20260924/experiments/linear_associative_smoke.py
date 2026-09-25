"""Small reproducible comparison for a delayed selected-only associative updater.

This script reuses the hidden-regime world from selected_only_rls.py but keeps the
linear associative implementation local to this experiment.  It compares a
uniform static control, an identical no-feedback control, OnlineRLSHead, and a
non-negative feature kernel updater that maintains S/Z sufficient statistics.
No unselected labels or hidden truth are passed to any learner.
"""
from __future__ import annotations

import argparse
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from online_head import OnlineRLSHead
from experiments.selected_only_rls import make_world

METHODS = ("static", "online_rls", "no_feedback", "associative")


def _percentile(values: Sequence[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=float), q)) if values else 0.0


class AssociativeKernelUpdater:
    """Decayed non-negative kernel sufficient statistics.

    For a feature x, phi(x)=[max(x,0), max(-x,0)] is non-negative.  At an
    arrival time k, all feedback in that batch is first decayed once and then
    added.  This makes the result invariant to the order of feedback records
    sharing the same arrival time.
    """

    def __init__(self, feature_dim: int, forgetting: float = 0.985,
                 ridge: float = 0.1, prior: float = 0.5,
                 max_weight: float = 8.0, uncertainty_scale: float = 0.30,
                 temperature: float = 1.0) -> None:
        if feature_dim <= 0 or not (0.0 < forgetting <= 1.0):
            raise ValueError("invalid feature dimension or forgetting")
        self.feature_dim = int(feature_dim)
        self.state_dim = 2 * self.feature_dim
        self.forgetting = float(forgetting)
        self.ridge = float(ridge)
        self.max_weight = float(max_weight)
        self.uncertainty_scale = float(uncertainty_scale)
        self.temperature = float(temperature)
        # Prior pseudo-observations keep a cold-start score at 0.5.
        self.S = np.full(self.state_dim, self.ridge * prior, dtype=np.float64)
        self.Z = np.full(self.state_dim, self.ridge, dtype=np.float64)
        self.last_time = 0
        self.observed = 0
        self._seen_feedback: set[str] = set()

    def phi(self, feature: Sequence[float]) -> np.ndarray:
        x = np.asarray(feature, dtype=np.float64)
        if x.shape != (self.feature_dim,) or not np.all(np.isfinite(x)):
            raise ValueError("feature shape or values are invalid")
        return np.concatenate((np.maximum(x, 0.0), np.maximum(-x, 0.0)))

    def _decay_to(self, t: int) -> None:
        if t < self.last_time:
            raise ValueError("arrival times must be non-decreasing")
        gap = int(t - self.last_time)
        if gap:
            factor = self.forgetting ** gap
            self.S *= factor
            self.Z *= factor
            self.last_time = int(t)

    def update_batch(self, t: int, feedback: Sequence[Mapping[str, object]]) -> int:
        """Apply one arrival batch; all records observe the same decay factor."""
        self._decay_to(int(t))
        accepted = 0
        for fb in feedback:
            fid = str(fb["feedback_id"])
            if fid in self._seen_feedback:
                continue
            label = float(fb["label"])
            propensity = float(fb["propensity"])
            if not (np.isfinite(label) and 0.0 <= label <= 1.0):
                raise ValueError("label must be in [0,1]")
            if not (np.isfinite(propensity) and 0.0 < propensity <= 1.0):
                raise ValueError("invalid propensity")
            weight = min(self.max_weight, 1.0 / propensity)
            k = self.phi(fb["feature"])  # selected candidate only
            self.S += weight * label * k
            self.Z += weight * k
            self._seen_feedback.add(fid)
            self.observed += 1
            accepted += 1
        return accepted

    def score(self, candidate_features: Mapping[str, Sequence[float]]) -> tuple[np.ndarray, np.ndarray]:
        means = []
        uncertainties = []
        for feature in candidate_features.values():
            q = self.phi(feature)
            mass = float(q @ self.Z)
            mean = float(q @ self.S / max(mass, 1e-12))
            uncertainty = float(1.0 / math.sqrt(1.0 + mass))
            means.append(np.clip(mean, 0.0, 1.0))
            uncertainties.append(uncertainty)
        logits = np.asarray(means) + self.uncertainty_scale * np.asarray(uncertainties)
        logits = (logits - np.max(logits)) / self.temperature
        logits = np.clip(logits, -60.0, 0.0)
        probs = np.exp(logits)
        probs /= np.sum(probs)
        return probs, np.asarray(uncertainties)

    def snapshot(self) -> dict:
        return {"S": self.S.tolist(), "Z": self.Z.tolist(),
                "last_time": self.last_time, "observed": self.observed}


def uniform_probs(n: int) -> np.ndarray:
    return np.full(n, 1.0 / n, dtype=np.float64)


def run_method(world: Mapping[str, object], method: str, seed: int) -> tuple[dict, list[dict], list[dict]]:
    events: Sequence[dict] = world["events"]  # type: ignore[assignment]
    d = int(world["feature_dim"])
    rls = None
    assoc = None
    if method == "online_rls":
        rls = OnlineRLSHead(feature_dim=d, forgetting=0.985, ridge=1.2,
                            max_parameter_norm=8.0, max_weight=8.0,
                            residual_scale=1.0, uncertainty_scale=0.30,
                            temperature=1.0)
    if method == "associative":
        assoc = AssociativeKernelUpdater(feature_dim=d, forgetting=0.985,
                                         ridge=0.1, prior=0.5,
                                         max_weight=8.0, uncertainty_scale=0.30,
                                         temperature=1.0)
    policy_rng = np.random.default_rng(seed + 100003)
    pending: dict[int, list[dict]] = defaultdict(list)
    rows: list[dict] = []
    feedback_records: list[dict] = []
    expected_rewards, realized_rewards, regrets = [], [], []
    policy_expected_rewards, policy_entropies = [], []
    decision_latencies_us, update_latencies_us = [], []
    switch_times: Sequence[int] = world["switch_times"]  # type: ignore[assignment]
    switch_windows: list[dict] = []

    def process_arrivals(t: int) -> None:
        arrivals = pending.pop(t, [])
        if not arrivals:
            return
        update_start = time.perf_counter_ns()
        if method == "online_rls" and rls is not None:
            for fb in arrivals:
                rls.update(fb["feature"], float(fb["label"]), float(fb["propensity"]),
                           feedback_id=fb["feedback_id"])
        elif method == "associative" and assoc is not None:
            assoc.update_batch(t, arrivals)
        update_elapsed = (time.perf_counter_ns() - update_start) / 1000.0
        if method in ("online_rls", "associative"):
            update_latencies_us.append(update_elapsed)
        for fb in arrivals:
            rows.append({"event_type": "feedback_arrived", "t": int(t),
                         "source_t": int(fb["source_t"]), "method": method,
                         "feedback_id": fb["feedback_id"], "label": int(fb["label"]),
                         "used_for_update": method in ("online_rls", "associative"),
                         "delay": int(fb["delay"]), "candidate_id": fb["candidate_id"],
                         "update_batch_latency_us": update_elapsed,
                         "update_batch_size": len(arrivals),
                         "label_hidden_until_arrival": True})
            feedback_records.append(dict(fb, arrival_t=int(t)))

    for t, event in enumerate(events):
        process_arrivals(t)
        menu: Sequence[str] = event["menu"]  # type: ignore[assignment]
        features: Mapping[str, Sequence[float]] = event["features"]  # type: ignore[assignment]
        decision_start = time.perf_counter_ns()
        if method in ("static", "no_feedback"):
            probs = uniform_probs(len(menu))
            uncertainty = np.zeros(len(menu), dtype=np.float64)
        elif method == "online_rls" and rls is not None:
            probs, uncertainty = rls.score(menu, [0.0] * len(menu), features, explore=True)
        elif method == "associative" and assoc is not None:
            probs, uncertainty = assoc.score({cid: features[cid] for cid in menu})
        else:
            raise ValueError(method)
        action_idx = int(policy_rng.choice(len(menu), p=probs))
        cid = menu[action_idx]
        decision_latencies_us.append((time.perf_counter_ns() - decision_start) / 1000.0)
        propensity = float(probs[action_idx])
        label = int(event["labels"][cid])
        truth_selected = float(event["truth"][cid])
        oracle_truth = float(max(event["truth"].values()))
        expected_rewards.append(truth_selected)
        realized_rewards.append(label)
        regrets.append(oracle_truth - truth_selected)
        policy_expected_rewards.append(float(np.dot(probs, [event["truth"][x] for x in menu])))
        policy_entropies.append(float(-np.sum(probs * np.log(np.maximum(probs, 1e-12)))))
        arrival = t + int(event["delay"])
        fb = {"feedback_id": f"{method}:{seed}:{t}", "source_t": t,
              "candidate_id": cid, "feature": list(features[cid]), "label": label,
              "propensity": propensity, "delay": int(event["delay"])}
        pending[arrival].append(fb)
        rows.append({"event_type": "decision", "t": t, "method": method,
                     "menu": list(menu), "selected_candidate": cid,
                     "propensity": propensity, "feedback_arrival": arrival,
                     "policy_probabilities": probs.tolist(),
                     "decision_latency_us": decision_latencies_us[-1],
                     "label_hidden": True, "regime_evaluation_only": int(event["regime"]),
                     "truth_selected_evaluation_only": truth_selected,
                     "oracle_truth_evaluation_only": oracle_truth,
                     "expected_reward_evaluation_only": truth_selected,
                     "uncertainty": float(uncertainty[action_idx])})

    for t in sorted(pending):
        process_arrivals(t)

    for sw in switch_times:
        lo, hi = int(sw), min(len(events), int(sw) + 25)
        if hi > lo:
            switch_windows.append({"switch_t": int(sw), "window": hi - lo,
                                   "expected_reward": float(np.mean(expected_rewards[lo:hi])),
                                   "regret": float(np.mean(regrets[lo:hi]))})
    updates = rls.observed if rls is not None else assoc.observed if assoc is not None else 0
    state_norm = (float(np.linalg.norm(rls.theta)) if rls is not None else
                  float(np.linalg.norm(assoc.S)) if assoc is not None else 0.0)
    result = {"method": method, "seed": seed, "horizon": len(events),
              "switch_count": len(switch_times), "feedback_count": len(feedback_records),
              "mean_expected_reward": float(np.mean(expected_rewards)),
              "mean_realized_reward": float(np.mean(realized_rewards)),
              "mean_regret": float(np.mean(regrets)),
              "mean_policy_expected_menu_reward": float(np.mean(policy_expected_rewards)),
              "mean_policy_entropy": float(np.mean(policy_entropies)),
              "post_switch_expected_reward": float(np.mean([x["expected_reward"] for x in switch_windows])) if switch_windows else None,
              "post_switch_regret": float(np.mean([x["regret"] for x in switch_windows])) if switch_windows else None,
              "switch_windows": switch_windows, "updates": int(updates),
              "state_norm": state_norm,
              "decision_latency_us_p50": _percentile(decision_latencies_us, 50),
              "decision_latency_us_p95": _percentile(decision_latencies_us, 95),
              "update_batch_latency_us_p50": _percentile(update_latencies_us, 50),
              "update_batch_latency_us_p95": _percentile(update_latencies_us, 95),
              "update_batch_count": len(update_latencies_us)}
    return result, rows, feedback_records


def order_invariance(records: Sequence[Mapping[str, object]], feature_dim: int) -> dict:
    """Replay identical arrival batches in original/reversed order."""
    by_t: dict[int, list[Mapping[str, object]]] = defaultdict(list)
    for record in records:
        by_t[int(record["arrival_t"])].append(record)
    a = AssociativeKernelUpdater(feature_dim=feature_dim)
    b = AssociativeKernelUpdater(feature_dim=feature_dim)
    for t in sorted(by_t):
        batch = by_t[t]
        a.update_batch(t, batch)
        b.update_batch(t, list(reversed(batch)))
    diff_s = float(np.max(np.abs(a.S - b.S)))
    diff_z = float(np.max(np.abs(a.Z - b.Z)))
    return {"arrival_batch_count": len(by_t), "max_abs_S_difference": diff_s,
            "max_abs_Z_difference": diff_z,
            "invariant_within_tolerance": bool(diff_s < 1e-12 and diff_z < 1e-12)}


def closed_form_check(records: Sequence[Mapping[str, object]], feature_dim: int,
                      forgetting: float = 0.985, ridge: float = 0.1,
                      prior: float = 0.5, max_weight: float = 8.0) -> dict:
    """Check the recursive state against its explicit decayed sum."""
    if not records:
        return {"max_abs_S_difference": 0.0, "max_abs_Z_difference": 0.0,
                "matches_closed_form": True}
    updater = AssociativeKernelUpdater(feature_dim=feature_dim, forgetting=forgetting,
                                       ridge=ridge, prior=prior,
                                       max_weight=max_weight)
    by_t: dict[int, list[Mapping[str, object]]] = defaultdict(list)
    for record in records:
        by_t[int(record["arrival_t"])].append(record)
    for t in sorted(by_t):
        updater.update_batch(t, by_t[t])
    final_t = max(by_t)
    initial = np.full(2 * feature_dim, ridge, dtype=np.float64)
    expected_z = initial * (forgetting ** final_t)
    expected_s = (initial * prior) * (forgetting ** final_t)
    for record in records:
        k = updater.phi(record["feature"])
        weight = min(max_weight, 1.0 / float(record["propensity"]))
        decay = forgetting ** (final_t - int(record["arrival_t"]))
        expected_z += decay * weight * k
        expected_s += decay * weight * float(record["label"]) * k
    diff_s = float(np.max(np.abs(updater.S - expected_s)))
    diff_z = float(np.max(np.abs(updater.Z - expected_z)))
    return {"max_abs_S_difference": diff_s, "max_abs_Z_difference": diff_z,
            "matches_closed_form": bool(diff_s < 1e-12 and diff_z < 1e-12)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="references/aamas/streamjev_20260924/experiments/logs")
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--horizon", type=int, default=100)
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    experiment_id = "linear_associative_smoke_20260925"
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True,
                                             stderr=subprocess.DEVNULL).strip()
    except Exception:
        git_commit = "unknown"
    started = datetime.now(timezone.utc).isoformat()
    config = {"experiment_id": experiment_id, "seed_count": args.seeds,
              "base_seed": 20260925, "horizon": args.horizon, "methods": list(METHODS),
              "environment": {"world": "selected_only_rls.make_world", "menu_size": 4,
                              "delays": [1, 8], "unselected_labels_delivered": False,
                              "oracle_argmax_delivered": False},
              "associative": {"feature_map": "concat(max(x,0),max(-x,0))",
                              "forgetting": 0.985, "ridge": 0.1, "prior": 0.5,
                              "ips_weight": "min(8,1/propensity)",
                              "batch_decay": "one decay per arrival timestamp"},
              "runtime": {"started_at_utc": started, "python": platform.python_version(),
                          "numpy": np.__version__, "platform": platform.platform(),
                          "git_commit": git_commit,
                          "command": f"python3 references/aamas/streamjev_20260924/experiments/linear_associative_smoke.py --seeds {args.seeds} --horizon {args.horizon}",
                          "cwd": str(Path.cwd())},
              "notes": "Synthetic falsification smoke only; truth fields are evaluation-only."}
    config_path = out / f"{experiment_id}_config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    all_results: list[dict] = []
    raw_path = out / f"{experiment_id}_raw.jsonl"
    invariances = []
    with raw_path.open("w", encoding="utf-8") as raw:
        for i in range(args.seeds):
            seed = 20260925 + i * 17
            world = make_world(seed, horizon=args.horizon)
            assoc_records = None
            for method in METHODS:
                result, rows, feedback_records = run_method(world, method, seed)
                all_results.append(result)
                if method == "associative":
                    assoc_records = feedback_records
                for row in rows:
                    raw.write(json.dumps({"experiment_id": experiment_id, "seed": seed, **row}, sort_keys=True) + "\n")
                raw.flush()
            assert assoc_records is not None
            inv = order_invariance(assoc_records, int(world["feature_dim"]))
            inv["seed"] = seed
            inv["closed_form"] = closed_form_check(assoc_records, int(world["feature_dim"]))
            invariances.append(inv)
    by_method = {m: [x for x in all_results if x["method"] == m] for m in METHODS}
    def mean_sd(entries: Sequence[dict], key: str) -> dict:
        vals = np.asarray([float(x[key]) for x in entries], dtype=float)
        sd = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
        half = 1.96 * sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
        return {"mean": float(vals.mean()), "sd": sd, "n": len(vals),
                "ci95_normal_approx": [float(vals.mean() - half), float(vals.mean() + half)]}
    metric_keys = ("mean_expected_reward", "mean_realized_reward", "mean_regret",
                   "post_switch_expected_reward", "post_switch_regret",
                   "decision_latency_us_p50", "decision_latency_us_p95",
                   "update_batch_latency_us_p50", "update_batch_latency_us_p95")
    summary = {m: {k: mean_sd(by_method[m], k) for k in metric_keys} for m in METHODS}
    static_by_seed = {int(x["seed"]): x for x in by_method["static"]}
    paired_delta = {}
    for method in METHODS:
        if method == "static":
            continue
        deltas = [float(x["mean_expected_reward"] - static_by_seed[int(x["seed"])] ["mean_expected_reward"])
                  for x in by_method[method]]
        paired_delta[method] = {"mean_expected_reward_delta_vs_static": float(np.mean(deltas)),
                                "sd": float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0,
                                "n": len(deltas)}
    result_payload = {"experiment_id": experiment_id,
                      "config_file": str(config_path), "raw_file": str(raw_path),
                      "per_seed": all_results, "summary": summary,
                      "paired_delta_vs_static": paired_delta,
                      "order_invariance": invariances,
                      "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                      "interpretation": "Synthetic selected-only smoke; no real-data quality claim."}
    results_path = out / f"{experiment_id}_results.json"
    results_path.write_text(json.dumps(result_payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result_payload, indent=2))


if __name__ == "__main__":
    main()
