from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from peerrolebench_pipe3_source_bound_boundary_qualification import run  # noqa: E402


def test_source_bound_offer_reaches_future_selection_on_same_boundary(tmp_path: Path):
    result = run(tmp_path / "run")
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert all(result["checks"].values())
    assert result["policy_updates"] == 1
    assert result["ledger_event_count"] == 9
