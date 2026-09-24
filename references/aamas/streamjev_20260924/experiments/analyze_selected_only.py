"""Post-hoc analysis of saved RLS evidence; never calls a model or learner."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    logs = root / "logs"
    prefix = "selected_only_rls_falsification_20260924"
    output = logs / "selected_only_review_20260924"
    inputs = [logs / f"{prefix}_{suffix}" for suffix in
              ("config.json", "raw.jsonl", "results.json")]
    start = time.perf_counter()
    trace_path = output.with_name(output.name + "_raw.jsonl")
    # This run is analysis of fixed evidence, not a rerun of the simulator.
    with trace_path.open("x", encoding="utf-8") as trace:
        def record(event, **payload):
            trace.write(json.dumps({"timestamp": now(), "event_type": event,
                                    "payload": payload}, ensure_ascii=False) + "\n")
            trace.flush()

        config = {
            "type": "posthoc_saved_evidence_analysis", "started_at": now(),
            "bootstrap_seed": 20260924, "bootstrap_replicates": 10000,
            "resampling_unit": "paired whole environment seed; not events",
            "input_sha256": {p.name: digest(p) for p in inputs},
            "analysis_script_sha256": digest(Path(__file__)),
            "checkout_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True).strip(),
            "python": platform.python_version(), "numpy": np.__version__,
            "command": "python3 references/aamas/streamjev_20260924/experiments/analyze_selected_only.py",
            "training_runs": 0, "llm_api_calls": 0, "a800_jobs": 0,
        }
        output.with_name(output.name + "_config.json").write_text(
            json.dumps(config, indent=2) + "\n")
        record("analysis_start", **config)
        try:
            saved = json.loads(inputs[2].read_text())
            rows = saved["per_seed"]
            by_method = defaultdict(dict)
            for row in rows:
                by_method[row["method"]][row["seed"]] = row
            seeds = sorted(by_method["static"])
            assert len(seeds) == 12
            assert all(sorted(v) == seeds for v in by_method.values())
            indices = np.random.default_rng(20260924).integers(
                0, len(seeds), size=(10000, len(seeds)))
            comparisons = {}
            metrics = ["mean_expected_reward", "mean_realized_reward",
                       "mean_policy_expected_menu_reward", "post_switch_expected_reward"]
            for method in ("online_rls", "label_shuffle", "no_feedback"):
                comparisons[method] = {}
                for metric in metrics:
                    deltas = np.array([by_method[method][s][metric]
                                       - by_method["static"][s][metric] for s in seeds])
                    ci = np.quantile(deltas[indices].mean(axis=1), [0.025, 0.975])
                    item = {
                        "mean_delta": float(deltas.mean()),
                        "bootstrap_ci95": ci.tolist(),
                        "positive_seeds": int((deltas > 1e-12).sum()),
                        "negative_seeds": int((deltas < -1e-12).sum()),
                        "tied_seeds": int((abs(deltas) <= 1e-12).sum()),
                        "per_seed_delta": dict(zip(map(str, seeds), deltas.tolist())),
                        "leave_one_out_mean_range": [
                            float(min(np.delete(deltas, i).mean() for i in range(len(seeds)))),
                            float(max(np.delete(deltas, i).mean() for i in range(len(seeds))))],
                    }
                    comparisons[method][metric] = item
                    record("paired_metric", method=method, metric=metric, **item)

            decisions, feedback = {}, {}
            for line in inputs[1].open():
                row = json.loads(line)
                kind = row["event_type"]
                source_t = row["t"] if kind == "decision" else row["source_t"]
                key = (row["method"], row["seed"], source_t)
                target = decisions if kind == "decision" else feedback
                assert key not in target, ("duplicate", key)
                target[key] = row
            assert len(decisions) == len(feedback) == 23040
            for key, event in decisions.items():
                fb = feedback[key]
                assert event["selected_candidate"] in event["menu"]
                assert event["selected_candidate"] == fb["candidate_id"]
                assert 0 < event["propensity"] <= 1
                assert event["propensity"] == fb["propensity"]
                assert event["feedback_arrival"] == fb["t"]
                assert fb["t"] - fb["source_t"] == fb["delay"]
            audit = {}
            for method in by_method:
                d = [r for k, r in decisions.items() if k[0] == method]
                f = [r for k, r in feedback.items() if k[0] == method]
                props = np.array([r["propensity"] for r in d])
                changed = sum(r["selected_candidate"] != decisions[
                    ("static", r["seed"], r["t"])]["selected_candidate"] for r in d)
                audit[method] = {
                    "decision_count": len(d), "feedback_count": len(f),
                    "propensity_min_p50_p95_max": np.quantile(props, [0, .5, .95, 1]).tolist(),
                    "inverse_propensity_over_cap_fraction": float((1 / props > 8).mean()),
                    "selected_action_change_vs_static_fraction": changed / len(d),
                    "updates_after_horizon": sum(r["event_type"] == "feedback_arrived_after_horizon"
                                                  and r["used_for_update"] for r in f),
                    "mean_realized_reward_from_raw": float(np.mean([r["label"] for r in f])),
                }
                assert np.isclose(audit[method]["mean_realized_reward_from_raw"],
                                  saved["summary"][method]["mean_realized_reward"]["mean"])
            result = {"analysis": config, "comparisons_vs_uniform_static": comparisons,
                      "raw_audit": audit, "finished_at": now(),
                      "wall_seconds": time.perf_counter() - start,
                      "interpretation": "Exploratory post-hoc analysis of synthetic logs. No new training; no confirmatory claim."}
            record("audit_complete", **audit)
            output.with_name(output.name + "_results.json").write_text(
                json.dumps(result, indent=2) + "\n")
            record("analysis_complete", wall_seconds=result["wall_seconds"])
            print(json.dumps({"paired": {m: {k: {a: v[a] for a in
                ("mean_delta", "bootstrap_ci95", "positive_seeds", "negative_seeds")}
                for k, v in vals.items()} for m, vals in comparisons.items()},
                "audit": audit}, indent=2))
        except Exception as exc:
            record("analysis_error", type=type(exc).__name__, message=str(exc))
            raise


if __name__ == "__main__":
    main()
