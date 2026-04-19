"""Unit tests for ``workspace.idea04_core.action_policy`` (E-002).

Run from repo root::

    python -m pytest workspace/idea04_core/test_action_policy.py -v

All LLM interaction is mocked so this suite makes zero network calls.
"""

from __future__ import annotations

import json
import pathlib
from typing import Callable

import pytest

from workspace.idea04_core.action_policy import (
    Action,
    ActionDecision,
    ActionPolicyError,
    _can_split,
    _call_llm_split,
    _estimate_utility_self,
    _estimate_utility_out,
    _estimate_utility_split,
    select_action,
)
from workspace.idea04_core.task_tree import (
    MAX_SUBTASKS_PER_SPLIT,
    MAX_TREE_DEPTH,
    MAX_TOTAL_NODES,
    TaskNode,
    TaskTreeState,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(*, evidence: list[str] | None = None, uncertainty: float = 0.5,
                depth: int = 0) -> TaskTreeState:
    root = TaskNode(
        task_id="root",
        parent_task_id=None,
        root_task_id="root",
        task_text="Which film was directed by the older director: Inception or Interstellar?",
        task_type_guess="comparison",
        input_evidence=list(evidence or []),
        current_uncertainty=uncertainty,
        depth=depth,
        owner_agent="decomposer",
    )
    return TaskTreeState(root)


def _mock_llm_returning(payload: dict | str) -> Callable[[str], str]:
    """Return a deterministic llm_callable that emits ``payload`` (json-encoded if dict)."""
    raw = payload if isinstance(payload, str) else json.dumps(payload)

    def _call(_prompt: str) -> str:
        return raw
    return _call


# ---------------------------------------------------------------------------
# 1. Core utility estimators in valid range
# ---------------------------------------------------------------------------


def test_utility_estimators_self_in_sane_range() -> None:
    state = _make_state(evidence=["e1", "e2"], uncertainty=0.3)
    u = _estimate_utility_self(state.root)
    # self utility = 0.5 * (2/6) + 0.3 * 0.7 + 0.2 = 0.167 + 0.21 + 0.2 = 0.577
    assert 0.0 <= u <= 1.5
    assert abs(u - (0.5 * (2/6) + 0.3 * 0.7 + 0.2)) < 1e-9


def test_utility_estimators_out_decreases_with_depth() -> None:
    n_shallow = TaskNode(
        task_id="x", parent_task_id=None, root_task_id="x", task_text="q", depth=0
    )
    n_deep = TaskNode(
        task_id="x", parent_task_id=None, root_task_id="x", task_text="q", depth=2
    )
    u_shallow = _estimate_utility_out(n_shallow, "neighbor", 0.7)
    u_deep = _estimate_utility_out(n_deep, "neighbor", 0.7)
    assert u_shallow > u_deep, "deeper hops must cost more"


def test_utility_split_returns_sentinel_when_infeasible() -> None:
    # depth at MAX_TREE_DEPTH → split infeasible
    state = _make_state(depth=MAX_TREE_DEPTH)
    u = _estimate_utility_split(state.root, state)
    assert u == -2.0


# ---------------------------------------------------------------------------
# 2. select_action — happy paths
# ---------------------------------------------------------------------------


def test_select_action_do_self_when_evidence_rich() -> None:
    """Plenty of evidence + low uncertainty → self utility wins."""
    state = _make_state(evidence=["e1", "e2", "e3", "e4", "e5", "e6"], uncertainty=0.1)
    decision = select_action(
        state.root,
        state,
        neighbors=["a", "b"],
        # neighbor belief intentionally low to force DO_SELF
        neighbor_belief_fn=lambda nb: 0.2,
    )
    assert decision.action == Action.DO_SELF
    assert "DO_SELF" in decision.rationale
    assert decision.utility_scores["self"] > decision.utility_scores["out_max"]


def test_select_action_outsource_when_neighbor_better() -> None:
    """Low evidence + high-quality neighbour → OUTSOURCE wins."""
    state = _make_state(evidence=[], uncertainty=0.7)
    decision = select_action(
        state.root,
        state,
        neighbors=["expert", "novice"],
        # asymmetric: expert is much better
        neighbor_belief_fn=lambda nb: 0.95 if nb == "expert" else 0.3,
        # llm_callable absent → SPLIT cannot win
        llm_callable=None,
    )
    assert decision.action == Action.OUTSOURCE
    assert decision.target_neighbor == "expert"


def test_select_action_split_with_valid_llm() -> None:
    """Low evidence at root + good llm_callable → SPLIT wins."""
    state = _make_state(evidence=[], uncertainty=0.6, depth=0)
    payload = {
        "subtasks": [
            {"task_text": "Who directed Inception?", "task_type_guess": "factoid"},
            {"task_text": "Who directed Interstellar?", "task_type_guess": "factoid"},
        ]
    }
    # neighbours weak so SPLIT can outscore OUTSOURCE
    decision = select_action(
        state.root,
        state,
        neighbors=["weak1", "weak2"],
        neighbor_belief_fn=lambda nb: 0.1,
        llm_callable=_mock_llm_returning(payload),
    )
    assert decision.action == Action.SPLIT
    assert len(decision.subtasks) == 2
    assert decision.subtasks[0].task_id == "root_sub1"
    assert decision.subtasks[0].depth == 1
    assert decision.subtasks[0].parent_task_id == "root"
    assert decision.subtasks[0].root_task_id == "root"


# ---------------------------------------------------------------------------
# 3. SPLIT downgrade paths
# ---------------------------------------------------------------------------


def test_split_downgrades_when_no_llm_callable() -> None:
    """SPLIT-best but llm_callable=None → silent downgrade to DO_SELF."""
    state = _make_state(evidence=[], uncertainty=0.6, depth=0)
    decision = select_action(
        state.root, state, neighbors=["weak"], neighbor_belief_fn=lambda nb: 0.05,
        llm_callable=None,
    )
    # split won the score race but no callable → DO_SELF
    assert decision.action == Action.DO_SELF
    assert "no llm_callable" in decision.rationale or "infeasible" in decision.rationale


def test_split_downgrades_at_max_depth() -> None:
    """At MAX_TREE_DEPTH the selector must not propose SPLIT regardless of LLM."""
    state = _make_state(depth=MAX_TREE_DEPTH)
    payload = {"subtasks": [{"task_text": "x", "task_type_guess": "factoid"}]}
    decision = select_action(
        state.root,
        state,
        neighbors=["nb"],
        neighbor_belief_fn=lambda nb: 0.1,
        llm_callable=_mock_llm_returning(payload),
    )
    assert decision.action != Action.SPLIT
    assert decision.utility_scores["split"] == -2.0


def test_split_downgrades_at_max_total_nodes() -> None:
    """When tree is near MAX_TOTAL_NODES (no room for 2 children) split must downgrade."""
    state = _make_state(evidence=[], uncertainty=0.6, depth=0)
    # Manually inflate state to MAX_TOTAL_NODES - 1 dummy nodes
    for i in range(MAX_TOTAL_NODES - 1):
        # spread under root subject to MAX_SUBTASKS_PER_SPLIT
        # cycle through depth chains to fit
        target_parent = "root"
        # find any parent with child slot + depth headroom
        for nid, node in state.nodes.items():
            if (
                len(node.child_task_ids) < MAX_SUBTASKS_PER_SPLIT
                and node.depth < MAX_TREE_DEPTH
            ):
                target_parent = nid
                break
        if state.total_nodes() >= MAX_TOTAL_NODES:
            break
        # make a synthetic child
        depth = state.nodes[target_parent].depth + 1
        if depth > MAX_TREE_DEPTH:
            break
        synth = TaskNode(
            task_id=f"synth{i}",
            parent_task_id=target_parent,
            root_task_id="root",
            task_text=f"synth-{i}",
            depth=depth,
        )
        state.add_subtask(target_parent, synth)
    # now near cap; SPLIT is infeasible because we cannot fit 2 more children
    assert state.total_nodes() >= MAX_TOTAL_NODES - 1
    decision = select_action(
        state.root,
        state,
        neighbors=["nb"],
        neighbor_belief_fn=lambda nb: 0.1,
        llm_callable=_mock_llm_returning({"subtasks": [{"task_text": "x"}]}),
    )
    assert decision.action != Action.SPLIT


def test_split_downgrades_when_llm_returns_invalid_json() -> None:
    """Malformed LLM output triggers downgrade with metadata['split_error']."""
    state = _make_state(evidence=[], uncertainty=0.7)
    bad_callable = _mock_llm_returning("not json at all just prose")
    decision = select_action(
        state.root,
        state,
        neighbors=["weak"],
        neighbor_belief_fn=lambda nb: 0.05,
        llm_callable=bad_callable,
    )
    assert decision.action == Action.DO_SELF
    assert "split_error" in decision.metadata or "SPLIT downgraded" in decision.rationale


def test_split_truncates_overflow_response() -> None:
    """If LLM returns 5 children, only the first MAX_SUBTASKS_PER_SPLIT are kept."""
    state = _make_state(evidence=[], uncertainty=0.6)
    payload = {
        "subtasks": [
            {"task_text": f"q{i}", "task_type_guess": "factoid"} for i in range(5)
        ]
    }
    decision = select_action(
        state.root,
        state,
        neighbors=["weak"],
        neighbor_belief_fn=lambda nb: 0.05,
        llm_callable=_mock_llm_returning(payload),
    )
    assert decision.action == Action.SPLIT
    assert len(decision.subtasks) == MAX_SUBTASKS_PER_SPLIT


def test_split_skips_malformed_subtasks() -> None:
    """LLM returns mix of valid and malformed entries; only valid ones survive."""
    state = _make_state(evidence=[], uncertainty=0.6)
    payload = {
        "subtasks": [
            {"task_text": "valid 1"},
            "not-a-dict",
            {"task_text": ""},  # empty text dropped
            {"task_text": "valid 2"},
        ]
    }
    decision = select_action(
        state.root,
        state,
        neighbors=["weak"],
        neighbor_belief_fn=lambda nb: 0.05,
        llm_callable=_mock_llm_returning(payload),
    )
    assert decision.action == Action.SPLIT
    texts = {t.task_text for t in decision.subtasks}
    assert texts == {"valid 1", "valid 2"}


# ---------------------------------------------------------------------------
# 4. Prompt loading + LLM call shape
# ---------------------------------------------------------------------------


def test_call_llm_split_loads_prompt_and_passes_node_text(tmp_path: pathlib.Path) -> None:
    """``_call_llm_split`` reads the prompt file, then sends node.task_text."""
    custom_prompt = tmp_path / "decompose.txt"
    custom_prompt.write_text("ROLE-SYS-PROMPT-SENTINEL", encoding="utf-8")

    captured: list[str] = []

    def _capture_llm(prompt: str) -> str:
        captured.append(prompt)
        return json.dumps({"subtasks": [{"task_text": "child A"}]})

    node = TaskNode(
        task_id="r",
        parent_task_id=None,
        root_task_id="r",
        task_text="UNIQUE-NODE-TEXT-456",
        input_evidence=["evidence-piece-789"],
    )
    out = _call_llm_split(node, _capture_llm, prompt_path=custom_prompt)
    assert len(out) == 1
    assert out[0].task_text == "child A"
    assert "ROLE-SYS-PROMPT-SENTINEL" in captured[0]
    assert "UNIQUE-NODE-TEXT-456" in captured[0]
    assert "evidence-piece-789" in captured[0]


def test_call_llm_split_raises_on_empty_response(tmp_path: pathlib.Path) -> None:
    custom_prompt = tmp_path / "decompose.txt"
    custom_prompt.write_text("X", encoding="utf-8")
    with pytest.raises(ActionPolicyError, match="empty response"):
        _call_llm_split(
            TaskNode(task_id="r", parent_task_id=None, root_task_id="r", task_text="q"),
            lambda _: "",
            prompt_path=custom_prompt,
        )


def test_call_llm_split_raises_on_missing_prompt_file(tmp_path: pathlib.Path) -> None:
    missing = tmp_path / "does_not_exist.txt"
    with pytest.raises(ActionPolicyError, match="cannot read decomposition prompt"):
        _call_llm_split(
            TaskNode(task_id="r", parent_task_id=None, root_task_id="r", task_text="q"),
            lambda _: '{"subtasks": []}',
            prompt_path=missing,
        )


# ---------------------------------------------------------------------------
# 5. _can_split guard semantics
# ---------------------------------------------------------------------------


def test_can_split_false_at_depth_cap() -> None:
    state = _make_state(depth=MAX_TREE_DEPTH)
    assert not _can_split(state.root, state)


def test_can_split_false_when_near_total_nodes_cap() -> None:
    """If only 1 node slot is free, splitting (which needs 2) must be False."""
    state = _make_state()
    # add MAX_TOTAL_NODES - 2 dummies under root (cap children at 3 by chaining)
    cur_parent = "root"
    next_id = 0
    while state.total_nodes() < MAX_TOTAL_NODES - 1:
        # find a parent with capacity
        for nid, node in state.nodes.items():
            if (
                len(node.child_task_ids) < MAX_SUBTASKS_PER_SPLIT
                and node.depth < MAX_TREE_DEPTH
            ):
                cur_parent = nid
                break
        depth = state.nodes[cur_parent].depth + 1
        if depth > MAX_TREE_DEPTH:
            break
        synth = TaskNode(
            task_id=f"s{next_id}",
            parent_task_id=cur_parent,
            root_task_id="root",
            task_text="x",
            depth=depth,
        )
        state.add_subtask(cur_parent, synth)
        next_id += 1
    # find any node still with depth/child headroom; _can_split must be False
    for n in state.nodes.values():
        if n.depth < MAX_TREE_DEPTH and len(n.child_task_ids) < MAX_SUBTASKS_PER_SPLIT:
            assert not _can_split(n, state), (
                f"_can_split should be False near total_nodes cap (have {state.total_nodes()})"
            )
            return  # one such node is enough


# ---------------------------------------------------------------------------
# 6. ActionDecision integrity
# ---------------------------------------------------------------------------


def test_action_decision_records_all_three_scores() -> None:
    state = _make_state(evidence=["e"], uncertainty=0.5)
    decision = select_action(
        state.root,
        state,
        neighbors=["nb"],
        neighbor_belief_fn=lambda nb: 0.6,
    )
    for k in ("self", "out_max", "split"):
        assert k in decision.utility_scores
