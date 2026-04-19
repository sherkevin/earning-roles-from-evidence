"""Recursive upstream-audit runtime for EDO Stage-2 (E-003).

Implements per-handoff audit, per ``idea.md §12`` and the executable spec at
``artifacts/edo_lite_executable_spec.md §4.2``.

Flow: when downstream node ``v`` returns a ``candidate_result`` to upstream
node ``u``, ``u`` calls :func:`audit_candidate` to decide one of four actions:

  - ``ACCEPT``           — value is good enough; commit and propagate up.
  - ``ACCEPT_WITH_NOTE`` — usable but flagged (short / refusal at deep hop).
  - ``REJECT_REROUTE``   — bad; ask another neighbour to retry the same task.
  - ``REJECT_RESPLIT``   — bad and structurally wrong; re-decompose.

Two complementary code paths share one entry point:

  1. Rule-based (default): inspect the candidate string for emptiness,
     refusal patterns, and length. Cheap, deterministic, no LLM call.
  2. LLM-based (opt-in via ``llm_callable``): ask an LLM to score the
     candidate and emit a structured JSON decision. Exists because some
     downstream errors are semantic (e.g. answer wrong but plausible-looking).

Each call emits one :class:`AuditEvent` (per ``idea.md §13.1`` ``ℓ_(u→v,z)``)
which:

  - is *applied* to the tree by :func:`apply_audit_to_tree` (writes
    ``downstream_node.audit_status``);
  - is *buffered* by :class:`AuditEventBuffer` for later jsonl flush
    (``audit_events.jsonl`` is the canonical persisted record).

audit_events.jsonl schema (one event per line, JSON object) — the *single
source of truth* for downstream Stage-2 analysis (R3 vector belief update,
S-117 results table, etc.):

  {
    "event_id": str,            # hash(ts + upstream + downstream + task)
    "schema_version": "audit_event_v1",
    "timestamp": ISO-8601 string,
    "upstream_id": str,         # agent / node id that audited
    "downstream_id": str,       # agent / node id that produced the result
    "task_id": str,             # which TaskNode the result is for
    "decision": "ACCEPT" | "ACCEPT_WITH_NOTE" | "REJECT_REROUTE" | "REJECT_RESPLIT",
    "rework_cost": float,       # [0, 1] estimate of upstream effort to fix
    "value_gain": float,        # [0, 1] perceived contribution to root task
    "timeliness": float,        # [0, 1] inverse-normalised hop_count budget use
    "decomposition_help": float,# [0, 1] only meaningful when result is a split
    "integration_help": float,  # [0, 1] only meaningful when integrating subresults
    "rationale": str,           # human-readable; produced by rule path or LLM
    "metadata": {...}           # forward-compat
  }
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import json
import pathlib
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .task_tree import TaskNode, TaskTreeError, TaskTreeState


# ---------------------------------------------------------------------------
# Constants and enums
# ---------------------------------------------------------------------------


class AuditDecision(str, Enum):
    """Four-class audit verdict, per ``idea.md §12.3``."""
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_NOTE = "ACCEPT_WITH_NOTE"
    REJECT_REROUTE = "REJECT_REROUTE"
    REJECT_RESPLIT = "REJECT_RESPLIT"


# Map AuditDecision back into TaskNode.audit_status (which uses lowercase per
# task_tree.VALID_AUDIT_STATUSES).
_DECISION_TO_AUDIT_STATUS: dict[AuditDecision, str] = {
    AuditDecision.ACCEPT: "accept",
    AuditDecision.ACCEPT_WITH_NOTE: "accept_with_note",
    AuditDecision.REJECT_REROUTE: "reject_reroute",
    AuditDecision.REJECT_RESPLIT: "reject_resplit",
}


MIN_ANSWER_LEN_CHARS: int = 3
SHALLOW_HOP_THRESHOLD: int = 1
"""``hop_count <= SHALLOW_HOP_THRESHOLD`` is "early"; refusals there → REJECT_REROUTE."""

DEFAULT_REFUSAL_PATTERNS: tuple[str, ...] = (
    "i don't know",
    "i do not know",
    "no information",
    "cannot answer",
    "not enough information",
    "insufficient",
    "unsure",
    "无法回答",
    "无法确定",
    "不确定",
    "信息不足",
    "无相关信息",
)

AUDIT_EVENT_SCHEMA_VERSION: str = "audit_event_v1"


class AuditError(ValueError):
    """Raised when an audit input or output is structurally invalid."""


# ---------------------------------------------------------------------------
# AuditEvent
# ---------------------------------------------------------------------------


@dataclass
class AuditEvent:
    """One audit edge ``u → v, z`` (per ``idea.md §13.1`` ``ℓ_(u→v,z)``).

    Floats are kept on ``[0, 1]``; out-of-range values raise :class:`AuditError`
    in ``__post_init__`` so corrupt events fail at construction time, not at
    downstream consumption time (R3 vector belief update would silently warp
    on negative inputs).
    """

    event_id: str
    upstream_id: str
    downstream_id: str
    task_id: str
    decision: AuditDecision
    rework_cost: float
    value_gain: float
    timeliness: float
    decomposition_help: float
    integration_help: float
    rationale: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = AUDIT_EVENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if isinstance(self.decision, str) and not isinstance(self.decision, AuditDecision):
            try:
                self.decision = AuditDecision(self.decision)
            except ValueError as e:
                raise AuditError(
                    f"invalid decision {self.decision!r}; valid: "
                    f"{[d.value for d in AuditDecision]}"
                ) from e
        for fname in ("rework_cost", "value_gain", "timeliness",
                      "decomposition_help", "integration_help"):
            v = float(getattr(self, fname))
            if not (0.0 <= v <= 1.0):
                raise AuditError(f"{fname} must be in [0, 1], got {v}")
            setattr(self, fname, v)
        if not self.timestamp:
            self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_jsonl_record(self) -> dict[str, Any]:
        rec = asdict(self)
        rec["decision"] = self.decision.value  # serialise enum → str
        return rec

    @classmethod
    def from_jsonl_record(cls, record: dict[str, Any]) -> "AuditEvent":
        known = {f.name for f in dataclasses.fields(cls)}
        filtered: dict[str, Any] = {k: v for k, v in record.items() if k in known}
        return cls(**filtered)


def _new_event_id(upstream_id: str, downstream_id: str, task_id: str) -> str:
    """Stable-ish id derived from inputs + current ts. Helpful for jsonl dedup."""
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    raw = f"{upstream_id}|{downstream_id}|{task_id}|{ts}"
    return "audit_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Rule-based audit
# ---------------------------------------------------------------------------


def _looks_like_refusal(text: str, patterns: tuple[str, ...] = DEFAULT_REFUSAL_PATTERNS) -> bool:
    s = text.lower()
    return any(p in s for p in patterns)


def _rule_based_audit(
    upstream_node: TaskNode,
    downstream_node: TaskNode,
    candidate_result: str,
    *,
    refusal_patterns: tuple[str, ...] = DEFAULT_REFUSAL_PATTERNS,
) -> tuple[AuditDecision, str, dict[str, float]]:
    """Pure-Python audit. Returns ``(decision, rationale, signal_floats)``.

    ``signal_floats`` is a dict with the four ``ℓ`` numeric fields the caller
    will copy into the AuditEvent.
    """
    txt = (candidate_result or "").strip()

    # Default mid-range signals; updated below per branch.
    rework_cost = 0.5
    value_gain = 0.5
    decomposition_help = 0.0
    integration_help = 0.0

    # 1. Empty / whitespace
    if not txt:
        return (
            AuditDecision.REJECT_REROUTE,
            "candidate is empty / whitespace-only",
            {"rework_cost": 0.9, "value_gain": 0.0,
             "decomposition_help": 0.0, "integration_help": 0.0},
        )

    # 2. Too short to plausibly carry an answer
    if len(txt) < MIN_ANSWER_LEN_CHARS:
        return (
            AuditDecision.ACCEPT_WITH_NOTE,
            f"candidate length {len(txt)} < MIN_ANSWER_LEN_CHARS={MIN_ANSWER_LEN_CHARS}",
            {"rework_cost": 0.4, "value_gain": 0.3,
             "decomposition_help": 0.0, "integration_help": 0.0},
        )

    # 3. Refusal patterns: branch on hop depth
    if _looks_like_refusal(txt, refusal_patterns):
        if downstream_node.depth <= SHALLOW_HOP_THRESHOLD:
            # Early refusal: cheap to retry, pay the reroute cost
            return (
                AuditDecision.REJECT_REROUTE,
                f"refusal at shallow hop (depth={downstream_node.depth} "
                f"<= SHALLOW_HOP_THRESHOLD={SHALLOW_HOP_THRESHOLD})",
                {"rework_cost": 0.6, "value_gain": 0.1,
                 "decomposition_help": 0.0, "integration_help": 0.0},
            )
        # Late refusal: budget likely spent; accept with a flag rather than burn more
        return (
            AuditDecision.ACCEPT_WITH_NOTE,
            f"refusal at deep hop (depth={downstream_node.depth} "
            f"> SHALLOW_HOP_THRESHOLD={SHALLOW_HOP_THRESHOLD}); "
            "accepting to spare budget",
            {"rework_cost": 0.2, "value_gain": 0.2,
             "decomposition_help": 0.0, "integration_help": 0.0},
        )

    # 4. Otherwise accept; reward higher value when more evidence has been collected
    has_evidence = bool(downstream_node.input_evidence)
    return (
        AuditDecision.ACCEPT,
        f"candidate is non-trivial (length {len(txt)}, "
        f"{'with' if has_evidence else 'without'} downstream evidence)",
        {"rework_cost": 0.05, "value_gain": 0.85 if has_evidence else 0.6,
         "decomposition_help": decomposition_help, "integration_help": integration_help},
    )


def _llm_based_audit(
    upstream_node: TaskNode,
    downstream_node: TaskNode,
    candidate_result: str,
    llm_callable: Callable[[str], str],
    prompt_path: Optional[pathlib.Path] = None,
) -> tuple[AuditDecision, str, dict[str, float]]:
    """Optional LLM-driven audit. Strict JSON output enforced.

    Schema expected from the LLM (a single JSON object, anywhere in the
    response — the parser greedily extracts the outermost ``{...}``)::

        {
          "decision": "ACCEPT" | "ACCEPT_WITH_NOTE" | "REJECT_REROUTE" | "REJECT_RESPLIT",
          "value_gain": float in [0,1],
          "rework_cost": float in [0,1],   (optional, defaults to 1 - value_gain)
          "rationale": str
        }
    """
    p = prompt_path if prompt_path is not None else _default_audit_prompt_path()
    try:
        sys_prompt = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise AuditError(f"cannot read audit prompt at {p}: {e}") from e

    user_msg = (
        f"Original task: {upstream_node.task_text}\n\n"
        f"Subtask given to {downstream_node.executor_agent or downstream_node.task_id}: "
        f"{downstream_node.task_text}\n\n"
        f"Returned candidate:\n{candidate_result}\n\n"
        "Return STRICT JSON per the system schema."
    )
    raw = llm_callable(f"{sys_prompt}\n\n{user_msg}")
    if not isinstance(raw, str) or not raw.strip():
        raise AuditError("llm_callable returned empty response")

    try:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("no JSON object found in LLM output")
        data = json.loads(raw[start : end + 1])
    except Exception as e:
        raise AuditError(f"LLM audit returned invalid JSON: {raw[:160]!r}") from e

    if not isinstance(data, dict):
        raise AuditError("LLM audit JSON root must be an object")
    raw_decision = data.get("decision")
    try:
        decision = AuditDecision(str(raw_decision))
    except ValueError as e:
        raise AuditError(
            f"LLM emitted unknown decision {raw_decision!r}; valid: "
            f"{[d.value for d in AuditDecision]}"
        ) from e

    def _f(k: str, default: float) -> float:
        v = data.get(k, default)
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = default
        return max(0.0, min(1.0, v))

    value_gain = _f("value_gain", 0.5)
    rework_cost = _f("rework_cost", 1.0 - value_gain)
    rationale = str(data.get("rationale", "")).strip() or "LLM-audit (no rationale)"
    return decision, rationale, {
        "rework_cost": rework_cost,
        "value_gain": value_gain,
        "decomposition_help": 0.0,
        "integration_help": 0.0,
    }


def _default_audit_prompt_path() -> pathlib.Path:
    """``prompts/audit_prompt.txt`` at the repo root."""
    return pathlib.Path(__file__).resolve().parent.parent.parent / "prompts" / "audit_prompt.txt"


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def _timeliness(downstream_node: TaskNode, max_handoff: int = 4) -> float:
    """``[0, 1]``: 1.0 when delivered immediately, decays linearly with depth."""
    return max(0.0, 1.0 - downstream_node.depth / max(1, max_handoff))


def audit_candidate(
    upstream_node: TaskNode,
    downstream_node: TaskNode,
    candidate_result: str,
    llm_callable: Optional[Callable[[str], str]] = None,
    audit_prompt_path: Optional[pathlib.Path] = None,
    max_handoff: int = 4,
) -> AuditEvent:
    """Produce one :class:`AuditEvent` for a downstream candidate result.

    The rule-based path always runs and is authoritative on the cheap signals
    (empty / refusal / very short). When ``llm_callable`` is supplied AND the
    rule path yielded ``ACCEPT`` (i.e. the easy gates passed), we additionally
    consult the LLM — its decision overrides the cheap ACCEPT but never
    overrides a cheap REJECT (LLMs are unreliable for the obvious failures).

    Args:
        upstream_node: The node that issued the subtask.
        downstream_node: The node that produced ``candidate_result``.
        candidate_result: The raw answer string from downstream.
        llm_callable: Optional LLM driver ``(prompt: str) -> str``.
        audit_prompt_path: Custom path to the audit system prompt;
            defaults to ``prompts/audit_prompt.txt``.
        max_handoff: Hop budget; used to compute the ``timeliness`` signal.

    Returns:
        An :class:`AuditEvent` with all numeric fields validated.
    """
    decision, rationale, signals = _rule_based_audit(
        upstream_node, downstream_node, candidate_result
    )

    # LLM consultation only on ACCEPT (cheap path already trusts other branches)
    if llm_callable is not None and decision == AuditDecision.ACCEPT:
        try:
            llm_decision, llm_rationale, llm_signals = _llm_based_audit(
                upstream_node, downstream_node, candidate_result,
                llm_callable, audit_prompt_path,
            )
        except AuditError as e:
            # LLM failure → keep rule decision, annotate metadata
            return AuditEvent(
                event_id=_new_event_id(upstream_node.task_id, downstream_node.task_id,
                                       downstream_node.task_id),
                upstream_id=upstream_node.task_id,
                downstream_id=downstream_node.task_id,
                task_id=downstream_node.task_id,
                decision=decision,
                rework_cost=signals["rework_cost"],
                value_gain=signals["value_gain"],
                timeliness=_timeliness(downstream_node, max_handoff),
                decomposition_help=signals["decomposition_help"],
                integration_help=signals["integration_help"],
                rationale=rationale + f" [LLM consultation failed: {e}]",
                metadata={"llm_audit_error": str(e)},
            )
        return AuditEvent(
            event_id=_new_event_id(upstream_node.task_id, downstream_node.task_id,
                                   downstream_node.task_id),
            upstream_id=upstream_node.task_id,
            downstream_id=downstream_node.task_id,
            task_id=downstream_node.task_id,
            decision=llm_decision,
            rework_cost=llm_signals["rework_cost"],
            value_gain=llm_signals["value_gain"],
            timeliness=_timeliness(downstream_node, max_handoff),
            decomposition_help=llm_signals["decomposition_help"],
            integration_help=llm_signals["integration_help"],
            rationale=f"[rule: {rationale}] [LLM: {llm_rationale}]",
            metadata={"audit_path": "rule+llm"},
        )

    return AuditEvent(
        event_id=_new_event_id(upstream_node.task_id, downstream_node.task_id,
                               downstream_node.task_id),
        upstream_id=upstream_node.task_id,
        downstream_id=downstream_node.task_id,
        task_id=downstream_node.task_id,
        decision=decision,
        rework_cost=signals["rework_cost"],
        value_gain=signals["value_gain"],
        timeliness=_timeliness(downstream_node, max_handoff),
        decomposition_help=signals["decomposition_help"],
        integration_help=signals["integration_help"],
        rationale=rationale,
        metadata={"audit_path": "rule"},
    )


def apply_audit_to_tree(state: TaskTreeState, event: AuditEvent) -> None:
    """Write the audit decision back into the task tree.

    Updates ``state.nodes[event.task_id].audit_status`` to the lowercase form
    used by ``task_tree.VALID_AUDIT_STATUSES``. Raises :class:`TaskTreeError`
    if ``event.task_id`` is not in the tree.
    """
    if event.task_id not in state.nodes:
        raise TaskTreeError(
            f"audit event task_id {event.task_id!r} not in tree"
        )
    state.nodes[event.task_id].audit_status = _DECISION_TO_AUDIT_STATUS[event.decision]


# ---------------------------------------------------------------------------
# AuditEventBuffer (in-memory + jsonl flush)
# ---------------------------------------------------------------------------


class AuditEventBuffer:
    """Thread-unsafe in-memory buffer for audit events.

    The runner accumulates events per sample, then calls :meth:`flush_to_jsonl`
    to append the whole batch to ``audit_events.jsonl`` atomically (one
    ``open(..., "a")`` per flush). Per-event jsonl writes would be safer
    against partial crashes but slower in tight loops; the buffer is the
    pragmatic middle.
    """

    __slots__ = ("_events",)

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self._events.append(event)

    def __len__(self) -> int:
        return len(self._events)

    def events(self) -> list[AuditEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()

    def flush_to_jsonl(self, path: pathlib.Path | str) -> int:
        """Append all buffered events as jsonl rows, then clear the buffer.

        Returns the number of events written. Caller is responsible for
        ensuring the parent directory exists.
        """
        out_path = pathlib.Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        with out_path.open("a", encoding="utf-8") as f:
            for ev in self._events:
                f.write(json.dumps(ev.to_jsonl_record(), ensure_ascii=False) + "\n")
                n += 1
        self.clear()
        return n

    @classmethod
    def load_from_jsonl(cls, path: pathlib.Path | str) -> "AuditEventBuffer":
        """Read ``path`` and return a buffer containing all events.

        Used by post-hoc analysis scripts; not by the live runner.
        """
        in_path = pathlib.Path(path)
        buf = cls()
        if not in_path.exists():
            return buf
        for line in in_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            buf.append(AuditEvent.from_jsonl_record(json.loads(line)))
        return buf
