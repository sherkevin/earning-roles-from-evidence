from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import (  # noqa: E402
    CandidateRef,
    ContextualTrustPolicy,
    FeatureContextualTrustPolicy,
    Feedback,
    NoUpdatePolicy,
    PooledControllerPolicy,
    RarePolicy,
    RawAcceptancePolicy,
    TerminalOnlyPolicy,
    UniformPolicy,
    policy_from_name,
)


def choose(policy, event_id="e0", context_key="ctx", seed=7, base=(0.2, 0.8)):
    return policy.choose(
        event_id=event_id,
        context_key=context_key,
        selector_id="selector-1",
        candidates=(CandidateRef("a", "v1"), CandidateRef("b", "v1")),
        base_scores=base,
        rng=np.random.default_rng(seed),
    )


FEATURES_A = {
    "a@v1": (1.0, 0.0),
    "b@v1": (0.0, 1.0),
}


def choose_feature(policy, event_id="e0", features=None, seed=7, base=(0.0, 0.0)):
    return policy.choose(
        event_id=event_id,
        context_key="ctx",
        selector_id="selector-1",
        candidates=(CandidateRef("a", "v1"), CandidateRef("b", "v1")),
        base_scores=base,
        rng=np.random.default_rng(seed),
        encoder_version="hash64-v1",
        feature_schema="hash64-v1-public",
        captured_features=FEATURES_A if features is None else features,
    )


def test_uniform_and_no_update_have_distinct_information_contracts_and_exact_propensity():
    uniform = UniformPolicy()
    no_update = NoUpdatePolicy()
    u = choose(uniform)
    n = choose(no_update)
    assert u.probabilities == pytest.approx((0.5, 0.5))
    assert n.probabilities[1] > n.probabilities[0]
    assert u.propensity == pytest.approx(u.probabilities[u.chosen_index])
    assert n.propensity == pytest.approx(n.probabilities[n.chosen_index])


def test_menu_permutation_preserves_each_policy_candidate_probability():
    for policy in (UniformPolicy(), NoUpdatePolicy(), TerminalOnlyPolicy(), ContextualTrustPolicy()):
        first = choose(policy, event_id="e0", seed=2)
        second = policy_from_name(policy.name)
        swapped = second.choose(
            event_id="e0", context_key="ctx", selector_id="selector-1",
            candidates=(CandidateRef("b", "v1"), CandidateRef("a", "v1")),
            base_scores=(0.8, 0.2), rng=np.random.default_rng(2),
        )
        first_by_id = dict(zip((candidate.key for candidate in first.candidates), first.probabilities))
        swapped_by_id = dict(zip((candidate.key for candidate in swapped.candidates), swapped.probabilities))
        assert swapped_by_id == pytest.approx(first_by_id)


def test_no_update_and_uniform_never_change_after_any_feedback():
    for policy in (UniformPolicy(), NoUpdatePolicy()):
        before = choose(policy)
        changed = policy.observe_feedback(Feedback("f0", "e0", "recipient_judgment", 1.0, 1.0))
        changed |= policy.observe_feedback(Feedback("f1", "e0", "terminal_outcome", 0.0, 2.0))
        after = policy.choose(
            event_id="e1", context_key="ctx", selector_id="selector-1",
            candidates=(CandidateRef("a", "v1"), CandidateRef("b", "v1")),
            base_scores=(0.2, 0.8), rng=np.random.default_rng(7),
        )
        assert changed is False
        assert after.probabilities == pytest.approx(before.probabilities)
        assert policy.updates == 0


def test_terminal_only_ignores_judgment_and_contextual_trust_ignores_terminal():
    terminal = TerminalOnlyPolicy()
    choose(terminal)
    assert terminal.observe_feedback(Feedback("j", "e0", "recipient_judgment", 0.0, 1.0)) is False
    assert terminal.observe_feedback(Feedback("t", "e0", "terminal_outcome", 1.0, 2.0)) is True
    assert terminal.updates == 1

    contextual = ContextualTrustPolicy()
    choose(contextual, context_key="ctx-a")
    assert contextual.observe_feedback(Feedback("t", "e0", "terminal_outcome", 1.0, 1.0)) is False
    assert contextual.observe_feedback(Feedback("j", "e0", "recipient_judgment", 1.0, 2.0)) is True
    assert contextual.updates == 1
    # Evidence from ctx-a does not alter the posterior for the same candidate in ctx-b.
    ctx_b = choose(contextual, event_id="e1", context_key="ctx-b", seed=9)
    assert ctx_b.probabilities[1] < 0.95


