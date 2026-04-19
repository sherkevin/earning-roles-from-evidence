"""End-to-end integration smoke for the 4 Stage-2 modules (E-005 step 0).

This is a *composition* test: it runs `task_tree`, `action_policy`,
`audit_runtime`, `persona_model` together through one realistic micro-flow
to confirm their public APIs lock in. **No LLM is called** — we mock
``llm_callable`` so the test runs offline at zero cost.

The flow simulated::

  1. Build a TaskTreeState rooted at a 2-hop comparison question.
  2. The decomposer agent calls select_action — SPLIT wins because
     evidence is empty and a high-quality LLM decomposition is mocked.
  3. SPLIT produces two child subtasks; we register them in the tree
     using TaskTreeState.add_subtask (the bound-aware path).
  4. Two evidence_seeker agents return candidate results for the children;
     audit_candidate produces one AuditEvent each (rule-based path,
     no LLM consult).
  5. apply_audit_to_tree writes ``audit_status`` back into each child node;
     update_belief_from_audit advances the BeliefStore for the
     evidence_seeker neighbours.
  6. AuditEventBuffer.flush_to_jsonl persists both events; load_from_jsonl
     restores them with byte-equal decisions.
  7. BeliefStore is serialized through serialize_v2 (dual-track) and
     deserialized; the v2 vector survives round-trip and the v1 scalar
     projection is consistent with the v2 mean.

If this test passes, E-005's integration step (wiring these into
methods.py / runner.py) only has to do plumbing — the data-shape glue
between the four modules is verified to hold.
"""

from __future__ import annotations

import json
import pathlib
from typing import Callable

import pytest

from workspace.idea04_core.action_policy import (
    Action,
    ActionDecision,
    select_action,
)
from workspace.idea04_core.audit_runtime import (
    AuditDecision,
    AuditEvent,
    AuditEventBuffer,
    apply_audit_to_tree,
    audit_candidate,
)
from workspace.idea04_core.persona_model import (
    DIM_COUNT,
    BeliefStore,
    NEUTRAL_INIT,
    PersonaVector,
    deserialize,
    evidence_extract,
    serialize_v2,
    update_belief_from_audit,
)
from workspace.idea04_core.task_tree import TaskNode, TaskTreeState


def _mock_llm_split() -> Callable[[str], str]:
    """LLM that returns a 2-child decomposition appropriate for the test root."""
    payload = {
        "subtasks": [
            {"task_text": "Who directed Inception, and what year was that director born?",
             "task_type_guess": "factoid"},
            {"task_text": "Who directed Interstellar, and what year was that director born?",
             "task_type_guess": "factoid"},
        ]
    }
    raw = json.dumps(payload)

    def _call(_p: str) -> str:
        return raw
    return _call


def test_stage2_full_micro_flow(tmp_path: pathlib.Path) -> None:
    # ----- 1. Build root + state -----
    root = TaskNode(
        task_id="root",
        parent_task_id=None,
        root_task_id="root",
        task_text=(
            "Which film, Inception or Interstellar, was directed by the older director?"
        ),
        task_type_guess="comparison",
        depth=0,
        owner_agent="decomposer",
        executor_agent="decomposer",
    )
    state = TaskTreeState(root)
    assert state.total_nodes() == 1

    # ----- 2. select_action: SPLIT wins because evidence empty + good LLM -----
    decision = select_action(
        state.root,
        state,
        neighbors=["evidence_seeker_alpha", "evidence_seeker_beta"],
        # weak neighbours so SPLIT outscores OUTSOURCE
        neighbor_belief_fn=lambda nb: 0.05,
        llm_callable=_mock_llm_split(),
    )
    assert decision.action == Action.SPLIT, (
        f"expected SPLIT, got {decision.action}; scores={decision.utility_scores}"
    )
    assert len(decision.subtasks) == 2

    # ----- 3. register subtasks via the bound-aware add_subtask path -----
    for sub in decision.subtasks:
        state.add_subtask("root", sub)
    assert state.total_nodes() == 3
    child_ids = state.nodes["root"].child_task_ids
    assert len(child_ids) == 2

    # ----- 4. simulate downstream candidate returns + audit -----
    buf = AuditEventBuffer()
    belief = BeliefStore()  # held by the decomposer agent

    candidate_results = {
        child_ids[0]: "Inception was directed by Christopher Nolan, born in 1970.",
        child_ids[1]: "",  # second downstream returned empty -> REJECT_REROUTE
    }
    expected_decisions = {
        child_ids[0]: AuditDecision.ACCEPT,
        child_ids[1]: AuditDecision.REJECT_REROUTE,
    }
    expected_audit_status = {
        child_ids[0]: "accept",
        child_ids[1]: "reject_reroute",
    }

    for child_id in child_ids:
        child = state.nodes[child_id]
        ev = audit_candidate(
            upstream_node=state.root,
            downstream_node=child,
            candidate_result=candidate_results[child_id],
        )
        # decision matches expectation
        assert ev.decision == expected_decisions[child_id]
        assert ev.task_id == child_id
        # write back into the tree
        apply_audit_to_tree(state, ev)
        assert state.nodes[child_id].audit_status == expected_audit_status[child_id]
        # buffer the event
        buf.append(ev)
        # ----- 5. update belief about the seeker that produced this candidate -----
        # We model: child[0] was produced by alpha, child[1] by beta.
        seeker = "evidence_seeker_alpha" if child_id == child_ids[0] else "evidence_seeker_beta"
        # toy task signature for these seekers (factoid heavy)
        sig = [0.0, 0.2, 0.0, 0.6, 0.6, 0.4, 0.0]  # 7 dims; emphasises exploration / breadth
        new_belief = update_belief_from_audit(belief, seeker, ev, sig)
        assert isinstance(new_belief, PersonaVector)
        assert len(new_belief.values) == DIM_COUNT

    # belief differentiation: alpha (good answer) should now have higher mean than beta (empty)
    alpha = belief.get("evidence_seeker_alpha")
    beta = belief.get("evidence_seeker_beta")
    assert alpha.mean() > beta.mean(), (
        f"expected alpha > beta after good vs bad audit; "
        f"alpha={alpha.as_dict()}, beta={beta.as_dict()}"
    )

    # ----- 6. flush events to jsonl + reload byte-equal -----
    out = tmp_path / "audit_events.jsonl"
    n_flushed = buf.flush_to_jsonl(out)
    assert n_flushed == 2
    assert len(buf) == 0
    reloaded = AuditEventBuffer.load_from_jsonl(out)
    assert len(reloaded) == 2
    decisions_round_trip = {ev.task_id: ev.decision for ev in reloaded.events()}
    assert decisions_round_trip == expected_decisions

    # ----- 7. dual-track persistence of the BeliefStore -----
    rec = serialize_v2(belief)
    assert rec["schema_version"] == "competence_v2_vector"
    assert "competence_v1_scalar" in rec
    assert "competence_v2_vector" in rec
    # v1 scalar must equal v2 mean per neighbour
    for nb_id, vec_list in rec["competence_v2_vector"].items():
        assert rec["competence_v1_scalar"][nb_id] == pytest.approx(
            sum(vec_list) / DIM_COUNT, abs=1e-9
        )
    # round trip
    rebuilt = deserialize(rec)
    assert rebuilt.get("evidence_seeker_alpha") == alpha
    assert rebuilt.get("evidence_seeker_beta") == beta

    # ----- 8. tree-level invariants survive the whole flow -----
    assert state.total_nodes() == 3
    assert state.root.task_id == "root"
    # root should still report "not_audited" itself; only children got audited
    assert state.root.audit_status == "not_audited"
    for cid in child_ids:
        assert state.nodes[cid].parent_task_id == "root"
        assert state.nodes[cid].depth == 1
        assert state.nodes[cid].audit_status in {"accept", "reject_reroute"}


