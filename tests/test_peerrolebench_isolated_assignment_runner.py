from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_isolated_assignment_runner_qualification import run  # noqa: E402


def test_isolated_read_selection_and_native_task_start_are_one_trace(tmp_path):
    result = run(tmp_path / "isolated-assignment")
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["trace"][1]["isolated_policy_trace"] is True
    assert result["ledger"][-1]["event_type"] == "task_start"
    assert result["ledger"][-1]["payload"]["task_index"] == 3
