"""Reference invariants for the candidate RARE-Anchor updater."""

from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_raresafe_candidate import RareAnchorState, RoleFeedback  # noqa: E402


def event(key, index, label, *, status="eligible", supersedes=None):
    return RoleFeedback(key, index, (1.0, 0.0, 0.0, 0.0), label, 1.0,
                        status=status, supersedes=supersedes)


def test_unknown_and_duplicate_do_not_change_policy_semantics():
    state = RareAnchorState(dimension=4, window_size=2)
    assert state.ingest(event("e0", 0, 1.0)) == "UPDATE"
    digest = state.semantic_digest()
    assert state.ingest(event("e0", 0, 1.0)) == "DUPLICATE"
    assert state.semantic_digest() == digest
    assert state.ingest(event("u", 1, None, status="unknown")) == "UNKNOWN"
    assert state.semantic_digest() == digest


def test_window_correction_and_late_event_are_explicit():
    state = RareAnchorState(dimension=4, window_size=2)
    state.ingest(event("e0", 0, 1.0))
    state.ingest(event("e1", 1, 0.0))
    before = state.semantic_digest()
    assert state.ingest(event("e0-c", 2, 0.0, supersedes="e0")) == "UPDATE"
    assert state.semantic_digest() != before
    after = state.semantic_digest()
    assert state.ingest(event("late", 1, 1.0)) == "QUEUED_CORRECTION"
    assert state.semantic_digest() == after


def test_snapshot_restore_is_exact_and_anchor_radius_is_bounded():
    state = RareAnchorState(dimension=4, window_size=2, radius=0.25)
    state.ingest(event("e0", 0, 1.0))
    restored = RareAnchorState.restore(state.snapshot())
    assert restored.digest() == state.digest()
    delta = sum((state.theta[i] - state.anchor[i]) ** 2 for i in range(4)) ** 0.5
    assert delta <= 0.25 + 1e-9


def test_event_time_interleaving_only_early_feedback_changes_next_choice():
    candidates = ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0))
    empty = RareAnchorState(dimension=4)
    baseline = empty.probabilities(candidates)
    early = RareAnchorState(dimension=4)
    early.ingest(event("early", 0, 1.0))
    assert early.probabilities(candidates) != baseline
    late = RareAnchorState(dimension=4)
    captured = late.probabilities(candidates)
    late.ingest(event("late", 0, 1.0))
    assert captured == baseline


def test_consolidation_preserves_anchor_policy_when_fast_window_is_cleared():
    state = RareAnchorState(dimension=1, radius=2.0)
    assert state.ingest(RoleFeedback("e", 0, (1.0,), 1.0, 1.0)) == "UPDATE"
    before = list(state.theta)
    assert before == [0.5]
    assert state.consolidate_if_safe([((1.0,), 1.0)]) is True
    assert state.theta == before
    assert state.anchor == before


def test_late_correction_queue_and_tombstones_are_bounded():
    state = RareAnchorState(dimension=1, pending_size=3)
    assert state.ingest(RoleFeedback("fresh", 10, (1.0,), 1.0, 1.0)) == "UPDATE"
    for index in range(10):
        assert state.ingest(RoleFeedback(f"late-{index}", 0, (1.0,), 1.0, 1.0)) == "QUEUED_CORRECTION"
    assert len(state.correction_queue) == 3
    assert state.pending_overflow == 7


def test_candidate_fixes_ridge_lambda():
    with pytest.raises(ValueError, match="lam=1"):
        RareAnchorState(dimension=1, lam=0.5)
