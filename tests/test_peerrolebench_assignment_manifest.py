from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_assignment_manifest import build_manifest, validate_manifest  # noqa: E402


ROWS = [
    {"event_type": "assignment_evidence_offer", "event_id": "offer-0", "offer_id": "offer-0",
     "decision_event_id": "", "record_hash": "a" * 64, "attestation_digest": "b" * 64},
    {"event_type": "decision_consumption_attestation", "event_id": "selection-0", "offer_id": "offer-0",
     "decision_event_id": "selection-0", "record_hash": "c" * 64, "attestation_digest": "d" * 64},
]


def test_aux_manifest_binds_offer_before_consumption():
    manifest = build_manifest(ROWS)
    root = validate_manifest(manifest, ROWS)
    assert root == manifest[-1]["manifest_record_hash"]
    assert root != "GENESIS"


def test_aux_manifest_rejects_consumption_before_offer_or_duplicate():
    with pytest.raises(ValueError, match="precedes"):
        build_manifest(list(reversed(ROWS)))
    with pytest.raises(ValueError, match="duplicate consumption"):
        build_manifest(ROWS + [dict(ROWS[1], event_id="selection-1", decision_event_id="selection-1")])


def test_aux_manifest_is_separate_from_native_event_types():
    from peerrolebench_policy_sidecar_manifest import build_manifest as native_build
    native = [{"ledger_record_hash": "a" * 64, "protocol_event_type": "peer_selection",
               "protocol_event_id": "s0", "sidecar_digest": "b" * 64}]
    assert native_build(native)[0]["protocol_event_type"] == "peer_selection"


def test_aux_manifest_rejects_tampered_previous_hash():
    manifest = build_manifest(ROWS)
    mutated = [dict(record) for record in manifest]
    mutated[1]["previous_hash"] = "f" * 64
    with pytest.raises(ValueError, match="hash-chain"):
        validate_manifest(mutated, ROWS)
