from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_observation_bridge_compatibility import run  # noqa: E402


def test_pipe2_handoff_is_not_source_file_bridge_compatible(tmp_path):
    result = run(tmp_path / "compatibility", seed=0)
    assert result["status"] == "BLOCKED_BY_HANDOFF_SEMANTICS"
    assert result["api_calls"] == 0
    assert result["gpu_jobs"] == 0
    assert result["policy_updates"] == 0
    assert result["scientific_claim_allowed"] is False
    assert any("typed handoff descriptor" in item for item in result["blockers"])
    assert any("recipient pre/post" in item for item in result["blockers"])
