import sys

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_canonical_pipe3_parity_qualification import _build_canonical_fixture  # noqa: E402
from peerrolebench_canonical_raw_adapter_qualification import (  # noqa: E402
    _build_raw_stream,
    _raw_sidecar,
    _run_positive,
    run,
)


def test_raw_positive_uses_canonical_judgment_and_updates_only_raw_arm():
    fixture = _build_canonical_fixture()
    result = _run_positive(fixture)
    assert result["status"] == "PASS"
    assert result["checks"]["raw_one_eligible"] is True
    assert result["checks"]["raw_one_update"] is True
    assert result["checks"]["other_arms_ignore_raw"] is True
    assert result["result"]["metrics"]["raw_acceptance"]["updates"] == 1
    assert result["result"]["metrics"]["raw_acceptance"]["n_revisible_prefix_rows"] == 2


@pytest.mark.parametrize(
    "name,kwargs",
    [
        ("wrong producer", {"producer_id": "peer-c"}),
        ("wrong ledger digest", {"ledger_record_hash": "0" * 64}),
        ("wrong registry digest", {"expected_registry_digest": "0" * 64}),
    ],
)
def test_raw_adapter_rejects_identity_mutations_before_runner(name, kwargs):
    fixture = _build_canonical_fixture()
    sidecar_kwargs = {
        key: value for key, value in kwargs.items() if key != "expected_registry_digest"
    }
    sidecar = _raw_sidecar(fixture, **sidecar_kwargs)
    expected_registry_digest = kwargs.get("expected_registry_digest")
    with pytest.raises(ValueError):
        _build_raw_stream(
            fixture, (sidecar,), expected_registry_digest=expected_registry_digest,
        )


def test_raw_adapter_rejects_valid_but_wrong_canonical_decision():
    fixture = _build_canonical_fixture()
    # ``reject`` is syntactically valid, but canonical j0 records ``accept``.
    with pytest.raises(ValueError, match="canonical judgment"):
        _build_raw_stream(fixture, (_raw_sidecar(fixture, decision="reject"),))


def test_raw_adapter_rejects_duplicate_unknown_and_late_before_runner():
    fixture = _build_canonical_fixture()
    good = _raw_sidecar(fixture)
    with pytest.raises(ValueError, match="duplicate"):
        _build_raw_stream(fixture, (good, good))
    with pytest.raises(ValueError):
        _build_raw_stream(fixture, (_raw_sidecar(fixture, decision="unknown"),))
    with pytest.raises(ValueError, match="unavailable at read_cut"):
        _build_raw_stream(fixture, (good,), late=True)


def test_raw_adapter_receipt_is_zero_call_and_fail_closed(tmp_path):
    summary = run(tmp_path / "raw-adapter")
    assert summary["status"] == "QUALIFIED_OFFLINE_SOURCE_ADAPTERS"
    assert summary["passed"] is True
    assert summary["real_api_calls"] == 0
    assert summary["gpu_jobs"] == 0
    assert summary["scientific_claim_allowed"] is False
    assert len(summary["rejected_cells"]) == 7
    assert all(
        row["runner_started"] is False
        and row["selection_count"] == 0
        and row["policy_update_count"] == 0
        for row in summary["rejected_cells"]
    )
