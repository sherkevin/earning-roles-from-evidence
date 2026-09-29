from __future__ import annotations

import hashlib

import pytest

from scripts.peerrolebench_metateam_profile_sidecar import (
    MetaTeamProfile,
    PROFILE_SCHEMA,
    _digest,
    reject_private_public_input,
)


def h(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def make_profile(**overrides) -> MetaTeamProfile:
    values = dict(
        profile_id="p-1",
        profile_revision=1,
        adapter_variant="public",
        candidate_key="agent-a@v1",
        producer_id="agent-a",
        producer_version="v1",
        recipient_id="agent-r",
        selected_candidate_key="agent-a@v1",
        selection_event_id="sel-0",
        source_event_id="judgment-0",
        delivery_id="delivery-0",
        source_decision_index=0,
        source_arrival_index=2,
        available_index=2,
        source_disposition="eligible",
        source_provenance="public",
        source_input_digest=h("public-bundle"),
        profile_schema=PROFILE_SCHEMA,
        parser_version="parser-v1",
        model_config_digest=h("model-config"),
        profile={
            "reliability": "medium",
            "strengths": ["integration"],
            "weaknesses": ["ordering"],
            "communication_style": "concise",
            "notes": ["selected public event"],
        },
    )
    values.update(overrides)
    return MetaTeamProfile(**values)


def test_public_profile_schema_and_digest_are_stable():
    profile = make_profile()
    assert profile.profile_digest == _digest(profile.payload())
    assert profile.payload()["profile"]["reliability"] == "medium"


def test_profile_requires_selected_public_eligible_source():
    with pytest.raises(ValueError, match="eligible public"):
        make_profile(source_disposition="unknown")
    with pytest.raises(ValueError, match="eligible public"):
        make_profile(source_provenance="unknown")


def test_profile_cannot_be_visible_before_arrival():
    with pytest.raises(ValueError, match="before its source arrival"):
        make_profile(source_arrival_index=3, available_index=2)


def test_profile_consumption_requires_later_decision_and_watermark():
    profile = make_profile()
    attestation = profile.consume_before(decision_index=2, read_cut=2)
    assert attestation.attestation_digest == _digest(attestation.payload())
    with pytest.raises(ValueError, match="later decision"):
        profile.consume_before(decision_index=0, read_cut=2)
    with pytest.raises(ValueError, match="not visible"):
        profile.consume_before(decision_index=2, read_cut=1)
    with pytest.raises(ValueError, match="after the decision"):
        profile.consume_before(decision_index=1, read_cut=2)


def test_correction_is_new_profile_with_lineage():
    first = make_profile()
    second = make_profile(
        profile_id="p-2", profile_revision=2, source_arrival_index=4,
        available_index=4, supersedes_profile_id=first.profile_id,
    )
    assert second.supersedes_profile_id == first.profile_id
    assert second.profile_revision > first.profile_revision


def test_profile_schema_is_fixed_and_bounded():
    with pytest.raises(ValueError, match="exactly match"):
        make_profile(profile={"reliability": "high"})
    with pytest.raises(ValueError, match="at most 5"):
        make_profile(profile={
            "reliability": "high", "strengths": ["a"] * 6,
            "weaknesses": [], "communication_style": "ok", "notes": [],
        })


def test_public_input_rejects_hidden_or_posthoc_fields():
    with pytest.raises(ValueError, match="forbidden"):
        reject_private_public_input({"source_event_id": "j0", "terminal_score": 1.0})
    with pytest.raises(ValueError, match="trajectory"):
        reject_private_public_input({"source_event_id": "j0", "trajectory": "trace"})


def test_digest_changes_when_profile_payload_changes():
    profile = make_profile()
    mutated = profile.payload()
    mutated["profile"]["notes"].append("mutation")
    assert _digest(mutated) != profile.profile_digest
