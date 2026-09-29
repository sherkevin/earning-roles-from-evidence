from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_raw_acceptance_replay_qualification import run  # noqa: E402


def test_raw_acceptance_replay_fixture_is_strict_and_zero_call(tmp_path):
    result = run(tmp_path / "raw-replay")
    assert result["passed"] is True
    assert result["real_api_calls"] == 0
    assert result["gpu_jobs"] == 0
    assert result["scientific_claim_allowed"] is False
    assert {case["case"] for case in result["cases"]} == {
        "canonical", "wrong_canonical_decision", "wrong_producer", "duplicate_sidecar",
    }
