from __future__ import annotations

import hashlib
from types import SimpleNamespace

import pytest

from scripts.peerrolebench_metateam_profile_sidecar import (
    MetaTeamProfile,
    PROFILE_SCHEMA,
    _digest,
    build_public_profile_fixture,
    replay_public_profile_fixture,
    reject_private_public_input,
)
from scripts.peerrolebench_baseline_policies import CandidateRef
from scripts.peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar


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


def decision_sidecar() -> DecisionSidecar:
    return DecisionSidecar(
        ledger_record_hash="a" * 64,
        protocol_event_type="peer_selection", protocol_event_id="s0",
        task_id="task", task_index=0, role="producer", event_id="e0",
        selector_id="selector",
        context_key="ctx",
        candidates=(CandidateRef("peer-a", "v1"), CandidateRef("peer-b", "v1")),
        base_scores=(0.2, 0.8), chosen_index=1,
        probabilities=(0.5, 0.5), propensity=0.5,
        state_version="state", encoder_version="enc", feature_schema="phi",
        policy_name="fixture", policy_version="v1", base_score_version="base",
        rng_algorithm="rng", rng_draw=0, selected_at=1.0,
    )


def feedback_sidecar() -> FeedbackSidecar:
    return FeedbackSidecar(
        ledger_record_hash="b" * 64,
        protocol_event_type="recipient_judgment", protocol_event_id="j0",
        feedback_id="f0", source_event_id="e0", selection_event_id="s0",
        delivery_id="d0", producer_id="peer-b", producer_version="v1",
        recipient_id="peer-r", source="recipient_judgment", arrived_at=5.0,
        delay=1.0, action="repair", disposition="eligible", provenance="public",
        label_mapping_version="judgment-v1", mapping_digest="c" * 64,
        responsibility_status="attributed", attribution_basis="contract-v1",
        label=0.5, arrival_index=5, action_id="a0", action_record_hash="d" * 64,
        artifact_sha256="e" * 64, delivery_record_hash="f" * 64,
        sidecar_version="peerrole-policy-sidecar-v4",
    )


def projection(candidate_key="peer-b@v1", source="recipient_judgment"):
    return SimpleNamespace(
        source=source, candidate_key=candidate_key,
        source_event_id="e0", disposition="eligible", provenance="public",
        arrival_index=5,
        public_payload=lambda: {
            "feedback_id": "f0", "source_event_id": "e0", "source": source,
            "candidate_key": candidate_key, "evidence_version": "evidence-v1",
            "source_index": 5, "arrival_index": 5, "arrived_at": 5.0,
            "delay": 1.0, "action": "repair", "disposition": "eligible",
            "provenance": "public", "label": 0.5,
        },
    )


def test_fixture_builder_binds_typed_selection_and_public_projection():
    result = build_public_profile_fixture(
        selection=decision_sidecar(), feedback_sidecar=feedback_sidecar(),
        public_projection=projection(), profile_id="p-builder", profile_revision=1,
        profile=make_profile().profile, parser_version="fixture-parser-v1",
        model_config_digest=h("model-config"),
    )
    assert result.candidate_key == "peer-b@v1"
    assert result.selected_candidate_key == "peer-b@v1"
    assert result.selection_event_id == "s0"
    assert result.source_arrival_index == 5


def test_fixture_builder_rejects_non_judgment_and_unselected_projection():
    with pytest.raises(ValueError, match="recipient judgment"):
        build_public_profile_fixture(
            selection=decision_sidecar(), feedback_sidecar=feedback_sidecar(),
            public_projection=projection(source="terminal_outcome"), profile_id="p", profile_revision=1,
            profile=make_profile().profile, parser_version="p",
            model_config_digest=h("model-config"),
        )
    with pytest.raises(ValueError, match="selected candidate"):
        build_public_profile_fixture(
            selection=decision_sidecar(), feedback_sidecar=feedback_sidecar(),
            public_projection=projection(candidate_key="peer-a@v1"), profile_id="p", profile_revision=1,
            profile=make_profile().profile, parser_version="p",
            model_config_digest=h("model-config"),
        )


def test_fixture_builder_rejects_availability_before_arrival():
    with pytest.raises(ValueError, match="availability"):
        build_public_profile_fixture(
            selection=decision_sidecar(), feedback_sidecar=feedback_sidecar(),
            public_projection=projection(), profile_id="p", profile_revision=1,
            profile=make_profile().profile, parser_version="p",
            model_config_digest=h("model-config"), available_index=4,
        )


def test_fixture_profile_replay_binds_source_and_digest():
    selection = decision_sidecar()
    feedback = feedback_sidecar()
    source = projection()
    profile = build_public_profile_fixture(
        selection=selection, feedback_sidecar=feedback, public_projection=source,
        profile_id="p-replay", profile_revision=1, profile=make_profile().profile,
        parser_version="fixture-parser-v1", model_config_digest=h("model-config"),
    )
    replayed = replay_public_profile_fixture(
        profile, selection=selection, feedback_sidecar=feedback, public_projection=source,
    )
    assert replayed.profile_digest == profile.profile_digest
    with pytest.raises(ValueError, match="selected candidate"):
        replay_public_profile_fixture(
            profile, selection=selection, feedback_sidecar=feedback,
            public_projection=projection(candidate_key="peer-a@v1"),
        )
