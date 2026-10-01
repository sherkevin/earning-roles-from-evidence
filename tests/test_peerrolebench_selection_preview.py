from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, ProducerScore, RecipientJudgment,
    RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import ContextualTrustPolicy  # noqa: E402
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, make_offer  # noqa: E402
from peerrolebench_selection_preview import FixedChoiceRNG, preview_selection  # noqa: E402


DIGEST = "a" * 64
OUT = "b" * 64


def common(**kwargs):
    values = dict(
        selector_id="peer-a", role="producer", base_scores=(0.0, 0.0),
        state_version="state", encoder_version="encoder", feature_schema="pipe3",
        policy_version="contextual-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0,
        read_cut=1, decision_index=1, captured_features=None,
    )
    values.update(kwargs)
    return values


def test_preview_assignment_commit_preserves_choice_and_propensity():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    rng0 = np.random.default_rng(7)
    first_offer = make_offer(
        offer_id="offer-0", task_id="task", task_index=0, role="producer",
        context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version="role-evidence-v1", available_index=0,
    )
    first = boundary.choose_and_seal(
        offer=first_offer, native_selection_id="s0", selector_id="peer-a", role="producer",
        base_scores=(100.0, -100.0), rng=rng0, state_version="state0",
        encoder_version="encoder", feature_schema="pipe3", policy_version="contextual-v1",
        base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=0,
        selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=False,
    )
    boundary.ledger.record_task_start("task", 0)
    boundary.ledger.record_delivery(Delivery("d0", "task", first.native_selection.chosen_peer_id, "peer-a",
                                             DIGEST, "source0", 0, "s0"))
    boundary.ledger.record_producer_score(ProducerScore("q0", "d0", DIGEST, "score-v1", "PASS", 1, 1.0, OUT, True, True))
    boundary.ledger.record_judgment(RecipientJudgment("j0", "d0", "peer-a", "accept_with_rework", DIGEST))
    boundary.ledger.record_action(ConsumerAction("a0", "d0", "peer-a", True, DIGEST, OUT, action="repair"))
    boundary.ledger.record_outcome(TerminalOutcome("o0", "d0", True, "outcome-v1", 1.0, OUT))
    boundary.ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "o0", "role-v1", 1.0))

    target_offer = make_offer(
        offer_id="offer-1", task_id="task", task_index=1, role="producer",
        context_key="PIPE3:1", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version="role-evidence-v1", available_index=1,
    )
    rng = np.random.default_rng(11)
    before_preview = boundary.policy.snapshot()
    preview = preview_selection(boundary, offer=target_offer, native_selection_id="s1",
                                **common(rng=rng))
    assert boundary.policy.snapshot() == before_preview
    chosen_id = preview.chosen.candidate_id
    assert preview.propensity == preview.probabilities[preview.chosen_index]
    boundary.ledger.record_assignment(LaterAssignment(
        "as1", "task", 1, chosen_id, "producer", ("e0",), preview.propensity,
    ))
    committed = boundary.choose_and_seal(
        offer=target_offer, native_selection_id="s1", rng=FixedChoiceRNG(preview),
        consume_evidence=False, **common(),
    )
    assert committed.native_selection.chosen_peer_id == chosen_id
    assert committed.native_selection.propensity == preview.propensity
    boundary.ledger.record_task_start("task", 1)


def test_preview_rng_or_menu_mutation_is_rejected():
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    offer = make_offer(
        offer_id="offer-0", task_id="task", task_index=0, role="producer",
        context_key="PIPE3:0", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version="role-evidence-v1", available_index=0,
    )
    preview = preview_selection(boundary, offer=offer, native_selection_id="s0",
                                rng=np.random.default_rng(3), **common(read_cut=0, decision_index=0))
    assignment_rng = FixedChoiceRNG(preview)
    try:
        assignment_rng.choice(3, p=preview.probabilities)
    except ValueError as exc:
        assert "candidate count" in str(exc)
    else:
        raise AssertionError("candidate-menu mutation must be rejected")
