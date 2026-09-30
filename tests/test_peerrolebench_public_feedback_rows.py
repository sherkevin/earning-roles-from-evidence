from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_policy_projection import PolicyFeedbackProjection  # noqa: E402
from peerrolebench_public_feedback_rows import (  # noqa: E402
    offer_from_projections, projection_to_public_row,
)


def projection(*, disposition="eligible", label=1.0, arrival_index=2):
    return PolicyFeedbackProjection(
        feedback_id="feedback-0", source_event_id="policy-selection-0",
        source="recipient_judgment", candidate_key="agent-b@v1",
        evidence_version="pipe3-evidence-v1", source_index=0,
        arrived_at=5.0, delay=3.0, action="repair", disposition=disposition,
        provenance="public" if disposition == "eligible" else "unknown",
        label=label if disposition == "eligible" else None,
        arrival_index=arrival_index,
    )


def test_projection_serializes_only_public_event_time_fields():
    row = projection_to_public_row(projection())
    assert row["candidate_key"] == "agent-b@v1"
    assert row["arrival_index"] == 2
    assert "responsibility_status" not in row


def test_unknown_requires_reason_and_never_gets_label():
    row = projection_to_public_row(projection(disposition="unknown"), unknown_reason="mixed-edit")
    assert row["unknown_reason"] == "mixed-edit"
    assert "label" not in row
    with pytest.raises(ValueError, match="unknown_reason"):
        projection_to_public_row(projection(disposition="unknown"))


def test_old_wall_clock_projection_is_rejected():
    with pytest.raises(ValueError, match="arrival_index"):
        projection_to_public_row(projection(arrival_index=None))


def test_offer_from_projection_binds_menu_and_evidence_version():
    offer = offer_from_projections(
        offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1,
        role="producer", context_key="PIPE3:1",
        candidate_keys=("agent-a@v1", "agent-b@v1"),
        projections=((projection(), None),),
        evidence_version="pipe3-evidence-v1", available_index=2,
    )
    assert offer.public_rows[0]["candidate_key"] == "agent-b@v1"
    assert offer.evidence_ids == ("policy-selection-0",)


def test_offer_rejects_projection_outside_menu_or_mismatched_version():
    with pytest.raises(ValueError, match="outside the offer menu"):
        offer_from_projections(
            offer_id="offer-1", task_id="task", task_index=1, role="producer",
            context_key="ctx", candidate_keys=("agent-a@v1",),
            projections=((projection(), None),),
            evidence_version="pipe3-evidence-v1", available_index=2,
        )
    with pytest.raises(ValueError, match="version"):
        offer_from_projections(
            offer_id="offer-1", task_id="task", task_index=1, role="producer",
            context_key="ctx", candidate_keys=("agent-a@v1", "agent-b@v1"),
            projections=((projection(), None),),
            evidence_version="other-version", available_index=2,
        )
