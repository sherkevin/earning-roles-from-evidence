from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_four_event_counterfactual import run_probe  # noqa: E402


def test_minimal_stream_is_replayable_and_same_information():
    result = run_probe()
    assert len(result["events"]) == 3
    assert len(result["runs"]) == 2
    assert result["identification"]["candidate_separates_on_minimal_stream"] is False
    before = next(run for run in result["runs"] if run["schedule"] == "before_assignment")
    after = next(run for run in result["runs"] if run["schedule"] == "after_assignment")
    assert before["assignment"]["rare"]["chosen"] == before["assignment"]["same_info_ungated"]["chosen"]
    assert before["assignment"]["same_probability"] is True
    assert after["assignment"]["rare"]["chosen"] == after["assignment"]["same_info_ungated"]["chosen"]
    assert result["api_calls"] == 0
    assert result["gpu"] == 0


def test_late_correction_cannot_rewrite_sealed_assignment():
    result = run_probe()
    after = next(run for run in result["runs"] if run["schedule"] == "after_assignment")
    assignment = after["assignment"]
    correction_rows = [row for row in after["trace"] if row["event"] == "e2-correction"]
    assert correction_rows and correction_rows[0]["after_assignment"] is True
    assert assignment["rare"]["state_digest"] != correction_rows[0]["rare_digest"]
    assert assignment["same_info_ungated"]["state_digest"] != correction_rows[0]["trust_digest"]
