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
from typing import Any, Optional, Tuple

from peerrolebench_pipe1_route_receipt import canonical_digest, validate_pipe1_route_receipt

ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "experiments/logs/n03_pipe1_native_material_audit_20261007_v1"
HARNESS = ROOT / "references/aamas/task_signal_materials_20261007/native_harness"
PIN = "d185aef1916fd86a9ba554d581fd256319a973af"
SEEDS = (0, 3)
WORKSPACE = {"etl.py", "run_etl.py", "source_sample.json", "target_schema.json"}
MATERIAL_BINDING_SCHEMA = "pipe1-material-binding-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def check(name: str, status: str, evidence: list[str], reason: str) -> dict:
    return {"check": name, "status": status, "evidence": evidence, "reason": reason}


def _display_path(path: Path) -> str:
    """Use a stable project-relative path where possible."""
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _material_payload(planner: dict[str, Any], executor: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    """Build the only material identity used by PIPE1 route binding.

    The payload is deliberately limited to the identity and hashes already
    captured by the frozen native audit.  It does not introduce domain labels,
    expected outputs, file paths, or provenance fields into the digest.
    """
    hashes = parent.get("hashes")
    if not isinstance(hashes, dict):
        raise ValueError("parent_only.hashes must be an object")
    expected_hash_keys = {"spec_md_sha256", "brief_md_sha256", "workspace_sha256"}
    if not expected_hash_keys.issubset(set(hashes)):
        raise ValueError(f"parent_only.hashes lacks required material hashes: {sorted(hashes)}")
    workspace = executor.get("workspace_files")
    if not isinstance(workspace, dict) or set(workspace) != WORKSPACE:
        raise ValueError("executor workspace does not match frozen PIPE1 workspace")
    task_id = planner.get("task_id")
    seed = planner.get("seed")
    if task_id != executor.get("task_id") or task_id != parent.get("task_id"):
        raise ValueError("task_id differs across frozen projections")
    if seed != executor.get("seed") or seed != parent.get("seed"):
        raise ValueError("seed differs across frozen projections")
    if not isinstance(planner.get("spec_md"), str) or not isinstance(executor.get("brief_md"), str):
        raise ValueError("frozen task text must be strings")
    calculated = {
        "spec_md_sha256": _sha_text(planner["spec_md"]),
        "brief_md_sha256": _sha_text(executor["brief_md"]),
        "workspace_sha256": {name: _sha_text(workspace[name]) for name in sorted(WORKSPACE)},
    }
    if any(hashes[key] != calculated[key] for key in expected_hash_keys):
        raise ValueError("frozen parent hashes do not match projected material")
    return {
        "task_id": task_id,
        "seed": seed,
        "spec_md_sha256": calculated["spec_md_sha256"],
        "brief_md_sha256": calculated["brief_md_sha256"],
        "workspace_sha256": calculated["workspace_sha256"],
    }


def build_material_binding(root: Path = MATERIAL) -> dict[str, Any]:
    """Derive a deterministic seed 0/3 binding from the frozen native audit."""
    root = root.resolve()
    materials: dict[str, Any] = {}
    for seed in SEEDS:
        directory = root / f"seed_{seed}"
        planner = json.loads((directory / "planner_view.json").read_text())
        executor = json.loads((directory / "executor_view.json").read_text())
        parent = json.loads((directory / "parent_only.json").read_text())
        payload = _material_payload(planner, executor, parent)
        materials[str(seed)] = {
            "task_id": payload["task_id"],
            "seed": payload["seed"],
            "material_digest": canonical_digest(payload),
            "payload": payload,
        }
    if set(materials) != {"0", "3"}:
        raise ValueError("PIPE1 material binding must contain exactly seeds 0 and 3")
    return {
        "schema": MATERIAL_BINDING_SCHEMA,
        "source": _display_path(root),
        "seeds": [0, 3],
        "materials": materials,
    }


def _read_material_binding(path: Optional[Path]) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    if path is None:
        return None, "No frozen PIPE1 material binding was supplied"
    path = path.resolve()
    try:
        if path.is_dir():
            candidate = build_material_binding(path)
            frozen = build_material_binding(MATERIAL)
            if candidate["materials"] != frozen["materials"]:
                return None, "Material binding does not match the frozen seed 0/3 audit"
            return candidate, None
        if path.is_file():
            value = json.loads(path.read_text())
            if not isinstance(value, dict) or value.get("schema") != MATERIAL_BINDING_SCHEMA:
                return None, "Material binding file has unsupported schema"
            frozen = build_material_binding(MATERIAL)
            if value.get("materials") != frozen["materials"]:
                return None, "Material binding does not match the frozen seed 0/3 audit"
            return value, None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        return None, f"Material binding could not be read: {type(exc).__name__}"
    return None, "Material binding path does not exist"


def _material_binding_check(receipt: dict[str, Any], path: Optional[Path]) -> tuple[dict, dict]:
    binding, read_error = _read_material_binding(path)
    metadata: dict[str, Any] = {"path": _display_path(path.resolve()) if path else None,
                                 "exists": bool(path and path.resolve().exists()),
                                 "schema": binding.get("schema") if binding else None}
    if read_error:
        status = "BLOCKED" if path is None else "FAIL"
        return check("material_binding", status, [], read_error), metadata
    materials = binding.get("materials") if isinstance(binding, dict) else None
    if not isinstance(materials, dict) or set(materials) != {"0", "3"}:
        return check("material_binding", "FAIL", [], "Binding must contain exactly frozen source seed 0 and target seed 3"), metadata
    errors: list[str] = []
    for role, seed in (("source", 0), ("target", 3)):
        expected = materials.get(str(seed))
        actual = receipt.get(role)
        if not isinstance(expected, dict) or not isinstance(actual, dict):
            errors.append(f"{role}: missing material record")
            continue
        expected_digest = expected.get("material_digest")
        if actual.get("task_id") != expected.get("task_id"):
            errors.append(f"{role}.task_id does not match frozen material")
        if actual.get("seed") != seed:
            errors.append(f"{role}.seed does not match frozen material")
        if actual.get("material_digest") != expected_digest:
            errors.append(f"{role}.material_digest does not match frozen material")
    if errors:
        metadata["errors"] = errors
        return check("material_binding", "FAIL", [], "; ".join(errors)), metadata
    metadata["material_digests"] = {seed: materials[seed].get("material_digest") for seed in ("0", "3")}
    return check("material_binding", "PASS", [_display_path(path.resolve())],
                 "Source seed 0 and target seed 3 match the frozen native material binding"), metadata


def _route_receipt_check(route_receipt: Optional[Path], material_binding: Optional[Path] = None) -> Tuple[dict, dict]:
    """Validate an optional operator-owned route receipt without executing it.

    The receipt is an eligibility precondition only.  A valid receipt contributes
    a PASS to the preflight, while the preflight still keeps the scientific gate
    closed until all independent execution checks pass.
    """
    if route_receipt is None:
        return (
            check("route_receipt", "BLOCKED", [],
                  "No PIPE1 route receipt was supplied; source-to-target lineage remains unverified"),
            {"path": None, "exists": False},
        )
    path = route_receipt.resolve()
    evidence = [_display_path(path)]
    if not path.is_file():
        return (
            check("route_receipt", "BLOCKED", evidence,
                  "The requested PIPE1 route receipt does not exist"),
            {"path": _display_path(path), "exists": False},
        )
    try:
        receipt = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return (
            check("route_receipt", "FAIL", evidence,
                  f"Route receipt could not be parsed: {type(exc).__name__}"),
            {"path": _display_path(path), "exists": True, "sha256": sha(path)},
        )
    result = validate_pipe1_route_receipt(receipt)
    if result.get("valid"):
        material_result, material_metadata = _material_binding_check(receipt, material_binding)
        metadata = {"path": _display_path(path), "exists": True, "sha256": sha(path),
                    "schema_version": result.get("schema_version"),
                    "material_binding": material_metadata}
        if material_result["status"] != "PASS":
            return check("route_receipt", material_result["status"], evidence,
                         material_result["reason"]), metadata
        return (
            check("route_receipt", "PASS", evidence,
                  "PIPE1 source seed 0 to target seed 3 receipt satisfies the zero-call route contract"),
            metadata,
        )
    return (
        check("route_receipt", "FAIL", evidence,
              "Route receipt fails closed: " + "; ".join(result.get("errors", [])[:5])),
        {"path": _display_path(path), "exists": True, "sha256": sha(path),
         "schema_version": result.get("schema_version"),
         "validation_errors": result.get("errors", [])},
    )


def run(out: Path, route_receipt: Optional[Path] = None, material_binding: Optional[Path] = None) -> None:
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    source_files = [Path(__file__).resolve(), MATERIAL / "config.json", MATERIAL / "summary.json"]
    source_files += [MATERIAL / f"seed_{s}" / f"{n}.json"
                     for s in SEEDS for n in ("planner_view", "executor_view", "parent_only")]
    source_files += list((MATERIAL / "source_snapshot").glob("*"))
    source_files += list(HARNESS.rglob("*.py")) + [HARNESS / "manifest.json"]
    if route_receipt is not None and route_receipt.is_file():
        source_files.append(route_receipt.resolve())
    if material_binding is not None:
        binding_path = material_binding.resolve()
        if binding_path.is_file():
            source_files.append(binding_path)
        elif binding_path.is_dir():
            source_files.extend(p for p in binding_path.rglob("*") if p.is_file())
    source_files = [p for p in source_files if p.is_file()]
    route_result, route_metadata = _route_receipt_check(route_receipt, material_binding)
    config = {
        "schema": "pipe1-preflight-v2",
        "kind": "ZERO_CALL_EXECUTION_PREFLIGHT",
        "status": "FROZEN_BEFORE_CHECKS",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "project_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "teambench_pin": PIN,
        "seeds": list(SEEDS),
        "source_sha256": {_display_path(p): sha(p) for p in source_files},
        "route_receipt": route_metadata,
        "api_calls": 0,
        "gpu_runs": 0,
        "generator_calls": 0,
        "candidate_executions": 0,
        "scientific_claim_allowed": False,
    }
    put(out / "config.json", config)
    results = []
    results.append(route_result)
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
    # Any failed prerequisite also fails closed.  A malformed route receipt
    # must never be hidden by the design-only status when other checks happen
    # to pass in a future preflight version.
    status = "BLOCKED_PRE_EXECUTION" if any(r["status"] in {"BLOCKED", "FAIL"} for r in results) else "QUALIFIED_DESIGN_ONLY"
    receipt = {"schema": "pipe1-preflight-v2", "status": status, "checks": results,
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
    parser.add_argument("--route-receipt", type=Path,
                        help="Optional zero-call PIPE1 source-to-target route receipt JSON")
    parser.add_argument("--material-binding", type=Path,
                        help="Frozen PIPE1 material-audit directory or binding JSON; required for a route PASS")
    args = parser.parse_args()
    run(args.out.resolve(), args.route_receipt.resolve() if args.route_receipt else None,
        args.material_binding.resolve() if args.material_binding else None)
