"""Zero-call qualification tests for the J/A/U/F factor mapping."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_factorial_mapping_qualification import (  # noqa: E402
    build_two_episode_ledger,
    inspect_mapping,
)


def test_two_episode_ledger_replays_and_consumes_future_assignment():
    result = inspect_mapping(build_two_episode_ledger())
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["ledger_replay_status"] == "PASS"
    assert result["module_mapping"]["F"]["assignment_consumed_by_ledger"] is True


def test_policy_sidecar_gap_is_explicit_instead_of_silently_supported():
    result = inspect_mapping(build_two_episode_ledger())
    assert result["supported_policy_cells"] == ["0000", "0010", "1000", "1010"]
    assert len(result["unsupported_policy_cells"]) == 12
    assert all(not cell["scientific_cell_ready"] for cell in result["cells"])
