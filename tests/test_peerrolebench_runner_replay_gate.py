"""The live runner must use the outer ledger replay gate before learning."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_real_closed_loop import load_ledger  # noqa: E402
from peer_role_protocol_20260925 import PeerRoleLedger, PeerSelection  # noqa: E402


def _partial_ledger() -> list[dict]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection(
        "s0", "task", 0, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 0.5,
    ))
    ledger.record_task_start("task", 0)
    return ledger.events


def test_runner_replays_inflight_partial_ledger(tmp_path):
    (tmp_path / "ledger.json").write_text(json.dumps(_partial_ledger()))
    ledger = load_ledger(tmp_path)
    assert ledger.snapshot()["event_count"] == 2


def test_runner_rejects_tampered_ledger_before_reuse(tmp_path):
    records = copy.deepcopy(_partial_ledger())
    records[1]["record_hash"] = "f" * 64
    (tmp_path / "ledger.json").write_text(json.dumps(records))
    with pytest.raises(RuntimeError, match=r"Ledger replay validation failed \[record_hash_mismatch\]"):
        load_ledger(tmp_path)
