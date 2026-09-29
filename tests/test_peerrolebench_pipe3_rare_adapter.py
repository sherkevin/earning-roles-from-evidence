from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import RarePolicy  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import (  # noqa: E402
    Pipe3SelectionBoundary,
    auxiliary_manifest_root,
    make_offer,
)


def registry():
    return [
        CandidateRegistryEntry("agent-a", "v1", "a" * 64, "internal/model", "b" * 64),
        CandidateRegistryEntry("agent-b", "v1", "b" * 64, "internal/model", "b" * 64),
        CandidateRegistryEntry("agent-c", "v1", "c" * 64, "internal/model", "b" * 64),
    ]


def test_pipe3_forwards_features_and_arrival_metadata_to_rare_adapter():
    boundary = Pipe3SelectionBoundary(RarePolicy(dimension=2), registry())
    features = {"agent-b@v1": (1.0, 0.0), "agent-c@v1": (0.0, 1.0)}
    offer0 = make_offer(
        offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="PIPE3:0", candidate_keys=tuple(features),
        public_rows=(), evidence_version="pipe3-evidence-v1", available_index=0,
    )
    first = boundary.choose_and_seal(
        offer=offer0, native_selection_id="selection-0", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(3), state_version="state-0",
        encoder_version="hash64-v1", feature_schema="features-0", policy_version="rare-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=True,
        captured_features=features,
    )
    row = {
        "feedback_id": "feedback-0", "source_event_id": first.policy_selection.event_id,
        "source": "recipient_judgment", "candidate_key": first.policy_selection.chosen.key,
        "evidence_version": "pipe3-evidence-v1", "source_index": 0, "arrival_index": 1,
        "arrived_at": 1.0, "delay": 1.0, "action": "accept", "disposition": "eligible",
        "provenance": "public", "label": 1.0,
    }
    offer1 = make_offer(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1", candidate_keys=tuple(features),
        public_rows=(row,), evidence_version="pipe3-evidence-v1", available_index=1,
        previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows),
    )
    second = boundary.choose_and_seal(
        offer=offer1, native_selection_id="selection-1", selector_id="agent-a", role="producer",
        base_scores=(0.0, 0.0), rng=np.random.default_rng(4), state_version="state-1",
        encoder_version="hash64-v1", feature_schema="features-0", policy_version="rare-0",
        base_score_version="base-0", rng_algorithm="numpy-pcg64", rng_draw=1,
        selected_at=1.0, read_cut=1, decision_index=1, consume_evidence=True,
        captured_features=features,
    )
    assert boundary.policy.updates == 1
    assert first.policy_selection.captured_features == tuple(sorted(features.items()))
    assert second.policy_selection.probabilities[0] != second.policy_selection.probabilities[1]
    boundary.validate_selection_manifests()
