"""Unit tests for the `edo_stage2_chain` method (E-005 step 3).

Mocks `call_llm` so the suite makes ZERO network calls. Verifies:
  - the new method dispatches to `_run_edo_stage2_chain_step`
  - all 4 R1/R2/R3 modules get exercised end-to-end
  - HandoffPacket carries the Stage-2 fields (task_tree_id, schema_version="v2")
  - dual-track competence (C-3) appears in `published_competence`
  - audit events accumulate in MethodState across hops
  - Stage-1 method paths remain untouched (sanity check)

Run::

    python -m pytest workspace/idea04_core/test_edo_stage2_chain_method.py -v
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

from workspace.idea04_core.audit_runtime import AuditDecision, AuditEvent
from workspace.idea04_core.contracts import (
    AgentInput,
    HandoffPacket,
    MethodState,
)
from workspace.idea04_core.methods import (
    METHOD_NAMES,
    _run_edo_stage2_chain_step,
    _signature_from_routing_features,
    default_competence,
    default_method_knobs,
    run_method_step,
)
from workspace.idea04_core.persona_model import (
    DIM_COUNT,
    BeliefStore,
    PersonaVector,
)
from workspace.idea04_core.task_tree import TaskNode, TaskTreeState


# ---------------------------------------------------------------------------
# Mocks
# ---------------------------------------------------------------------------


def _fake_llm_response(text: str) -> dict[str, Any]:
    """Minimal call_llm-shaped response (used by extract_text / extract_usage)."""
    return {
        "choices": [{"message": {"role": "assistant", "content": text}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def _patched_call_llm_sequence(responses: list[str]):
    """Return a patcher that yields successive responses on each call."""
    iter_resp = iter(responses)

    def _fake(messages, **kwargs):
        try:
            return _fake_llm_response(next(iter_resp))
        except StopIteration:
            return _fake_llm_response("default mocked answer")

    return _fake


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(method_name: str = "edo_stage2_chain") -> MethodState:
    nodes = ["decomposer", "evidence_seeker", "verifier", "synthesizer"]
    state = MethodState(
        method_name=method_name,
        topology="chain",
        max_handoff=4,
        competence_by_agent={n: default_competence(n) for n in nodes},
        neighbor_beliefs_by_agent={},
        method_knobs=default_method_knobs(method_name),
        seen_nodes=set(),
    )
    # Pre-seed Stage-2 state (the runner does this; tests bypass the runner)
    root = TaskNode(
        task_id="sample42_root",
        parent_task_id=None,
        root_task_id="sample42_root",
        task_text="Which film, Inception or Interstellar, was directed by the older director?",
        task_type_guess="comparison",
        depth=0,
        owner_agent="decomposer",
        executor_agent="decomposer",
    )
    state.task_tree_state_v2 = TaskTreeState(root)
    state.belief_store_by_agent_v2 = {n: BeliefStore() for n in nodes}
    return state


def _make_input(state: MethodState, packet: HandoffPacket | None = None) -> AgentInput:
    if packet is None:
        packet = HandoffPacket(
            task_id="sample42",
            question=state.task_tree_state_v2.root.task_text,
            current_subgoal="decompose_question",
            evidence_so_far=[],
            uncertainty=0.6,
            reason_for_forward="",
            recommended_next_skill="decomposer",
            visited_nodes=[],
            hop_count=0,
            last_actor="",
            candidate_answer="",
            published_competence={"_topology": "chain"},
        )
    return AgentInput(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        incoming_packet=packet,
        local_state={"self_claim": 0.5},
        neighbor_list=["evidence_seeker"],
        method_state=state,
    )


# ---------------------------------------------------------------------------
# 1. Method registration
# ---------------------------------------------------------------------------


def test_edo_stage2_chain_is_registered_method() -> None:
    assert "edo_stage2_chain" in METHOD_NAMES


# ---------------------------------------------------------------------------
# 2. signature_from_routing_features
# ---------------------------------------------------------------------------


def test_signature_from_routing_features_emits_7_dims() -> None:
    rf = {
        "question_is_multihop": True,
        "hop_count": 0,
        "evidence_count": 5,
        "evidence_sufficiency": 0.42,
        "packet_uncertainty": 0.6,
    }
    sig = _signature_from_routing_features(rf, max_handoff=4)
    assert len(sig) == DIM_COUNT
    assert all(0.0 <= v <= 1.0 for v in sig)
    assert sig[0] == 1.0  # need_decompose at hop 0 multihop
    assert sig[1] == 0.0  # need_verification (hop_count < 2)
    assert sig[5] == 0.6  # uncertainty


# ---------------------------------------------------------------------------
# 3. End-to-end one hop with patched LLM
# ---------------------------------------------------------------------------


def test_stage2_step_hop0_dispatches_to_evidence_seeker() -> None:
    """Hop 0 with empty evidence → action policy should NOT immediately accept;
    SPLIT or OUTSOURCE should win and the packet should forward."""
    state = _make_state()
    agent_input = _make_input(state)
    # The decomposer hop 0 calls _llm_forward_contribution OR _call_llm_split.
    # We feed responses for both potential paths.
    responses = [
        json.dumps({  # potential split decomposition response
            "subtasks": [
                {"task_text": "Who directed Inception and what year were they born?",
                 "task_type_guess": "factoid"},
                {"task_text": "Who directed Interstellar and what year were they born?",
                 "task_type_guess": "factoid"},
            ]
        }),
        "Forward contribution: gather director birth dates.",  # forward contribution fallback
    ]
    with patch("workspace.idea04_core.methods.call_llm", side_effect=_patched_call_llm_sequence(responses)):
        out = run_method_step(
            agent_name="decomposer",
            agent_input=agent_input,
            hop_index=0,
        )
    # decomposer at hop 0 with no evidence should not "accept" (forward instead)
    assert out.decision == "forward"
    assert out.outgoing_packet.recommended_next_skill == "evidence_seeker"
    # Stage-2 fields populated
    assert out.outgoing_packet.task_tree_id == "sample42_root"
    assert out.outgoing_packet.schema_version == "v2"
    # No prior to audit at hop 0
    assert out.outgoing_packet.audit_status_of_prior is None
    # dual-track competence present in published_competence
    pc = out.outgoing_packet.published_competence
    assert "competence_v2_vector" in pc
    assert "decomposer" in pc["competence_v2_vector"]
    assert len(pc["competence_v2_vector"]["decomposer"]) == DIM_COUNT


def test_stage2_step_hop1_audits_prior_contribution() -> None:
    """At hop 1, evidence_seeker must audit the decomposer's prior candidate
    and record an AuditEvent into MethodState's buffer."""
    state = _make_state()
    # Manually register decomposer's hop0 node so audit can find it
    from workspace.idea04_core.methods import _stage2_pick_current_node
    _stage2_pick_current_node(state.task_tree_state_v2, "decomposer", 0)

    packet = HandoffPacket(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        current_subgoal="evidence_seeker_step_1",
        evidence_so_far=["[decomposer] gathered partial evidence about directors"],
        uncertainty=0.55,
        reason_for_forward="forward",
        recommended_next_skill="evidence_seeker",
        visited_nodes=["decomposer"],
        hop_count=1,
        last_actor="decomposer",
        candidate_answer="Christopher Nolan directed both films, born 1970.",
        published_competence={"_topology": "chain", "decomposer": 0.5},
        task_tree_id="sample42_root",
        audit_status_of_prior=None,
        schema_version="v2",
    )
    agent_input = AgentInput(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        incoming_packet=packet,
        local_state={"self_claim": 0.5},
        neighbor_list=["verifier"],
        method_state=state,
    )
    responses = [
        json.dumps({"subtasks": [{"task_text": "more digging", "task_type_guess": "factoid"}]}),
        "Evidence-seeker contribution.",
    ]
    initial_buf_len = len(state.audit_events_buffer_v2)
    with patch("workspace.idea04_core.methods.call_llm", side_effect=_patched_call_llm_sequence(responses)):
        out = run_method_step(
            agent_name="evidence_seeker",
            agent_input=agent_input,
            hop_index=1,
        )
    # An audit event should have been emitted
    assert len(state.audit_events_buffer_v2) == initial_buf_len + 1
    audit_ev: AuditEvent = state.audit_events_buffer_v2[-1]
    # Prior was a non-empty candidate → audit should ACCEPT
    assert audit_ev.decision == AuditDecision.ACCEPT
    # The packet now reports prior status
    assert out.outgoing_packet.audit_status_of_prior == "ACCEPT"
    # The decomposer's belief vector should have moved off neutral
    eseeker_belief = state.belief_store_by_agent_v2["evidence_seeker"]
    decomposer_belief_vec = eseeker_belief.get("decomposer")
    # At least one axis must differ from the neutral 0.5 default after a positive update
    assert any(abs(v - 0.5) > 1e-6 for v in decomposer_belief_vec.values), (
        f"belief about decomposer should have shifted; got {decomposer_belief_vec.as_dict()}"
    )


