"""Preview-and-commit seam for assignment-before-selection ordering.

The native ledger requires `LaterAssignment` before the target selection, while
the policy boundary normally samples inside `choose_and_seal`.  This module
previews the exact policy Selection transactionally, restores policy/RNG state,
lets the caller record the assignment, and then replays the same probabilities
through a fixed-choice RNG.  It never re-samples after assignment.
"""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping, Sequence

from peerrolebench_baseline_policies import Selection
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, _capture_rng_state, _restore_rng_state


def preview_selection(
    boundary: Pipe3SelectionBoundary,
    *, offer: Any, native_selection_id: str, selector_id: str, role: str,
    base_scores: Sequence[float], rng: Any, state_version: str,
    encoder_version: str, feature_schema: str, policy_version: str,
    base_score_version: str, rng_algorithm: str, rng_draw: int,
    selected_at: float, read_cut: int, decision_index: int,
    captured_features: Mapping[str, Sequence[float]] | None = None,
) -> Selection:
    """Return a policy selection without committing it to policy or ledger."""
    offer_candidate_ids = tuple(key.rsplit("@", 1)[0] for key in offer.candidate_keys)
    refs = tuple(ref for ref in boundary.registry if ref.candidate_id in offer_candidate_ids)
    # Use the boundary's canonical preflight, including menu/version/read-cut
    # checks, before touching mutable policy/RNG state.
    resolved = boundary.registry
    from peerrolebench_candidate_registry import candidate_refs
    canonical_refs = candidate_refs(offer_candidate_ids, resolved)
    boundary._preflight_selection(
        offer=offer, refs=canonical_refs, native_selection_id=native_selection_id,
        selector_id=selector_id, role=role, base_scores=base_scores,
        state_version=state_version, encoder_version=encoder_version,
        feature_schema=feature_schema, policy_version=policy_version,
        base_score_version=base_score_version, rng_algorithm=rng_algorithm,
        rng_draw=rng_draw, selected_at=selected_at, read_cut=read_cut,
        decision_index=decision_index, consume_evidence=False,
        captured_features=captured_features,
    )
    policy_state = copy.deepcopy(boundary.policy.__dict__)
    rng_state = _capture_rng_state(rng)
    try:
        return boundary.policy.choose(
            event_id=f"policy-{native_selection_id}", context_key=offer.context_key,
            selector_id=selector_id, candidates=canonical_refs, base_scores=base_scores,
            rng=rng, state_version=state_version, encoder_version=encoder_version,
            feature_schema=feature_schema, selected_at=selected_at,
            captured_features=captured_features,
        )
    finally:
        boundary.policy.__dict__.clear()
        boundary.policy.__dict__.update(policy_state)
        _restore_rng_state(rng, rng_state)


class FixedChoiceRNG:
    """Replay exactly one previewed choice and probability vector."""

    def __init__(self, preview: Selection) -> None:
        self.index = int(preview.chosen_index)
        self.probabilities = tuple(float(value) for value in preview.probabilities)

    def choice(self, n: int, *, p: Sequence[float]):
        if int(n) != len(self.probabilities):
            raise ValueError("preview candidate count changed before commit")
        if len(p) != len(self.probabilities) or not all(
            math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)
            for left, right in zip(p, self.probabilities)
        ):
            raise ValueError("preview probabilities changed before assignment commit")
        return self.index


__all__ = ["FixedChoiceRNG", "preview_selection"]
