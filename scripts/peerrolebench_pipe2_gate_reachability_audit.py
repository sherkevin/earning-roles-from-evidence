"""Enumerate the responsibility-gate paths for the PIPE2 derived candidate.

This is a bounded, zero-call diagnostic.  It reuses the candidate material
and the two existing gates, but does not execute candidate code, call an LLM,
or mutate policy state.  The purpose is to expose structural reachability
before paying for a live episode: which ownership/action/defect combinations
can actually yield an eligible producer label, and where the canonical and
PIPE2-specific gates disagree.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_derived_material_adapter import (  # noqa: E402
    build_derived_materials,
    load_derived_pipe2,
)
from peerrolebench_pipe2_responsibility_label import (  # noqa: E402
    evaluate_pipe2_feedback,
)
from peerrolebench_two_stage_gate import evaluate_source_gate  # noqa: E402


VERSION = "pipe2-gate-reachability-audit-v1"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _artifact(seed: int, scenario: str) -> str:
    return sha256(f"PIPE2_data_pipeline:{seed}:{scenario}".encode())


def _score(artifact: str, *, status: str, label: int) -> dict[str, Any]:
    return {
        "status": status,
        "label": label,
        "quality_score": float(label),
        "coverage_complete": True,
        "decision_complete": True,
        "artifact_sha256": artifact,
    }


def _judgment(artifact: str, *, decision: str, defect: bool) -> dict[str, Any]:
    return {
        "decision": decision,
        "target_role": "producer",
        "observed_artifact_sha256": artifact,
        "coverage_complete": True,
        "decision_complete": True,
        "producer_defect_registered": defect,
    }


def _action(artifact: str, changed: list[str], *, action: str) -> dict[str, Any]:
    return {
        "consumer_action": action,
        "changed_paths": changed,
        "delivery_sha256": artifact,
        "used_artifact": True,
    }


def _outcome(artifact: str) -> dict[str, Any]:
    return {
        "status": "PASS",
        "artifact_sha256": artifact,
        "coverage_complete": True,
        "decision_complete": True,
    }


def scenarios() -> list[dict[str, Any]]:
    return [
        {"name": "registered_fail_direct_use_no_edit", "score": ("FAIL", 0),
         "defect": True, "decision": "accept", "action": "use", "changed": []},
        {"name": "registered_fail_direct_use_recipient_edit", "score": ("FAIL", 0),
         "defect": True, "decision": "accept", "action": "use",
         "changed": ["pipeline/transform.py"]},
        {"name": "registered_fail_rework_recipient_edit", "score": ("FAIL", 0),
         "defect": True, "decision": "accept_with_rework", "action": "repair",
         "changed": ["pipeline/transform.py"]},
        {"name": "registered_fail_direct_use_producer_edit", "score": ("FAIL", 0),
         "defect": True, "decision": "accept", "action": "use",
         "changed": ["pipeline/extract.py"]},
        {"name": "registered_fail_direct_use_mixed_edit", "score": ("FAIL", 0),
         "defect": True, "decision": "accept", "action": "use",
         "changed": ["pipeline/extract.py", "pipeline/transform.py"]},
        {"name": "pass_direct_use_no_edit", "score": ("PASS", 1),
         "defect": False, "decision": "accept", "action": "use", "changed": []},
        {"name": "pass_direct_use_recipient_edit", "score": ("PASS", 1),
         "defect": False, "decision": "accept", "action": "use",
         "changed": ["pipeline/transform.py"]},
        {"name": "legacy_producer_edit_direct_use", "score": ("PASS", 1),
         "defect": False, "decision": "accept", "action": "use",
         "changed": ["pipeline/extract.py"]},
    ]


def run_case(materials: dict[str, Any], seed: int, spec: dict[str, Any]) -> dict[str, Any]:
    artifact = _artifact(seed, spec["name"])
    status, label = spec["score"]
    score = _score(artifact, status=status, label=label)
    judgment = _judgment(artifact, decision=spec["decision"], defect=spec["defect"])
    action = _action(artifact, spec["changed"], action=spec["action"])
    outcome = _outcome(artifact)
    canonical = evaluate_source_gate(materials, score, judgment, action, outcome)
    pipe2 = evaluate_pipe2_feedback(
        materials,
        artifact_sha256=artifact,
        producer_score=score,
        judgment=judgment,
        action=action,
        outcome=outcome,
    )
    return {
        "scenario": spec["name"],
        "inputs": {"score_status": status, "score_label": label,
                   "defect_registered": spec["defect"],
                   "decision": spec["decision"], "consumer_action": spec["action"],
                   "changed_paths": spec["changed"]},
        "canonical": {"status": canonical.status,
                      "eligible": canonical.attribution_eligible,
                      "reason": canonical.reason,
                      "producer_changed": list(canonical.producer_paths_changed),
                      "recipient_changed": list(canonical.recipient_paths_changed)},
        "pipe2": {"status": pipe2["feedback_status"],
                  "eligible": pipe2["feedback_eligible"],
                  "reason": pipe2["reason"],
                  "producer_changed": pipe2["producer_owned_paths_changed"],
                  "recipient_changed": pipe2["recipient_owned_paths_changed"]},
        "status_disagrees": canonical.status != pipe2["feedback_status"]
        or canonical.attribution_eligible != pipe2["feedback_eligible"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    raw = out / "raw.jsonl"
    generated = load_derived_pipe2(args.seed)
    materials = build_derived_materials(args.seed)
    source_files = {
        role: {path: hashlib.sha256(text.encode()).hexdigest()
               for path, text in payload["source_files"].items()}
        for role, payload in materials["agent_payloads"].items()
    }
    config = {
        "audit_version": VERSION,
        "command": sys.argv,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "python": sys.version,
        "platform": platform.platform(),
        "seed": args.seed,
        "material_root_digest": generated.metadata["derived_root_digest"],
        "material_source_hashes": source_files,
        "canonical_gate_version": "two-stage-role-evidence-v2",
        "pipe2_gate_version": "pipe2-responsibility-label-v1",
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
        "purpose": "structural reachability and gate disagreement audit; no label/update",
    }
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    with raw.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps({"event_type": "config", "payload": config}, ensure_ascii=False) + "\n")
        cases = [run_case(materials, args.seed, spec) for spec in scenarios()]
        for case in cases:
            handle.write(json.dumps({"event_type": "case", "payload": case}, ensure_ascii=False) + "\n")
        summary = {
            "audit_version": VERSION,
            "seed": args.seed,
            "case_count": len(cases),
            "canonical_eligible": sum(case["canonical"]["eligible"] for case in cases),
            "pipe2_eligible": sum(case["pipe2"]["eligible"] for case in cases),
            "disagreement_count": sum(case["status_disagrees"] for case in cases),
            "disagreement_scenarios": [case["scenario"] for case in cases if case["status_disagrees"]],
            "scientific_claim_allowed": False,
            "policy_update_allowed": False,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        handle.write(json.dumps({"event_type": "summary", "payload": summary}, ensure_ascii=False) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
