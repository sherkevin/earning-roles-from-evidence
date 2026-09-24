import pytest

from replay_adapter import make_decision_event, make_feedback_event


def test_public_replay_input_preserves_selected_output_but_not_truth():
    event = make_decision_event(
        event_id="e1", episode_id="p1", decision_type="select",
        selector_input={
            "entity_id": "z1", "remaining_calls": 2,
            "history": [{"provider_id": "a", "label": 0, "status": "ok"}],
            "candidates": [{"provider_id": "b", "family": "tool", "snapshot_round": 1}],
        }, chosen_id="b", propensity=0.5, state_version="s0", observed_at=1.0,
    )
    assert event.context["history"][0]["label"] == 0
    assert "ground_truth" not in event.context


def test_feedback_is_delayed_and_terminal_only():
    feedback = make_feedback_event(
        feedback_id="f1", source_event_id="e1", correct=1,
        selected_at=1.0, arrived_at=3.5,
    )
    assert feedback.delay == 2.5
    with pytest.raises(ValueError, match="before"):
        make_feedback_event(feedback_id="f2", source_event_id="e1", correct=0,
                            selected_at=2.0, arrived_at=1.0)


def test_decision_carries_feature_and_encoder_versions_for_delayed_update():
    event = make_decision_event(
        event_id="e2", episode_id="p1", decision_type="select",
        selector_input={"candidates": [{"provider_id": "a"}]},
        chosen_id="a", propensity=1.0, state_version="s2", observed_at=2.0,
        encoder_version="laya-v1", feature_schema="phi-v1",
        captured_features={"a": [1.0, 0.5]},
    )
    assert event.encoder_version == "laya-v1"
    assert event.feature_schema == "phi-v1"
    assert event.captured_features["a"] == (1.0, 0.5)
