"""Focused contract tests for the independent terminal-only channel."""

from __future__ import annotations

from dataclasses import replace
import sys

import pytest

sys.path.insert(0, "scripts")
sys.path.insert(0, "references/aamas")

from peerrolebench_canonical_pipe3_parity_qualification import _build_canonical_fixture  # noqa: E402
from peerrolebench_canonical_terminal_adapter_qualification import (  # noqa: E402
    _selection_sidecar, _terminal_sidecar, _positive,
)
from peerrolebench_terminal_outcome_projection import (  # noqa: E402
    TERMINAL_LABEL_MAPPING_DIGEST, TERMINAL_LABEL_MAPPING_VERSION,
    TerminalOutcomeSidecar, project_terminal_outcome,
)


@pytest.fixture()
def canonical():
    fixture = _build_canonical_fixture()
    selection, _ = _selection_sidecar(fixture)
    sidecar, outcome, delivery = _terminal_sidecar(fixture, selection)
    return fixture, selection, sidecar, outcome, delivery


def test_terminal_label_is_derived_from_native_success_and_hides_private_fields(canonical):
    fixture, selection, sidecar, outcome, delivery = canonical
    projected = project_terminal_outcome(
        sidecar, selection=selection, outcome_record=outcome,
        delivery_record=delivery, read_cut=5,
    )
    assert projected.label == 1.0
    assert projected.to_feedback().source == "terminal_outcome"
    assert not {"scorer_version", "score_payload_sha256", "success"} & set(projected.public_payload())


@pytest.mark.parametrize(
    "changes",
    [
        {"ledger_record_hash": "f" * 64},
        {"delivery_id": "d1"},
        {"selection_event_id": "s1"},
        {"producer_id": "peer-c"},
    ],
)
def test_terminal_lineage_mutations_fail_before_projection(canonical, changes):
    fixture, selection, sidecar, outcome, delivery = canonical
    mutated = replace(sidecar, **changes)
    with pytest.raises(ValueError):
        project_terminal_outcome(
            mutated, selection=selection, outcome_record=outcome,
            delivery_record=delivery, read_cut=5,
        )


def test_mapping_unknown_and_late_are_rejected(canonical):
    fixture, selection, sidecar, outcome, delivery = canonical
    with pytest.raises(ValueError, match="unsupported terminal label mapping"):
        TerminalOutcomeSidecar(
            **{**sidecar.__dict__, "label_mapping_version": "terminal-success-v2", "mapping_digest": "a" * 64}
        )
    unknown = replace(sidecar, success=None, disposition="unknown", provenance="unknown")
    with pytest.raises(ValueError, match="UNKNOWN/ineligible"):
        project_terminal_outcome(
            unknown, selection=selection, outcome_record=outcome,
            delivery_record=delivery, read_cut=5,
        )
    late = replace(sidecar, arrival_index=99)
    with pytest.raises(ValueError, match="after the frozen read cut"):
        project_terminal_outcome(
            late, selection=selection, outcome_record=outcome,
            delivery_record=delivery, read_cut=5,
        )


def test_canonical_terminal_matrix_cell_has_only_terminal_update(canonical):
    fixture, *_ = canonical
    result = _positive(fixture)
    assert result["status"] == "PASS"
    assert result["checks"]["terminal_only_one_eligible"]
    assert result["checks"]["terminal_only_one_update"]
    assert result["checks"]["other_arms_ignore_terminal"]
    assert result["checks"]["seven_arm_public_input_digests_equal"]
    assert result["checks"]["snapshot_replay_equal"]
