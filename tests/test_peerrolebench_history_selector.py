from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.peerrolebench_history_selector import select_from_public_history
from scripts.peerrolebench_peer_history import PeerHistoryV1


def _projections():
    return {
        "peer-a@v1": PeerHistoryV1.empty("peer-a").selector_projection(
            candidate_key="peer-a@v1"
        ),
        "peer-b@v1": PeerHistoryV1.empty("peer-b").selector_projection(
            candidate_key="peer-b@v1"
        ),
    }


def test_selector_consumes_only_public_projection_and_is_reproducible():
    projections = _projections()
    first = select_from_public_history(
        candidate_keys=tuple(projections), projections=projections,
        base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
    )
    second = select_from_public_history(
        candidate_keys=tuple(projections), projections=projections,
        base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
    )
    assert first == second
    assert first["probabilities"] == [0.5, 0.5]


def test_selector_rejects_projection_identity_or_hidden_field_mutation():
    projections = _projections()
    wrong_identity = deepcopy(projections)
    wrong_identity["peer-a@v1"]["candidate_key"] = "peer-b@v1"
    with pytest.raises(ValueError, match="candidate key"):
        select_from_public_history(
            candidate_keys=tuple(projections), projections=wrong_identity,
            base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
        )

    hidden = deepcopy(projections)
    hidden["peer-a@v1"]["private_artifact"] = "must-not-enter-selector"
    with pytest.raises(ValueError, match="non-public"):
        select_from_public_history(
            candidate_keys=tuple(projections), projections=hidden,
            base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
        )


def test_selector_rejects_future_history_at_read_cut():
    projections = _projections()
    projections["peer-a@v1"]["scopes"] = [{
        "scope_key": "scope",
        "role_signature_hash": "r",
        "execution_state_fingerprint": "s",
        "n_pass": 1,
        "n_fail": 0,
        "n_unknown": 0,
        "last_arrival": 21,
        "smoothed_rate": 2 / 3,
        "cost_mean_wall_ms": 0.0,
    }]
    projections["peer-a@v1"]["scope_count"] = 1
    with pytest.raises(ValueError, match="read cut"):
        select_from_public_history(
            candidate_keys=tuple(projections), projections=projections,
            base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
        )


def test_selector_uses_only_the_target_scope_and_rejects_ambiguous_default():
    projections = _projections()
    target = {
        "scope_key": "role:state-a",
        "role_signature_hash": "r",
        "execution_state_fingerprint": "s-a",
        "n_pass": 1, "n_fail": 0, "n_unknown": 0,
        "last_arrival": 5, "smoothed_rate": 2 / 3,
        "cost_mean_wall_ms": 0.0,
    }
    unrelated = {
        "scope_key": "role:state-b",
        "role_signature_hash": "r2",
        "execution_state_fingerprint": "s-b",
        "n_pass": 0, "n_fail": 1, "n_unknown": 0,
        "last_arrival": 5, "smoothed_rate": 1 / 3,
        "cost_mean_wall_ms": 0.0,
    }
    projections["peer-a@v1"]["scopes"] = [target, unrelated]
    projections["peer-a@v1"]["scope_count"] = 2
    with pytest.raises(ValueError, match="target scope"):
        select_from_public_history(
            candidate_keys=tuple(projections), projections=projections,
            base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
        )
    first = select_from_public_history(
        candidate_keys=tuple(projections), projections=projections,
        base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
        target_scope_key="role:state-a",
    )
    changed = deepcopy(projections)
    changed["peer-a@v1"]["scopes"][1]["smoothed_rate"] = 1.0
    second = select_from_public_history(
        candidate_keys=tuple(changed), projections=changed,
        base_scores=(0.0, 0.0), read_cut=20, rng_seed=10,
        target_scope_key="role:state-a",
    )
    assert first["probabilities"] == second["probabilities"]
    assert first["chosen_peer"] == second["chosen_peer"]
