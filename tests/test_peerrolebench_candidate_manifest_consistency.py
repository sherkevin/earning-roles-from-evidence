from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_candidate_manifest_consistency import (  # noqa: E402
    C1_CARD, OLD_CARD, PARITY_CARD, _load, audit,
)


def test_current_candidate_cards_fail_closed_on_real_disagreements():
    result = audit(_load(OLD_CARD), _load(PARITY_CARD), _load(C1_CARD))
    assert result["status"] == "BLOCKED_PRE_EXECUTION"
    blocker_ids = {row["id"] for row in result["blockers"]}
    assert "root_split_disagreement" in blocker_ids
    assert "strongest_control_name_disagreement" in blocker_ids
    assert "c1_arm_coverage_gap" in blocker_ids
    assert result["scientific_claim_allowed"] is False
    assert result["api_runs_allowed"] is False
    assert result["gpu_runs_allowed"] is False


def test_audit_keeps_the_explicit_closest_adapter_requirement():
    result = audit(_load(OLD_CARD), _load(PARITY_CARD), _load(C1_CARD))
    assert "closest_adapter_row_missing" not in {row["id"] for row in result["blockers"]}
    assert "Meta-Team-L2-public" in result["parity_card"]["arms"]
