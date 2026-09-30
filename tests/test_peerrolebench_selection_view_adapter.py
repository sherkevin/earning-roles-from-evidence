from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import PeerSelection  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_baseline_policies import CandidateRef  # noqa: E402
from peerrolebench_metateam_profile_qualification import profile  # noqa: E402
from peerrolebench_metateam_profile_sidecar import (  # noqa: E402
    MetaTeamAssignmentOffer, bind_assignment_to_selection,
)
from peerrolebench_selection_view_adapter import (  # noqa: E402
    VersionedSelectionView, versioned_keys_to_native_ids,
    view_from_native_selection, view_from_versioned_selection,
)


def registry():
    return [
        CandidateRegistryEntry("agent-a", "v1", "a" * 64, "fixture", "b" * 64),
        CandidateRegistryEntry("agent-b", "v2", "c" * 64, "fixture", "b" * 64),
    ]


def test_versioned_keys_preserve_order_and_exact_versions():
    assert versioned_keys_to_native_ids(("agent-b@v2", "agent-a@v1"), registry()) == (
        "agent-b", "agent-a"
    )
    with pytest.raises(ValueError, match="requested version"):
        versioned_keys_to_native_ids(("agent-b@v1",), registry())
    with pytest.raises(ValueError, match="unique"):
        versioned_keys_to_native_ids(("agent-a@v1", "agent-a@v1"), registry())
    with pytest.raises(ValueError, match="strings"):
        versioned_keys_to_native_ids(("agent-a@v1", 3), registry())


def test_native_selection_gets_versioned_view_without_reordering():
    native = PeerSelection(
        "selection-3", "task", 3, "recipient", "producer",
        ("agent-b", "agent-a"), "agent-b", 0.5,
    )
    view = view_from_native_selection(native, registry(), selected_at=3.0)
    assert [candidate.key for candidate in view.candidates] == ["agent-b@v2", "agent-a@v1"]
    assert view.chosen_key == "agent-b@v2"
    assert view.task_index == 3
    with pytest.raises(ValueError, match="finite"):
        view_from_native_selection(native, registry(), selected_at=float("nan"))
    with pytest.raises(ValueError, match="non-negative"):
        view_from_native_selection(native, registry(), selected_at=-1.0)


def test_versioned_view_binds_native_menu_to_later_assignment():
    source = profile(
        profile_id="profile-b", candidate_key="agent-b@v2",
        selected_candidate_key="agent-b@v2",
    )
    offer = MetaTeamAssignmentOffer.build(
        offer_id="offer-3", task_id="task", decision_index=3, read_cut=2,
        candidate_keys=("agent-a@v1", "agent-b@v2"), profiles=(source,),
    )
    attestation = offer.attest_consumption((source.profile_id,))
    native = PeerSelection(
        "selection-3", "task", 3, "recipient", "producer",
        ("agent-a", "agent-b"), "agent-b", 0.5,
    )
    view = view_from_native_selection(native, registry(), selected_at=3.0)
    bind_assignment_to_selection(offer, attestation, view)


def test_versioned_view_rejects_wrong_choice_or_self_selection():
    with pytest.raises(ValueError, match="outside"):
        view_from_versioned_selection(
            candidate_keys=("agent-a@v1", "agent-b@v2"), chosen_key="agent-c@v1",
            task_index=3, selected_at=3.0, selector_id="recipient", registry=registry(),
        )
    with pytest.raises(ValueError, match="cannot choose itself"):
        VersionedSelectionView(
            candidates=(CandidateRef("recipient", "v1"), CandidateRef("agent-b", "v2")),
            chosen_index=0, task_index=3, selected_at=3.0, selector_id="recipient",
        )
    with pytest.raises(ValueError, match="task_index"):
        view_from_versioned_selection(
            candidate_keys=("agent-a@v1", "agent-b@v2"), chosen_key="agent-a@v1",
            task_index="3", selected_at=3.0, selector_id="recipient", registry=registry(),
        )
