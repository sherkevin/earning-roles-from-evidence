"""Test-only selector adapter that consumes only public PeerHistory projections.

This is not the proposed learner.  It is a deterministic comparator used by
the four-cell qualification to prove that a projection is actually part of
the E2 decision input and that empty/reset histories are equivalent.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from typing import Any, Mapping, Sequence


VERSION = "peer-history-selector-consumption-test-v1"
_PUBLIC_PROJECTION_KEYS = frozenset({
    "schema", "candidate_key", "entry_count", "scope_count", "scopes",
    "history_digest", "version",
})
_PUBLIC_SCOPE_KEYS = frozenset({
    "scope_key", "role_signature_hash", "execution_state_fingerprint",
    "n_pass", "n_fail", "n_unknown", "last_arrival", "smoothed_rate",
    "cost_mean_wall_ms",
})


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _projection_score(projection: Mapping[str, Any], *, candidate_key: str,
                      read_cut: int) -> float:
    if projection.get("schema") != "peer-history-v2":
        raise ValueError("unsupported history projection schema")
    if projection.get("candidate_key") != candidate_key:
        raise ValueError("history projection candidate key mismatch")
    if set(projection) != _PUBLIC_PROJECTION_KEYS:
        raise ValueError("history projection contains non-public fields")
    if int(projection.get("entry_count", -1)) < 0:
        raise ValueError("invalid history entry count")
    if int(projection.get("scope_count", -1)) < 0:
        raise ValueError("invalid history scope count")
    scopes = projection.get("scopes")
    if not isinstance(scopes, list):
        raise ValueError("history projection scopes must be a list")
    if int(projection["scope_count"]) != len(scopes):
        raise ValueError("history projection scope count mismatch")
    rates: list[float] = []
    for scope in scopes:
        if not isinstance(scope, Mapping):
            raise ValueError("history scope must be an object")
        if set(scope) != _PUBLIC_SCOPE_KEYS:
            raise ValueError("history scope contains non-public fields")
        last_arrival = scope.get("last_arrival")
        if last_arrival is not None and int(last_arrival) > int(read_cut):
            raise ValueError("history row is unavailable at the E2 read cut")
        rate = scope.get("smoothed_rate")
        if rate is not None:
            rate = float(rate)
            if not math.isfinite(rate) or not 0.0 <= rate <= 1.0:
                raise ValueError("history rate is outside [0,1]")
            rates.append(rate)
    if not rates:
        return 0.0
    return 2.0 * (sum(rates) / len(rates) - 0.5)


def select_from_public_history(
    *, candidate_keys: Sequence[str], projections: Mapping[str, Mapping[str, Any]],
    base_scores: Sequence[float], read_cut: int, rng_seed: int,
) -> dict[str, Any]:
    """Return a reproducible choice from public projection inputs only."""
    keys = tuple(str(key) for key in candidate_keys)
    if not keys or len(keys) != len(base_scores) or len(set(keys)) != len(keys):
        raise ValueError("candidate menu and base scores must align")
    if set(projections) != set(keys):
        raise ValueError("projection keys must equal the candidate menu")
    scores = tuple(float(base) + _projection_score(
                       projections[key], candidate_key=key, read_cut=read_cut
                   )
                   for key, base in zip(keys, base_scores))
    if not all(math.isfinite(score) for score in scores):
        raise ValueError("non-finite selection score")
    shifted = tuple(math.exp(score - max(scores)) for score in scores)
    denominator = sum(shifted)
    probabilities = tuple(value / denominator for value in shifted)
    draw = random.Random(int(rng_seed)).random()
    cumulative = 0.0
    chosen_index = len(keys) - 1
    for index, probability in enumerate(probabilities):
        cumulative += probability
        if draw < cumulative:
            chosen_index = index
            break
    public_inputs = {
        "selector_version": VERSION,
        "candidate_keys": list(keys),
        "base_scores": list(map(float, base_scores)),
        "read_cut": int(read_cut),
        "projections": {key: projections[key] for key in keys},
    }
    return {
        "selector_version": VERSION,
        "input_digest": _digest(public_inputs),
        "projection_digests": {
            key: _digest(projections[key]) for key in keys
        },
        "scores": list(scores),
        "probabilities": list(probabilities),
        "rng_seed": int(rng_seed),
        "rng_draw": draw,
        "chosen_peer": keys[chosen_index],
        "propensity": probabilities[chosen_index],
    }


__all__ = ["VERSION", "select_from_public_history"]
