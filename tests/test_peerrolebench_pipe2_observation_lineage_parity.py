from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_observation_lineage_parity import (  # noqa: E402
    _parity_arms,
    build_fixture,
    validate_fixture,
)


def test_noisy_observation_is_public_but_not_credit():
    fixture = build_fixture(0)
    result = validate_fixture(fixture)
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert fixture["source_observation"]["judgment"] == "accept_with_rework"
    assert fixture["source_observation"]["credit_eligible"] is False
    assert fixture["credit"]["policy_update_allowed"] is False
    assert "recipient_changed_paths" not in fixture["public_observation"]


def test_same_information_arms_hold_menu_timing_and_cost_fixed():
    arms = _parity_arms(build_fixture(0))
    for key in ("menu_digest", "feature_digest", "arrival_digest", "read_cut", "propensity", "cost_scope"):
        assert len({str(arm[key]) for arm in arms.values()}) == 1
    assert arms["observation"]["history_payload"] != arms["count_only"]["history_payload"]
    assert arms["observation"]["history_payload"] != arms["j_masked"]["history_payload"]


def test_target_outcome_is_after_future_selection_and_independent():
    fixture = build_fixture(0)
    assert fixture["target_outcome"]["independent"] is True
    assert fixture["target_outcome"]["arrival_index"] > fixture["future_assignment"]["read_cut"]
    assert fixture["target_outcome"]["selection_id"] == fixture["target_selection"]["selection_id"]


def test_mutation_inventory_is_fail_closed_and_never_updates():
    from peerrolebench_pipe2_observation_lineage_parity import mutation_results
    mutations = mutation_results(build_fixture(0))
    assert {row["mutation"] for row in mutations} == {
        "judgment_after_action", "assignment_before_observation", "menu_mismatch",
        "late_observation_read_cut", "target_outcome_before_selection",
        "recipient_edit_as_producer_credit",
    }
    assert all(row["accepted"] is False and row["failures"] for row in mutations)
    assert all(row["runner_started"] is False and row["policy_update"] is False for row in mutations)
