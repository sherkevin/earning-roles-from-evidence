"""Zero-call qualification for the fail-closed shared-source v2 seam."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_shared_source_v2 import (  # noqa: E402
    ARM_NAMES, canonical_source_digest, project_source_to_arms,
    validate_arm_projections, validate_selection_binding,
)


SEALED_DIGESTS = {
    "ELIGIBLE": "e704176f1c1e72595245c72a00ced823d78fef22b4db11df4316ca7b84e2826d",
    "PENDING_ATTRIBUTION": "c9653f6b975b3846ac28f7fa70fdd11d2fe25251e5da9b296855f5ae667dcbde",
    "UNKNOWN": "885b870038980efdd84692dd2153a5f3a6b455ec308524e94af56550195a218f",
}


def _source(status: str = "ELIGIBLE") -> dict:
    complete = status != "UNKNOWN"
    episode = "SOURCE_COMPLETE" if status == "ELIGIBLE" else ("STOPPED_PRE_TARGET" if complete else "SOURCE_INCOMPLETE")
    inclusion = "ITT_AND_ELIGIBLE" if status == "ELIGIBLE" else "ITT_ONLY"
    source = {
        "source_event_id": "pipe3-source-0", "task_id": "PIPE3_stream_processing",
        "root": "PIPE3_stream_processing", "seed": 0, "delivery_digest": "a" * 64,
        "judgment": {"decision": "accept", "target_role": "producer"},
        "action": {"consumer_action": "use", "changed_paths": []},
        "producer_score": {"status": "FAIL", "label": 0},
        "outcome": {"status": "PASS", "quality_score": 1.0},
        "gate": {"status": status, "structural_owner_role": "producer"},
        "cost": {
            "source_cost_id": "pipe3-source-0", "source_cost_units": 15.0,
            "target_cost_units": 0.0, "cost_status": "COMPLETE",
            "source_cost_units_observed": True,
        },
        "episode_status": episode, "gate_status": status, "estimand_inclusion": inclusion,
        "source_complete": complete, "target_started": False, "target_status": "NOT_STARTED",
        "provenance": {
            "policy_invariant": True, "artifact_digest": "a" * 64,
            "contract_digest": "b" * 64, "registry_digest": "c" * 64,
            "scorer_digest": "d" * 64, "prompt_digest": "e" * 64,
            "raw_response_digest": "f" * 64,
        },
        "source_seal": {"manifest_id": "sealed-pipe3-source-v1", "source_digest": SEALED_DIGESTS[status]},
    }
    source["source_receipt_digest"] = canonical_source_digest(source)
    assert source["source_receipt_digest"] == SEALED_DIGESTS[status]
    return source


def _binding() -> dict:
    binding = {
        "policy_decision_id": "decision-0", "native_selection_id": "native-0",
        "decision_digest": "1" * 64, "native_record_digest": "2" * 64,
        "candidate_registry_digest": "3" * 64, "policy_input_digest": "4" * 64,
        "state_before_digest": "5" * 64, "chosen_candidate": "peer-b@v1",
        "candidate_menu": ["peer-b@v1", "peer-c@v1"], "propensity": 0.5,
    }
    payload = dict(binding)
    import hashlib
    binding["binding_digest"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    config = {
        "qualification_version": "shared-source-projection-qualification-v2",
        "projection_version": "shared-source-projection-v2", "llm_calls": 0,
        "gpu_jobs": 0, "native_grader_invoked": False, "scientific_claim_allowed": False,
        "external_seal_manifest": "embedded test manifest; future live card must use sealed artifact manifest",
        "python": platform.python_version(), "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    results = []

    rows = project_source_to_arms(_source(), SEALED_DIGESTS["ELIGIBLE"], ARM_NAMES)
    results.append({"case": "V2-01_valid_external_seal", "result": validate_arm_projections(rows, SEALED_DIGESTS["ELIGIBLE"]), "passed": True})

    mutations = [
        ("V2-02_all_rows_nested_action_mutation", lambda row: row["action"].__setitem__("changed_paths", ["processor.py"])),
        ("V2-03_all_rows_delivery_mutation", lambda row: row.__setitem__("delivery_digest", "b" * 64)),
        ("V2-04_projection_digest_mutation", lambda row: row.__setitem__("arm_projection_digest", "c" * 64)),
        ("V2-05_namespace_arm_swap", lambda row: row.__setitem__("policy_namespace", "source:pipe3-source-0:policy:swapped")),
        ("V2-06_source_seal_mutation", lambda row: row["source_seal"].__setitem__("manifest_id", "forged")),
    ]
    for name, mutate in mutations:
        mutated = project_source_to_arms(_source(), SEALED_DIGESTS["ELIGIBLE"], ARM_NAMES)
        for row in mutated:
            mutate(row)
        try:
            validate_arm_projections(mutated, SEALED_DIGESTS["ELIGIBLE"])
        except ValueError as exc:
            results.append({"case": name, "status": "REJECTED", "error": str(exc), "passed": True})
        else:
            results.append({"case": name, "status": "ACCEPTED", "passed": False})

    for status in ("PENDING_ATTRIBUTION", "UNKNOWN"):
        projected = project_source_to_arms(_source(status), SEALED_DIGESTS[status], ARM_NAMES)
        report = validate_arm_projections(projected, SEALED_DIGESTS[status])
        results.append({"case": f"V2-07_{status.lower()}_denominator_state", "result": report, "passed": report["estimand_inclusion"] == "ITT_ONLY"})

    binding = _binding()
    results.append({"case": "V2-08_selection_binding_valid", "result": validate_selection_binding(binding), "passed": True})
    binding["chosen_candidate"] = "peer-x@v1"
    try:
        validate_selection_binding(binding)
    except ValueError as exc:
        results.append({"case": "V2-09_selection_binding_mutation", "status": "REJECTED", "error": str(exc), "passed": True})
    else:
        results.append({"case": "V2-09_selection_binding_mutation", "status": "ACCEPTED", "passed": False})

    summary = {**config, "status": "QUALIFIED_OFFLINE" if all(r["passed"] for r in results) else "FAILED_OFFLINE", "passed": all(r["passed"] for r in results), "case_count": len(results), "results": results}
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    with (output / "raw.jsonl").open("w") as handle:
        for row in results:
            handle.write(json.dumps({"event_type": "shared_source_v2_case", "payload": row}, ensure_ascii=False) + "\n")
    print(json.dumps({"passed": summary["passed"], "case_count": len(results), "llm_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
