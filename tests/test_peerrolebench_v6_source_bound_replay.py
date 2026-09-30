from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_v6_source_bound_replay_qualification import run  # noqa: E402


def test_frozen_real_v6_pending_attribution_replays_as_unknown(tmp_path):
    summary = run(tmp_path / "v6-replay")
    assert summary["status"] == "QUALIFIED_OFFLINE"
    assert summary["source_ledger_status"] == "UNKNOWN"
    assert summary["pending_attribution_preserved"] is True
    assert summary["real_api_calls"] == 0
