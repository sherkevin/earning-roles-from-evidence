import json
from pathlib import Path

import pytest

from scripts.peerrolebench_pipe3_chain_contract_qualification import qualify


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "configs/aamas2027/n03_pipe3_real_smoke_v7.json"


def test_pipe3_chain_card_qualifies_without_external_work(tmp_path):
    result = qualify(CARD, tmp_path / "pass")
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["real_api_calls"] == 0
    assert result["gpu_jobs"] == 0
    assert result["scientific_claim_allowed"] is False
    assert result["check_count"] == 27


def test_pipe3_chain_card_rejects_missing_target_credit_key(tmp_path):
    card = json.loads(CARD.read_text())
    card["lineage_keys"]["target_credit"] = ["assignment_id"]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    result = qualify(path, tmp_path / "fail")
    assert result["status"] == "FAILED_OFFLINE"
    assert any(row["name"] == "lineage_target_credit" and row["status"] == "FAIL"
               for row in result["checks"])


def test_pipe3_chain_card_rejects_source_adoption_as_later_use(tmp_path):
    card = json.loads(CARD.read_text())
    card["credit_contract"]["source_adoption_is_later_use"] = True
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    result = qualify(path, tmp_path / "fail")
    assert result["status"] == "FAILED_OFFLINE"
    assert any(row["name"] == "source_not_later_use" and row["status"] == "FAIL"
               for row in result["checks"])


@pytest.mark.parametrize("case", ["recipient_only", "mixed", "outside_contract", "producer_pass_without_registered_defect"])
def test_pipe3_responsibility_cases_do_not_issue_producer_label(tmp_path, case):
    card = json.loads(CARD.read_text())
    assert card["responsibility_cases"][case]["producer_label_allowed"] is False
