from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class HandoffPacket:
    task_id: str
    question: str
    current_subgoal: str
    evidence_so_far: list[str]
    uncertainty: float
    reason_for_forward: str
    recommended_next_skill: str
    visited_nodes: list[str] = field(default_factory=list)
    hop_count: int = 0
    last_actor: str = ""
    candidate_answer: str = ""
    published_competence: dict[str, Any] = field(default_factory=dict)

    # ── Stage-2 optional fields (forward-compat; None / "v1" for Stage-1 packets) ──
    # Per pinned C-3: these are appended at the end with safe defaults so any
    # historical jsonl reader (validate_logs.py R0 baseline) still parses cleanly.
    task_tree_id: str | None = None
    audit_status_of_prior: str | None = None
    schema_version: str = "v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MethodState:
    method_name: str
    topology: str
    max_handoff: int
    competence_by_agent: dict[str, dict[str, float]] = field(default_factory=dict)
    neighbor_beliefs_by_agent: dict[str, dict[str, float]] = field(default_factory=dict)
    method_knobs: dict[str, Any] = field(default_factory=dict)
    seen_nodes: set[str] = field(default_factory=set)
    # ── Stage-2 optional state (None / empty for Stage-1 methods) ──
    # task_tree_state_v2: workspace.idea04_core.task_tree.TaskTreeState
    # belief_store_by_agent_v2: dict[str, workspace.idea04_core.persona_model.BeliefStore]
    # audit_events_buffer_v2: list[workspace.idea04_core.audit_runtime.AuditEvent]
    # Typed as Any here to avoid circular imports between contracts and stage-2 modules.
    task_tree_state_v2: Any = None
    belief_store_by_agent_v2: dict[str, Any] = field(default_factory=dict)
    audit_events_buffer_v2: list[Any] = field(default_factory=list)


@dataclass
class AgentInput:
    task_id: str
    question: str
    incoming_packet: HandoffPacket
    local_state: dict[str, Any]
    neighbor_list: list[str]
    method_state: MethodState


@dataclass
class CompetenceUpdate:
    before: dict[str, float]
    after: dict[str, float]
    signal: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEntry:
    task_id: str
    hop_index: int
    node_name: str
    decision: str
    chosen_target: str
    reason: str
    routing_features: dict[str, Any] = field(default_factory=dict)
    neighbor_scores: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentOutput:
    decision: str
    outgoing_packet: HandoffPacket
    raw_response: str
    competence_update: CompetenceUpdate
    trace: TraceEntry
    generated_answer: str = ""
    usage_calls: list[dict[str, Any]] = field(default_factory=list)
