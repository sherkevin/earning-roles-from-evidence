"""Zero-call qualification for the structural-owner responsibility gate.

This qualification intentionally exercises only typed sidecars and the pure
gate.  It does not call an LLM, execute a candidate, or update a policy.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_producer_scorer_v2_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_responsibility_label import producer_feedback_eligibility  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_two_stage_gate import evaluate_source_gate  # noqa: E402


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _score(status: str = "FAIL", label: int | None = 0) -> dict:
    return {"status": status, "label": label, "coverage_complete": True,
            "decision_complete": True}


def _outcome(status: str = "PASS") -> dict:
    return {"status": status, "coverage_complete": True,
            "decision_complete": True, "outcome_id": "y0", "quality_score": 1.0}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)

    materials = build_materials(load_pipe3(0))
    event_digest = "a" * 64
    config = {
        "qualification_version": "pipe3-structural-owner-gate-qualification-v1",
        "gate_versions": ["pipe3-responsibility-label-v2-structural-owner",
                           "two-stage-role-evidence-v3-structural-owner"],
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
        "scientific_claim_allowed": False, "python": platform.python_version(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    q = _score("FAIL", 0)
    y = _outcome("PASS")
    cases = [
        ("A1_producer_owner_judged_producer", [], "producer", True, "ELIGIBLE", "producer", True),
        ("A2_producer_owner_judged_recipient", [], "recipient", True, "ELIGIBLE", "producer", False),
        ("A3_recipient_only_judged_producer", ["processor.py"], "producer", True, "PENDING_ATTRIBUTION", "recipient", False),
        ("A4_mixed_owner", ["producer.py", "processor.py"], "producer", True, "UNKNOWN", "mixed", False),
        ("A5_no_registered_attribution", [], "producer", False, "PENDING_ATTRIBUTION", "unknown", None),
        ("A6_producer_owner_judged_unknown", [], "unknown", True, "ELIGIBLE", "producer", None),
    ]
    results = []
    for name, changed_paths, target_role, registered, expected, expected_owner, expected_agreement in cases:
        judgment = {"target_role": target_role, "observed_artifact_sha256": event_digest,
                    "producer_defect_registered": registered, "decision": "accept"}
        action = {"changed_paths": changed_paths, "consumer_action": "use",
                  "used_artifact": True}
        gate = evaluate_source_gate(materials, q, judgment, action, y)
        simple = producer_feedback_eligibility(materials, q, judgment, action, y)
        result = {
            "case": name, "expected_status": expected, "expected_owner": expected_owner,
            "expected_judged_role_agrees": expected_agreement,
            "two_stage": gate.payload(), "simple_gate": simple,
            "passed": gate.status == expected and gate.structural_owner_role == expected_owner
            and gate.judged_role_agrees == expected_agreement
            and simple["producer_feedback_status"] == expected
            and simple["structural_owner_role"] == expected_owner,
        }
        results.append(result)

    duplicate_judgment = {"target_role": "recipient", "observed_artifact_sha256": event_digest,
                          "producer_defect_registered": True, "decision": "accept"}
    duplicate_action = {"changed_paths": [], "consumer_action": "use", "used_artifact": True}
    first = evaluate_source_gate(materials, q, duplicate_judgment, duplicate_action, y).payload()
    second = evaluate_source_gate(materials, q, duplicate_judgment, duplicate_action, y).payload()
    results.append({"case": "A7_duplicate_replay", "first": first, "second": second,
                    "passed": first == second})

    try:
        evaluate_source_gate(
            materials, q,
            {"target_role": "producer", "observed_artifact_sha256": event_digest,
             "producer_defect_registered": True},
            {"changed_paths": ["models.py"], "consumer_action": "use", "used_artifact": True}, y,
        )
    except ValueError as exc:
        results.append({"case": "A8_contract_mutation", "status": "UNKNOWN",
                        "error": str(exc), "evidence_published": False,
                        "policy_update_allowed": False, "passed": True})
    else:
        results.append({"case": "A8_contract_mutation", "status": "FAIL",
                        "evidence_published": True, "policy_update_allowed": True,
                        "passed": False})

    summary = {
        **config, "status": "QUALIFIED_OFFLINE" if all(row["passed"] for row in results) else "FAILED_OFFLINE",
        "passed": all(row["passed"] for row in results), "case_count": len(results),
        "results": results, "materials_digest": _digest(materials),
        "remaining_gates": [
            "update active live cards to carry explicit structural owner registration",
            "re-run bounded same-information live comparison with judged-role disagreement logged",
            "independent roots, baseline parity, later-use and quality-cost confirmation remain open",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for row in results:
            handle.write(json.dumps({"timestamp_utc": config["created_at_utc"],
                                     "event_type": "structural_owner_case", "payload": row},
                                    ensure_ascii=False) + "\n")
    print(json.dumps({"passed": summary["passed"], "case_count": len(results),
                      "llm_calls": 0, "gpu_jobs": 0,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
