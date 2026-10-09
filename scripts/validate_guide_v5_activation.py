#!/usr/bin/env python3
"""Fail-closed validation of the v5 activation manifest.

This validator is a pre-run guard. A successful invocation means that the manifest
is internally complete; it never asserts that the benchmark or method has scientific
evidence. Until every activation check is true, API/GPU execution must remain off.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_ARMS = {
    "uniform_no_update",
    "no_update",
    "raw_acceptance",
    "terminal_only",
    "contextual_trust_linear_full_public_phi",
    "task_conditioned_ridge",
    "pooled_controller_own_namespace",
    "RARE_frozen_card",
    "closest_published_adapter",
}
REQUIRED_CHECKS = {
    "all_roots_authority_material_scorer_pass",
    "three_structural_roots_pass",
    "three_independent_streams_per_root_arm_pass",
    "all_required_arms_live_parity_pass",
    "future_assignment_independent_y_pass",
    "common_cohort_or_randomized_transport_pass",
    "mde_lambda_precision_stopping_frozen",
    "complete_cost_and_denominator_pass",
    "clean_replay_pass",
    "independent_scientific_review_pass",
}


def load(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    return data


def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    if data.get("manifest_version") != "peerrolebench-guide-v5-activation-v0.3":
        errors.append("unexpected manifest_version")
    if data.get("guide_version") != "v5_20261008":
        errors.append("guide_version is not v5_20261008")
    if data.get("primary_track") != "ArtifactRole":
        errors.append("primary_track must be ArtifactRole")
    roots = data.get("root_slots")
    if not isinstance(roots, list) or len(roots) < 3:
        errors.append("at least three root slots are required")
    else:
        ids = [r.get("root_id") for r in roots if isinstance(r, dict)]
        signatures = [r.get("structural_signature") for r in roots if isinstance(r, dict)]
        if len(ids) != len(set(ids)):
            errors.append("root_id values must be unique")
        if len(signatures) != len(set(signatures)):
            errors.append("structural_signature values must be unique")
        for root in roots:
            if not isinstance(root, dict):
                errors.append("root slot must be an object")
                continue
            if not root.get("structural_signature"):
                errors.append(f"root {root.get('root_id')} lacks structural_signature")
            if int(root.get("independent_streams", 0)) < 0:
                errors.append(f"root {root.get('root_id')} has negative stream count")
            if root.get("status") not in {"QUALIFIED", "ACTIVE", "BLOCKED_ROOT_QUALIFICATION", "BLOCKED_LATER_Y_AND_PARITY", "CANDIDATE_NEXT_ZERO_CALL_QUALIFICATION"}:
                errors.append(f"root {root.get('root_id')} has unknown status")
            if root.get("status") != "QUALIFIED":
                blockers.append(f"root:{root.get('root_id')}:{root.get('status')}")
    arms = data.get("required_arms")
    arm_ids = {a.get("arm_id") for a in arms or [] if isinstance(a, dict)}
    missing = EXPECTED_ARMS - arm_ids
    if missing:
        errors.append("missing required arms: " + ",".join(sorted(missing)))
    for arm in arms or []:
        if isinstance(arm, dict) and arm.get("status") not in {"LIVE_QUALIFIED", "NO_GO_ROW_REQUIRED"}:
            blockers.append(f"arm:{arm.get('arm_id')}:{arm.get('status')}")
    checks = data.get("activation_checks")
    if not isinstance(checks, dict):
        errors.append("activation_checks must be an object")
        checks = {}
    missing_checks = REQUIRED_CHECKS - set(checks)
    if missing_checks:
        errors.append("missing activation checks: " + ",".join(sorted(missing_checks)))
    false_checks = sorted(k for k in REQUIRED_CHECKS if checks.get(k) is not True)
    blockers.extend(f"check:{k}" for k in false_checks)
    if data.get("api_runs_allowed") is not False or data.get("gpu_runs_allowed") is not False:
        errors.append("api_runs_allowed and gpu_runs_allowed must remain false before activation")
    if any(checks.get(k) is not True for k in REQUIRED_CHECKS):
        if data.get("status") != "BLOCKED_PRE_ACTIVATION":
            errors.append("status must remain BLOCKED_PRE_ACTIVATION while a check is false")
        if data.get("scientific_claim_allowed") is not False:
            errors.append("scientific_claim_allowed must be false before activation")
    else:
        if data.get("status") != "READY_FOR_INDEPENDENT_ACTIVATION_REVIEW":
            errors.append("all checks true but status is not activation-review state")
    return {
        "valid": not errors,
        "errors": errors,
        "blockers": sorted(set(blockers)),
        "api_runs_allowed": data.get("api_runs_allowed"),
        "gpu_runs_allowed": data.get("gpu_runs_allowed"),
        "scientific_claim_allowed": data.get("scientific_claim_allowed"),
        "activation_ready": not errors and not false_checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    try:
        result = validate(load(args.manifest))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"valid": False, "errors": [str(exc)], "blockers": []}
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else (
        "VALID: activation ready" if result["valid"] and result["activation_ready"] else
        "VALID: manifest is fail-closed and remains blocked" if result["valid"] else
        "INVALID: " + "; ".join(result["errors"])
    ))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
