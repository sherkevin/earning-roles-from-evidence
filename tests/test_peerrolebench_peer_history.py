import hashlib
import json

import pytest

from scripts.peerrolebench_peer_history import (
    AssignmentSealV1,
    HistoryCostV1,
    HistoryEntryV1,
    PeerHistoryV1,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _seal(agent: str = "peer-a", assignment: str = "as0") -> AssignmentSealV1:
    return AssignmentSealV1(assignment, agent, _sha("role"), _sha("state"), 3, _sha("registry"))


def _entry(agent: str = "peer-a", assignment: str = "as0", entry: str = "e0", status: str = "PASS", arrival: int = 4) -> HistoryEntryV1:
    return HistoryEntryV1(entry, agent, agent, _sha("role"), _sha("state"), _sha("delivery"),
                          "judgment-0", 1.0 if status == "PASS" else None,
                          "outcome-0", 1.0 if status == "PASS" else None,
                          _sha("metric"), HistoryCostV1(input_tokens=2, output_tokens=3, wall_ms=4.0),
                          arrival, assignment, status)


def test_empty_peer_content_is_homogeneous_and_projection_is_public_only():
    left = PeerHistoryV1.empty("peer-a")
    right = PeerHistoryV1.empty("peer-b")
    assert left.content_digest() == right.content_digest()
    projection = left.selector_projection()
    assert projection["entry_count"] == 0
    assert "artifact_sha256" not in json.dumps(projection)
    assert "task_id" not in json.dumps(projection)


def test_history_requires_assignment_seal_and_rejects_duplicate_lineage():
    history = PeerHistoryV1.empty("peer-a")
    with pytest.raises(ValueError, match="prior assignment seal"):
        history.append(_entry())
    history.seal_assignment(_seal())
    history.append(_entry())
    with pytest.raises(ValueError, match="duplicate history entry"):
        history.append(_entry(entry="e0", arrival=5))


def test_unknown_is_counted_without_positive_support():
    history = PeerHistoryV1.empty("peer-a")
    history.seal_assignment(_seal())
    unknown = HistoryEntryV1("e0", "peer-a", "peer-a", _sha("role"), _sha("state"), _sha("delivery"),
                             "judgment-0", None, "outcome-0", None, _sha("metric"), HistoryCostV1(), 4, "as0", "UNKNOWN")
    history.append(unknown)
    scope = history.selector_projection()["scopes"][0]
    assert scope["n_unknown"] == 1
    assert scope["smoothed_rate"] is None


def test_determinate_history_requires_situated_recipient_judgment():
    with pytest.raises(ValueError, match="recipient judgment label"):
        HistoryEntryV1("e0", "peer-a", "peer-a", _sha("role"), _sha("state"), _sha("delivery"),
                       "judgment-0", None, "outcome-0", 1.0, _sha("metric"), HistoryCostV1(),
                       4, "as0", "PASS")


def test_snapshot_replay_and_digest_mismatch_fail_closed():
    history = PeerHistoryV1.empty("peer-a")
    history.seal_assignment(_seal())
    history.append(_entry())
    snapshot = history.snapshot()
    restored = PeerHistoryV1.replay(snapshot)
    assert restored.state_digest() == history.state_digest()
    snapshot["state_digest"] = _sha("tampered")
    with pytest.raises(ValueError, match="digest mismatch"):
        PeerHistoryV1.replay(snapshot)


def test_snapshot_replay_rejects_unknown_version():
    history = PeerHistoryV1.empty("peer-a")
    history.seal_assignment(_seal())
    history.append(_entry())
    snapshot = history.snapshot()
    snapshot["version"] = "peer-history-v1"
    with pytest.raises(ValueError, match="unsupported peer history version"):
        PeerHistoryV1.replay(snapshot)


def test_entry_scope_mismatch_is_rejected():
    history = PeerHistoryV1.empty("peer-a")
    history.seal_assignment(_seal())
    wrong = _entry()
    wrong = HistoryEntryV1(wrong.entry_id, wrong.agent_key, wrong.subject_key, _sha("other-role"),
                           wrong.execution_state_fingerprint, wrong.delivery_digest,
                           wrong.recipient_judgment_id, wrong.recipient_judgment_label,
                           wrong.later_outcome_id, wrong.later_outcome_label, wrong.metric_digest,
                           wrong.cost, wrong.arrival_index, wrong.assignment_id, wrong.status)
    with pytest.raises(ValueError, match="does not match assignment scope"):
        history.append(wrong)


def test_projection_rejects_candidate_agent_mismatch():
    history = PeerHistoryV1.empty("peer-a")
    with pytest.raises(ValueError, match="candidate does not match"):
        history.selector_projection(candidate_key="peer-b@v1")
