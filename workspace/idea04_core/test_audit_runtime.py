"""Unit tests for ``workspace.idea04_core.audit_runtime`` (E-003).

Run from repo root::

    python -m pytest workspace/idea04_core/test_audit_runtime.py -v

All LLM interaction is mocked; this suite makes zero network calls.
"""

from __future__ import annotations

import json
import pathlib
from typing import Callable

import pytest

from workspace.idea04_core.audit_runtime import (
    AUDIT_EVENT_SCHEMA_VERSION,
    AuditDecision,
    AuditError,
    AuditEvent,
    AuditEventBuffer,
    apply_audit_to_tree,
    audit_candidate,
)
from workspace.idea04_core.task_tree import TaskNode, TaskTreeError, TaskTreeState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pair(downstream_depth: int = 1, evidence: list[str] | None = None) -> tuple[TaskTreeState, TaskNode, TaskNode]:
    """Return (state, upstream, downstream) where upstream → downstream chain."""
    upstream = TaskNode(
        task_id="up",
        parent_task_id=None,
        root_task_id="up",
        task_text="Compositional question",
        depth=0,
        owner_agent="decomposer",
        executor_agent="decomposer",
    )
    state = TaskTreeState(upstream)
    parent_id = "up"
    cur = upstream
    for d in range(1, downstream_depth + 1):
        is_leaf = d == downstream_depth
        nid = "down" if is_leaf else f"chain{d}"
        node = TaskNode(
            task_id=nid,
            parent_task_id=parent_id,
            root_task_id="up",
            task_text=f"sub-question at depth {d}",
            input_evidence=list(evidence or []) if is_leaf else [],
            depth=d,
            owner_agent="evidence_seeker",
            executor_agent="evidence_seeker",
        )
        state.add_subtask(parent_id, node)
        parent_id = nid
        cur = node
    return state, upstream, cur


def _mock_llm(raw_or_dict) -> Callable[[str], str]:
    raw = raw_or_dict if isinstance(raw_or_dict, str) else json.dumps(raw_or_dict)

    def _call(_prompt: str) -> str:
        return raw
    return _call


# ---------------------------------------------------------------------------
# 1. Rule-based audit branches
# ---------------------------------------------------------------------------


def test_audit_empty_candidate_rejects_reroute() -> None:
    state, up, down = _make_pair(downstream_depth=1)
    ev = audit_candidate(up, down, candidate_result="")
    assert ev.decision == AuditDecision.REJECT_REROUTE
    assert ev.value_gain == 0.0
    assert "empty" in ev.rationale


def test_audit_whitespace_candidate_rejects_reroute() -> None:
    state, up, down = _make_pair(downstream_depth=1)
    ev = audit_candidate(up, down, candidate_result="   \n\t  ")
    assert ev.decision == AuditDecision.REJECT_REROUTE


def test_audit_short_candidate_accept_with_note() -> None:
    state, up, down = _make_pair(downstream_depth=1)
    ev = audit_candidate(up, down, candidate_result="ok")  # length 2 < MIN=3
    assert ev.decision == AuditDecision.ACCEPT_WITH_NOTE
    assert "MIN_ANSWER_LEN_CHARS" in ev.rationale


def test_audit_refusal_at_shallow_hop_rejects_reroute() -> None:
    state, up, down = _make_pair(downstream_depth=1)  # depth=1 = shallow
    ev = audit_candidate(up, down, candidate_result="I don't know the answer")
    assert ev.decision == AuditDecision.REJECT_REROUTE
    assert "shallow hop" in ev.rationale


def test_audit_refusal_at_deep_hop_accepts_with_note() -> None:
    state, up, down = _make_pair(downstream_depth=3)  # depth=3 > SHALLOW=1
    ev = audit_candidate(up, down, candidate_result="无法确定答案")
    assert ev.decision == AuditDecision.ACCEPT_WITH_NOTE
    assert "deep hop" in ev.rationale


def test_audit_normal_candidate_accepts() -> None:
    state, up, down = _make_pair(downstream_depth=2, evidence=["e1", "e2"])
    ev = audit_candidate(
        up, down,
        candidate_result="Christopher Nolan directed Inception in 2010.",
    )
    assert ev.decision == AuditDecision.ACCEPT
    assert ev.value_gain >= 0.6


def test_audit_timeliness_decreases_with_depth() -> None:
    _, up_a, dn_a = _make_pair(downstream_depth=1)
    _, up_b, dn_b = _make_pair(downstream_depth=3)
    ev_shallow = audit_candidate(up_a, dn_a, "Real answer text here.")
    ev_deep = audit_candidate(up_b, dn_b, "Real answer text here.")
    assert ev_shallow.timeliness > ev_deep.timeliness