def test_stage2_step_terminal_synthesizer_accepts() -> None:
    """At synthesizer (no neighbours), action policy must DO_SELF (accept)."""
    state = _make_state()
    # Pre-register a chain so audit at terminal can find prior
    from workspace.idea04_core.methods import _stage2_pick_current_node
    for h, ag in enumerate(["decomposer", "evidence_seeker", "verifier"]):
        _stage2_pick_current_node(state.task_tree_state_v2, ag, h)

    packet = HandoffPacket(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        current_subgoal="synthesizer_step_3",
        evidence_so_far=[
            "Inception was directed by Christopher Nolan, born 1970.",
            "Interstellar was directed by Christopher Nolan, born 1970.",
        ],
        uncertainty=0.3,
        reason_for_forward="forward",
        recommended_next_skill="synthesizer",
        visited_nodes=["decomposer", "evidence_seeker", "verifier"],
        hop_count=3,
        last_actor="verifier",
        candidate_answer="Both films were directed by Christopher Nolan.",
        published_competence={"_topology": "chain"},
        task_tree_id="sample42_root",
        schema_version="v2",
    )
    agent_input = AgentInput(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        incoming_packet=packet,
        local_state={"self_claim": 0.7},
        neighbor_list=[],  # synthesizer has no neighbours
        method_state=state,
    )
    with patch(
        "workspace.idea04_core.methods.call_llm",
        side_effect=_patched_call_llm_sequence(["Both films were directed by Christopher Nolan."]),
    ):
        out = run_method_step(
            agent_name="synthesizer",
            agent_input=agent_input,
            hop_index=3,
        )
    assert out.decision == "accept"
    assert out.outgoing_packet.candidate_answer == "Both films were directed by Christopher Nolan."
    assert out.generated_answer == "Both films were directed by Christopher Nolan."


