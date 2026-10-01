from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_contract import (  # noqa: E402
    BASELINE_ARM_SPECS,
    COST_FIELDS,
    contract_digest,
    contract_payload,
    validate_contract,
    validate_cost_ledger,
)


def _ledger(*, measured: bool) -> dict[str, dict[str, dict[str, object]]]:
    units = {
        "producer": "seconds", "recipient": "seconds", "judge": "seconds",
        "scorer": "seconds", "selection": "seconds", "policy_update": "seconds",
        "retry": "count", "communication": "records", "repair": "count",
        "replay": "records", "state": "bytes", "api_calls": "count",
        "input_tokens": "tokens", "output_tokens": "tokens",
        "gpu_seconds": "seconds", "wall_seconds": "seconds",
    }
    return {
        spec.name: {
            field: {"value": 0.0, "measured": measured, "source": "fixture", "unit": units[field]}
            for field in COST_FIELDS
        }
        for spec in BASELINE_ARM_SPECS
    }


def test_contract_seals_registered_arms_and_digest():
    payload = validate_contract()
    assert payload["contract_version"] == "artifactrole-baselines-v1"
    assert {row["name"] for row in payload["arms"]} == {spec.name for spec in BASELINE_ARM_SPECS}
    assert payload["contract_digest"] == contract_digest({k: v for k, v in payload.items() if k != "contract_digest"})
    assert payload["requirements"]["full_cost_ledger"] is True


def test_contract_rejects_changed_arm_set_and_explicitly_keeps_parity_open():
    altered = list(BASELINE_ARM_SPECS[:-1])
    with pytest.raises(ValueError, match="arm set"):
        validate_contract(altered)
    payload = contract_payload()
    contextual = next(row for row in payload["arms"] if row["name"] == "contextual_trust")
    rare = next(row for row in payload["arms"] if row["name"] == "RARE")
    assert contextual["parity_status"] == "open_live_parity"
    assert rare["parity_status"] == "open_live_parity"
    assert contextual["correction_support"] != rare["correction_support"]


def test_cost_ledger_accepts_offline_unmeasured_receipts_but_not_missing_or_fake_measures():
    normalized = validate_cost_ledger(_ledger(measured=False), require_measured=False)
    assert set(normalized) == {spec.name for spec in BASELINE_ARM_SPECS}
    with pytest.raises(ValueError, match="not measured"):
        validate_cost_ledger(_ledger(measured=False), require_measured=True)
    broken = _ledger(measured=False)
    broken["uniform"].pop("judge")
    with pytest.raises(ValueError, match="missing fields"):
        validate_cost_ledger(broken, require_measured=False)
