from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_policy_sidecar_manifest import build_manifest, validate_manifest  # noqa: E402


ROWS = [
    {"ledger_record_hash": "a" * 64, "protocol_event_type": "peer_selection",
     "protocol_event_id": "s0", "sidecar_digest": "b" * 64},
    {"ledger_record_hash": "c" * 64, "protocol_event_type": "terminal_outcome",
     "protocol_event_id": "o0", "sidecar_digest": "d" * 64},
]


def test_manifest_chain_and_exact_coverage():
    manifest = build_manifest(ROWS)
    root = validate_manifest(manifest, ROWS)
    assert root == manifest[-1]["manifest_record_hash"]
    assert root != "GENESIS"


def test_manifest_rejects_chain_tamper_and_missing_coverage():
    manifest = build_manifest(ROWS)
    tampered = [dict(row) for row in manifest]
    tampered[1]["previous_hash"] = "e" * 64
    with pytest.raises(ValueError, match="hash-chain"):
        validate_manifest(tampered, ROWS)
    with pytest.raises(ValueError, match="cover"):
        validate_manifest(manifest[:1], ROWS)


def test_manifest_rejects_duplicate_event_and_invalid_digest():
    with pytest.raises(ValueError, match="duplicate"):
        build_manifest(ROWS + [dict(ROWS[0])])
    with pytest.raises(ValueError, match="SHA-256"):
        build_manifest([{**ROWS[0], "sidecar_digest": "bad"}])