# ---------------------------------------------------------------------------
# 2. apply_audit_to_tree
# ---------------------------------------------------------------------------


def test_apply_audit_writes_back_to_node() -> None:
    state, up, down = _make_pair(downstream_depth=1)
    assert down.audit_status == "not_audited"
    ev = audit_candidate(up, down, candidate_result="An answer.")
    apply_audit_to_tree(state, ev)
    # ev.decision == ACCEPT → audit_status="accept" (lowercase per task_tree)
    assert state.nodes["down"].audit_status == "accept"


def test_apply_audit_each_decision_maps_correctly() -> None:
    state, up, down = _make_pair(downstream_depth=1)
    for dec, expected_status in [
        (AuditDecision.ACCEPT, "accept"),
        (AuditDecision.ACCEPT_WITH_NOTE, "accept_with_note"),
        (AuditDecision.REJECT_REROUTE, "reject_reroute"),
        (AuditDecision.REJECT_RESPLIT, "reject_resplit"),
    ]:
        ev = AuditEvent(
            event_id=f"e_{expected_status}",
            upstream_id="up",
            downstream_id="down",
            task_id="down",
            decision=dec,
            rework_cost=0.5, value_gain=0.5, timeliness=0.5,
            decomposition_help=0.0, integration_help=0.0,
        )
        apply_audit_to_tree(state, ev)
        assert state.nodes["down"].audit_status == expected_status


def test_apply_audit_rejects_unknown_task_id() -> None:
    state, _, _ = _make_pair(downstream_depth=1)
    ev = AuditEvent(
        event_id="e_oops",
        upstream_id="up",
        downstream_id="ghost",
        task_id="ghost",  # not in tree
        decision=AuditDecision.ACCEPT,
        rework_cost=0.1, value_gain=0.9, timeliness=0.9,
        decomposition_help=0.0, integration_help=0.0,
    )
    with pytest.raises(TaskTreeError, match="not in tree"):
        apply_audit_to_tree(state, ev)


# ---------------------------------------------------------------------------
# 3. AuditEvent validation + jsonl round-trip
# ---------------------------------------------------------------------------


def test_event_rejects_invalid_decision_string() -> None:
    with pytest.raises(AuditError, match="invalid decision"):
        AuditEvent(
            event_id="x",
            upstream_id="u", downstream_id="d", task_id="t",
            decision="MAYBE",  # type: ignore[arg-type]
            rework_cost=0.5, value_gain=0.5, timeliness=0.5,
            decomposition_help=0.0, integration_help=0.0,
        )


def test_event_rejects_out_of_range_signal() -> None:
    with pytest.raises(AuditError, match="value_gain"):
        AuditEvent(
            event_id="x",
            upstream_id="u", downstream_id="d", task_id="t",
            decision=AuditDecision.ACCEPT,
            rework_cost=0.5, value_gain=1.7, timeliness=0.5,
            decomposition_help=0.0, integration_help=0.0,
        )


def test_event_jsonl_round_trip() -> None:
    ev = AuditEvent(
        event_id="abc",
        upstream_id="u", downstream_id="d", task_id="t",
        decision=AuditDecision.ACCEPT_WITH_NOTE,
        rework_cost=0.3, value_gain=0.7, timeliness=0.8,
        decomposition_help=0.1, integration_help=0.2,
        rationale="test", metadata={"foo": "bar", "v2_field": [1, 2, 3]},
    )
    rec = ev.to_jsonl_record()
    assert rec["decision"] == "ACCEPT_WITH_NOTE"  # serialised as str
    assert rec["schema_version"] == AUDIT_EVENT_SCHEMA_VERSION
    ev2 = AuditEvent.from_jsonl_record(rec)
    assert ev2.decision == ev.decision
    assert ev2.metadata == ev.metadata
    assert ev2.event_id == ev.event_id


def test_event_jsonl_load_drops_unknown_future_fields() -> None:
    """forward-compat: an unknown new field in the record must be silently dropped."""
    rec = {
        "event_id": "x", "upstream_id": "u", "downstream_id": "d", "task_id": "t",
        "decision": "ACCEPT",
        "rework_cost": 0.1, "value_gain": 0.9, "timeliness": 0.9,
        "decomposition_help": 0.0, "integration_help": 0.0,
        "schema_version": "audit_event_v1",
        "future_field_v2": {"nested": "stuff"},
    }
    ev = AuditEvent.from_jsonl_record(rec)
    assert ev.event_id == "x"


