from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_signed_ridge import DisjointSignedRidgeState  # noqa: E402


KEYS = ("agent-a@v1", "agent-b@v1")


def test_selected_only_signed_updates_equal_independent_full_block_ridge():
    rho, dimension = 0.4, 2
    bank = DisjointSignedRidgeState(KEYS, dimension, rho)
    observations = [
        (KEYS[0], [0.8, 0.0], 1.0),
        (KEYS[1], [0.8, 0.0], -0.7),
        (KEYS[0], [0.0, 0.9], -1.0),
        (KEYS[1], [0.0, 0.9], 0.5),
        (KEYS[0], [0.8, 0.0], -0.2),
    ]
    rows, targets = [], []
    for key, z, target in observations:
        before = bank.predict(key, z)
        assert bank.update(key, z, target) == pytest.approx(before)
        row = np.zeros(len(KEYS) * dimension)
        block = KEYS.index(key)
        row[block * dimension:(block + 1) * dimension] = z
        rows.append(row)
        targets.append(target)
        X = np.stack(rows)
        expected = np.linalg.solve(
            rho * np.eye(len(KEYS) * dimension) + X.T @ X,
            X.T @ np.asarray(targets),
        )
        for index, candidate in enumerate(KEYS):
            np.testing.assert_allclose(
                bank.weights(candidate), expected[index * dimension:(index + 1) * dimension],
                rtol=1e-12, atol=1e-12,
            )
    assert bank.total_updates == len(observations)
    assert bank.memory_bytes == len(KEYS) * (dimension**2 + 2 * dimension) * 8


def test_context_reverses_candidate_scores_and_unselected_state_stays_unchanged():
    bank = DisjointSignedRidgeState(KEYS, 2, 1.0)
    bank.update(KEYS[0], [1.0, 0.0], 1.0)
    before_b = bank.weights(KEYS[1])
    bank.update(KEYS[0], [0.0, 1.0], -1.0)
    np.testing.assert_array_equal(bank.weights(KEYS[1]), before_b)
    assert bank.count(KEYS[1]) == 0
    bank.update(KEYS[1], [1.0, 0.0], -1.0)
    bank.update(KEYS[1], [0.0, 1.0], 1.0)
    first = bank.scores(KEYS, [1.0, 0.0])
    second = bank.scores(KEYS, [0.0, 1.0])
    assert first[KEYS[0]] > first[KEYS[1]]
    assert second[KEYS[0]] < second[KEYS[1]]


def test_menu_permutation_subset_and_new_version_do_not_shift_keyed_scores():
    keys = (*KEYS, "agent-a@v2")
    bank = DisjointSignedRidgeState(keys, 2, 1.0)
    bank.update("agent-a@v1", [0.6, 0.3], -0.8)
    original = bank.scores(KEYS, [0.6, 0.3])
    permuted = bank.scores(tuple(reversed(KEYS)), [0.6, 0.3])
    subset = bank.scores((KEYS[0],), [0.6, 0.3])
    assert original == permuted
    assert subset[KEYS[0]] == original[KEYS[0]]
    assert bank.predict("agent-a@v2", [0.6, 0.3]) == 0.0
    assert bank.count("agent-a@v2") == 0


def test_invalid_input_and_unknown_or_duplicate_keys_do_not_mutate_bank():
    bank = DisjointSignedRidgeState(KEYS, 2, 1.0)
    bank.update(KEYS[0], [0.5, 0.0], 1.0)
    before = {key: (bank.weights(key), bank.count(key)) for key in KEYS}
    for key, context, target in (
        (KEYS[0], [2.0, 0.0], 1.0),
        (KEYS[0], [0.5, 0.0], float("inf")),
        ("agent-a@v2", [0.5, 0.0], -1.0),
    ):
        with pytest.raises(ValueError):
            bank.update(key, context, target)
    with pytest.raises(ValueError, match="unique"):
        bank.scores((KEYS[0], KEYS[0]), [0.5, 0.0])
    with pytest.raises(ValueError, match="unknown"):
        bank.scores((KEYS[0], "agent-a@v2"), [0.5, 0.0])
    with pytest.raises(ValueError, match="unique"):
        DisjointSignedRidgeState((KEYS[0], KEYS[0]), 2, 1.0)
    for key, (weights, count) in before.items():
        np.testing.assert_array_equal(bank.weights(key), weights)
        assert bank.count(key) == count
