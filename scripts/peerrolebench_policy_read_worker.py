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


def main() -> int:
    try:
        request = json.load(sys.stdin)
        response = read(request)
        sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")
        return 0
    except Exception as exc:
        sys.stdout.write(json.dumps({"schema_version": SCHEMA, "status": "UNKNOWN", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
