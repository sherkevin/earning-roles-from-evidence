from copy import deepcopy

import pytest

from scripts.peerrolebench_signal_contract import (
    ARM_NAMES, default_arm_contracts, inventory_episode,
)


def test_real_disagreement_preserves_scores_and_action_without_relabelling():
    episode = {
        "producer_score": {"status": "FAIL", "label": 0, "quality_score": 2 / 3},
        "judgment": {"decision": "accept"},
        "action": {"consumer_action": "use", "changed_paths": [], "source_files": {"p.py": "text"}},
        "adoption_score": {"status": "FAIL", "label": 0, "quality_score": .5},
        "outcome": {"status": "FAIL", "quality_score": .5},
        "recipient_score": {"status": "PASS", "quality_score": 1.0},
    }
    original = deepcopy(episode)
    result = inventory_episode(episode)
    rows = {row["channel"]: row for row in result["signals"]}
    assert set(rows) == {"Qp", "J", "A", "D", "Y", "L"}
    assert rows["Qp"]["observed"] == episode["producer_score"]
    assert rows["J"]["mapped_judgment_label"] == 1.0
    assert rows["D"]["observed"]["quality_score"] == rows["Y"]["observed"]["quality_score"] == .5
    assert rows["Y"]["derived_from"] == ("D", "recipient")
    assert rows["A"]["observed"]["consumer_action"] == "use"
    assert "source_files" not in rows["A"]["observed"]
    assert all(row["policy_eligible"] is False for row in rows.values())
    assert rows["L"]["observation_status"] == "NOT_AUDITED"
    assert result["terminal_baseline_qualified"] is False
    assert result["native_lineage_validated"] is False
    assert episode == original
    rows["Qp"]["observed"]["status"] = "mutation"
    assert episode == original


@pytest.mark.parametrize("decision", ["made_up", {}, None])
def test_unknown_judgment_cannot_become_a_label_and_unknown_scores_are_preserved(decision):
    result = inventory_episode({"judgment": {"decision": decision},
                                "outcome": {"status": "UNKNOWN", "quality_score": None}})
    rows = {row["channel"]: row for row in result["signals"]}
    assert rows["J"]["mapped_judgment_label"] is None
    assert rows["J"]["observation_status"] == "UNKNOWN"
    assert rows["Y"]["observed"] == {"status": "UNKNOWN", "quality_score": None}
    assert all(not row["policy_eligible"] for row in rows.values())


def test_live_linear_policy_is_an_explicit_family_mapping_not_algorithm_equivalence():
    contracts = default_arm_contracts()
    assert set(ARM_NAMES) < set(contracts)
    linear = contracts["contextual_trust_linear"]
    assert linear["registry_family"] == "contextual_trust"
    assert linear["algorithm_equivalent_to_registry_implementation"] is False
    assert not any(row["parity_qualified"] for row in contracts.values())
    assert contracts["no_update"]["accepted_sources"] == ()
    assert contracts["RARE"]["correction_support"] == "event_time_correction"


def test_invalid_episode_and_unknown_arm_are_rejected():
    with pytest.raises(TypeError):
        inventory_episode([])
    with pytest.raises(ValueError):
        inventory_episode({}, arm="unknown")
