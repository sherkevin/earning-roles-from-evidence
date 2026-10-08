"""Logged numerical checks for a candidate comparator; no model/API execution."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

from peerrolebench_signed_ridge import SignedRidgeState

ROOT = Path(__file__).resolve().parents[1]


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    files = ["scripts/peerrolebench_signed_ridge.py",
             "scripts/peerrolebench_signed_ridge_check.py",
             "tests/test_peerrolebench_signed_ridge.py"]
    config = {
        "version": "signed-ridge-numerical-check-v3",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "synthetic numerical controls, not scientific task results",
        "real_api_calls": 0, "gpu_jobs": 0, "seed": 0,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
        "command": [sys.executable, *sys.argv],
        "test_command": [sys.executable, "-m", "pytest", "-q", files[2]],
        "source_sha256": {},
        "cases": [
            {"name": "opposing_tiny_rho", "dimension": 1, "rho": 1e-16, "n": 2},
            {"name": "correlated64", "dimension": 64, "rho": 1.0, "n": 128},
            {"name": "correlated_small_rho", "dimension": 8, "rho": 1e-4, "n": 128},
        ],
        "max_abs_prefix_error": 1e-8,
        "timing_scope": "core update including numerical input validation; excludes feature encoding, selection, reward legality, persistence and oracle",
        "timing_interpretation": "local observations without deadline or performance acceptance claim",
    }
    for rel in files:
        data = (ROOT / rel).read_bytes()
        dest = output / "source" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        config["source_sha256"][rel] = hashlib.sha256(data).hexdigest()
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    def log(row: dict) -> None:
        with (output / "raw.jsonl").open("a") as stream:
            stream.write(json.dumps({"at_utc": datetime.now(timezone.utc).isoformat(), **row}) + "\n")

    log({"event": "configured"})
    with (output / "pytest_console.txt").open("w") as stream:
        tests = subprocess.run(config["test_command"], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    log({"event": "unit_tests_finished", "exit_code": tests.returncode})
    results = []
    for case in config["cases"]:
        d, n, rho = case["dimension"], case["n"], case["rho"]
        if d == 1:
            X, u = np.ones((2, 1)), np.array([1.0, -1.0])
        else:
            rng = np.random.default_rng(config["seed"])
            direction = rng.normal(size=d)
            X = direction[None, :] + 0.1 * rng.normal(size=(n, d))
            X *= 0.95 / np.linalg.norm(X, axis=1, keepdims=True)
            u = np.sin(np.arange(n)) - 0.75
        (output / (case["name"] + "_inputs.json")).write_text(
            json.dumps({"x": X.tolist(), "u": u.tolist()}, indent=2) + "\n")
        state = SignedRidgeState(d, rho)
        times, errors = [], []
        for k, (x, target) in enumerate(zip(X, u), start=1):
            before_A = rho * np.eye(d) + X[:k-1].T @ X[:k-1]
            before_b = X[:k-1].T @ u[:k-1]
            oracle_prediction = float(x @ np.linalg.solve(before_A, before_b))
            start = time.perf_counter_ns()
            prediction = state.update(x, float(target))
            elapsed = (time.perf_counter_ns() - start) / 1e9
            oracle = np.linalg.solve(rho * np.eye(d) + X[:k].T @ X[:k], X[:k].T @ u[:k])
            error = float(np.max(np.abs(state.weights - oracle)))
            prediction_error = abs(prediction - oracle_prediction)
            times.append(elapsed)
            errors.append(max(error, prediction_error))
            log({"event": "prefix", "case": case["name"], "prefix": k,
                 "prediction_before_update": prediction, "oracle_prediction": oracle_prediction,
                 "weights": state.weights.tolist(), "oracle_weights": oracle.tolist(),
                 "max_abs_weight_error": error, "prediction_error": prediction_error,
                 "update_seconds": elapsed, "array_state_bytes": state.memory_bytes})
        results.append({"case": case["name"], "prefixes": n,
                        "max_abs_error": max(errors),
                        "pass": max(errors) <= config["max_abs_prefix_error"],
                        "update_seconds_p50": float(np.quantile(times, .5)),
                        "update_seconds_p95": float(np.quantile(times, .95)),
                        "array_state_bytes": state.memory_bytes})
    # A mathematical control, not a measured utility comparison of real peers.
    phi = np.array([.8, .6])
    full = SignedRidgeState(2, 1.0)
    full.update(phi, 1.0)
    diagonal_weights = phi / (1.0 + phi * phi)
    menu = np.array([[.8, -.4], [-.2, .8]])
    ranking = {"event": "diagonal_ranking_control", "kind": "synthetic algebraic example",
               "training_feature": phi.tolist(), "target": 1.0, "query_menu": menu.tolist(),
               "full_scores": (menu @ full.weights).tolist(),
               "diagonal_scores": (menu @ diagonal_weights).tolist()}
    log(ranking)
    summary = {"status": "PASS" if tests.returncode == 0 and all(r["pass"] for r in results) else "FAIL",
               "unit_test_exit": tests.returncode, "cases": results,
               "diagonal_ranking_control": ranking, "real_api_calls": 0, "gpu_jobs": 0,
               "scientific_claim_allowed": False, "live_integration_complete": False,
               "source_unchanged": all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h
                                       for p, h in config["source_sha256"].items())}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))
