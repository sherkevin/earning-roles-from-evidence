"""Parent-side isolated public-profile read and trace verification."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence

from peerrolebench_metateam_profile_sidecar import MetaTeamAssignmentOffer


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_policy_read_worker.py"
SCHEMA = "peerrole-public-profile-read-v1"


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


__all__ = ["IsolatedPolicyReadTrace", "read_profiles_isolated"]
