"""Strict selected-only online RLS falsification experiment.

The environment generates hidden reward probabilities and per-candidate outcomes,
but the policy sees only the displayed menu/features and receives a label for
its selected candidate after a random delay.  No unselected outcome or oracle
argmax is passed to any learner.  The script compares a frozen uniform policy,
a selected-only OnlineRLSHead, a label-shuffled RLS control, and a no-feedback
control.  All configurations, per-event traces, and aggregate results are
written as JSON/JSONL for reproducibility.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from online_head import OnlineRLSHead

METHODS = ("static", "online_rls", "label_shuffle", "no_feedback")


def sigmoid(x: float) -> float:
    x = max(-12.0, min(12.0, float(x)))
    return 1.0 / (1.0 + math.exp(-x))


def _jsonable(v):
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, (np.floating, np.integer)):
        return v.item()
    return v


def make_world(seed: int, horizon: int = 480, n_candidates: int = 8,
               menu_size: int = 4, context_dim: int = 2,
               feature_seed_offset: int = 9973) -> Mapping[str, object]:
    """Create a fixed hidden stream independent of learner actions.

    Candidate menus, contexts, hidden regime switches, delayed feedback delays,
    and Bernoulli outcomes are all sampled before a learner runs.  Thus methods
    can be replayed on the same environment without sharing hidden labels.
    """
    rng = np.random.default_rng(seed)
    feature_rng = np.random.default_rng(seed + feature_seed_offset)
    candidate_ids = [f"c{i}" for i in range(n_candidates)]
    candidate_vectors = feature_rng.normal(0.0, 0.8, size=(n_candidates, 4))
    candidate_vectors /= np.maximum(
        np.linalg.norm(candidate_vectors, axis=1, keepdims=True), 1e-8
    )
    feature_dim = 1 + context_dim + candidate_vectors.shape[1]

    # Regime schedule is random and not predictable from the decision index.
    # A fresh parameter vector at each switch avoids the old fixed before/after
    # leakage and tests recovery under multiple unrelated changes.
    theta = rng.normal(0.0, 0.85, size=feature_dim)
    next_switch = int(rng.integers(45, 100))
    regime = 0
    switch_times: List[int] = []
    events: List[dict] = []
    for t in range(horizon):
        if t >= next_switch:
            regime += 1
            theta = rng.normal(0.0, 0.85, size=feature_dim)
            switch_times.append(t)
            # Random inter-switch gap with a broad support.
            next_switch = t + int(rng.integers(35, 105))
        context = rng.normal(0.0, 0.75, size=context_dim)
        menu = rng.choice(candidate_ids, size=menu_size, replace=False).tolist()
        rng.shuffle(menu)
        features = {
            cid: np.concatenate(([1.0], context, candidate_vectors[int(cid[1:])])).astype(float)
            for cid in menu
        }
        truth = {cid: sigmoid(float(theta @ features[cid])) for cid in menu}
        # Outcomes are generated for audit but only the selected candidate's
        # outcome is ever delivered to a learner.
        labels = {cid: int(rng.random() < truth[cid]) for cid in menu}
        delay = int(rng.integers(1, 9))
        events.append({
            "t": t,
            "menu": menu,
            "features": {cid: features[cid].tolist() for cid in menu},
            "truth": truth,  # evaluation-only; never passed to learners
            "labels": labels,  # evaluation-only until selected feedback arrives
            "delay": delay,
            "regime": regime,  # evaluation-only
        })
    return {
        "seed": seed,
        "candidate_ids": candidate_ids,
        "feature_dim": feature_dim,
        "menu_size": menu_size,
        "context_dim": context_dim,
        "events": events,
        "switch_times": switch_times,
    }


def uniform_probs(n: int) -> np.ndarray:
    return np.full(n, 1.0 / n, dtype=np.float64)


def run_method(world: Mapping[str, object], method: str, seed: int) -> tuple[dict, list[dict]]:
    if method not in METHODS:
        raise ValueError(f"unknown method {method}")
    events: Sequence[dict] = world["events"]  # type: ignore[assignment]
    d = int(world["feature_dim"])
    head = None
    if method in ("online_rls", "label_shuffle"):
        head = OnlineRLSHead(
            feature_dim=d,
            forgetting=0.985,
            ridge=1.2,
            max_parameter_norm=8.0,
            max_weight=8.0,
            residual_scale=1.0,
            uncertainty_scale=0.30,
            temperature=1.0,
        )
    policy_rng = np.random.default_rng(seed + 100003)
    shuffle_rng = np.random.default_rng(seed + 300007)
    pending: Dict[int, list[dict]] = defaultdict(list)
    observed_labels: List[int] = []
    rows: list[dict] = []
    expected_rewards: List[float] = []
    realized_rewards: List[int] = []
    regrets: List[float] = []
    policy_expected_rewards: List[float] = []
    policy_entropies: List[float] = []
    switch_windows: list[dict] = []
    switch_times: Sequence[int] = world["switch_times"]  # type: ignore[assignment]
    switch_set = set(int(x) for x in switch_times)

    for t, event in enumerate(events):
        # Delayed selected-only labels arrive before the next decision.  The
        # hidden truth/other candidate labels remain inaccessible.
        arrivals = pending.pop(t, [])
        for fb in arrivals:
            true_label = int(fb["label"])
            update_label = true_label
            if method == "label_shuffle":
                # Preserve the marginal label distribution while breaking the
                # feature/outcome association. No unselected labels are used.
                update_label = int(observed_labels[shuffle_rng.integers(len(observed_labels))]) if observed_labels else 0
            used = method in ("online_rls", "label_shuffle")
            if used and head is not None:
                head.update(fb["feature"], float(update_label), float(fb["propensity"]),
                            feedback_id=f"{method}:{fb['source_t']}")
            observed_labels.append(true_label)
            rows.append({
                "event_type": "feedback_arrived",
                "t": t,
                "source_t": int(fb["source_t"]),
                "method": method,
                "label": true_label,
                "update_label": update_label if used else None,
                "label_hidden_until_arrival": True,
                "used_for_update": used,
                "propensity": float(fb["propensity"]),
                "delay": int(fb["delay"]),
                "candidate_id": fb["candidate_id"],
            })

        menu: Sequence[str] = event["menu"]  # type: ignore[assignment]
        features: Mapping[str, Sequence[float]] = event["features"]  # type: ignore[assignment]
        if head is None:
            probs = uniform_probs(len(menu))
            uncertainty = np.zeros(len(menu), dtype=np.float64)
        else:
            probs, uncertainty = head.score(menu, [0.0] * len(menu), features, explore=True)
        action_idx = int(policy_rng.choice(len(menu), p=probs))
        cid = menu[action_idx]
        propensity = float(probs[action_idx])
        label = int(event["labels"][cid])  # hidden from policy until arrival
        truth_selected = float(event["truth"][cid])
        oracle_truth = float(max(event["truth"].values()))
        expected_rewards.append(truth_selected)
        realized_rewards.append(label)
        regrets.append(oracle_truth - truth_selected)
        # This is an evaluation-only counterfactual value of the sampled
        # policy distribution.  The learner receives neither ``truth`` nor
        # any unselected labels.
        policy_expected_rewards.append(float(np.dot(probs, [event["truth"][x] for x in menu])))
        policy_entropies.append(float(-np.sum(probs * np.log(np.maximum(probs, 1e-12)))))
        arrival = t + int(event["delay"])
        pending[arrival].append({
            "source_t": t,
            "candidate_id": cid,
            "feature": list(features[cid]),
            "label": label,
            "propensity": propensity,
            "delay": int(event["delay"]),
        })
        rows.append({
            "event_type": "decision",
            "t": t,
            "method": method,
            "menu": list(menu),
            "selected_candidate": cid,
            "propensity": propensity,
            "label_hidden": True,
            "feedback_arrival": arrival,
            "regime_evaluation_only": int(event["regime"]),
            "truth_selected_evaluation_only": truth_selected,
            "oracle_truth_evaluation_only": oracle_truth,
            "expected_reward_evaluation_only": truth_selected,
            "uncertainty": float(uncertainty[action_idx]),
        })

    # Flush delayed labels after the final decision, so update counts and raw
    # logs include every selected-only feedback event.
    for t in sorted(pending):
        for fb in pending[t]:
            true_label = int(fb["label"])
            update_label = true_label
            if method == "label_shuffle":
                update_label = int(observed_labels[shuffle_rng.integers(len(observed_labels))]) if observed_labels else 0
            used = method in ("online_rls", "label_shuffle")
            if used and head is not None:
                head.update(fb["feature"], float(update_label), float(fb["propensity"]),
                            feedback_id=f"{method}:{fb['source_t']}")
            observed_labels.append(true_label)
            rows.append({
                "event_type": "feedback_arrived_after_horizon",
                "t": int(t),
                "source_t": int(fb["source_t"]),
                "method": method,
                "label": true_label,
                "update_label": update_label if used else None,
                "label_hidden_until_arrival": True,
                "used_for_update": used,
                "propensity": float(fb["propensity"]),
                "delay": int(fb["delay"]),
                "candidate_id": fb["candidate_id"],
            })

    # Recovery windows are defined from hidden switch times for evaluation only;
    # no switch time enters policy state or updates.
    for sw in switch_times:
        lo, hi = int(sw), min(len(events), int(sw) + 25)
        if hi > lo:
            switch_windows.append({
                "switch_t": int(sw),
                "window": hi - lo,
                "expected_reward": float(np.mean(expected_rewards[lo:hi])),
                "regret": float(np.mean(regrets[lo:hi])),
            })
    result = {
        "method": method,
        "seed": seed,
        "horizon": len(events),
        "switch_count": len(switch_times),
        "feedback_count": len(observed_labels),
        "mean_expected_reward": float(np.mean(expected_rewards)),
        "mean_realized_reward": float(np.mean(realized_rewards)),
        "mean_regret": float(np.mean(regrets)),
        "mean_policy_expected_menu_reward": float(np.mean(policy_expected_rewards)),
        "mean_policy_entropy": float(np.mean(policy_entropies)),
        "post_switch_expected_reward": float(np.mean([x["expected_reward"] for x in switch_windows])) if switch_windows else None,
        "post_switch_regret": float(np.mean([x["regret"] for x in switch_windows])) if switch_windows else None,
        "switch_windows": switch_windows,
        "final_observed_parameter_updates": int(head.observed) if head is not None else 0,
        "final_theta_norm": float(np.linalg.norm(head.theta)) if head is not None else 0.0,
    }
    return result, rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="references/aamas/streamjev_20260924/experiments/logs")
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--horizon", type=int, default=480)
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    experiment_id = "selected_only_rls_falsification_20260924"
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        git_commit = "unknown"
    started_at = datetime.now(timezone.utc).isoformat()
    config = {
        "experiment_id": experiment_id,
        "seed_count": args.seeds,
        "base_seed": 20260924,
        "horizon": args.horizon,
        "methods": list(METHODS),
        "environment": {
            "n_candidates": 8,
            "menu_size": 4,
            "random_candidate_permutation": True,
            "random_regime_switches": True,
            "random_feedback_delay_range": [1, 8],
            "unselected_labels_delivered_to_learner": False,
            "oracle_argmax_delivered_to_learner": False,
        },
        "learner": {
            "name": "OnlineRLSHead",
            "forgetting": 0.985,
            "ridge": 1.2,
            "max_weight": 8.0,
            "uncertainty_scale": 0.30,
            "temperature": 1.0,
            "feedback_deduplication": "feedback_id in bounded seen set",
        },
        "runtime": {
            "started_at_utc": started_at,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit,
            "command": "python3 experiments/selected_only_rls.py --seeds %d --horizon %d" % (args.seeds, args.horizon),
        },
        "notes": "Corrected selected-only experiment; hidden truth fields in raw logs are evaluation-only and never passed to updates.",
    }
    (out / f"{experiment_id}_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    all_results: list[dict] = []
    raw_path = out / f"{experiment_id}_raw.jsonl"
    # Stream rows so a crash leaves a useful audit trail.
    with raw_path.open("w", encoding="utf-8") as raw:
        for i in range(args.seeds):
            seed = 20260924 + i * 17
            world = make_world(seed, horizon=args.horizon)
            for method in METHODS:
                result, rows = run_method(world, method, seed)
                all_results.append(result)
                for row in rows:
                    raw.write(json.dumps({"experiment_id": experiment_id, "seed": seed, **row}, sort_keys=True) + "\n")
                raw.flush()
    by_method: dict[str, list[dict]] = {m: [x for x in all_results if x["method"] == m] for m in METHODS}
    summary: dict[str, dict] = {}
    for method, entries in by_method.items():
        def mean_sd(key: str) -> dict:
            vals = np.asarray([float(x[key]) for x in entries], dtype=float)
            sd = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
            half = 1.96 * sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
            return {
                "mean": float(vals.mean()), "sd": sd, "n": int(len(vals)),
                "ci95_normal_approx": [float(vals.mean() - half), float(vals.mean() + half)],
            }
        summary[method] = {
            "mean_expected_reward": mean_sd("mean_expected_reward"),
            "mean_realized_reward": mean_sd("mean_realized_reward"),
            "mean_regret": mean_sd("mean_regret"),
            "mean_policy_expected_menu_reward": mean_sd("mean_policy_expected_menu_reward"),
            "mean_policy_entropy": mean_sd("mean_policy_entropy"),
            "post_switch_expected_reward": mean_sd("post_switch_expected_reward"),
            "post_switch_regret": mean_sd("post_switch_regret"),
            "updates": mean_sd("final_observed_parameter_updates"),
        }
    # Pair by environment seed.  This is a descriptive paired comparison, not
    # a significance test; later benchmark runs should add bootstrap CIs.
    static_by_seed = {int(x["seed"]): x for x in by_method["static"]}
    paired_delta = {}
    for method in METHODS:
        if method == "static":
            continue
        deltas = [
            float(x["mean_expected_reward"] - static_by_seed[int(x["seed"])] ["mean_expected_reward"])
            for x in by_method[method]
        ]
        paired_delta[method] = {
            "mean_expected_reward_delta_vs_static": float(np.mean(deltas)),
            "sd": float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0,
            "n": len(deltas),
        }
        if len(deltas) > 1:
            half = 1.96 * float(np.std(deltas, ddof=1)) / math.sqrt(len(deltas))
            paired_delta[method]["ci95_normal_approx"] = [
                float(np.mean(deltas) - half), float(np.mean(deltas) + half)
            ]
    finished_at = datetime.now(timezone.utc).isoformat()
    result_payload = {
        "experiment_id": experiment_id,
        "config_file": str(out / f"{experiment_id}_config.json"),
        "raw_file": str(raw_path),
        "per_seed": all_results,
        "summary": summary,
        "paired_delta_vs_static": paired_delta,
        "finished_at_utc": finished_at,
        "interpretation": "Selected-only falsification smoke; not a real-data quality claim. Compare paired seeds and controls before any paper claim.",
    }
    (out / f"{experiment_id}_results.json").write_text(json.dumps(result_payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result_payload, indent=2))


if __name__ == "__main__":
    main()
