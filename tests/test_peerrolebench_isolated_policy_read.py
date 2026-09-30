from pathlib import Path
import hashlib
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_isolated_policy_read import (  # noqa: E402
    read_profiles_isolated,
    read_source_offer_isolated,
)
from peerrolebench_isolated_policy_read_qualification import offer  # noqa: E402
from peerrolebench_pipe3_runner_v1 import make_offer  # noqa: E402
from peerrolebench_policy_read_worker import read_source_offer  # noqa: E402


def test_isolated_reader_returns_digest_bound_trace():
    sealed = offer()
    trace = read_profiles_isolated(sealed, ("profile-a-r1",), read_cut=2)
    assert trace.isolated is True
    assert trace.offer_digest == sealed.offer_digest
    assert trace.profile_ids == ("profile-a-r1",)


def test_isolated_reader_rejects_read_before_profile_available():
    with pytest.raises(ValueError):
        read_profiles_isolated(offer(), ("profile-a-r1",), read_cut=0)


def _source_offer(*, previous_aux_hash="f" * 64, available_index=0):
    return make_offer(
        offer_id="source-offer-test",
        task_id="PIPE3_stream_processing",
        task_index=1,
        role="producer",
        context_key="PIPE3:1",
        candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(),
        evidence_version="pipe3-evidence-v1",
        available_index=available_index,
        previous_aux_hash=previous_aux_hash,
    )


def test_isolated_reader_consumes_exact_source_bound_offer():
    source = _source_offer()
    trace = read_source_offer_isolated(source, read_cut=0, previous_aux_hash="f" * 64)
    assert trace.isolated is True
    assert trace.offer_id == source.offer_id
    assert trace.offer_record_hash == source.offer_record_hash
    assert trace.bundle_digest == source.bundle_digest
    assert trace.candidate_keys == source.candidate_keys
    assert trace.public_rows_digest


def test_isolated_reader_rejects_offer_not_bound_to_supplied_auxiliary_root():
    source = _source_offer()
    with pytest.raises(ValueError, match="not bound"):
        read_source_offer_isolated(source, read_cut=0, previous_aux_hash="e" * 64)


def test_isolated_reader_rejects_read_before_source_offer_watermark():
    source = _source_offer(available_index=2)
    with pytest.raises(ValueError, match="before source-offer availability"):
        read_source_offer_isolated(source, read_cut=1, previous_aux_hash="f" * 64)


def _source_worker_request(source, *, read_cut=0):
    policy_input = hashlib.sha256(json.dumps({
        "bundle_digest": source.bundle_digest,
        "candidate_keys": list(source.candidate_keys),
        "read_cut": read_cut,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return {
        "schema_version": "peerrole-source-bound-public-read-v1",
        "offer": source.payload(),
        "offer_record_hash": source.offer_record_hash,
        "bundle_digest": source.bundle_digest,
        "candidate_keys": list(source.candidate_keys),
        "read_cut": read_cut,
        "policy_input_digest": policy_input,
    }


def test_source_worker_recomputes_bundle_digest():
    source = _source_offer()
    request = _source_worker_request(source)
    request["bundle_digest"] = "0" * 64
    with pytest.raises(ValueError, match="bundle digest"):
        read_source_offer(request)


def test_source_worker_recomputes_policy_input_digest():
    source = _source_offer()
    request = _source_worker_request(source)
    request["policy_input_digest"] = "0" * 64
    with pytest.raises(ValueError, match="policy input digest"):
        read_source_offer(request)
