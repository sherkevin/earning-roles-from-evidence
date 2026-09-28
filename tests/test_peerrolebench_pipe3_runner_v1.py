from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary,
    auxiliary_manifest_root,
    make_offer,
)


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64


def registry():
    return [
        CandidateRegistryEntry("agent-a", "v1", DIGEST_A, "internal/model", DIGEST_B),
        CandidateRegistryEntry("agent-b", "v1", DIGEST_B, "internal/model", DIGEST_B),
        CandidateRegistryEntry("agent-c", "v1", DIGEST_C, "internal/model", DIGEST_B),
    ]


def test_boundary_seals_native_selection_and_auxiliary_consumption_separately():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    offer = make_offer(
        offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0",
        candidate_keys=("agent-b@v1", "agent-c@v1"), public_rows=(),
        evidence_version="pipe3-evidence-v1", available_index=0,
    )
    seal = boundary.choose_and_seal(
        offer=offer, native_selection_id="selection-0", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(3), state_version="state-0",
        encoder_version="encoder-0", feature_schema="features-0", policy_version="policy-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=True,
    )
    native_root, auxiliary_root = boundary.validate_selection_manifests()
    assert seal.native_selection.chosen_peer_id in {"agent-b", "agent-c"}
    assert seal.decision_sidecar.ledger_record_hash == boundary.ledger.events[-1]["record_hash"]
    assert native_root != "GENESIS"
    assert auxiliary_root != "GENESIS"
    assert boundary.native_manifest_rows[0]["protocol_event_type"] == "peer_selection"
    assert boundary.auxiliary_manifest_rows[0]["event_type"] == "assignment_evidence_offer"
    assert boundary.auxiliary_manifest_rows[1]["event_type"] == "decision_consumption_attestation"


def test_boundary_rejects_evidence_for_an_unselected_candidate():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    first_offer = make_offer(
        offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(), evidence_version="pipe3-evidence-v1", available_index=0,
    )
    first = boundary.choose_and_seal(
        offer=first_offer, native_selection_id="selection-0", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(3), state_version="state-0",
        encoder_version="encoder-0", feature_schema="features-0", policy_version="policy-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=True,
    )
    wrong = "agent-c@v1" if first.policy_selection.chosen.key == "agent-b@v1" else "agent-b@v1"
    row = {
        "feedback_id": "feedback-0", "source_event_id": first.policy_selection.event_id,
        "source": "recipient_judgment", "candidate_key": wrong, "evidence_version": "pipe3-evidence-v1",
        "source_index": 0, "arrival_index": 1, "arrived_at": 1.0, "delay": 1.0,
        "action": "accept", "disposition": "eligible", "provenance": "public", "label": 1.0,
    }
    offer = make_offer(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=("agent-a@v1", "agent-c@v1"),
        public_rows=(row,), evidence_version="pipe3-evidence-v1", available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    with pytest.raises(ValueError, match="selected candidate"):
        boundary.choose_and_seal(
            offer=offer, native_selection_id="selection-1", selector_id="agent-b", role="producer",
            base_scores=(0.0, 0.0), rng=np.random.default_rng(3), state_version="state-1",
            encoder_version="encoder-0", feature_schema="features-0", policy_version="policy-0",
            base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=1,
            selected_at=1.0, read_cut=1, decision_index=1, consume_evidence=True,
        )


def test_boundary_applies_selected_feedback_before_a_later_decision():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    first_offer = make_offer(
        offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(), evidence_version="pipe3-evidence-v1", available_index=0,
    )
    first = boundary.choose_and_seal(
        offer=first_offer, native_selection_id="selection-0", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(3), state_version="state-0",
        encoder_version="encoder-0", feature_schema="features-0", policy_version="policy-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=True,
    )
    row = {
        "feedback_id": "feedback-0", "source_event_id": first.policy_selection.event_id,
        "source": "recipient_judgment", "candidate_key": first.policy_selection.chosen.key,
        "evidence_version": "pipe3-evidence-v1", "source_index": 0, "arrival_index": 1,
        "arrived_at": 1.0, "delay": 1.0, "action": "accept", "disposition": "eligible",
        "provenance": "public", "label": 1.0,
    }
    second_offer = make_offer(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(row,), evidence_version="pipe3-evidence-v1", available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    boundary.choose_and_seal(
        offer=second_offer, native_selection_id="selection-1", selector_id="agent-a",
        role="producer", base_scores=(0.0, 0.0), rng=np.random.default_rng(4), state_version="state-1",
        encoder_version="encoder-0", feature_schema="features-0", policy_version="policy-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=1,
        selected_at=1.0, read_cut=1, decision_index=1, consume_evidence=True,
    )
    assert boundary.policy.updates == 1
    boundary.validate_selection_manifests()
