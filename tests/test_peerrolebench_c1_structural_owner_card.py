import json
from pathlib import Path

import pytest

import scripts.peerrolebench_c1_pipe3_bounded_live as c1


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "configs/aamas2027/n03_c1_pipe3_bounded_live_dev_v2.json"


def test_v2_card_declares_structural_owner_contract():
    card = json.loads(CARD.read_text(encoding="utf-8"))
    c1._validate_responsibility_card(card)
    assert card["responsibility_gate"]["judged_role_policy"] == "calibration_only"


@pytest.mark.parametrize(
    "field,value",
    [
        ("version", "two-stage-role-evidence-v2"),
        ("eligibility_owner_source", "model_target_role"),
        ("judged_role_policy", "eligibility_hard_gate"),
        ("disagreement_field", "ignored"),
    ],
)
def test_v2_card_rejects_structural_owner_contract_mutation(field, value):
    card = json.loads(CARD.read_text(encoding="utf-8"))
    card["responsibility_gate"][field] = value
    with pytest.raises(ValueError):
        c1._validate_responsibility_card(card)