# ---------------------------------------------------------------------------
# 4. Stage-1 paths must remain unaffected
# ---------------------------------------------------------------------------


def test_stage1_method_unchanged_by_stage2_addition() -> None:
    """Smoke: dispatching a Stage-1 method (single_agent) must not touch
    state.task_tree_state_v2 / state.belief_store_by_agent_v2 / audit buffer."""
    state = MethodState(
        method_name="single_agent",
        topology="chain",
        max_handoff=4,
        competence_by_agent={"decomposer": default_competence("decomposer")},
        neighbor_beliefs_by_agent={},
        method_knobs=default_method_knobs("single_agent"),
        seen_nodes=set(),
    )
    packet = HandoffPacket(
        task_id="sample0",
        question="What is 2+2?",
        current_subgoal="decompose",
        evidence_so_far=[],
        uncertainty=0.5,
        reason_for_forward="",
        recommended_next_skill="decomposer",
        visited_nodes=[],
        hop_count=0,
        last_actor="",
        candidate_answer="",
        published_competence={"_topology": "chain"},
    )
    agent_input = AgentInput(
        task_id="sample0",
        question="What is 2+2?",
        incoming_packet=packet,
        local_state={"self_claim": 0.5},
        neighbor_list=[],
        method_state=state,
    )
    with patch(
        "workspace.idea04_core.methods.call_llm",
        side_effect=_patched_call_llm_sequence(["4"]),
    ):
        out = run_method_step(
            agent_name="decomposer",
            agent_input=agent_input,
            hop_index=0,
        )
    # Stage-1 returns "accept" on single_agent + outgoing_packet has Stage-2 defaults
    assert out.decision == "accept"
    assert out.outgoing_packet.task_tree_id is None
    assert out.outgoing_packet.schema_version == "v1"
    # No Stage-2 state was created
    assert state.task_tree_state_v2 is None
    assert state.belief_store_by_agent_v2 == {}
    assert state.audit_events_buffer_v2 == []


# ---------------------------------------------------------------------------
# 5. Bound enforcement integration
# ---------------------------------------------------------------------------


def test_stage2_step_handles_split_at_depth_cap_gracefully() -> None:
    """When the tree is at MAX_TREE_DEPTH, action policy should NOT propose SPLIT
    and the step function should still emit a valid AgentOutput."""
    from workspace.idea04_core.task_tree import MAX_TREE_DEPTH
    state = _make_state()
    # Build chain to depth = MAX_TREE_DEPTH
    parent_id = "sample42_root"
    for d in range(1, MAX_TREE_DEPTH + 1):
        node = TaskNode(
            task_id=f"deepchain{d}",
            parent_task_id=parent_id,
            root_task_id="sample42_root",
            task_text=f"deep step {d}",
            depth=d,
        )
        state.task_tree_state_v2.add_subtask(parent_id, node)
        parent_id = f"deepchain{d}"
    packet = HandoffPacket(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        current_subgoal="evidence_seeker_step_1",
        evidence_so_far=[],
        uncertainty=0.7,
        reason_for_forward="forward",
        recommended_next_skill="evidence_seeker",
        visited_nodes=["decomposer"],
        hop_count=1,
        last_actor="decomposer",
        candidate_answer="something useful",
        published_competence={"_topology": "chain"},
    )
    agent_input = AgentInput(
        task_id="sample42",
        question=state.task_tree_state_v2.root.task_text,
        incoming_packet=packet,
        local_state={"self_claim": 0.5},
        neighbor_list=["verifier"],
        method_state=state,
    )
    with patch(
        "workspace.idea04_core.methods.call_llm",
        side_effect=_patched_call_llm_sequence([
            json.dumps({"subtasks": [{"task_text": "x"} for _ in range(3)]}),
            "fallback contribution",
        ]),
    ):
        out = run_method_step(
            agent_name="evidence_seeker",
            agent_input=agent_input,
            hop_index=1,
        )
    assert out.decision in {"accept", "forward"}
    rf = out.trace.routing_features
    # SPLIT must not be the chosen action when capped
    assert rf.get("edo_stage2_action") in {"do_self", "outsource"}
