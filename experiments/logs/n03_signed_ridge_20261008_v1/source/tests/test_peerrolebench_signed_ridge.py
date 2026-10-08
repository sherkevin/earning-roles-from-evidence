from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_signed_ridge import SignedRidgeState  # noqa: E402


def test_signed_correlated_prefixes_match_independent_batch_solve():
    rho = 0.7
    state = SignedRidgeState(3, rho)
    samples = [
        ([0.6, 0.5, 0.0], -0.8),
        ([0.6, 0.5, 0.0], 0.3),  # repeated correlated row
        ([0.0, 0.0, 0.0], -2.0),  # zero feature carries no update
        ([0.5, 0.4, 0.2], -1.2),
        ([0.2, -0.3, 0.6], 0.9),
    ]
    rows: list[np.ndarray] = []
    targets: list[float] = []
    for x, u in samples:
        feature = np.asarray(x, dtype=np.float64)
        expected_before = float(feature @ state.weights)
        assert state.update(x, u) == pytest.approx(expected_before)
        rows.append(feature)
        targets.append(u)
        X = np.stack(rows)
        expected = np.linalg.solve(rho * np.eye(3) + X.T @ X, X.T @ np.asarray(targets))
        np.testing.assert_allclose(state.weights, expected, rtol=1e-12, atol=1e-12)
        assert state.count == len(rows)
    assert state.memory_bytes == (3 * 3 + 3) * 8


def test_negative_target_has_exact_ridge_effect():
    state = SignedRidgeState(1, 1.0)
    assert state.predict([1.0]) == 0.0
    assert state.update([1.0], -2.0) == 0.0
    assert state.weights[0] == -1.0
    assert state.inverse[0, 0] == 0.5
    assert state.predict([1.0]) == -1.0


@pytest.mark.parametrize("x,u", [
    ([1.0, 0.0, 0.0], 1.0),  # dimension
    ([1.01, 0.0], 1.0),  # range
    ([float("nan"), 0.0], 1.0),
    ([float("inf"), 0.0], 1.0),
    ([0.5, 0.0], float("nan")),
    ([0.5, 0.0], float("inf")),
    ([0.5, 0.0], "invalid"),
])
def test_invalid_inputs_leave_state_unchanged(x, u):
    state = SignedRidgeState(2, 1.0)
    state.update([0.5, 0.0], -1.0)
    weights, inverse, count = state.weights, state.inverse, state.count
    with pytest.raises(ValueError):
        state.update(x, u)
    np.testing.assert_array_equal(state.weights, weights)
    np.testing.assert_array_equal(state.inverse, inverse)
    assert state.count == count


def test_arithmetic_overflow_leaves_state_unchanged():
    state = SignedRidgeState(1, 1e-308)
    weights, inverse = state.weights, state.inverse
    with pytest.raises(ValueError, match="not finite"):
        state.update([1.0], -1.0)
    np.testing.assert_array_equal(state.weights, weights)
    np.testing.assert_array_equal(state.inverse, inverse)
    assert state.count == 0


def test_exposed_arrays_do_not_alias_state():
    state = SignedRidgeState(2, 1.0)
    state.update([0.5, 0.0], -1.0)
    weights, inverse = state.weights, state.inverse
    weights[:] = 99.0
    inverse[:] = 99.0
    assert state.weights[0] < 0
    assert state.inverse[0, 0] < 1.0


@pytest.mark.parametrize("dimension,rho", [(0, 1.0), (True, 1.0), (2, 0.0),
                                           (2, float("inf")), (2, float("nan"))])
def test_invalid_initialization(dimension, rho):
    with pytest.raises(ValueError):
        SignedRidgeState(dimension, rho)