def test_stage2_split_downgrades_at_total_nodes_cap_and_pipeline_still_runs() -> None:
    """Ensure the bound-aware downgrade path interoperates cleanly with the rest.

    Construct a tree just below MAX_TOTAL_NODES, ask select_action: SPLIT must
    NOT win; OUTSOURCE/DO_SELF takes over; pipeline produces a coherent
    AuditEvent and BeliefStore update with no exception.
    """
    from workspace.idea04_core.task_tree import (
        MAX_SUBTASKS_PER_SPLIT,
        MAX_TOTAL_NODES,
        MAX_TREE_DEPTH,
    )
    root = TaskNode(
        task_id="root",
        parent_task_id=None,
        root_task_id="root",
        task_text="multi-hop question",
        depth=0,
        owner_agent="decomposer",
    )
    state = TaskTreeState(root)
    # Inflate close to MAX_TOTAL_NODES while respecting subtree fanout cap
    next_id = 0
    while state.total_nodes() < MAX_TOTAL_NODES - 1:
        # find a parent with fanout slot AND depth headroom
        target = None
        for nid, node in state.nodes.items():
            if (
                len(node.child_task_ids) < MAX_SUBTASKS_PER_SPLIT
                and node.depth < MAX_TREE_DEPTH
            ):
                target = nid
                break
        if target is None:
            break
        parent = state.nodes[target]
        synth = TaskNode(
            task_id=f"s{next_id}",
            parent_task_id=target,
            root_task_id="root",
            task_text=f"synth-{next_id}",
            depth=parent.depth + 1,
        )
        state.add_subtask(target, synth)
        next_id += 1

    decision = select_action(
        state.root,
        state,
        neighbors=["nb"],
        neighbor_belief_fn=lambda nb: 0.5,
        llm_callable=_mock_llm_split(),
    )
    assert decision.action != Action.SPLIT, (
        "SPLIT must downgrade when no slots remain; "
        f"got {decision.action} with scores {decision.utility_scores}"
    )

    # Simulate a downstream return for whatever the action chose; pipeline must not blow up
    if decision.action == Action.OUTSOURCE:
        downstream_id = next(iter(state.nodes.keys()))  # any existing node as proxy
    else:
        downstream_id = state.root.task_id
    ev = audit_candidate(
        upstream_node=state.root,
        downstream_node=state.nodes[downstream_id],
        candidate_result="Some sensible answer.",
    )
    assert ev.decision in {AuditDecision.ACCEPT, AuditDecision.ACCEPT_WITH_NOTE}
    apply_audit_to_tree(state, ev)
    sig = [0.5] * DIM_COUNT
    bs = BeliefStore()
    new_b = update_belief_from_audit(bs, "nb", ev, sig)
    assert all(0.0 <= v <= 1.0 for v in new_b.values)