def test_raw_acceptance_uses_separate_public_channel_and_accept_reject_actions():
    raw = RawAcceptancePolicy()
    choose(raw)
    choose(raw, event_id="e1")
    assert raw.observe_feedback(
        Feedback("judgment", "e0", "recipient_judgment", 1.0, 1.0, action="accept")
    ) is False
    assert raw.observe_feedback(
        Feedback("wrong-action", "e1", "raw_acceptance", 1.0, 2.0, action="use")
    ) is False
    assert raw.observe_feedback(
        Feedback("accept", "e0", "raw_acceptance", 1.0, 3.0, action="accept")
    ) is True
    assert raw.updates == 1


def test_pooled_controller_transfers_public_judgment_across_contexts():
    pooled = PooledControllerPolicy()
    first = choose(pooled, context_key="ctx-a", seed=3, base=(0.5, 0.5))
    assert pooled.observe_feedback(
        Feedback("j0", first.event_id, "recipient_judgment", 1.0, 1.0, action="accept")
    ) is True
    second = choose(pooled, event_id="e1", context_key="ctx-b", seed=9, base=(0.5, 0.5))
    chosen_index = next(index for index, candidate in enumerate(second.candidates)
                        if candidate.key == first.chosen.key)
    assert second.probabilities[chosen_index] > 0.5
    restored = PooledControllerPolicy.restore(pooled.snapshot())
    assert restored.snapshot()["state"] == pooled.snapshot()["state"]


def test_unknown_or_illegal_feedback_cannot_update_and_duplicate_is_idempotent():
    policy = ContextualTrustPolicy()
    choose(policy)
    assert policy.observe_feedback(Feedback("pending", "e0", "recipient_judgment", 1.0, 1.0, disposition="pending")) is False
    assert policy.observe_feedback(Feedback("illegal", "e0", "recipient_judgment", 1.0, 1.0, provenance="unknown")) is False
    assert policy.updates == 0
    assert policy.observe_feedback(Feedback("ok", "e0", "recipient_judgment", 1.0, 1.0)) is True
    assert policy.observe_feedback(Feedback("ok", "e0", "recipient_judgment", 1.0, 1.0)) is False
    assert policy.updates == 1
    with pytest.raises(ValueError, match="unknown source decision"):
        policy.observe_feedback(Feedback("missing", "does-not-exist", "recipient_judgment", 1.0, 1.0))


def test_invalid_menus_and_feedback_are_rejected():
    policy = UniformPolicy()
    with pytest.raises(ValueError):
        choose(policy, base=(0.2,))
    choose(policy)
    with pytest.raises(ValueError):
        policy.observe_feedback(Feedback("bad", "e0", "other", 1.0, 1.0))
    with pytest.raises(ValueError):
        policy.observe_feedback(Feedback("bad-label", "e0", "recipient_judgment", 2.0, 1.0))


def test_versioned_candidates_do_not_share_terminal_trust_and_snapshot_restores():
    policy = TerminalOnlyPolicy()
    first = policy.choose(
        event_id="e0", context_key="ctx", selector_id="selector-1",
        candidates=(CandidateRef("a", "v1"), CandidateRef("b", "v1")),
        base_scores=(0.5, 0.5), rng=np.random.default_rng(1),
        state_version="s0", encoder_version="enc1", feature_schema="phi1", selected_at=3.0,
    )
    assert policy.observe_feedback(Feedback("t0", "e0", "terminal_outcome", 1.0, 4.0, delay=1.0, action="use")) is True
    snapshot = policy.snapshot()
    restored = TerminalOnlyPolicy.restore(snapshot)
    second = restored.choose(
        event_id="e1", context_key="ctx", selector_id="selector-1",
        candidates=(CandidateRef("a", "v2"), CandidateRef("b", "v2")),
        base_scores=(0.5, 0.5), rng=np.random.default_rng(2),
        state_version="s1", encoder_version="enc1", feature_schema="phi1", selected_at=5.0,
    )
    assert second.probabilities == pytest.approx((0.5, 0.5))
    assert restored.snapshot()["decisions"]["e0"]["chosen_key"] == first.chosen.key
    assert restored.snapshot()["state"] == snapshot["state"]


def test_same_source_channel_is_not_counted_twice_but_judgment_and_terminal_are_distinct():
    policy = ContextualTrustPolicy()
    choose(policy)
    assert policy.observe_feedback(Feedback("j0", "e0", "recipient_judgment", 1.0, 1.0)) is True
    assert policy.observe_feedback(Feedback("j1", "e0", "recipient_judgment", 0.0, 2.0)) is False
    assert policy.observe_feedback(Feedback("t0", "e0", "terminal_outcome", 0.0, 3.0)) is False
    assert policy.updates == 1


