from scripts.peerrolebench_build_external_source_manifest import episode_cost


def _source(**overrides):
    source = {
        "judgment_api": {
            "elapsed_seconds": 1.5,
            "usage_complete": True,
            "usage": {"input_tokens": 10, "output_tokens": 4},
        },
        "action_api": {
            "elapsed_seconds": 5.0,
            "usage_complete": True,
            "usage": {"input_tokens": 20, "output_tokens": 8},
        },
        "action": {"action_wall_seconds": 5.0},
        "producer_score": {"scorer_wall_seconds": 1.0, "status": "PASS"},
        "recipient_score": {"status": "PASS"},
        "adoption_score": {"status": "PASS"},
        "outcome": {"scorer_wall_seconds": 2.0, "status": "PASS"},
    }
    source.update(overrides)
    return source


def test_episode_cost_uses_outcome_total_and_counts_action_once():
    cost = episode_cost(_source())

    assert cost["source_cost_units"] == 9.5  # 1.5 + 5.0 + 1.0 + 2.0
    assert cost["scorer_timing_mode"] == "producer_plus_outcome_total"
    assert cost["action_timing_source"] == "action_wall_seconds"
    assert cost["wall_complete"] is True
    assert cost["token_complete"] is True
    assert cost["cost_status"] == "COMPLETE"
    assert cost["unknown_fields"] == []
    assert cost["producer_generation_measured"] is False
    assert cost["full_route_cost_complete"] is False


def test_episode_cost_falls_back_to_independent_scorer_timings():
    source = _source(
        outcome={"status": "PASS"},
        recipient_score={"scorer_wall_seconds": 0.4, "status": "PASS"},
        adoption_score={"scorer_wall_seconds": 0.6, "status": "PASS"},
    )
    cost = episode_cost(source)

    assert cost["scorer_timing_mode"] == "producer_plus_recipient_adoption"
    assert cost["scorer_wall_seconds"]["selected_total"] == 2.0
    assert cost["source_cost_units"] == 8.5
    assert cost["wall_complete"] is True


def test_episode_cost_does_not_double_count_disagreeing_action_timings():
    cost = episode_cost(_source(action={"action_wall_seconds": 7.0}))

    assert cost["source_cost_units"] == 11.5
    assert cost["action_wall_seconds"] == 7.0
    assert "action_timing_disagreement" in cost["unknown_fields"]
    assert cost["wall_complete"] is False
    assert cost["cost_status"] == "UNKNOWN"


def test_episode_cost_exposes_missing_tokens_and_timing_as_null_unknown():
    source = _source(
        judgment_api={},
        action_api={"usage": {"input_tokens": 3}, "usage_complete": False},
        action={},
        producer_score={"status": "PASS"},
        recipient_score={"status": "PASS"},
        adoption_score={"status": "PASS"},
        outcome={"status": "PASS"},
    )
    cost = episode_cost(source)

    assert cost["api"]["judgment"]["input_tokens"] is None
    assert cost["api"]["judgment"]["output_tokens"] is None
    assert cost["api"]["judgment"]["wall_seconds"] is None
    assert cost["api"]["action"]["input_tokens"] == 3
    assert cost["api"]["action"]["output_tokens"] is None
    assert cost["action_wall_seconds"] is None
    assert cost["wall_complete"] is False
    assert cost["token_complete"] is False
    assert cost["cost_status"] == "UNKNOWN"
    assert "judgment_api.input_tokens" in cost["unknown_fields"]
    assert "judgment_api.wall_seconds" in cost["unknown_fields"]
    assert "producer_scorer_seconds" in cost["unknown_fields"]


def test_episode_cost_keeps_explicit_zero_as_a_measured_value():
    zero_api = {
        "elapsed_seconds": 0,
        "usage_complete": True,
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }
    cost = episode_cost(_source(
        judgment_api=zero_api,
        action_api=zero_api,
        action={"action_wall_seconds": 0},
        producer_score={"scorer_wall_seconds": 0, "status": "PASS"},
        outcome={"scorer_wall_seconds": 0, "status": "PASS"},
    ))

    assert cost["source_cost_units"] == 0.0
    assert cost["wall_complete"] is True
    assert cost["token_complete"] is True
    assert cost["cost_status"] == "COMPLETE"
    assert cost["unknown_fields"] == []


def test_generated_producer_cost_is_added_once_and_kept_separate_from_qp():
    cost = episode_cost(_source(producer_api={
        "elapsed_seconds": 3.0, "usage_complete": True,
        "usage": {"input_tokens": 9, "output_tokens": 6},
    }))
    assert cost["source_cost_units"] == 12.5  # legacy 9.5 + generation 3; Qp already included
    assert cost["api"]["producer"]["input_tokens"] == 9
    assert cost["api"]["producer"]["output_tokens"] == 6
    assert cost["scorer_wall_seconds"]["producer"] == 1.0
    assert cost["producer_generation_measured"] is True
    assert cost["cost_status"] == "COMPLETE"
    assert cost["full_route_cost_complete"] is False


def test_missing_generation_receipt_is_not_free_or_complete():
    cost = episode_cost(_source(producer_api=None))
    assert cost["source_cost_units"] == 9.5
    assert cost["cost_status"] == "UNKNOWN"
    assert cost["source_cost_units_observed"] is False
    assert cost["producer_generation_measured"] is False
    assert "producer_api.wall_seconds" in cost["unknown_fields"]
    assert "producer_api.input_tokens" in cost["unknown_fields"]


def test_failed_generation_retains_measured_time_without_inventing_tokens():
    cost = episode_cost(_source(producer_api={
        "elapsed_seconds": 120.0, "usage_complete": False,
        "http_status": "000", "usage": None,
    }))
    assert cost["source_cost_units"] == 129.5
    assert cost["cost_status"] == "UNKNOWN"
    assert cost["wall_complete"] is True
    assert cost["token_complete"] is False
    assert cost["api"]["producer"]["output_tokens"] is None
