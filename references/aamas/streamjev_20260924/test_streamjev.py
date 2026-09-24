import numpy as np
import pytest

from fast_state import DualFastState
from protocol import Candidate, DecisionEvent, FeedbackEvent, candidate_tuple


def test_pre_action_contract_rejects_hidden_truth():
    with pytest.raises(ValueError, match="post-action"):
        DecisionEvent(
            event_id="e1", episode_id="p1", decision_type="select",
            context={"task": "x", "tool_output": "leak"},
            candidates=candidate_tuple([Candidate("a", "tool", "v1")]),
            chosen_id="a", propensity=1.0, state_version="s0", observed_at=0.0,
        )


def test_only_selected_candidate_is_updated():
    state = DualFastState(feature_dim=2, gate_warmup=1)
    before = state.snapshot()
    state.update("a", [1.0, 0.0], label=1.0, propensity=1.0)
    assert state.stats["a"].alpha > 1.0
    assert "b" not in state.stats
    assert state.observed == 1
    assert before["observed"] == 0


def test_fast_update_is_bounded_and_snapshot_roundtrips():
    state = DualFastState(feature_dim=3, max_update_norm=0.05, gate_warmup=1)
    state.update("a", [100.0, 0.0, 0.0], label=1.0, propensity=0.1)
    assert np.linalg.norm(state.w) <= 0.0500001
    restored = DualFastState.restore(state.snapshot())
    probs1, _, _ = state.score(["a"], [0.0], {"a": [1.0, 0.0, 0.0]})
    probs2, _, _ = restored.score(["a"], [0.0], {"a": [1.0, 0.0, 0.0]})
    assert np.allclose(probs1, probs2)


def test_menu_order_does_not_change_candidate_scores():
    state = DualFastState(feature_dim=2, gate_warmup=1)
    state.update("a", [1.0, 0.0], 1.0, 1.0)
    state.update("b", [0.0, 1.0], 0.0, 1.0)
    features = {"a": [1.0, 0.0], "b": [0.0, 1.0]}
    p1, _, _ = state.score(["a", "b"], [0.1, 0.1], features)
    p2, _, _ = state.score(["b", "a"], [0.1, 0.1], features)
    assert np.isclose(p1[0], p2[1])
    assert np.isclose(p1[1], p2[0])
