"""Unit tests for ``workspace.idea04_core.task_tree`` (E-001).

Run with::

    python -m pytest workspace/idea04_core/test_task_tree.py -v
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from workspace.idea04_core.task_tree import (
    MAX_SUBTASKS_PER_SPLIT,
    MAX_TREE_DEPTH,
    MAX_TOTAL_NODES,
    TASK_TREE_SCHEMA_VERSION,
    TaskNode,
    TaskTreeError,
    TaskTreeState,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_root(task_id: str = "root") -> TaskNode:
    return TaskNode(
        task_id=task_id,
        parent_task_id=None,
        root_task_id=task_id,
        task_text="What is the capital of France?",
        task_type_guess="qa",
        required_output="city name",
        depth=0,
        owner_agent="decomposer",
        executor_agent="decomposer",
    )


def _make_child(task_id: str, parent: TaskNode) -> TaskNode:
    return TaskNode(
        task_id=task_id,
        parent_task_id=parent.task_id,
        root_task_id=parent.root_task_id,
        task_text=f"sub of {parent.task_id}",
        depth=parent.depth + 1,
    )


# ---------------------------------------------------------------------------
# 1. Round-trip serialisation
# ---------------------------------------------------------------------------

def test_round_trip_serialization_node() -> None:
    """A TaskNode round-trips byte-identically via to_jsonl_record / from_jsonl_record."""
    n = _make_root()
    n.input_evidence = ["e1", "e2"]
    n.candidate_result = "Paris"
    n.metadata = {"router_score": 0.83, "future_field": [1, 2, 3]}

    rec = n.to_jsonl_record()
    n2 = TaskNode.from_jsonl_record(rec)
    assert asdict(n2) == asdict(n)


def test_round_trip_serialization_state() -> None:
    """A small tree round-trips through jsonl lines."""
    root = _make_root()
    state = TaskTreeState(root)
    c1 = _make_child("c1", root)
    state.add_subtask("root", c1)
    c2 = _make_child("c2", root)
    state.add_subtask("root", c2)
    g11 = _make_child("g11", state.nodes["c1"])
    state.add_subtask("c1", g11)

    lines = state.to_jsonl_lines()
    assert len(lines) == 4

    state2 = TaskTreeState.from_jsonl_lines(lines)
    assert state2.total_nodes() == 4
    assert state2.max_depth() == 2
    # node-by-node identity
    for nid, n in state.nodes.items():
        assert nid in state2.nodes
        assert asdict(state2.nodes[nid]) == asdict(n)


# ---------------------------------------------------------------------------
# 2. Parent-child consistency
# ---------------------------------------------------------------------------

def test_parent_child_consistency_after_add() -> None:
    root = _make_root()
    state = TaskTreeState(root)
    child = _make_child("c1", root)
    state.add_subtask("root", child)
    assert "c1" in state.nodes["root"].child_task_ids
    assert state.nodes["c1"].parent_task_id == "root"
    assert state.nodes["c1"].root_task_id == "root"
    assert state.nodes["c1"].depth == 1


def test_add_subtask_patches_inconsistent_root_id() -> None:
    """If subtask comes in with stale root_task_id, add_subtask silently corrects."""
    root = _make_root()
    state = TaskTreeState(root)
    bad_child = TaskNode(
        task_id="c1",
        parent_task_id=None,
        root_task_id="some_other_root",  # wrong
        task_text="x",
    )
    state.add_subtask("root", bad_child)
    assert state.nodes["c1"].root_task_id == "root"
    assert state.nodes["c1"].parent_task_id == "root"


def test_add_subtask_rejects_wrong_explicit_parent() -> None:
    root = _make_root()
    state = TaskTreeState(root)
    bad_child = TaskNode(
        task_id="c1",
        parent_task_id="other_parent_id",  # explicit but wrong
        root_task_id="root",
        task_text="x",
    )
    with pytest.raises(TaskTreeError, match="parent_task_id"):
        state.add_subtask("root", bad_child)


def test_add_subtask_rejects_unknown_parent() -> None:
    root = _make_root()
    state = TaskTreeState(root)
    child = _make_child("c1", root)
    with pytest.raises(TaskTreeError, match="not in tree"):
        state.add_subtask("nope", child)


def test_add_subtask_rejects_duplicate_id() -> None:
    root = _make_root()
    state = TaskTreeState(root)
    state.add_subtask("root", _make_child("c1", root))
    with pytest.raises(TaskTreeError, match="already exists"):
        state.add_subtask("root", _make_child("c1", root))


# ---------------------------------------------------------------------------
# 3. Bounds
# ---------------------------------------------------------------------------

def test_max_subtasks_bound() -> None:
    """4th sibling raises."""
    root = _make_root()
    state = TaskTreeState(root)
    for i in range(MAX_SUBTASKS_PER_SPLIT):
        state.add_subtask("root", _make_child(f"c{i}", root))
    with pytest.raises(TaskTreeError, match="cap reached"):
        state.add_subtask("root", _make_child("overflow", root))


def test_max_depth_bound() -> None:
    """Adding a child at depth = MAX_TREE_DEPTH+1 raises."""
    root = _make_root()
    state = TaskTreeState(root)
    cur = root
    for d in range(1, MAX_TREE_DEPTH + 1):
        nxt = _make_child(f"d{d}", cur)
        state.add_subtask(cur.task_id, nxt)
        cur = state.nodes[f"d{d}"]
    # cur is now at MAX_TREE_DEPTH; adding a child would push depth to MAX+1
    too_deep = _make_child("toodeep", cur)
    with pytest.raises(TaskTreeError, match="MAX_TREE_DEPTH"):
        state.add_subtask(cur.task_id, too_deep)


def test_max_total_nodes_bound() -> None:
    """13th node (counting root) raises."""
    root = _make_root()
    state = TaskTreeState(root)
    # Build a tree that fills exactly MAX_TOTAL_NODES then overflows once.
    # Strategy: chain to depth MAX_TREE_DEPTH (4 nodes), then fan-out children
    # under the last few until we hit the cap.
    cur = root
    next_id = 0

    def fresh_id() -> str:
        nonlocal next_id
        next_id += 1
        return f"n{next_id}"

    # add nodes greedily: depth-first then breadth-first; stop when full
    while state.total_nodes() < MAX_TOTAL_NODES:
        # try adding a child to any node that has capacity AND room in depth
        added = False
        for nid in list(state.nodes.keys()):
            n = state.nodes[nid]
            if (
                len(n.child_task_ids) < MAX_SUBTASKS_PER_SPLIT
                and n.depth < MAX_TREE_DEPTH
                and state.total_nodes() < MAX_TOTAL_NODES
            ):
                state.add_subtask(nid, _make_child(fresh_id(), n))
                added = True
                break
        if not added:
            break  # tree shape doesn't allow more without violating depth

    assert state.total_nodes() == MAX_TOTAL_NODES, (
        f"could not fill to cap with these bounds; got {state.total_nodes()}"
    )

    # any further add must fail at the total-nodes guard
    # find any non-leaf with sub-cap children and depth < MAX_TREE_DEPTH
    overflow_parent = None
    for nid, n in state.nodes.items():
        if (
            len(n.child_task_ids) < MAX_SUBTASKS_PER_SPLIT
            and n.depth < MAX_TREE_DEPTH
        ):
            overflow_parent = nid
            break
    if overflow_parent is None:
        # in this case the depth/subtask limits already block adds; we still
        # need to demonstrate the total-nodes guard — pick any node.
        overflow_parent = next(iter(state.nodes))
    with pytest.raises(TaskTreeError):
        state.add_subtask(
            overflow_parent, _make_child("overflow", state.nodes[overflow_parent])
        )


# ---------------------------------------------------------------------------
# 4. Forward-compat (dual-track schema, per pinned cautions C-3)
# ---------------------------------------------------------------------------

def test_jsonl_load_silently_drops_unknown_fields() -> None:
    """Loading a record that has a future field (e.g. competence_v2_vector) must not crash."""
    n = _make_root()
    rec = n.to_jsonl_record()
    rec["competence_v2_vector"] = {"decomposer": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]}
    rec["competence_v1_scalar"] = {"decomposer": 0.83}
    rec["totally_new_v3_field"] = "foo"
    loaded = TaskNode.from_jsonl_record(rec)
    # known fields preserved
    assert loaded.task_id == n.task_id
    # unknown fields silently dropped (not echoed in metadata)
    assert "competence_v2_vector" not in asdict(loaded)


def test_jsonl_load_handles_missing_optional_fields() -> None:
    """Older records lacking newer optional fields fall back to defaults."""
    minimal = {
        "task_id": "x",
        "parent_task_id": None,
        "root_task_id": "x",
        "task_text": "q",
    }
    loaded = TaskNode.from_jsonl_record(minimal)
    assert loaded.status == "pending"
    assert loaded.audit_status == "not_audited"
    assert loaded.depth == 0
    assert loaded.candidate_result is None
    assert loaded.schema_version == TASK_TREE_SCHEMA_VERSION


def test_state_validates_corrupt_jsonl() -> None:
    """from_jsonl_lines raises if structural invariants are violated."""
    root = _make_root()
    rec_root = root.to_jsonl_record()
    bad_child = _make_child("c1", root)
    bad_child.parent_task_id = "nonexistent"
    rec_child = bad_child.to_jsonl_record()
    lines = [json.dumps(rec_root), json.dumps(rec_child)]
    with pytest.raises(TaskTreeError, match="not in tree"):
        TaskTreeState.from_jsonl_lines(lines)


# ---------------------------------------------------------------------------
# 5. Validation negative tests
# ---------------------------------------------------------------------------

def test_root_must_have_no_parent() -> None:
    bad_root = TaskNode(
        task_id="r",
        parent_task_id="someone",  # invalid for root
        root_task_id="r",
        task_text="q",
    )
    with pytest.raises(TaskTreeError, match="root must have parent_task_id=None"):
        TaskTreeState(bad_root)


def test_root_root_task_id_must_match() -> None:
    bad_root = TaskNode(
        task_id="r",
        parent_task_id=None,
        root_task_id="other",  # invalid
        task_text="q",
    )
    with pytest.raises(TaskTreeError, match="root_task_id"):
        TaskTreeState(bad_root)


def test_invalid_status_rejected() -> None:
    with pytest.raises(TaskTreeError, match="invalid status"):
        TaskNode(
            task_id="x",
            parent_task_id=None,
            root_task_id="x",
            task_text="q",
            status="banana",
        )


def test_invalid_audit_status_rejected() -> None:
    with pytest.raises(TaskTreeError, match="invalid audit_status"):
        TaskNode(
            task_id="x",
            parent_task_id=None,
            root_task_id="x",
            task_text="q",
            audit_status="grumpy",
        )


def test_uncertainty_out_of_range_rejected() -> None:
    with pytest.raises(TaskTreeError, match="current_uncertainty"):
        TaskNode(
            task_id="x",
            parent_task_id=None,
            root_task_id="x",
            task_text="q",
            current_uncertainty=1.5,
        )
