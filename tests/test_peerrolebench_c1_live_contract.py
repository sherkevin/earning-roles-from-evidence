import json
import re
import subprocess

import pytest

import scripts.peerrolebench_c1_pipe3_bounded_live as c1
from scripts.peerrolebench_ledger_replay import replay_ledger_events


def _fake_actor(_out, _stage_dir, stage, prompt, _card):
    """Deterministic actor only for zero-API contract qualification."""
    if stage == "judgment":
        digest = re.search(r"The artifact digest is ([0-9a-f]{64})", prompt).group(1)
        return ({
            "decision": "accept",
            "confidence": 1.0,
            "rationale": "contract fixture",
            "repair_plan": "",
            "observed_artifact_sha256": digest,
            "target_role": "producer",
            "target_paths": ["producer.py"],
            "defect_type": "producer_contract",
            "evidence_refs": ["artifact_digest"],
        }, {"elapsed_seconds": 0.001, "usage": {"input_tokens": 1, "output_tokens": 1}})
    if stage == "action":
        payload = json.loads(prompt.split("ACTION PAYLOAD:\n", 1)[1])
        return ({"source_files": payload["source_files"]}, {"elapsed_seconds": 0.001, "usage": {"input_tokens": 1, "output_tokens": 1}})
    raise AssertionError(stage)


def test_c1_zero_api_contract_qualifies_all_arms(tmp_path, monkeypatch):
    monkeypatch.setattr(c1.api, "call_api", _fake_actor)
    card = json.loads(c1.CARD.read_text(encoding="utf-8"))
    card["source_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=c1.ROOT, text=True
    ).strip()
    card_copy = tmp_path / "card.json"
    card_copy.write_text(json.dumps(card), encoding="utf-8")
    result = c1.run(tmp_path / "c1", card_path=card_copy)
    assert result["status"] == "COMPLETE_DEVELOPMENT_ONLY"
    assert result["passed"] is True
    assert result["real_api_calls"] == 0
    assert result["scientific_claim_allowed"] is False
    assert result["cost_ledger"]["double_count_rejected"] is True
    assert result["cost_ledger"]["arm_count"] == 3
    assert result["cost_ledger"]["source_cost_units_counted_once"] > 0.0
    assert result["cost_ledger"]["target_cost_units_sum"] > 0.0
    by_arm = {row["arm"]: row for row in result["results"]}
    assert set(by_arm) == {"no_update", "contextual_trust_linear", "RARE"}
    assert all(row["source_eligible"] is True for row in by_arm.values())
    assert by_arm["no_update"]["update"]["status"] == "NOT_RUN"
    assert by_arm["contextual_trust_linear"]["update"]["status"] == "UPDATED"
    assert by_arm["RARE"]["update"]["status"] == "UPDATED"
    for row in by_arm.values():
        assert row["source"]["action"]["repair_cost"] == 0.0
        assert row["target"]["action"]["repair_cost"] == 0.0
    for row in by_arm.values():
        replay = replay_ledger_events(row["ledger"])
        assert replay.status == "PASS" and replay.complete is True
        assert row["cost"]["scorer_seconds"] >= 0.0
        assert row["cost"]["update_seconds"] >= 0.0
        assert row["cost"]["state_bytes"] > 0
        assert row["cost_ledger_row"]["cost"]["target_cost_status"] in {"COMPLETE", "UNKNOWN"}
        assert row["cost_ledger_row"]["cost"]["target_cost_units"] >= 0.0
        if row["cost_ledger_row"]["cost"]["target_cost_status"] == "UNKNOWN":
            assert row["target_cost"]["unknown_fields"]
        assert row["target_cost"]["target_cost_units"] == row["cost_ledger_row"]["cost"]["target_cost_units"]
        assert len(row["selection_bindings"]) == 2
        assert row["manifest_roots"]["native"] != "GENESIS"
        assert row["manifest_roots"]["auxiliary"] != "GENESIS"
        assert row["post_update_selection"]["preview_only"] is True
        assert row["post_update_selection"]["ledger_included"] is False


def test_target_cost_survives_failure_after_target_episode(tmp_path, monkeypatch):
    monkeypatch.setattr(c1.api, "call_api", _fake_actor)
    original = c1._select_post_update

    def fail_after_target(boundary, arm, features, decision_index):
        if arm == "RARE":
            raise RuntimeError("synthetic post-target failure")
        return original(boundary, arm, features, decision_index)

    monkeypatch.setattr(c1, "_select_post_update", fail_after_target)
    card = json.loads(c1.CARD.read_text(encoding="utf-8"))
    card["source_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=c1.ROOT, text=True
    ).strip()
    card_copy = tmp_path / "card.json"
    card_copy.write_text(json.dumps(card), encoding="utf-8")
    result = c1.run(tmp_path / "c1", card_path=card_copy)
    rare = next(row for row in result["results"] if row["arm"] == "RARE")
    assert rare["status"] == "UNKNOWN"
    assert rare["cost_ledger_row"]["cost"]["target_cost_status"] == "UNKNOWN"
    assert rare["cost_ledger_row"]["cost"]["target_cost_units"] > 0.0
    assert "arm_failure_after_target" in rare["cost_ledger_row"]["cost"]["target_unknown_fields"]
    assert (tmp_path / "c1" / "RARE" / "target_cost_receipt.json").is_file()


def test_invalid_api_budget_is_rejected_before_actor_call(tmp_path, monkeypatch):
    def fail_actor(*_args, **_kwargs):
        raise AssertionError("invalid budget must fail before API")

    monkeypatch.setattr(c1.api, "call_api", fail_actor)
    card = json.loads(c1.CARD.read_text(encoding="utf-8"))
    card["source_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=c1.ROOT, text=True
    ).strip()
    card["maximum_api_requests"] = 7
    card_copy = tmp_path / "card.json"
    card_copy.write_text(json.dumps(card), encoding="utf-8")
    with pytest.raises(RuntimeError, match="API budget"):
        c1.run(tmp_path / "invalid-budget", card_path=card_copy)
