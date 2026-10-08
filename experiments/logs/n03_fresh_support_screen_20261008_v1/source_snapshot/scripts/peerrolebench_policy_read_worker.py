"""Small isolated public-profile reader used by the PIPE3 runner.

The worker receives only the sealed public offer payload.  It does not import
the scorer, ledger, actor source, or private attribution gate.  Its response
is an attestation that the public profile IDs and read cut were consumed.  A
separate process is an audit boundary for the non-adversarial runner; it is
not claimed to be a hostile-code sandbox.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from typing import Any, Mapping


SCHEMA = "peerrole-public-profile-read-v1"
SOURCE_OFFER_SCHEMA = "peerrole-source-bound-public-read-v1"
ROLE_EVIDENCE_SCHEMA = "peerrole-role-evidence-read-v1"
SOURCE_OFFER_KEYS = frozenset({
    "offer_id", "task_id", "task_index", "role", "context_key", "candidate_keys",
    "evidence_ids", "evidence_version", "public_rows", "available_index", "watermark_schema",
})
SOURCE_ROW_KEYS = frozenset({
    "feedback_id", "source_event_id", "source", "candidate_key", "evidence_version",
    "source_index", "arrival_index", "arrived_at", "delay", "action", "disposition",
    "provenance", "label", "supersedes", "unknown_reason",
})
ROLE_EVIDENCE_OFFER_KEYS = frozenset({
    "schema", "offer_id", "task_id", "task_index", "role", "context_key",
    "candidate_keys", "evidence_ids", "evidence_version", "public_evidence",
    "available_index", "watermark_schema", "candidate_registry_digest",
})
ROLE_EVIDENCE_ROW_KEYS = frozenset({
    "evidence_id", "candidate_key", "role", "source_task_index", "delivery_id",
    "judgment_id", "action_id", "outcome_id", "artifact_sha256", "judgment",
    "action", "outcome_status", "quality_score", "available_index",
})


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read(request: Mapping[str, Any]) -> dict[str, Any]:
    if request.get("schema_version") != SCHEMA:
        raise ValueError("unsupported policy-read schema")
    offer_digest = request.get("offer_digest")
    profile_ids = request.get("profile_ids")
    read_cut = request.get("read_cut")
    profiles = request.get("profiles")
    if not isinstance(offer_digest, str) or len(offer_digest) != 64:
        raise ValueError("offer_digest must be a SHA-256 digest")
    if not isinstance(profile_ids, list) or profile_ids != sorted(set(profile_ids)) or not all(isinstance(v, str) and v for v in profile_ids):
        raise ValueError("profile_ids must be sorted unique strings")
    if type(read_cut) is not int or read_cut < 0:
        raise ValueError("read_cut must be a non-negative integer")
    if not isinstance(profiles, list) or len(profiles) != len(profile_ids):
        raise ValueError("public profile payload count does not match profile_ids")
    seen = []
    for profile in profiles:
        if not isinstance(profile, Mapping) or profile.get("profile_id") not in profile_ids:
            raise ValueError("public profile identity mismatch")
        if profile.get("profile_id") in seen:
            raise ValueError("duplicate public profile")
        available = profile.get("available_index")
        if type(available) is not int or available > read_cut or available < 0:
            raise ValueError("profile is not available at read cut")
        seen.append(profile["profile_id"])
    if sorted(seen) != profile_ids:
        raise ValueError("public profile IDs are not consumed in canonical order")
    public_digest = digest({"offer_digest": offer_digest, "profile_ids": profile_ids, "read_cut": read_cut, "profiles": profiles})
    policy_input_digest = digest({"offer_digest": offer_digest, "profile_ids": profile_ids, "read_cut": read_cut})
    return {
        "schema_version": SCHEMA, "status": "PASS", "offer_digest": offer_digest,
        "profile_ids": profile_ids, "read_cut": read_cut,
        "policy_input_digest": policy_input_digest, "public_profiles_digest": public_digest,
    }


def read_source_offer(request: Mapping[str, Any]) -> dict[str, Any]:
    """Read one source-bound public bundle without importing private state."""
    if request.get("schema_version") != SOURCE_OFFER_SCHEMA:
        raise ValueError("unsupported source-offer read schema")
    offer = request.get("offer")
    if not isinstance(offer, dict) or set(offer) != SOURCE_OFFER_KEYS:
        raise ValueError("source offer must contain exactly the public offer fields")
    if offer.get("watermark_schema") != "global-event-index-v1":
        raise ValueError("unsupported source-offer watermark schema")
    candidate_keys = offer.get("candidate_keys")
    if (not isinstance(candidate_keys, list) or candidate_keys != sorted(set(candidate_keys))
            or not all(isinstance(value, str) and value for value in candidate_keys)):
        raise ValueError("source-offer candidate menu must be sorted unique strings")
    rows = offer.get("public_rows")
    if not isinstance(rows, list):
        raise ValueError("source-offer public_rows must be a list")
    seen_feedback = set()
    for row in rows:
        if not isinstance(row, dict) or not set(row) <= SOURCE_ROW_KEYS:
            raise ValueError("source-offer row contains private or unknown fields")
        if not {"feedback_id", "source_event_id", "candidate_key", "arrival_index"} <= set(row):
            raise ValueError("source-offer row is missing public identity fields")
        if row["candidate_key"] not in candidate_keys:
            raise ValueError("source-offer row references an unknown candidate")
        if not row["feedback_id"] or row["feedback_id"] in seen_feedback:
            raise ValueError("source-offer feedback ids must be unique")
        seen_feedback.add(row["feedback_id"])
    for name in ("offer_record_hash", "bundle_digest", "policy_input_digest"):
        value = request.get(name)
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"{name} must be a SHA-256 digest")
    if request["bundle_digest"] != digest(offer):
        raise ValueError("source-offer bundle digest does not match payload")
    read_cut = request.get("read_cut")
    if type(read_cut) is not int or read_cut < int(offer["available_index"]):
        raise ValueError("read_cut is before source-offer availability")
    expected_policy_input = digest({
        "bundle_digest": request["bundle_digest"],
        "candidate_keys": candidate_keys,
        "read_cut": read_cut,
    })
    if request["policy_input_digest"] != expected_policy_input:
        raise ValueError("source-offer policy input digest does not match payload")
    return {
        "status": "PASS", "schema_version": SOURCE_OFFER_SCHEMA,
        "offer_id": offer["offer_id"], "offer_record_hash": request["offer_record_hash"],
        "bundle_digest": request["bundle_digest"], "candidate_keys": candidate_keys,
        "task_id": offer["task_id"], "task_index": offer["task_index"],
        "role": offer["role"], "context_key": offer["context_key"],
        "evidence_ids": offer["evidence_ids"], "evidence_version": offer["evidence_version"],
        "available_index": offer["available_index"], "watermark_schema": offer["watermark_schema"],
        "read_cut": read_cut, "policy_input_digest": request["policy_input_digest"],
        "public_rows_digest": digest({"public_rows": rows}),
    }


def read_role_evidence_offer(request: Mapping[str, Any]) -> dict[str, Any]:
    """Read a native RoleEvidenceUpdate projection, without updater access."""
    if request.get("schema_version") != ROLE_EVIDENCE_SCHEMA:
        raise ValueError("unsupported role-evidence read schema")
    offer = request.get("offer")
    if not isinstance(offer, dict) or set(offer) != ROLE_EVIDENCE_OFFER_KEYS:
        raise ValueError("role-evidence offer has an unexpected schema")
    if offer.get("schema") != "peerrole-role-evidence-offer-v1" or offer.get("watermark_schema") != "global-event-index-v1":
        raise ValueError("unsupported role-evidence offer version")
    candidate_keys = offer.get("candidate_keys")
    if (not isinstance(candidate_keys, list) or candidate_keys != sorted(set(candidate_keys))
            or not all(isinstance(value, str) and value for value in candidate_keys)):
        raise ValueError("role-evidence candidate menu must be sorted unique strings")
    evidence_ids = offer.get("evidence_ids")
    if (not isinstance(evidence_ids, list) or evidence_ids != sorted(set(evidence_ids))
            or not all(isinstance(value, str) and value for value in evidence_ids)):
        raise ValueError("role-evidence ids must be sorted unique strings")
    rows = offer.get("public_evidence")
    if not isinstance(rows, list) or len(rows) != len(evidence_ids):
        raise ValueError("role-evidence row count does not match evidence ids")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != ROLE_EVIDENCE_ROW_KEYS:
            raise ValueError("role-evidence row contains private or unknown fields")
        if row["evidence_id"] not in evidence_ids or row["evidence_id"] in seen:
            raise ValueError("role-evidence row identity mismatch")
        if row["candidate_key"] not in candidate_keys:
            raise ValueError("role-evidence row references an unknown candidate")
        if row["role"] != offer["role"]:
            raise ValueError("role-evidence row role does not match offer role")
        if not isinstance(row["artifact_sha256"], str) or len(row["artifact_sha256"]) != 64:
            raise ValueError("role-evidence artifact digest is invalid")
        if int(row["source_task_index"]) >= int(offer["task_index"]):
            raise ValueError("role-evidence source is not before target task")
        if int(row["available_index"]) > int(offer["available_index"]):
            raise ValueError("role-evidence row exceeds offer watermark")
        seen.add(str(row["evidence_id"]))
    if sorted(seen) != evidence_ids:
        raise ValueError("role-evidence ids do not cover public rows")
    for name in ("offer_record_hash", "bundle_digest", "policy_input_digest"):
        value = request.get(name)
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"{name} must be a SHA-256 digest")
    if request["bundle_digest"] != digest(offer):
        raise ValueError("role-evidence bundle digest does not match payload")
    read_cut = request.get("read_cut")
    if type(read_cut) is not int or read_cut < int(offer["available_index"]):
        raise ValueError("read cut is before role-evidence availability")
    expected_policy_input = digest({
        "bundle_digest": request["bundle_digest"],
        "candidate_keys": candidate_keys,
        "evidence_ids": evidence_ids,
        "read_cut": read_cut,
    })
    if request["policy_input_digest"] != expected_policy_input:
        raise ValueError("role-evidence policy input digest does not match payload")
    return {
        "status": "PASS", "schema_version": ROLE_EVIDENCE_SCHEMA,
        "offer_id": offer["offer_id"], "offer_record_hash": request["offer_record_hash"],
        "bundle_digest": request["bundle_digest"], "candidate_keys": candidate_keys,
        "evidence_ids": evidence_ids, "task_id": offer["task_id"], "task_index": offer["task_index"],
        "role": offer["role"], "context_key": offer["context_key"],
        "evidence_version": offer["evidence_version"], "available_index": offer["available_index"],
        "watermark_schema": offer["watermark_schema"], "read_cut": read_cut,
        "candidate_registry_digest": offer["candidate_registry_digest"],
        "policy_input_digest": request["policy_input_digest"],
        "public_evidence_digest": digest({"public_evidence": rows}),
    }


def main() -> int:
    try:
        request = json.load(sys.stdin)
        if request.get("schema_version") == SOURCE_OFFER_SCHEMA:
            response = read_source_offer(request)
        elif request.get("schema_version") == ROLE_EVIDENCE_SCHEMA:
            response = read_role_evidence_offer(request)
        else:
            response = read(request)
        sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
        return 0
    except Exception as exc:
        sys.stdout.write(json.dumps({"schema_version": SCHEMA, "status": "UNKNOWN", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
