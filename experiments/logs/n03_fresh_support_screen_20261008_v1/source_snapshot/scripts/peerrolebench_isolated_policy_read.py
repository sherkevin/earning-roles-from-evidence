"""Parent-side isolated public-profile read and trace verification."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence

from peerrolebench_assignment_attestation import AssignmentEvidenceOffer
from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer
from peerrolebench_role_evidence_offer import RoleEvidenceOffer


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_policy_read_worker.py"
SCHEMA = "peerrole-public-profile-read-v1"
SOURCE_OFFER_SCHEMA = "peerrole-source-bound-public-read-v1"
ROLE_EVIDENCE_SCHEMA = "peerrole-role-evidence-read-v1"


@dataclass(frozen=True)
class IsolatedPolicyReadTrace:
    schema_version: str
    worker_sha256: str
    offer_digest: str
    profile_ids: tuple[str, ...]
    read_cut: int
    policy_input_digest: str
    public_profiles_digest: str
    isolated: bool = True


@dataclass(frozen=True)
class IsolatedSourceOfferReadTrace:
    schema_version: str
    worker_sha256: str
    offer_id: str
    offer_record_hash: str
    bundle_digest: str
    candidate_keys: tuple[str, ...]
    read_cut: int
    policy_input_digest: str
    public_rows_digest: str
    isolated: bool = True


@dataclass(frozen=True)
class IsolatedRoleEvidenceReadTrace:
    schema_version: str
    worker_sha256: str
    offer_id: str
    offer_record_hash: str
    bundle_digest: str
    candidate_keys: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    read_cut: int
    policy_input_digest: str
    public_evidence_digest: str
    isolated: bool = True


def read_profiles_isolated(
    offer: MetaTeamAssignmentOffer,
    profile_ids: Sequence[str],
    *,
    read_cut: int,
    timeout_seconds: float = 5.0,
) -> IsolatedPolicyReadTrace:
    selected = tuple(profile_ids)
    if selected != tuple(sorted(set(selected))):
        raise ValueError("profile_ids must be sorted and unique")
    known = {profile.profile_id: profile for profile in offer.profiles}
    if any(profile_id not in known for profile_id in selected):
        raise ValueError("profile is not in the sealed offer")
    if type(read_cut) is not int or read_cut < offer.read_cut:
        raise ValueError("read cut is before the sealed offer cut")
    request = {
        "schema_version": SCHEMA, "offer_digest": offer.offer_digest,
        "profile_ids": list(selected), "read_cut": read_cut,
        "profiles": [known[profile_id].payload() for profile_id in selected],
    }
    try:
        completed = subprocess.run(
            [sys.executable, str(WORKER)], input=json.dumps(request, ensure_ascii=False),
            text=True, capture_output=True, timeout=timeout_seconds, cwd=str(ROOT), check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("isolated policy reader timed out") from exc
    if completed.returncode != 0:
        raise ValueError(f"isolated policy reader failed: {completed.stdout.strip() or completed.stderr.strip()}")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("isolated policy reader returned invalid JSON") from exc
    if response.get("status") != "PASS" or response.get("schema_version") != SCHEMA:
        raise ValueError(f"isolated policy reader did not pass: {response}")
    if response.get("offer_digest") != offer.offer_digest or tuple(response.get("profile_ids", ())) != selected:
        raise ValueError("isolated policy reader identity mismatch")
    expected_input = hashlib.sha256(json.dumps(
        {"offer_digest": offer.offer_digest, "profile_ids": list(selected), "read_cut": read_cut},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()
    if response.get("policy_input_digest") != expected_input:
        raise ValueError("isolated policy reader input digest mismatch")
    return IsolatedPolicyReadTrace(
        schema_version=SCHEMA,
        worker_sha256=hashlib.sha256(WORKER.read_bytes()).hexdigest(),
        offer_digest=offer.offer_digest, profile_ids=selected, read_cut=read_cut,
        policy_input_digest=expected_input,
        public_profiles_digest=str(response["public_profiles_digest"]),
    )


def _source_offer_record_hash(offer: AssignmentEvidenceOffer, previous_aux_hash: str) -> str:
    if previous_aux_hash != "GENESIS" and (not isinstance(previous_aux_hash, str) or len(previous_aux_hash) != 64):
        raise ValueError("previous_aux_hash must be GENESIS or a SHA-256 digest")
    return hashlib.sha256(json.dumps({
        "record_version": "pipe3-assignment-offer-v1",
        "previous_aux_hash": previous_aux_hash,
        **offer.payload(),
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read_source_offer_isolated(
    source_offer: Any,
    *,
    read_cut: int,
    previous_aux_hash: str,
    timeout_seconds: float = 5.0,
) -> IsolatedSourceOfferReadTrace:
    """Read the exact source-bound AssignmentEvidenceOffer in a child process."""
    offer = getattr(source_offer, "offer", source_offer)
    if not isinstance(offer, AssignmentEvidenceOffer):
        raise TypeError("source_offer must expose an AssignmentEvidenceOffer")
    if type(read_cut) is not int or read_cut < offer.available_index:
        raise ValueError("read cut is before source-offer availability")
    expected_record_hash = _source_offer_record_hash(offer, previous_aux_hash)
    if offer.offer_record_hash != expected_record_hash:
        raise ValueError("source offer record hash is not bound to the auxiliary root")
    expected_policy_input = hashlib.sha256(json.dumps({
        "bundle_digest": offer.bundle_digest,
        "candidate_keys": list(offer.candidate_keys),
        "read_cut": read_cut,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    expected_rows_digest = hashlib.sha256(json.dumps(
        {"public_rows": [dict(row) for row in offer.public_rows]},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()
    request = {
        "schema_version": SOURCE_OFFER_SCHEMA,
        "offer": offer.payload(),
        "offer_record_hash": offer.offer_record_hash,
        "bundle_digest": offer.bundle_digest,
        "candidate_keys": list(offer.candidate_keys),
        "read_cut": read_cut,
        "policy_input_digest": expected_policy_input,
    }
    try:
        completed = subprocess.run(
            [sys.executable, str(WORKER)], input=json.dumps(request, ensure_ascii=False),
            text=True, capture_output=True, timeout=timeout_seconds, cwd=str(ROOT), check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("isolated source-offer reader timed out") from exc
    if completed.returncode != 0:
        raise ValueError(f"isolated source-offer reader failed: {completed.stdout.strip() or completed.stderr.strip()}")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("isolated source-offer reader returned invalid JSON") from exc
    if response.get("status") != "PASS" or response.get("schema_version") != SOURCE_OFFER_SCHEMA:
        raise ValueError(f"isolated source-offer reader did not pass: {response}")
    if response.get("offer_id") != offer.offer_id or response.get("offer_record_hash") != offer.offer_record_hash:
        raise ValueError("isolated source-offer identity mismatch")
    if response.get("bundle_digest") != offer.bundle_digest:
        raise ValueError("isolated source-offer bundle digest mismatch")
    if tuple(response.get("candidate_keys", ())) != offer.candidate_keys:
        raise ValueError("isolated source-offer candidate menu mismatch")
    for name, expected in (
        ("task_id", offer.task_id), ("task_index", offer.task_index),
        ("role", offer.role), ("context_key", offer.context_key),
        ("evidence_ids", list(offer.evidence_ids)), ("evidence_version", offer.evidence_version),
        ("available_index", offer.available_index), ("watermark_schema", offer.watermark_schema),
    ):
        if response.get(name) != expected:
            raise ValueError(f"isolated source-offer {name} mismatch")
    if response.get("read_cut") != read_cut or response.get("policy_input_digest") != expected_policy_input:
        raise ValueError("isolated source-offer policy input mismatch")
    if response.get("public_rows_digest") != expected_rows_digest:
        raise ValueError("isolated source-offer public rows digest mismatch")
    return IsolatedSourceOfferReadTrace(
        schema_version=SOURCE_OFFER_SCHEMA,
        worker_sha256=hashlib.sha256(WORKER.read_bytes()).hexdigest(),
        offer_id=offer.offer_id, offer_record_hash=offer.offer_record_hash,
        bundle_digest=offer.bundle_digest, candidate_keys=offer.candidate_keys,
        read_cut=read_cut, policy_input_digest=expected_policy_input,
        public_rows_digest=expected_rows_digest,
    )


def _role_evidence_offer_record_hash(offer: RoleEvidenceOffer, previous_aux_hash: str) -> str:
    if previous_aux_hash != "GENESIS" and (not isinstance(previous_aux_hash, str) or len(previous_aux_hash) != 64):
        raise ValueError("previous_aux_hash must be GENESIS or a SHA-256 digest")
    return hashlib.sha256(json.dumps({
        "record_version": "peerrole-role-evidence-offer-v1",
        "previous_aux_hash": previous_aux_hash,
        **offer.payload(),
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read_role_evidence_offer_isolated(
    offer: RoleEvidenceOffer,
    *,
    read_cut: int,
    previous_aux_hash: str,
    timeout_seconds: float = 5.0,
) -> IsolatedRoleEvidenceReadTrace:
    """Read the native role-evidence projection in a separate process."""
    if not isinstance(offer, RoleEvidenceOffer):
        raise TypeError("offer must be a RoleEvidenceOffer")
    if type(read_cut) is not int or read_cut < offer.available_index:
        raise ValueError("read cut is before role-evidence availability")
    expected_record_hash = _role_evidence_offer_record_hash(offer, previous_aux_hash)
    if offer.offer_record_hash != expected_record_hash:
        raise ValueError("role-evidence offer record hash is not bound to auxiliary root")
    expected_policy_input = hashlib.sha256(json.dumps({
        "bundle_digest": offer.bundle_digest,
        "candidate_keys": list(offer.candidate_keys),
        "evidence_ids": list(offer.evidence_ids),
        "read_cut": read_cut,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    expected_public_digest = hashlib.sha256(json.dumps(
        {"public_evidence": [dict(row) for row in offer.public_evidence]},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()
    request = {
        "schema_version": ROLE_EVIDENCE_SCHEMA,
        "offer": offer.payload(), "offer_record_hash": offer.offer_record_hash,
        "bundle_digest": offer.bundle_digest, "candidate_keys": list(offer.candidate_keys),
        "read_cut": read_cut, "policy_input_digest": expected_policy_input,
    }
    try:
        completed = subprocess.run(
            [sys.executable, str(WORKER)], input=json.dumps(request, ensure_ascii=False),
            text=True, capture_output=True, timeout=timeout_seconds, cwd=str(ROOT), check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("isolated role-evidence reader timed out") from exc
    if completed.returncode != 0:
        raise ValueError(f"isolated role-evidence reader failed: {completed.stdout.strip() or completed.stderr.strip()}")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("isolated role-evidence reader returned invalid JSON") from exc
    if response.get("status") != "PASS" or response.get("schema_version") != ROLE_EVIDENCE_SCHEMA:
        raise ValueError(f"isolated role-evidence reader did not pass: {response}")
    for name, expected in (
        ("offer_id", offer.offer_id), ("offer_record_hash", offer.offer_record_hash),
        ("bundle_digest", offer.bundle_digest), ("candidate_keys", list(offer.candidate_keys)),
        ("evidence_ids", list(offer.evidence_ids)), ("task_id", offer.task_id),
        ("task_index", offer.task_index), ("role", offer.role),
        ("context_key", offer.context_key), ("evidence_version", offer.evidence_version),
        ("available_index", offer.available_index), ("watermark_schema", offer.watermark_schema),
        ("candidate_registry_digest", offer.candidate_registry_digest),
        ("read_cut", read_cut), ("policy_input_digest", expected_policy_input),
        ("public_evidence_digest", expected_public_digest),
    ):
        if response.get(name) != expected:
            raise ValueError(f"isolated role-evidence {name} mismatch")
    return IsolatedRoleEvidenceReadTrace(
        schema_version=ROLE_EVIDENCE_SCHEMA,
        worker_sha256=hashlib.sha256(WORKER.read_bytes()).hexdigest(),
        offer_id=offer.offer_id, offer_record_hash=offer.offer_record_hash,
        bundle_digest=offer.bundle_digest, candidate_keys=offer.candidate_keys,
        evidence_ids=offer.evidence_ids, read_cut=read_cut,
        policy_input_digest=expected_policy_input, public_evidence_digest=expected_public_digest,
    )


__all__ = ["IsolatedPolicyReadTrace", "IsolatedSourceOfferReadTrace", "IsolatedRoleEvidenceReadTrace", "read_profiles_isolated", "read_source_offer_isolated", "read_role_evidence_offer_isolated"]
