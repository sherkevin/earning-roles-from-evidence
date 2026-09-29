from dataclasses import replace
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_policy_matrix_runner_v1 import (  # noqa: E402
    ARM_NAMES,
    PolicyMatrixRunner,
    fixture_case,
    _registry,
    run_fixture_suite,
)
from peerrolebench_event_time_schedule import schedule_digest  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment  # noqa: E402


def test_all_arms_pass_seven_offline_contract_cases(tmp_path):
    result = run_fixture_suite(tmp_path / "matrix")
    assert result["status"] == "QUALIFIED_OFFLINE"
    assert result["passed"] is True
    assert result["real_api_calls"] == 0
    assert result["gpu_jobs"] == 0
    assert result["scientific_claim_allowed"] is False
    assert set(result["results"]) == {
        "recipient_only", "producer_defect", "terminal", "raw_acceptance", "unknown_late_correction", "unknown", "unselected",
    }
    for case_result in result["results"].values():
        assert set(case_result["metrics"]) == set(ARM_NAMES)
        assert all(item["snapshot_equal"] for item in case_result["replay"].values())


def test_runner_rejects_future_read_cut_and_schedule_digest():
    offers, schedule, digest = fixture_case("recipient_only")
    runner = PolicyMatrixRunner(registry=_registry())
    with pytest.raises(ValueError, match="read_cut is after decision_index"):
        runner.run([replace(offers[0], read_cut=1), offers[1]], schedule, expected_schedule_digest=digest)
    with pytest.raises(ValueError, match="digest mismatch"):
        runner.run(offers, schedule, expected_schedule_digest="0" * 64)


def test_runner_binds_protocol_event_identity_and_decision_order():
    offers, schedule, digest = fixture_case("recipient_only")
    runner = PolicyMatrixRunner(registry=_registry())
    altered_schedule = [replace(schedule[0], protocol_event_id="different-event")]
    altered_digest = schedule_digest(altered_schedule)
    with pytest.raises(ValueError, match="protocol event disagrees"):
        runner.run(offers, altered_schedule, expected_schedule_digest=altered_digest)
    altered_source = [replace(schedule[0], source_event_id="different-source")]
    altered_source_digest = schedule_digest(altered_source)
    with pytest.raises(ValueError, match="source event disagrees"):
        runner.run(offers, altered_source, expected_schedule_digest=altered_source_digest)
    with pytest.raises(ValueError, match="duplicate decision index"):
        runner.run(
            [replace(offers[0], decision_index=1), replace(offers[1], decision_index=1)],
            schedule, expected_schedule_digest=digest,
        )


def test_runner_rejects_offer_available_after_read_cut():
    offers, schedule, digest = fixture_case("recipient_only")
    runner = PolicyMatrixRunner(registry=_registry())
    late = replace(offers[1], read_cut=0)
    with pytest.raises(ValueError, match="unavailable at read_cut"):
        runner.run([offers[0], late], schedule, expected_schedule_digest=digest)


def test_runner_rejects_candidate_outside_frozen_registry():
    offers, schedule, digest = fixture_case("recipient_only")
    runner = PolicyMatrixRunner(registry=_registry()[:2])
    with pytest.raises(ValueError, match="unregistered candidate keys"):
        runner.run(offers, schedule, expected_schedule_digest=digest)


def _timing_schedule(feedback_id: str, arrival_index: int, source_event_id: str = "policy-selection-0"):
    rows = (ArrivalAssignment(
        feedback_id=feedback_id, protocol_event_type="recipient_judgment",
        protocol_event_id="j0", source_event_id=source_event_id,
        arrival_index=arrival_index,
    ),)
    return rows, schedule_digest(rows)


