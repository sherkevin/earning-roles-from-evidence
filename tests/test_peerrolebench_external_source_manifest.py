import json
from pathlib import Path

from scripts.peerrolebench_build_external_source_manifest import build_source_receipt
from scripts.peerrolebench_shared_source_v2 import freeze_source_receipt


RUN = Path("experiments/logs/n03_c1_pipe3_bounded_live_20261006_v4")


def test_historical_source_manifest_is_parent_sealed_and_validated():
    source = build_source_receipt(RUN, "no_update", 0, "historical-c1-source-v1")
    assert source["source_seal"]["source_digest"] == source["source_receipt_digest"]
    assert source["provenance"]["policy_invariant"] is True
    assert source["target_status"] == "NOT_STARTED"
    validated = freeze_source_receipt(source, source["source_receipt_digest"])
    assert validated["projection_version"] == "shared-source-projection-v2"


def test_manifest_rejects_external_digest_mutation():
    source = build_source_receipt(RUN, "no_update", 0, "historical-c1-source-v1")
    source["judgment"]["decision"] = "reject_redo"
    try:
        freeze_source_receipt(source, source["source_receipt_digest"])
    except ValueError as exc:
        assert "source payload does not match external source seal" in str(exc)
    else:
        raise AssertionError("mutated source was accepted")
