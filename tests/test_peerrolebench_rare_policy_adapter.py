from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import (  # noqa: E402
    CandidateRef,
    Feedback,
    RarePolicy,
    BaselinePolicy,
)


REFS = (CandidateRef("a", "v1"), CandidateRef("b", "v1"))
FEATURES = {"a@v1": (1.0, 0.0), "b@v1": (0.0, 1.0)}


def choose(policy: RarePolicy, event_id: str = "e0"):
    return policy.choose(
        event_id=event_id,
        context_key="ctx",
        selector_id="selector",
        candidates=REFS,
        base_scores=(0.0, 0.0),
        rng=np.random.default_rng(4),
        state_version="s0",
        encoder_version="hash64-v1",
        feature_schema="phi2",
        captured_features=FEATURES,
    )


def test_rare_requires_fixed_bounded_features_and_mixes_exploration():
    policy = RarePolicy(dimension=2, exploration=0.1)
    selection = choose(policy)
    assert selection.captured_features == tuple(sorted(FEATURES.items()))
    assert sum(selection.probabilities) == pytest.approx(1.0)
    assert all(value >= 0.05 for value in selection.probabilities)
    with pytest.raises(ValueError, match="fixed features"):
        policy.choose(
            event_id="bad-missing", context_key="ctx", selector_id="selector",
            candidates=REFS, base_scores=(0.0, 0.0), rng=np.random.default_rng(1),
            encoder_version="hash64-v1", captured_features={"a@v1": (1.0, 0.0)},
        )
    with pytest.raises(ValueError, match="L2 norm"):
        policy.choose(
            event_id="bad-norm", context_key="ctx", selector_id="selector",
            candidates=REFS, base_scores=(0.0, 0.0), rng=np.random.default_rng(1),
            encoder_version="hash64-v1",
            captured_features={"a@v1": (2.0, 0.0), "b@v1": (0.0, 1.0)},
        )


def test_rare_consumes_selected_judgment_and_ignores_unknown_without_label():
    policy = RarePolicy(dimension=2)
    selection = choose(policy)
    unknown = Feedback(
        "u0", selection.event_id, "recipient_judgment", None, 1.0,
        disposition="unknown", provenance="unknown", arrival_index=0,
    )
    assert policy.observe_feedback(unknown) is False
    assert policy.updates == 0
    eligible = Feedback(
        "f0", selection.event_id, "recipient_judgment", 1.0, 2.0,
        action="accept", arrival_index=1,
    )
    assert policy.observe_feedback(eligible) is True
    assert policy.updates == 1
    assert policy.state.updates == 1


def test_rare_accepts_delayed_correction_for_the_same_public_channel():
    policy = RarePolicy(dimension=2)
    selection = choose(policy)
    first = Feedback(
        "f0", selection.event_id, "recipient_judgment", 1.0, 1.0,
        action="accept", arrival_index=1,
    )
    correction = Feedback(
        "f0-correction", selection.event_id, "recipient_judgment", 0.0, 3.0,
        action="reject", arrival_index=3, supersedes="f0",
    )
    assert policy.observe_feedback(first) is True
    before = policy.state.digest()
    assert policy.observe_feedback(correction) is True
    assert policy.state.digest() != before
    assert policy.state.window["f0-correction"].label == 0.0
    assert "f0" in policy.state.superseded


def test_rare_rejects_cross_selection_correction_and_allows_metadata_retry():
    policy = RarePolicy(dimension=2)
    first = choose(policy, "e0")
    with pytest.raises(ValueError, match="arrival_index"):
        policy.observe_feedback(Feedback(
            "bad", first.event_id, "recipient_judgment", 1.0, 1.0,
        ))
    assert policy.observe_feedback(Feedback(
        "bad", first.event_id, "recipient_judgment", 1.0, 1.0, arrival_index=1,
    )) is True
    second = choose(policy, "e1")
    with pytest.raises(ValueError, match="crosses source-event"):
        policy.observe_feedback(Feedback(
            "cross", second.event_id, "recipient_judgment", 0.0, 2.0,
            arrival_index=2, supersedes="bad",
        ))


def test_rare_snapshot_restore_preserves_selection_and_correction_state():
    policy = RarePolicy(dimension=2)
    selection = choose(policy)
    policy.observe_feedback(Feedback(
        "f0", selection.event_id, "recipient_judgment", 1.0, 1.0,
        arrival_index=1,
    ))
    restored = BaselinePolicy.restore(policy.snapshot())
    assert isinstance(restored, RarePolicy)
    assert restored.snapshot() == policy.snapshot()
    next_original = policy.choose(
        event_id="e1", context_key="ctx", selector_id="selector", candidates=REFS,
        base_scores=(0.0, 0.0), rng=np.random.default_rng(10), encoder_version="hash64-v1",
        captured_features=FEATURES,
    )
    next_restored = restored.choose(
        event_id="e1", context_key="ctx", selector_id="selector", candidates=REFS,
        base_scores=(0.0, 0.0), rng=np.random.default_rng(10), encoder_version="hash64-v1",
        captured_features=FEATURES,
    )
    assert next_restored.probabilities == pytest.approx(next_original.probabilities)
    assert next_restored.chosen.key == next_original.chosen.key