# ---------------------------------------------------------------------------
# 4. AuditEventBuffer flush + load round-trip
# ---------------------------------------------------------------------------


def test_buffer_flush_round_trip(tmp_path: pathlib.Path) -> None:
    buf = AuditEventBuffer()
    state, up, down = _make_pair(downstream_depth=1)
    for txt in ("First answer.", "Second answer.", "Third answer."):
        buf.append(audit_candidate(up, down, candidate_result=txt))
    assert len(buf) == 3
    out = tmp_path / "audit_events.jsonl"
    n = buf.flush_to_jsonl(out)
    assert n == 3
    assert len(buf) == 0
    assert out.exists()
    # round-trip
    loaded = AuditEventBuffer.load_from_jsonl(out)
    assert len(loaded) == 3
    for ev in loaded.events():
        assert ev.decision == AuditDecision.ACCEPT


def test_buffer_load_from_missing_file_returns_empty(tmp_path: pathlib.Path) -> None:
    loaded = AuditEventBuffer.load_from_jsonl(tmp_path / "does_not_exist.jsonl")
    assert len(loaded) == 0


def test_buffer_flush_appends_not_overwrites(tmp_path: pathlib.Path) -> None:
    out = tmp_path / "audit_events.jsonl"
    state, up, down = _make_pair(downstream_depth=1)

    buf1 = AuditEventBuffer()
    buf1.append(audit_candidate(up, down, candidate_result="batch1"))
    assert buf1.flush_to_jsonl(out) == 1

    buf2 = AuditEventBuffer()
    buf2.append(audit_candidate(up, down, candidate_result="batch2"))
    buf2.append(audit_candidate(up, down, candidate_result="batch3"))
    assert buf2.flush_to_jsonl(out) == 2

    loaded = AuditEventBuffer.load_from_jsonl(out)
    assert len(loaded) == 3


# ---------------------------------------------------------------------------
# 5. LLM-based audit path
# ---------------------------------------------------------------------------


def test_llm_audit_only_consulted_on_rule_accept() -> None:
    """LLM is consulted only when the rule path returned ACCEPT."""
    captured: list[str] = []

    def _capturing_llm(prompt: str) -> str:
        captured.append(prompt)
        return json.dumps({"decision": "ACCEPT", "value_gain": 0.85, "rationale": "looks good"})

    # rule path on empty → REJECT_REROUTE; LLM must NOT be called
    state, up, down = _make_pair(downstream_depth=1)
    audit_candidate(up, down, candidate_result="", llm_callable=_capturing_llm)
    assert captured == []

    # rule path on plausible answer → ACCEPT; LLM IS called
    audit_candidate(up, down, candidate_result="Real answer.", llm_callable=_capturing_llm)
    assert len(captured) == 1


def test_llm_audit_can_override_rule_accept_to_reject_resplit() -> None:
    state, up, down = _make_pair(downstream_depth=1)

    def _llm_says_resplit(_p: str) -> str:
        return json.dumps({
            "decision": "REJECT_RESPLIT",
            "value_gain": 0.1,
            "rationale": "answer is plausibly worded but factually wrong",
        })

    ev = audit_candidate(up, down, candidate_result="Plausible-looking answer.",
                        llm_callable=_llm_says_resplit)
    assert ev.decision == AuditDecision.REJECT_RESPLIT
    assert "rule+llm" in ev.metadata.get("audit_path", "")


def test_llm_audit_invalid_json_keeps_rule_decision() -> None:
    state, up, down = _make_pair(downstream_depth=1)

    def _bad_llm(_p: str) -> str:
        return "not json at all"

    ev = audit_candidate(up, down, candidate_result="A real answer.", llm_callable=_bad_llm)
    # rule path said ACCEPT; LLM failed → keep ACCEPT, annotate metadata
    assert ev.decision == AuditDecision.ACCEPT
    assert "llm_audit_error" in ev.metadata


def test_llm_audit_loads_prompt_file(tmp_path: pathlib.Path) -> None:
    custom_prompt = tmp_path / "audit.txt"
    custom_prompt.write_text("UNIQUE-AUDIT-SYS-PROMPT", encoding="utf-8")

    captured: list[str] = []

    def _llm(prompt: str) -> str:
        captured.append(prompt)
        return json.dumps({"decision": "ACCEPT", "value_gain": 0.9})

    state, up, down = _make_pair(downstream_depth=1)
    audit_candidate(
        up, down,
        candidate_result="Real answer.",
        llm_callable=_llm,
        audit_prompt_path=custom_prompt,
    )
    assert len(captured) == 1
    assert "UNIQUE-AUDIT-SYS-PROMPT" in captured[0]
