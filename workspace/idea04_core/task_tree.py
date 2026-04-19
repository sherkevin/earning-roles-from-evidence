"""Task-tree state for EDO Stage-2 (E-001).

Implements `TaskNode` (16 fields per ``idea.md §7.3`` + structural extras) and
`TaskTreeState` (parent-child manager with bounded recursion).

Bounds, per ``[pinned_cautions_for_engineer_20260420]`` C-4 #2 and
``artifacts/edo_lite_executable_spec.md §4.3``:

  - ``MAX_SUBTASKS_PER_SPLIT = 3``  (a single split() may produce <= 3 children)
  - ``MAX_TREE_DEPTH = 3``          (root.depth = 0; deepest leaf depth = 3)
  - ``MAX_TOTAL_NODES = 12``        (entire tree, root included)

Forward-compat (per pinned cautions C-3): unknown jsonl fields are silently
ignored on load.  ``metadata`` dict accepts arbitrary additions (e.g. an
audit-decision tuple hung off a node) without bumping the schema version.

Schema-version stability: every node carries a ``schema_version`` string.
The current writer emits ``"task_tree_v1"``.  Future migrations should add a
new constant and gate behaviour on it; never silently mutate v1 records.

This module **does not** depend on / import the runner, methods, or
contracts; it is pure-data so E-002 (split policy) and E-003 (audit runtime)
can integrate without circular imports.
"""

from __future__ import annotations

import dataclasses
import json
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants and validation tables
# ---------------------------------------------------------------------------

MAX_SUBTASKS_PER_SPLIT: int = 3
MAX_TREE_DEPTH: int = 3
MAX_TOTAL_NODES: int = 12

TASK_TREE_SCHEMA_VERSION: str = "task_tree_v1"

VALID_STATUSES: frozenset[str] = frozenset(
    {"pending", "in_progress", "completed", "failed", "cancelled"}
)
VALID_AUDIT_STATUSES: frozenset[str] = frozenset(
    {"not_audited", "accept", "accept_with_note", "reject_reroute", "reject_resplit"}
)


class TaskTreeError(ValueError):
    """Raised when a task-tree operation violates a structural invariant."""


# ---------------------------------------------------------------------------
# TaskNode
# ---------------------------------------------------------------------------

