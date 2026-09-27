from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "peerrolebench_pipe3_task_qualification",
    ROOT / "scripts/peerrolebench_pipe3_task_qualification.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_ledger_contract_is_strictly_ordered():
    result = MODULE.validate_ledger()
    assert result["passed"] is True
    assert result["checks"]["selection_before_delivery"] is True
    assert result["checks"]["hidden_score_not_actor_visible"] is True


def test_pipe3_pin_and_task_contract_have_disjoint_writable_paths():
    assert MODULE.PRODUCER_OWNED == ("producer.py",)
    assert MODULE.RECIPIENT_OWNED == ("processor.py",)
    assert set(MODULE.PRODUCER_OWNED).isdisjoint(MODULE.RECIPIENT_OWNED)
    assert set(MODULE.HIDDEN_PATHS).isdisjoint(MODULE.PRODUCER_OWNED + MODULE.RECIPIENT_OWNED)
