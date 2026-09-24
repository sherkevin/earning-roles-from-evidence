import numpy as np

from online_head import OnlineRLSHead


def test_rls_updates_live_parameters_and_is_menu_order_safe():
    head = OnlineRLSHead(feature_dim=2, ridge=1.0)
    features = {"a": [1.0, 0.0], "b": [0.0, 1.0]}
    before = head.theta.copy()
    head.update(features["a"], label=1.0, propensity=1.0)
    assert head.observed == 1
    assert not np.allclose(before, head.theta)
    p1, u1 = head.score(["a", "b"], [0.1, 0.1], features)
    p2, u2 = head.score(["b", "a"], [0.1, 0.1], {"a": features["a"], "b": features["b"]})
    assert np.allclose(p1[0], p2[1])
    assert np.allclose(u1[0], u2[1])


def test_rls_bounds_parameters_and_snapshot_roundtrip():
    head = OnlineRLSHead(feature_dim=3, max_parameter_norm=0.1, max_weight=20.0)
    for _ in range(10):
        head.update([100.0, 0.0, 0.0], label=1.0, propensity=0.01)
    assert np.linalg.norm(head.theta) <= 0.100001
    restored = OnlineRLSHead.restore(head.snapshot())
    assert np.allclose(restored.theta, head.theta)
    assert restored.observed == head.observed


def test_rls_rejects_invalid_feedback_and_features():
    head = OnlineRLSHead(feature_dim=2)
    for args in [([1.0, np.nan], 1.0, 1.0), ([1.0, 0.0], 2.0, 1.0), ([1.0, 0.0], 1.0, 0.0)]:
        try:
            head.update(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid event was accepted")


def test_rls_bounds_extreme_values_and_deduplicates_feedback():
    head = OnlineRLSHead(feature_dim=2, max_feature_norm=2.0, max_seen_feedback=2)
    assert head.update([1e200, 0.0], 1.0, 1.0, feedback_id="f1") is True
    observed = head.observed
    assert head.update([1e200, 0.0], 1.0, 1.0, feedback_id="f1") is False
    assert head.observed == observed
    probs, uncertainty = head.score(["a", "b"], [1e308, -1e308], {
        "a": [1e200, 0.0], "b": [0.0, 1e200]
    })
    assert np.all(np.isfinite(probs))
    assert np.all(np.isfinite(uncertainty))
    assert np.isclose(np.sum(probs), 1.0)


def test_choose_returns_exact_logged_propensity_and_snapshot_dedup_state():
    head = OnlineRLSHead(feature_dim=2, encoder_version="enc1", feature_schema="phi1")
    decision = head.choose(["a", "b"], [0.0, 0.0], {
        "a": [1.0, 0.0], "b": [0.0, 1.0]
    }, np.random.default_rng(3), encoder_version="enc1", feature_schema="phi1")
    assert decision["chosen_id"] in {"a", "b"}
    assert decision["propensity"] == decision["probabilities"][decision["chosen_index"]]
    head.update([1.0, 0.0], 1.0, decision["propensity"], feedback_id="f1")
    restored = OnlineRLSHead.restore(head.snapshot())
    assert restored.update([1.0, 0.0], 1.0, decision["propensity"], feedback_id="f1") is False
    try:
        restored.score(["a"], [0.0], {"a": [1.0, 0.0]}, encoder_version="enc2")
    except ValueError:
        pass
    else:
        raise AssertionError("stale encoder version was accepted")
