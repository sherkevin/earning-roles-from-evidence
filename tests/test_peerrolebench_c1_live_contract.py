import json
import re
import subprocess

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
    by_arm = {row["arm"]: row for row in result["results"]}
    assert set(by_arm) == {"no_update", "contextual_trust_linear", "RARE"}
    assert all(row["source_eligible"] is True for row in by_arm.values())
    assert by_arm["no_update"]["update"]["status"] == "NOT_RUN"
    assert by_arm["contextual_trust_linear"]["update"]["status"] == "UPDATED"
    assert by_arm["RARE"]["update"]["status"] == "UPDATED"
    for row in by_arm.values():
        replay = replay_ledger_events(row["ledger"])
        assert replay.status == "PASS" and replay.complete is True
