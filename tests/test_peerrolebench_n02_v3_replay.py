from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_n02_v3_replay import replay_episode  # noqa: E402


N02_ROOT = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926"


@pytest.mark.parametrize("index", [0, 1])
def test_real_n02_episode_is_unknown_without_producer_score(index: int):
    result = replay_episode(N02_ROOT, index)
    assert result["historical_judgment"] == "accept_with_rework"
    assert result["historical_action"] == "repair"
    assert result["historical_terminal_success"] is True
    assert result["producer_score_observed"] is False
    assert result["historical_role_evidence_present"] is True
    assert result["gate"]["feedback_status"] == "PENDING_ATTRIBUTION"
    assert result["label_emitted"] is None
    assert result["policy_update_allowed"] is False
    assert result["historical_evidence_rejected_by_current_gate"] is True