def test_non_rare_comparators_treat_corrections_as_unknown_no_update():
    policy = ContextualTrustPolicy()
    choose(policy)
    assert policy.observe_feedback(Feedback("f0", "e0", "recipient_judgment", 1.0, 1.0)) is True
    assert policy.observe_feedback(Feedback(
        "f0-correction", "e0", "recipient_judgment", 0.0, 2.0, supersedes="f0",
    )) is False
    assert policy.updates == 1


def test_feature_contextual_uses_same_public_features_and_old_context_control_does_not():
    linear = FeatureContextualTrustPolicy(dimension=2)
    context_only = ContextualTrustPolicy()
    first = choose_feature(linear)
    choose_feature(context_only, features=FEATURES_A)
    changed = linear.observe_feedback(Feedback("f0", first.event_id, "recipient_judgment", 1.0, 1.0))
    assert changed is True
    learned_key = first.chosen.key
    other_key = next(candidate.key for candidate in first.candidates if candidate.key != learned_key)

    after = choose_feature(linear, event_id="e1", features=FEATURES_A, seed=3)
    swapped = choose_feature(linear, event_id="e2", features={
        "a@v1": FEATURES_A[other_key], "b@v1": FEATURES_A[learned_key],
    }, seed=3)
    after_by_key = dict(zip((candidate.key for candidate in after.candidates), after.probabilities))
    swapped_by_key = dict(zip((candidate.key for candidate in swapped.candidates), swapped.probabilities))
    assert after_by_key[learned_key] > after_by_key[other_key]
    assert swapped_by_key[learned_key] > swapped_by_key[other_key]

    context_a = choose(ContextualTrustPolicy(), event_id="ctx-a", base=(0.3, 0.3), seed=3)
    context_b = ContextualTrustPolicy().choose(
        event_id="ctx-a", context_key="ctx", selector_id="selector-1",
        candidates=context_a.candidates, base_scores=(0.3, 0.3), rng=np.random.default_rng(3),
        encoder_version="hash64-v1", feature_schema="hash64-v1-public",
        captured_features={"a@v1": (0.0, 1.0), "b@v1": (1.0, 0.0)},
    )
    assert context_a.probabilities == pytest.approx(context_b.probabilities)


def test_feature_contextual_requires_exact_bounded_feature_contract():
    policy = FeatureContextualTrustPolicy(dimension=2)
    with pytest.raises(ValueError, match="L2 norm"):
        choose_feature(policy, features={"a@v1": (1.0, 1.0), "b@v1": (0.0, 1.0)})
    with pytest.raises(ValueError, match="configured dimension"):
        choose_feature(policy, features={"a@v1": (1.0,), "b@v1": (0.0,)})


def test_feature_contextual_unknown_duplicate_and_correction_do_not_update():
    policy = FeatureContextualTrustPolicy(dimension=2)
    first = choose_feature(policy)
    assert policy.observe_feedback(Feedback("pending", first.event_id, "recipient_judgment", 1.0, 1.0,
                                             disposition="pending")) is False
    assert policy.observe_feedback(Feedback("f0", first.event_id, "recipient_judgment", 1.0, 2.0)) is True
    assert policy.observe_feedback(Feedback("f0-correction", first.event_id, "recipient_judgment", 0.0, 3.0,
                                             supersedes="f0")) is False
    assert policy.observe_feedback(Feedback("f0-duplicate", first.event_id, "recipient_judgment", 0.0, 4.0)) is False
    assert policy.updates == 1
    assert policy.snapshot()["state"]["n_updates"] == 1


def test_feature_contextual_snapshot_restore_preserves_next_decision():
    policy = FeatureContextualTrustPolicy(dimension=2)
    first = choose_feature(policy)
    assert policy.observe_feedback(Feedback("f0", first.event_id, "recipient_judgment", 1.0, 1.0)) is True
    restored = FeatureContextualTrustPolicy.restore(policy.snapshot())
    left = choose_feature(policy, event_id="e1", seed=11)
    right = choose_feature(restored, event_id="e1", seed=11)
    assert left.probabilities == pytest.approx(right.probabilities)
    assert restored.snapshot()["state"] == policy.snapshot()["state"]


def test_rare_and_feature_contextual_share_base_score_input():
    rare = RarePolicy(dimension=2, exploration=0.0)
    linear = FeatureContextualTrustPolicy(dimension=2)
    low = choose_feature(rare, base=(0.0, 0.0), seed=3)
    high = choose_feature(rare, event_id="e1", base=(0.0, 2.0), seed=3)
    assert high.probabilities[1] > low.probabilities[1]
    linear_low = choose_feature(linear, base=(0.0, 0.0), seed=3)
    linear_high = choose_feature(linear, event_id="e1", base=(0.0, 2.0), seed=3)
    assert linear_high.probabilities[1] > linear_low.probabilities[1]
