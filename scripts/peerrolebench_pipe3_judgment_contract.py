"""Validation for responsibility-aware PIPE3 recipient judgments."""
from __future__ import annotations


TARGET_ROLES = {"producer", "recipient", "sink", "mixed", "unknown"}
DEFECT_TYPES = {"producer_contract", "recipient_integration", "sink_adoption", "mixed", "unknown"}


def validate_structured_judgment(value, artifact_digest, public_paths):
    if not isinstance(value, dict):
        raise ValueError("judgment must be an object")
    decision = value.get("decision")
    if decision not in {"accept", "accept_with_rework", "reject_redo"}:
        raise ValueError("invalid judgment decision")
    if value.get("observed_artifact_sha256") != artifact_digest:
        raise ValueError("judgment artifact digest mismatch")
    confidence = value.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        raise ValueError("judgment confidence must be in [0, 1]")
    target_role = value.get("target_role")
    if target_role not in TARGET_ROLES:
        raise ValueError("judgment target_role is invalid")
    target_paths = value.get("target_paths")
    if not isinstance(target_paths, list) or not all(isinstance(path, str) for path in target_paths):
        raise ValueError("judgment target_paths must be a list of strings")
    unknown_paths = set(target_paths) - set(public_paths)
    if unknown_paths:
        raise ValueError(f"judgment names paths outside public material: {sorted(unknown_paths)}")
    defect_type = value.get("defect_type")
    if defect_type not in DEFECT_TYPES:
        raise ValueError("judgment defect_type is invalid")
    evidence_refs = value.get("evidence_refs")
    if (not isinstance(evidence_refs, list) or not evidence_refs
            or not all(isinstance(ref, str) and ref for ref in evidence_refs)):
        raise ValueError("judgment evidence_refs must be a non-empty string list")
    return {
        "decision": decision,
        "confidence": float(confidence),
        "target_role": target_role,
        "target_paths": list(target_paths),
        "defect_type": defect_type,
        "evidence_refs": list(evidence_refs),
        "observed_artifact_sha256": artifact_digest,
        "repair_plan": str(value.get("repair_plan", "")),
        "rationale": str(value.get("rationale", "")),
    }
