from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_responsibility_lineage_qualification import (  # noqa: E402
    _lineage_rows, _result,
)
from peerrolebench_policy_sidecar_stream_qualification import canonical_ledger  # noqa: E402


def test_strict_lineage_accepts_canonical_and_rejects_cross_links():
    events = canonical_ledger()
    rows = _lineage_rows(events)
    assert _result(events, rows)["status"] == "PASS"
    assert _result(events, rows, mutate="wrong_delivery")["status"] == "INVALID"
    assert _result(events, rows, mutate="wrong_artifact")["status"] == "INVALID"
    assert _result(events, rows, mutate="wrong_action")["status"] == "INVALID"
    assert _result(events, rows, mutate="wrong_producer")["status"] == "INVALID"
