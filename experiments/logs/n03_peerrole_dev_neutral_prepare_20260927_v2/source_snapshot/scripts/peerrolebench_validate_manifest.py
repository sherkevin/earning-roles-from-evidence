"""Validate the candidate benchmark/baseline manifest without running experiments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_BASELINES = {
    "uniform", "no_update", "raw_acceptance", "terminal_only",
    "contextual_trust", "pooled_controller", "RARE",
}
REQUIRED_SHARED_FLAGS = {
    "same_candidate_set", "same_propensity_stream", "same_model_and_request_budget",
    "same_legal_history", "same_delay_and_reordering", "same_full_cost_accounting",
}


def validate(manifest: dict) -> dict:
    errors: list[str] = []
    if manifest.get("manifest_version") != "peerrolebench-benchmark-baseline-candidate-v1":
        errors.append("manifest_version")
    if manifest.get("status") != "CANDIDATE_NOT_FROZEN":
        errors.append("status_must_remain_candidate")
    roots = manifest.get("roots")
    if not isinstance(roots, list) or len(roots) < 2:
        errors.append("at_least_two_roots")
        roots = []
    root_ids = [root.get("root_id") for root in roots if isinstance(root, dict)]
    task_ids = [root.get("task_id") for root in roots if isinstance(root, dict)]
    signatures = [root.get("structural_signature") for root in roots if isinstance(root, dict)]
    if len(root_ids) != len(set(root_ids)):
        errors.append("duplicate_root_id")
    if len(task_ids) != len(set(task_ids)):
        errors.append("duplicate_task_id")
    if len(signatures) != len(set(signatures)):
        errors.append("duplicate_structural_signature")
    splits = {root.get("split") for root in roots if isinstance(root, dict)}
    if splits != {"development", "confirmation"}:
        errors.append("development_confirmation_split")
    if not set(manifest.get("baselines", [])) >= REQUIRED_BASELINES:
        errors.append("baseline_matrix_incomplete")
    shared = manifest.get("shared_information_contract", {})
    for key in REQUIRED_SHARED_FLAGS:
        if shared.get(key) is not True:
            errors.append(f"shared_information:{key}")
    if shared.get("private_scorer_visible_to_policy") is not False:
        errors.append("private_scorer_visibility")
    if shared.get("future_outcome_visible_before_update") is not False:
        errors.append("future_outcome_visibility")
    if manifest.get("scientific_claim_allowed") is not False:
        errors.append("scientific_claim_gate")
    if manifest.get("gpu_jobs_allowed") is not False:
        errors.append("gpu_gate")
    if manifest.get("real_api_runs_allowed") is not False:
        errors.append("api_gate")
    return {"valid": not errors, "errors": errors,
            "root_count": len(roots), "baseline_count": len(manifest.get("baselines", []))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