def test_early_feedback_changes_next_choice_but_late_feedback_cannot_rewrite_it():
    from peerrolebench_policy_matrix_runner_v1 import _offer, _row

    keys = ("agent-b@v1", "agent-c@v1")
    first = _offer(
        offer_id="timing-0", task_index=0, candidate_keys=keys, public_rows=(),
        available_index=0, native_selection_id="selection-0", read_cut=0,
        decision_index=0, selected_at=0.0, rng_seed=11, context_key="shared-context",
    )
    early_row = _row(
        feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
        source="recipient_judgment", candidate_key="agent-b@v1", arrival_index=1, label=1.0,
    )
    early = _offer(
        offer_id="timing-early", task_index=1, candidate_keys=keys, public_rows=(early_row,),
        available_index=1, native_selection_id="selection-1", read_cut=1,
        decision_index=1, selected_at=1.0, rng_seed=12, context_key="shared-context",
    )
    early_schedule, early_digest = _timing_schedule("f0", 1)
    early_result = PolicyMatrixRunner(
        registry=_registry(), arm_names=("contextual_trust", "no_update"),
    ).run([first, early], early_schedule, expected_schedule_digest=early_digest)
    assert early_result["traces"]["contextual_trust"][1]["probabilities"] != early_result["traces"]["no_update"][1]["probabilities"]

    late_row = _row(
        feedback_id="f-late", source_event_id="policy-selection-0", protocol_event_id="j0",
        source="recipient_judgment", candidate_key="agent-b@v1", arrival_index=3, label=1.0,
    )
    second = _offer(
        offer_id="timing-second", task_index=1, candidate_keys=keys, public_rows=(),
        available_index=0, native_selection_id="selection-1", read_cut=1,
        decision_index=1, selected_at=1.0, rng_seed=12, context_key="shared-context",
    )
    late = _offer(
        offer_id="timing-late", task_index=2, candidate_keys=keys, public_rows=(late_row,),
        available_index=3, native_selection_id="selection-2", read_cut=3,
        decision_index=3, selected_at=3.0, rng_seed=13, context_key="shared-context",
    )
    late_schedule, late_digest = _timing_schedule("f-late", 3)
    late_result = PolicyMatrixRunner(
        registry=_registry(), arm_names=("contextual_trust", "no_update"),
    ).run([first, second, late], late_schedule, expected_schedule_digest=late_digest)
    assert late_result["traces"]["contextual_trust"][1]["feedback"] == []
    assert late_result["traces"]["contextual_trust"][1]["probabilities"] == late_result["traces"]["no_update"][1]["probabilities"]
    assert late_result["traces"]["contextual_trust"][2]["feedback"][0]["disposition"] == "eligible"


def test_feedback_cannot_self_reference_the_selection_being_made():
    from peerrolebench_policy_matrix_runner_v1 import _offer, _row

    row = _row(
        feedback_id="self", source_event_id="policy-selection-1", protocol_event_id="j0",
        source="recipient_judgment", candidate_key="agent-b@v1", arrival_index=1, label=1.0,
    )
    offer = _offer(
        offer_id="self-offer", task_index=1, candidate_keys=("agent-b@v1", "agent-c@v1"),
        public_rows=(row,), available_index=1, native_selection_id="selection-1",
        read_cut=1, decision_index=1, selected_at=1.0, rng_seed=11,
    )
    schedule, digest = _timing_schedule("self", 1, source_event_id="policy-selection-1")
    with pytest.raises(ValueError, match="unknown source selection"):
        PolicyMatrixRunner(registry=_registry()).run(
            [offer], schedule, expected_schedule_digest=digest,
        )


def test_unselected_shared_fixture_is_skipped_without_update():
    offers, schedule, digest = fixture_case("recipient_only")
    # Point the public judgment at the candidate that was not selected by the
    # source event.  It must be skipped, never relabeled as a negative sample.
    from peerrolebench_policy_matrix_runner_v1 import _offer, _row

    row = _row(
        feedback_id="f0", source_event_id="policy-selection-0", protocol_event_id="j0",
        source="recipient_judgment", candidate_key="agent-c@v1", arrival_index=1,
        label=1.0,
    )
    changed = _offer(
        offer_id="recipient_only-unselected", task_index=1,
        candidate_keys=("agent-b@v1", "agent-c@v1"), public_rows=(row,),
        available_index=1, native_selection_id="selection-1", read_cut=1,
        decision_index=1, selected_at=1.0, rng_seed=12,
    )
    result = PolicyMatrixRunner(registry=_registry()).run(
        [offers[0], changed], schedule, expected_schedule_digest=digest,
    )
    assert all(result["metrics"][name]["n_unselected"] == 1 for name in ARM_NAMES)
    for name in ARM_NAMES:
        if result["metrics"][name]["n_unselected"]:
            assert result["metrics"][name]["n_eligible"] == 0
            assert result["metrics"][name]["updates"] == 0


def test_unknown_rows_require_an_explicit_reason():
    offers, schedule, digest = fixture_case("recipient_only")
    row = dict(offers[1].offer.public_rows[0])
    row["disposition"] = "unknown"
    row["provenance"] = "unknown"
    row.pop("label", None)
    # Rebuild the offer through the public constructor by using the helper's
    # canonical maker; the runner, rather than the constructor, owns the
    # explicit UNKNOWN reason policy.
    from peerrolebench_policy_matrix_runner_v1 import _offer, _registry

    unknown_offer = _offer(
        offer_id="unknown-offer", task_index=1,
        candidate_keys=("agent-b@v1", "agent-c@v1"), public_rows=(row,),
        available_index=1, native_selection_id="selection-1", read_cut=1,
        decision_index=1, selected_at=1.0, rng_seed=12,
        protocol_event_ids={"f0": "j0"},
    )
    with pytest.raises(ValueError, match="UNKNOWN evidence"):
        PolicyMatrixRunner(registry=_registry()).run(
            [offers[0], unknown_offer], schedule, expected_schedule_digest=digest,
        )
