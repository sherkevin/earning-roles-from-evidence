from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_hidden_consumer_scorer_worker import empty, pair  # noqa: E402


def test_empty_accepts_direct_and_json_tuple_forms():
    assert empty(None)
    assert empty((None, None))
    assert empty([None, None])
    assert not empty(({"payload": 1}, "receipt"))


def test_pair_accepts_direct_and_json_tuple_forms():
    assert pair(({"payload": 1}, "receipt"))
    assert pair([{"payload": 1}, "receipt"])
    assert not pair(None)