@dataclass
class TaskNode:
    """A single node in an EDO task tree.

    Fields 1-14 are the canonical 14-tuple from ``idea.md §7.3``; fields 15-16
    (``child_task_ids``, ``candidate_result``) are structural extras needed by
    the runtime but implied by the same spec.  ``metadata`` and
    ``schema_version`` are forward-compat plumbing (per pinned cautions C-3).
    """

    # ----- 14 canonical fields (idea.md §7.3) -----
    task_id: str
    parent_task_id: Optional[str]            # None iff root
    root_task_id: str
    task_text: str
    task_type_guess: str = ""
    required_output: str = ""
    input_evidence: list[str] = field(default_factory=list)
    current_uncertainty: float = 0.5
    depth: int = 0
    budget_remaining: int = 4096
    status: str = "pending"
    owner_agent: str = ""
    executor_agent: str = ""
    audit_status: str = "not_audited"

    # ----- structural extras -----
    child_task_ids: list[str] = field(default_factory=list)
    candidate_result: Optional[str] = None

    # ----- forward-compat plumbing -----
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = TASK_TREE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise TaskTreeError(
                f"invalid status {self.status!r}; valid: {sorted(VALID_STATUSES)}"
            )
        if self.audit_status not in VALID_AUDIT_STATUSES:
            raise TaskTreeError(
                f"invalid audit_status {self.audit_status!r}; "
                f"valid: {sorted(VALID_AUDIT_STATUSES)}"
            )
        if not (0.0 <= float(self.current_uncertainty) <= 1.0):
            raise TaskTreeError(
                f"current_uncertainty must be in [0, 1], got {self.current_uncertainty}"
            )
        if int(self.depth) < 0:
            raise TaskTreeError(f"depth must be >= 0, got {self.depth}")
        if int(self.budget_remaining) < 0:
            raise TaskTreeError(
                f"budget_remaining must be >= 0, got {self.budget_remaining}"
            )

    # ----- serialisation -----

    def to_jsonl_record(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict (one row of jsonl)."""
        return asdict(self)

    @classmethod
    def from_jsonl_record(cls, record: dict[str, Any]) -> "TaskNode":
        """Construct from a jsonl row.

        Forward-compat: any keys not present in the dataclass are silently
        dropped (per pinned cautions C-3).  Missing optional keys fall back to
        their dataclass defaults.
        """
        known = {f.name for f in dataclasses.fields(cls)}
        filtered: dict[str, Any] = {k: v for k, v in record.items() if k in known}
        return cls(**filtered)


# ---------------------------------------------------------------------------
# TaskTreeState
# ---------------------------------------------------------------------------

class TaskTreeState:
    """Container managing a single task tree's invariants.

    Public surface used by E-002 (split) and E-003 (audit):

      - ``add_subtask(parent_id, subtask)``  enforces all three bounds
      - ``to_jsonl_lines() / from_jsonl_lines(...)``  pure (de)serialisation
      - ``total_nodes()`` / ``max_depth()``  introspection helpers

    Direct construction takes only a root.  Use ``from_jsonl_lines`` to
    rehydrate a serialised tree atomically (skips per-add bound checks but
    runs a single full validation pass at the end).
    """

    __slots__ = ("root", "nodes")

    def __init__(self, root: TaskNode) -> None:
        if root.parent_task_id is not None:
            raise TaskTreeError(
                f"root must have parent_task_id=None, got {root.parent_task_id!r}"
            )
        if root.depth != 0:
            raise TaskTreeError(f"root must have depth=0, got {root.depth}")
        if root.root_task_id != root.task_id:
            raise TaskTreeError(
                f"root.root_task_id ({root.root_task_id!r}) must equal "
                f"root.task_id ({root.task_id!r})"
            )
        self.root: TaskNode = root
        self.nodes: dict[str, TaskNode] = {root.task_id: root}

    # ----- mutation -----

    def add_subtask(self, parent_id: str, subtask: TaskNode) -> None:
        """Attach ``subtask`` under ``parent_id``, enforcing all bounds.

        Patches the subtask's ``parent_task_id`` / ``root_task_id`` / ``depth``
        for consistency.  If the subtask already specifies a non-matching
        ``parent_task_id``, raises rather than overwriting (caller bug).
        """
        if parent_id not in self.nodes:
            raise TaskTreeError(f"parent_id {parent_id!r} not in tree")
        if subtask.task_id in self.nodes:
            raise TaskTreeError(
                f"subtask task_id {subtask.task_id!r} already exists"
            )
        if len(self.nodes) >= MAX_TOTAL_NODES:
            raise TaskTreeError(
                f"adding would exceed MAX_TOTAL_NODES={MAX_TOTAL_NODES}; "
                f"current={len(self.nodes)}"
            )

        parent = self.nodes[parent_id]
        if len(parent.child_task_ids) >= MAX_SUBTASKS_PER_SPLIT:
            raise TaskTreeError(
                f"parent {parent_id!r} already has "
                f"{MAX_SUBTASKS_PER_SPLIT} children (cap reached)"
            )

        new_depth = parent.depth + 1
        if new_depth > MAX_TREE_DEPTH:
            raise TaskTreeError(
                f"adding child at depth {new_depth} would exceed "
                f"MAX_TREE_DEPTH={MAX_TREE_DEPTH}"
            )

        # Consistency patches
        if subtask.parent_task_id is None:
            subtask.parent_task_id = parent_id
        elif subtask.parent_task_id != parent_id:
            raise TaskTreeError(
                f"subtask.parent_task_id={subtask.parent_task_id!r} != "
                f"target parent_id={parent_id!r}"
            )
        if subtask.root_task_id != self.root.task_id:
            subtask.root_task_id = self.root.task_id
        if subtask.depth != new_depth:
            subtask.depth = new_depth

        # Commit
        self.nodes[subtask.task_id] = subtask
        parent.child_task_ids.append(subtask.task_id)

    # ----- introspection -----

    def total_nodes(self) -> int:
        return len(self.nodes)

    def max_depth(self) -> int:
        return max(n.depth for n in self.nodes.values())

    # ----- serialisation -----

    def to_jsonl_lines(self) -> list[str]:
        """Serialise every node to one jsonl line, in BFS order from the root."""
        order: list[str] = []
        seen: set[str] = set()
        q: deque[str] = deque([self.root.task_id])
        while q:
            nid = q.popleft()
            if nid in seen:
                continue
            seen.add(nid)
            order.append(nid)
            for cid in self.nodes[nid].child_task_ids:
                if cid in self.nodes:
                    q.append(cid)
        # defensive: any nodes not reachable (should not happen) appended last
        for nid in self.nodes:
            if nid not in seen:
                order.append(nid)
        return [
            json.dumps(self.nodes[nid].to_jsonl_record(), ensure_ascii=False)
            for nid in order
        ]

    @classmethod
    def from_jsonl_lines(cls, lines: list[str]) -> "TaskTreeState":
        """Reconstruct a TaskTreeState from jsonl lines and validate it.

        Skips per-add bound checks (the constructor only inspects the root)
        and runs a single full structural validation at the end.  This makes
        it safe to round-trip trees that were *built* with bound checks but
        whose jsonl form would otherwise replay them unnecessarily.
        """
        if not lines:
            raise TaskTreeError("empty jsonl input")
        records = [json.loads(line) for line in lines if line.strip()]
        if not records:
            raise TaskTreeError("jsonl input contains no records")

        nodes = [TaskNode.from_jsonl_record(r) for r in records]
        roots = [n for n in nodes if n.parent_task_id is None]
        if len(roots) != 1:
            raise TaskTreeError(f"expected exactly 1 root, got {len(roots)}")
        root = roots[0]

        state = cls(root)  # initialises with root only
        # Bypass add_subtask (which would mutate child_task_ids); register
        # all non-root nodes directly, then validate.
        for n in nodes:
            if n.task_id == root.task_id:
                continue
            if n.task_id in state.nodes:
                raise TaskTreeError(f"duplicate task_id {n.task_id!r} in jsonl")
            state.nodes[n.task_id] = n

        state._validate_tree_structure()
        return state

    def _validate_tree_structure(self) -> None:
        """Verify all parent-child links + bounds.  Raises ``TaskTreeError`` on any breach."""
        n_total = len(self.nodes)
        if n_total > MAX_TOTAL_NODES:
            raise TaskTreeError(
                f"total nodes {n_total} > MAX_TOTAL_NODES={MAX_TOTAL_NODES}"
            )

        for n in self.nodes.values():
            # parent must exist (except root) and reciprocate
            if n.parent_task_id is None:
                if n.task_id != self.root.task_id:
                    raise TaskTreeError(
                        f"non-root node {n.task_id!r} has parent_task_id=None"
                    )
            else:
                if n.parent_task_id not in self.nodes:
                    raise TaskTreeError(
                        f"node {n.task_id!r} parent {n.parent_task_id!r} not in tree"
                    )
                if n.task_id not in self.nodes[n.parent_task_id].child_task_ids:
                    raise TaskTreeError(
                        f"node {n.task_id!r} not in its parent's child_task_ids"
                    )

            # children must exist and reciprocate
            if len(n.child_task_ids) > MAX_SUBTASKS_PER_SPLIT:
                raise TaskTreeError(
                    f"node {n.task_id!r} has {len(n.child_task_ids)} children "
                    f"(> MAX_SUBTASKS_PER_SPLIT={MAX_SUBTASKS_PER_SPLIT})"
                )
            for cid in n.child_task_ids:
                if cid not in self.nodes:
                    raise TaskTreeError(
                        f"node {n.task_id!r} references unknown child {cid!r}"
                    )
                if self.nodes[cid].parent_task_id != n.task_id:
                    raise TaskTreeError(
                        f"child {cid!r} parent_task_id != {n.task_id!r}"
                    )

            # root_task_id must be globally consistent
            if n.root_task_id != self.root.task_id:
                raise TaskTreeError(
                    f"node {n.task_id!r} root_task_id={n.root_task_id!r} != "
                    f"actual root={self.root.task_id!r}"
                )

            # depth must equal parent.depth + 1 (or 0 for root)
            expected_depth = (
                0 if n.parent_task_id is None
                else self.nodes[n.parent_task_id].depth + 1
            )
            if n.depth != expected_depth:
                raise TaskTreeError(
                    f"node {n.task_id!r} depth={n.depth} != expected={expected_depth}"
                )

        # depth bound (depend on each node's depth field, validated above)
        if self.nodes:
            md = self.max_depth()
            if md > MAX_TREE_DEPTH:
                raise TaskTreeError(f"max depth {md} > MAX_TREE_DEPTH={MAX_TREE_DEPTH}")
