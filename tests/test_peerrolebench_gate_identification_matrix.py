from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_gate_identification_matrix import run_matrix  # noqa: E402


def test_gate_matrix_separates_only_when_visible_raw_signal_is_positive():
    result = run_matrix()
    cases = result["cases"]
    assert cases["raw_positive_orthogonal"]["probability_separation"] is True
    assert cases["raw_positive_nonorthogonal"]["probability_separation"] is True
    assert cases["raw_zero_orthogonal"]["probability_separation"] is False
    assert cases["raw_missing_orthogonal"]["probability_separation"] is False
    assert result["api_calls"] == 0
    assert result["gpu"] == 0
    assert result["scientific_claim_allowed"] is False


def test_missing_signal_is_not_encoded_as_zero():
    result = run_matrix()
    missing = result["cases"]["raw_missing_orthogonal"]
    assert missing["trace"][0]["gated_status"] == "UNKNOWN"
    assert missing["trace"][0]["ungated_status"] == "UNKNOWN"
