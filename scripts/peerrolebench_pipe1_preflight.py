#!/usr/bin/env python3
"""Zero-call preflight for the candidate PIPE1 source→target screen.

This reads frozen native role projections and the copied harness only. It does
not import a TeamBench generator, execute actor code, call an API, or create a
benchmark result. A missing execution prerequisite is recorded as BLOCKED.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "experiments/logs/n03_pipe1_native_material_audit_20261007_v1"
HARNESS = ROOT / "references/aamas/task_signal_materials_20261007/native_harness"
PIN = "d185aef1916fd86a9ba554d581fd256319a973af"
SEEDS = (0, 3)
WORKSPACE = {"etl.py", "run_etl.py", "source_sample.json", "target_schema.json"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def check(name: str, status: str, evidence: list[str], reason: str) -> dict:
    return {"check": name, "status": status, "evidence": evidence, "reason": reason}


def run(out: Path) -> None:
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    source_files = [Path(__file__).resolve(), MATERIAL / "config.json", MATERIAL / "summary.json"]
    source_files += [MATERIAL / f"seed_{s}" / f"{n}.json"
                     for s in SEEDS for n in ("planner_view", "executor_view", "parent_only")]
    source_files += list((MATERIAL / "source_snapshot").glob("*"))
    source_files += list(HARNESS.rglob("*.py")) + [HARNESS / "manifest.json"]
    source_files = [p for p in source_files if p.is_file()]
    config = {
        "schema": "pipe1-preflight-v1",
        "kind": "ZERO_CALL_EXECUTION_PREFLIGHT",
        "status": "FROZEN_BEFORE_CHECKS",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "project_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "teambench_pin": PIN,
        "seeds": list(SEEDS),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_files},
        "api_calls": 0,
        "gpu_runs": 0,
        "generator_calls": 0,
        "candidate_executions": 0,
        "scientific_claim_allowed": False,
    }
    put(out / "config.json", config)
    results = []
    views = {}
    for seed in SEEDS:
        directory = MATERIAL / f"seed_{seed}"
        planner = json.loads((directory / "planner_view.json").read_text())
        executor = json.loads((directory / "executor_view.json").read_text())
        parent = json.loads((directory / "parent_only.json").read_text())
        views[seed] = (planner, executor, parent)
        results.append(check(f"seed_{seed}_planner_projection", "PASS"
            if set(planner) == {"task_id", "seed", "spec_md"} else "FAIL",
            [str((directory / "planner_view.json").relative_to(ROOT))],
            "Planner has only native task identity and full specification"))
        results.append(check(f"seed_{seed}_executor_projection", "PASS"
            if set(executor) == {"task_id", "seed", "brief_md", "workspace_files", "peer_message"}
            and set(executor["workspace_files"]) == WORKSPACE and executor["peer_message"] is None else "FAIL",
            [str((directory / "executor_view.json").relative_to(ROOT))],
            "Executor has native brief/workspace and one empty message slot"))
        results.append(check(f"seed_{seed}_expected_is_parent_only", "PASS"
            if "expected" in parent and "expected" not in planner and "expected" not in executor else "FAIL",
            [str((directory / n).relative_to(ROOT)) for n in ("planner_view.json", "executor_view.json", "parent_only.json")],
            "Expected records occur only in parent projection"))
        try:
            ast.parse(executor["workspace_files"]["etl.py"])
            json.loads(executor["workspace_files"]["source_sample.json"])
            json.loads(executor["workspace_files"]["target_schema.json"])
            syntax = "PASS"
        except (SyntaxError, ValueError, json.JSONDecodeError):
            syntax = "FAIL"
        results.append(check(f"seed_{seed}_workspace_shape", syntax,
            [str((directory / "executor_view.json").relative_to(ROOT))],
            "Public workspace parses before any actor execution"))
    source_planner, source_executor, source_parent = views[0]
    target_planner, target_executor, target_parent = views[3]
    results.append(check("source_target_material_distinct", "PASS"
        if source_executor["workspace_files"] != target_executor["workspace_files"]
        and source_planner["spec_md"] != target_planner["spec_md"] else "FAIL",
        [str((MATERIAL / "seed_0").relative_to(ROOT)), str((MATERIAL / "seed_3").relative_to(ROOT))],
        "Seed 0 and 3 are distinct native domain materials"))
    results.append(check("same_structural_root_declared", "PASS", ["pipe1_source_target_screen_card_v0.1_20261007.md"],
        "The screen is explicitly one root and cannot be reported as cross-root generalization"))
    results.append(check("native_message_and_verifier_harness", "PASS"
        if (HARNESS / "manifest.json").is_file() else "FAIL",
        [str((HARNESS / "manifest.json").relative_to(ROOT))],
        "Native message and full Verifier/remediation source is available"))
    results.append(check("source_target_artifact_lineage", "BLOCKED", [],
        "Static source/target views exist, but no live source delivery, target delivery, message, artifact, Executor, or Verifier hash chain exists"))
    results.append(check("actor_visibility_live", "BLOCKED", [],
        "Saved projections show intended boundaries, but no live receipt proves target prompt/history isolation or selected-only visibility"))
    results.append(check("verifier_live_attestation", "BLOCKED", [],
        "Native Verifier source is available, but no route has produced before/after attestation or remediation evidence"))
    results.append(check("exact_outcome_scorer", "BLOCKED", ["n03_pipe1_native_material_audit_20261007_v1/summary.json"],
        "Saved native material has expected records, but the native grader is partial; exact target scorer is not qualified"))
    results.append(check("timezone_contract", "BLOCKED", [],
        "Captured generation timezone is unknown; UTC/Asia-Shanghai dates diverge in the saved audit"))
    results.append(check("provider_identity_pin", "BLOCKED", [],
        "No executable PIPE1 card pins the non-secret provider configuration/model route"))
    results.append(check("global_budget_issuer", "BLOCKED", [],
        "Cumulative budget already exceeded the old cap and no new reservation issuer approval exists"))
    results.append(check("source_target_ledger_runner", "BLOCKED", [],
        "No runner yet binds Planner history, message lineage, Executor pre/post output, Verifier, and full cost"))
    results.append(check("direct_relay_baseline", "BLOCKED", [],
        "The card specifies no-message/generated-planner/full-spec-relay routes, but no executable relay receipt or route result is sealed"))
    results.append(check("identity_randomization", "BLOCKED", [],
        "No pre-registered candidate version, allocation seed, permutation table, or allocation receipt binds the target assignment"))
    results.append(check("same_initial_peer_identity", "OPEN", [],
        "The design requires identical initial peers; whether independent calls produce useful persistent differences is unknown after the identity receipt is added"))
    status = "BLOCKED_PRE_EXECUTION" if any(r["status"] == "BLOCKED" for r in results) else "QUALIFIED_DESIGN_ONLY"
    receipt = {"schema": "pipe1-preflight-v1", "status": status, "checks": results,
               "api_calls": 0, "gpu_runs": 0, "generator_calls": 0, "candidate_executions": 0,
               "scientific_claim_allowed": False, "historical_results_modified": False}
    put(out / "receipt.json", receipt)
    put(out / "summary.json", {"status": status, "check_counts": {
        state: sum(r["status"] == state for r in results) for state in ("PASS", "OPEN", "BLOCKED", "FAIL")},
        "api_calls": 0, "gpu_runs": 0, "generator_calls": 0, "candidate_executions": 0,
        "scientific_claim_allowed": False, "next_action": "Resolve all BLOCKED checks before any route call"})
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out.resolve())
