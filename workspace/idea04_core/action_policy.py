"""3-action policy for EDO Stage-2 (E-002).

Implements the three primitive actions per ``idea.md §10``:

  - ``DO_SELF``    — current agent solves the task locally
  - ``OUTSOURCE``  — pass to the locally best visible neighbour
  - ``SPLIT``      — call an LLM decomposition once and produce <= 3 subtasks

The selector returns an :class:`ActionDecision` containing the chosen action,
a per-action rationale, and the utility scores that drove the choice. The
caller is responsible for actually committing OUTSOURCE/SPLIT side-effects
(routing the packet, attaching subtasks to the tree).

Hard bounds inherited from :mod:`workspace.idea04_core.task_tree`:
``MAX_SUBTASKS_PER_SPLIT = 3``, ``MAX_TREE_DEPTH = 3``, ``MAX_TOTAL_NODES = 12``
(per pinned cautions C-4 #2). When a SPLIT would breach any bound, the
selector silently downgrades to the next-best non-violating action.

The LLM decomposition path is gated by an injected ``llm_callable`` so unit
tests can mock without burning API quota. The system prompt lives in
``prompts/decomposition_prompt.txt`` (E-002 also creates it).
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .task_tree import (
    MAX_SUBTASKS_PER_SPLIT,
    MAX_TREE_DEPTH,
    MAX_TOTAL_NODES,
    TaskNode,
    TaskTreeState,
)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class Action(str, Enum):
    """Three-action enum. ``str`` mixin makes JSON serialisation trivial."""
    DO_SELF = "do_self"
    OUTSOURCE = "outsource"
    SPLIT = "split"


@dataclass
class ActionDecision:
    """Outcome of one ``select_action`` call.

    Attributes:
        action: The chosen action.
        target_neighbor: Set when ``action == OUTSOURCE``; otherwise ``None``.
        subtasks: A list of *proposed* subtasks when ``action == SPLIT``;
            empty list otherwise. The caller must register them with
            :meth:`TaskTreeState.add_subtask`.
        rationale: Free-form string explaining the choice (audit-friendly).
        utility_scores: ``{"self": x, "out_max": y, "split": z}`` for trace
            logging. ``-2.0`` means "infeasible" (e.g. SPLIT at depth cap).
        metadata: Forward-compat extension bag (per pinned cautions C-3).
    """

    action: Action
    target_neighbor: Optional[str] = None
    subtasks: list[TaskNode] = field(default_factory=list)
    rationale: str = ""
    utility_scores: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class ActionPolicyError(ValueError):
    """Raised when LLM decomposition output cannot be parsed."""


# ---------------------------------------------------------------------------
# Heuristic utility estimators
# ---------------------------------------------------------------------------
#
# These are *prototype* instantiations of the formulas in ``idea.md §11.2``
# expressed in terms of fields actually populated by the current runner. They
# are intentionally simple (clip-then-linear) so that the unit tests can
# assert exact values; the canonical proxy weights are documented in
# ``artifacts/edo_lite_executable_spec.md §2.2``.


def _evidence_sufficiency(node: TaskNode) -> float:
    """Map ``len(input_evidence)`` to ``[0, 1]``; saturates at 6+ pieces."""
    n = len(node.input_evidence)
    return min(1.0, n / 6.0)


def _need_decompose_score(node: TaskNode) -> float:
    """Heuristic in ``[0, 1]``: low-evidence root nodes benefit most from split."""
    if node.depth >= MAX_TREE_DEPTH:
        return 0.0
    base = 1.0 - _evidence_sufficiency(node)
    if node.depth == 0:
        return base
    # later hops: half-weighted (decomposition value drops as we descend)
    return 0.5 * base


def _estimate_utility_self(node: TaskNode) -> float:
    """U_self proxy. High when own evidence is rich and uncertainty is low."""
    return 0.5 * _evidence_sufficiency(node) + 0.3 * (1.0 - float(node.current_uncertainty)) + 0.2


def _estimate_utility_out(
    node: TaskNode,
    neighbor: str,
    neighbor_belief: float = 0.6,
) -> float:
    """U_out proxy. Includes per-hop send cost (penalises chained outsourcing)."""
    send_cost = 0.1 * (node.depth + 1)
    audit_cost = 0.05 * (1.0 - _evidence_sufficiency(node))
    return 0.6 * float(neighbor_belief) - send_cost - audit_cost


def _estimate_utility_split(node: TaskNode, state: TaskTreeState) -> float:
    """U_split proxy. Returns the special sentinel ``-2.0`` when infeasible."""
    if not _can_split(node, state):
        return -2.0
    return 0.4 * _need_decompose_score(node) + 0.2 - 0.05 * node.depth


def _can_split(node: TaskNode, state: TaskTreeState) -> bool:
    """True iff a SPLIT would not violate any of the three bounds.

    Conservative: requires at least 2 free node slots, since a useful split
    produces at least 2 children. (Producing exactly 1 subtask is degenerate
    and equivalent to OUTSOURCE.)
    """
    if node.depth >= MAX_TREE_DEPTH:
        return False
    if len(node.child_task_ids) >= MAX_SUBTASKS_PER_SPLIT:
        return False
    # leave room for at least 2 children
    if state.total_nodes() > MAX_TOTAL_NODES - 2:
        return False
    return True


# ---------------------------------------------------------------------------
# Public selector
# ---------------------------------------------------------------------------


def select_action(
    node: TaskNode,
    state: TaskTreeState,
    neighbors: list[str],
    llm_callable: Optional[Callable[[str], str]] = None,
    neighbor_belief_fn: Optional[Callable[[str], float]] = None,
    decomposition_prompt_path: Optional[pathlib.Path] = None,
) -> ActionDecision:
    """Choose one of ``{DO_SELF, OUTSOURCE, SPLIT}`` for ``node``.

    Args:
        node: The task currently held by the deciding agent.
        state: Whole tree (needed for global bound checks).
        neighbors: Visible neighbour agent ids; empty list disables OUTSOURCE.
        llm_callable: ``str -> str`` LLM driver. ``None`` disables SPLIT
            (selector silently downgrades a SPLIT-best decision to DO_SELF
            with a rationale note).
        neighbor_belief_fn: ``str -> float in [0,1]`` returning the local
            belief score for each neighbour. ``None`` defaults to 0.6 for all.
        decomposition_prompt_path: Path to system prompt for SPLIT;
            defaults to ``prompts/decomposition_prompt.txt`` at the repo root.

    Returns:
        :class:`ActionDecision` with all utility scores recorded for tracing.
    """
    if neighbor_belief_fn is None:
        def _default_belief(_: str) -> float:
            return 0.6
        neighbor_belief_fn = _default_belief

    u_self = _estimate_utility_self(node)

    out_scores: dict[str, float] = {
        nb: _estimate_utility_out(node, nb, neighbor_belief_fn(nb)) for nb in neighbors
    }
    if out_scores:
        best_nb = max(out_scores.items(), key=lambda kv: kv[1])
        u_out_max = best_nb[1]
        best_nb_id: Optional[str] = best_nb[0]
    else:
        u_out_max = -1.0
        best_nb_id = None

    u_split = _estimate_utility_split(node, state)

    scores = {
        "self": u_self,
        "out_max": u_out_max,
        "split": u_split,
    }

    # tie-break order is fixed: prefer DO_SELF > OUTSOURCE > SPLIT
    # so that bound-violating SPLIT (==-2.0) never wins ties
    winner = max(scores.items(), key=lambda kv: (kv[1], -["self", "out_max", "split"].index(kv[0])))
    winning_action_key = winner[0]

    if winning_action_key == "self":
        return ActionDecision(
            action=Action.DO_SELF,
            rationale=f"DO_SELF utility {u_self:.3f} highest",
            utility_scores=scores,
        )

    if winning_action_key == "out_max":
        if best_nb_id is None:
            # defensive: no neighbours but somehow won; fall back
            return ActionDecision(
                action=Action.DO_SELF,
                rationale="no neighbours available; fell back to DO_SELF",
                utility_scores=scores,
            )
        return ActionDecision(
            action=Action.OUTSOURCE,
            target_neighbor=best_nb_id,
            rationale=f"OUTSOURCE to {best_nb_id!r} (utility {u_out_max:.3f})",
            utility_scores=scores,
        )

    # SPLIT branch — try; fall through to next-best on infeasibility / LLM failure
    def _next_best_after_split(reason: str, extra_meta: Optional[dict] = None) -> ActionDecision:
        """Pick the better of {DO_SELF, OUTSOURCE} when SPLIT gets downgraded.

        Resists the temptation to always pick DO_SELF: if the OUTSOURCE score
        was actually higher than DO_SELF, we should respect that ranking.
        """
        meta = {"split_downgrade": reason}
        if extra_meta:
            meta.update(extra_meta)
        if u_out_max > u_self and best_nb_id is not None:
            return ActionDecision(
                action=Action.OUTSOURCE,
                target_neighbor=best_nb_id,
                rationale=(
                    f"SPLIT was best (utility {u_split:.3f}) but downgraded ({reason}); "
                    f"next-best OUTSOURCE to {best_nb_id!r} (utility {u_out_max:.3f})"
                ),
                utility_scores=scores,
                metadata=meta,
            )
        return ActionDecision(
            action=Action.DO_SELF,
            rationale=(
                f"SPLIT was best (utility {u_split:.3f}) but downgraded ({reason}); "
                f"next-best DO_SELF (utility {u_self:.3f})"
            ),
            utility_scores=scores,
            metadata=meta,
        )

    if not _can_split(node, state):
        # Should already be filtered by u_split == -2.0, but defensive
        return _next_best_after_split(
            f"infeasible (depth={node.depth}/MAX={MAX_TREE_DEPTH}, "
            f"total_nodes={state.total_nodes()}/MAX={MAX_TOTAL_NODES})"
        )
    if llm_callable is None:
        return _next_best_after_split("no llm_callable supplied")

    try:
        subtasks = _call_llm_split(node, llm_callable, decomposition_prompt_path)
    except ActionPolicyError as e:
        return _next_best_after_split(f"LLM failure: {e}", extra_meta={"split_error": str(e)})

    if not subtasks:
        return _next_best_after_split("LLM produced 0 valid subtasks")

    return ActionDecision(
        action=Action.SPLIT,
        subtasks=subtasks,
        rationale=f"SPLIT utility {u_split:.3f} best; produced {len(subtasks)} subtasks",
        utility_scores=scores,
    )


# ---------------------------------------------------------------------------
# LLM-driven decomposition
# ---------------------------------------------------------------------------


def _default_decomposition_prompt_path() -> pathlib.Path:
    """Return the canonical prompts/ path under the repo root."""
    # workspace/idea04_core/action_policy.py -> repo root is two parents up.
    return pathlib.Path(__file__).resolve().parent.parent.parent / "prompts" / "decomposition_prompt.txt"


def _call_llm_split(
    node: TaskNode,
    llm_callable: Callable[[str], str],
    prompt_path: Optional[pathlib.Path] = None,
) -> list[TaskNode]:
    """Use the injected LLM driver to decompose ``node`` into <= 3 subtasks.

    Raises ``ActionPolicyError`` on parse failure; the caller (``select_action``)
    catches and downgrades to DO_SELF, ensuring runtime stability.
    """
    p = prompt_path if prompt_path is not None else _default_decomposition_prompt_path()
    try:
        sys_prompt = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise ActionPolicyError(f"cannot read decomposition prompt at {p}: {e}") from e

    user_msg = (
        f"Original task to decompose:\n{node.task_text}\n\n"
        f"Already-collected evidence (for context):\n"
        + ("\n".join(node.input_evidence[:6]) if node.input_evidence else "(none yet)")
        + "\n\nReturn STRICT JSON in the schema specified by the system prompt."
    )
    full_prompt = f"{sys_prompt}\n\n{user_msg}"

    raw = llm_callable(full_prompt)
    if not isinstance(raw, str) or not raw.strip():
        raise ActionPolicyError("llm_callable returned empty response")

    # Locate the first {...} block defensively (LLMs sometimes prepend prose)
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("no JSON object found in LLM output")
        data = json.loads(raw[start : end + 1])
    except Exception as e:
        raise ActionPolicyError(f"LLM split returned invalid JSON: {raw[:160]!r}") from e

    if not isinstance(data, dict):
        raise ActionPolicyError(
            f"LLM split JSON root must be an object, got {type(data).__name__}"
        )
    subtasks_raw = data.get("subtasks", [])
    if not isinstance(subtasks_raw, list):
        raise ActionPolicyError(
            f"LLM split JSON 'subtasks' must be a list, got {type(subtasks_raw).__name__}"
        )

    # Filter malformed entries FIRST, then cap; otherwise a sequence like
    # [valid, garbage, garbage, valid] would lose the second valid item.
    valid_entries: list[dict[str, Any]] = []
    for st in subtasks_raw:
        if not isinstance(st, dict):
            continue
        text = str(st.get("task_text", "")).strip()
        if not text:
            continue
        valid_entries.append({"task_text": text, "task_type_guess": str(st.get("task_type_guess", ""))})

    valid_entries = valid_entries[:MAX_SUBTASKS_PER_SPLIT]

    out: list[TaskNode] = []
    for i, st in enumerate(valid_entries):
        sub = TaskNode(
            task_id=f"{node.task_id}_sub{i+1}",
            parent_task_id=node.task_id,
            root_task_id=node.root_task_id,
            task_text=st["task_text"],
            task_type_guess=st["task_type_guess"],
            depth=node.depth + 1,
            owner_agent=node.owner_agent,
        )
        out.append(sub)
    return out
