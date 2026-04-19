"""Unit tests for ``workspace.idea04_core.persona_model`` (E-004 / R3).

Run from repo root::

    python -m pytest workspace/idea04_core/test_persona_model.py -v
"""

from __future__ import annotations

import pytest

from workspace.idea04_core.audit_runtime import AuditDecision, AuditEvent
from workspace.idea04_core.persona_model import (
    DIM_COUNT,
    EMA_NU_DEFAULT,
    NEUTRAL_INIT,
    PERSONA_DIMS,
    SCHEMA_V1,
    SCHEMA_V2,
    BeliefStore,
    PersonaModelError,
    PersonaVector,
    apply_evidence,
    deserialize,
    evidence_extract,
    serialize_v2,
    update_belief_from_audit,
)


# ---------------------------------------------------------------------------
# 1. PersonaVector basics
# ---------------------------------------------------------------------------


def test_persona_vector_default_neutral_at_0_5() -> None:
    v = PersonaVector()
    assert len(v.values) == DIM_COUNT
    assert all(x == NEUTRAL_INIT for x in v.values)
    assert v.mean() == NEUTRAL_INIT


def test_persona_vector_rejects_wrong_length() -> None:
    with pytest.raises(PersonaModelError, match=f"{DIM_COUNT} dims"):
        PersonaVector(values=tuple([0.1] * 5))
    with pytest.raises(PersonaModelError, match=f"{DIM_COUNT} dims"):
        PersonaVector(values=tuple([0.1] * 9))


def test_persona_vector_clips_out_of_range() -> None:
    raw = (-0.5, 0.0, 0.3, 0.7, 1.0, 1.7, 0.5)
    v = PersonaVector(values=raw)
    assert v.values == (0.0, 0.0, 0.3, 0.7, 1.0, 1.0, 0.5)


def test_persona_vector_from_scalar_broadcasts() -> None:
    v = PersonaVector.from_scalar(0.4)
    assert v.values == tuple([0.4] * DIM_COUNT)


def test_persona_vector_from_scalar_clips() -> None:
    assert PersonaVector.from_scalar(-0.7).values == tuple([0.0] * DIM_COUNT)
    assert PersonaVector.from_scalar(2.3).values == tuple([1.0] * DIM_COUNT)


def test_persona_vector_as_dict_uses_named_axes() -> None:
    raw = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
    v = PersonaVector(values=raw)
    d = v.as_dict()
    assert set(d.keys()) == set(PERSONA_DIMS)
    assert d["need_decompose"] == 0.1
    assert d["cost_sensitivity"] == 0.7


def test_persona_vector_fit_dot_product() -> None:
    persona = PersonaVector(values=(0.5,) * DIM_COUNT)
    sig = (1.0,) * DIM_COUNT
    # dot = 0.5 * 7 = 3.5; / 7 = 0.5
    assert persona.fit(sig) == pytest.approx(0.5)

    persona2 = PersonaVector(values=(1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0))
    sig2 = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    # dot = 4; / 7 ≈ 0.5714
    assert persona2.fit(sig2) == pytest.approx(4 / DIM_COUNT)


def test_persona_vector_fit_rejects_wrong_signature_length() -> None:
    persona = PersonaVector()
    with pytest.raises(PersonaModelError, match="signature must have"):
        persona.fit([0.1, 0.2, 0.3])


# ---------------------------------------------------------------------------
# 2. BeliefStore
# ---------------------------------------------------------------------------


def test_belief_store_get_default_returns_neutral() -> None:
    store = BeliefStore()
    v = store.get("unknown_neighbour")
    assert v.values == tuple([NEUTRAL_INIT] * DIM_COUNT)


def test_belief_store_set_and_get_round_trip() -> None:
    store = BeliefStore()
    target = PersonaVector(values=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7))
    store.set("nb1", target)
    assert store.get("nb1") == target
    assert "nb1" in store
    assert "nb2" not in store
    assert len(store) == 1


def test_belief_store_keys_lists_neighbours() -> None:
    store = BeliefStore()
    store.set("a", PersonaVector.from_scalar(0.6))
    store.set("b", PersonaVector.from_scalar(0.4))
    assert sorted(store.keys()) == ["a", "b"]


# ---------------------------------------------------------------------------
# 3. evidence_extract
# ---------------------------------------------------------------------------


def _good_event(value_gain: float = 0.85, rework_cost: float = 0.05,
                timeliness: float = 1.0, depth: int = 1) -> AuditEvent:
    return AuditEvent(
        event_id=f"e_{value_gain}_{rework_cost}",
        upstream_id="up", downstream_id="down", task_id="down",
        decision=AuditDecision.ACCEPT,
        rework_cost=rework_cost, value_gain=value_gain,
        timeliness=timeliness,
        decomposition_help=0.0, integration_help=0.0,
    )


def _bad_event(value_gain: float = 0.0, rework_cost: float = 0.9,
               timeliness: float = 1.0) -> AuditEvent:
    return AuditEvent(
        event_id="e_bad",
        upstream_id="up", downstream_id="down", task_id="down",
        decision=AuditDecision.REJECT_REROUTE,
        rework_cost=rework_cost, value_gain=value_gain,
        timeliness=timeliness,
        decomposition_help=0.0, integration_help=0.0,
    )


def test_evidence_extract_high_value_gain_pushes_high_signature_axes_up() -> None:
    """High value_gain on a heavily-demanded axis → evidence near 1 on that axis."""
    sig = [1.0] + [0.0] * (DIM_COUNT - 1)  # only axis 0 is demanded
    ev = evidence_extract(_good_event(value_gain=0.95), sig)
    # axis 0: on_axis = 1*0.95 = 0.95; off_axis = 0; damped = 0.5+(0.95-0.5)*1 = 0.95
    assert ev.values[0] == pytest.approx(0.95, abs=1e-6)


def test_evidence_extract_bad_event_pushes_demanded_axes_down() -> None:
    sig = [1.0] + [0.0] * (DIM_COUNT - 1)
    ev = evidence_extract(_bad_event(), sig)
    # axis 0: on_axis = 1*0 = 0; off_axis = 0*0.1*0.5 = 0; damped = 0.5+(0-0.5)*1 = 0
    assert ev.values[0] == pytest.approx(0.0, abs=1e-6)


def test_evidence_extract_neutral_signature_yields_neutral_evidence_on_off_axes() -> None:
    """Axes the task did NOT demand (signature=0) drift toward neutral on a perfect audit."""
    sig = [1.0] + [0.0] * (DIM_COUNT - 1)
    ev = evidence_extract(_good_event(value_gain=1.0, rework_cost=0.0), sig)
    # axis 1: on_axis = 0; off_axis = 1*1*0.5 = 0.5; damped = 0.5+(0.5-0.5)*1 = 0.5
    assert ev.values[1] == pytest.approx(0.5, abs=1e-6)


def test_evidence_extract_timeliness_dampens_signal() -> None:
    sig = [1.0] + [0.0] * (DIM_COUNT - 1)
    ev_fresh = evidence_extract(_good_event(value_gain=0.95, timeliness=1.0), sig)
    ev_late = evidence_extract(_good_event(value_gain=0.95, timeliness=0.2), sig)
    # axis 0 dampened toward NEUTRAL_INIT=0.5
    assert ev_fresh.values[0] > ev_late.values[0]
    # late case: 0.5 + (0.95-0.5)*0.2 = 0.59
    assert ev_late.values[0] == pytest.approx(0.59, abs=1e-6)


def test_evidence_extract_rejects_wrong_signature_length() -> None:
    with pytest.raises(PersonaModelError, match="task_signature"):
        evidence_extract(_good_event(), [0.1, 0.2, 0.3])


# ---------------------------------------------------------------------------
# 4. apply_evidence (EMA update)
# ---------------------------------------------------------------------------


def test_apply_evidence_ema_with_nu_0_2() -> None:
    prior = PersonaVector(values=(0.5,) * DIM_COUNT)
    evidence = PersonaVector(values=(1.0,) * DIM_COUNT)
    new = apply_evidence(prior, evidence, nu=0.2)
    # 0.8*0.5 + 0.2*1 = 0.6
    for v in new.values:
        assert v == pytest.approx(0.6, abs=1e-6)


def test_apply_evidence_default_nu_matches_constant() -> None:
    prior = PersonaVector.neutral()
    evidence = PersonaVector(values=(0.9,) * DIM_COUNT)
    new = apply_evidence(prior, evidence)  # default nu
    expected = (1 - EMA_NU_DEFAULT) * 0.5 + EMA_NU_DEFAULT * 0.9
    for v in new.values:
        assert v == pytest.approx(expected, abs=1e-6)


def test_apply_evidence_clips_to_unit_interval() -> None:
    prior = PersonaVector(values=(0.0,) * DIM_COUNT)
    # constructed evidence will already be clipped, but verify combination stays bounded
    evidence = PersonaVector(values=(1.0,) * DIM_COUNT)
    for _ in range(20):
        prior = apply_evidence(prior, evidence, nu=0.3)
    for v in prior.values:
        assert 0.0 <= v <= 1.0


def test_apply_evidence_convergence_over_repeated_constant_evidence() -> None:
    """Repeating the same evidence drives the belief geometrically toward it."""
    belief = PersonaVector.neutral()  # 0.5
    target = PersonaVector(values=(0.9,) * DIM_COUNT)
    for _ in range(15):
        belief = apply_evidence(belief, target, nu=EMA_NU_DEFAULT)
    # geometric: 0.9 - (0.9-0.5)*(1-0.2)^15 ≈ 0.9 - 0.4*0.0352 ≈ 0.886
    for v in belief.values:
        assert 0.85 < v < 0.91


def test_apply_evidence_nu_clipped_to_unit_interval() -> None:
    prior = PersonaVector.neutral()
    evidence = PersonaVector(values=(1.0,) * DIM_COUNT)
    # nu > 1 should clip to 1 → evidence wins entirely
    new = apply_evidence(prior, evidence, nu=2.5)
    for v in new.values:
        assert v == pytest.approx(1.0, abs=1e-6)
    # nu < 0 should clip to 0 → prior wins entirely
    new2 = apply_evidence(prior, evidence, nu=-1.0)
    for v in new2.values:
        assert v == pytest.approx(0.5, abs=1e-6)


# ---------------------------------------------------------------------------
# 5. update_belief_from_audit (full pipeline helper)
# ---------------------------------------------------------------------------


def test_update_belief_from_audit_writes_back() -> None:
    store = BeliefStore()
    sig = [0.7, 0.5, 0.3, 0.5, 0.5, 0.5, 0.5]
    new = update_belief_from_audit(store, "nb", _good_event(value_gain=0.9), sig)
    assert "nb" in store
    assert store.get("nb") == new


def test_update_belief_from_audit_initialises_from_neutral() -> None:
    store = BeliefStore()
    sig = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    new = update_belief_from_audit(store, "nb", _good_event(value_gain=1.0), sig)
    # axis 0: prior=0.5; evidence=1.0; new = 0.8*0.5 + 0.2*1.0 = 0.6
    assert new.values[0] == pytest.approx(0.6, abs=1e-6)


# ---------------------------------------------------------------------------
# 6. Dual-track schema (C-3 hard constraint)
# ---------------------------------------------------------------------------


def test_serialize_v2_includes_both_tracks() -> None:
    store = BeliefStore()
    store.set("a", PersonaVector(values=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)))
    store.set("b", PersonaVector(values=(0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9)))
    rec = serialize_v2(store)
    assert rec["schema_version"] == SCHEMA_V2
    assert SCHEMA_V1 in rec
    assert SCHEMA_V2 in rec
    # v1 mean projection
    assert rec[SCHEMA_V1]["a"] == pytest.approx(sum([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]) / 7)
    assert rec[SCHEMA_V1]["b"] == pytest.approx(0.9)
    # v2 vector exact
    assert rec[SCHEMA_V2]["a"] == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]


def test_deserialize_v2_round_trip() -> None:
    store = BeliefStore()
    store.set("a", PersonaVector(values=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)))
    rec = serialize_v2(store)
    loaded = deserialize(rec)
    assert loaded.get("a") == store.get("a")


def test_deserialize_v1_scalar_broadcasts_to_v2() -> None:
    """Backward-compat: a record with only competence_v1_scalar must still load."""
    legacy = {
        "schema_version": SCHEMA_V1,
        SCHEMA_V1: {"a": 0.7, "b": 0.3},
    }
    store = deserialize(legacy)
    assert store.get("a").values == tuple([0.7] * DIM_COUNT)
    assert store.get("b").values == tuple([0.3] * DIM_COUNT)


def test_deserialize_flat_v1_layout() -> None:
    """Even older path: the record is a flat scalar dict + schema_version=v1."""
    legacy = {
        "schema_version": SCHEMA_V1,
        "a": 0.42,
        "b": 0.58,
    }
    store = deserialize(legacy)
    assert store.get("a").values == tuple([0.42] * DIM_COUNT)


def test_deserialize_unknown_schema_raises() -> None:
    with pytest.raises(PersonaModelError, match="cannot recognise"):
        deserialize({"schema_version": "competence_v3_quaternion", "irrelevant": True})


def test_deserialize_silently_drops_unknown_keys() -> None:
    """Forward-compat: future fields must be silently dropped (per C-3)."""
    rec = serialize_v2(BeliefStore.from_v2_dict({"a": [0.5] * DIM_COUNT}))
    rec["competence_v3_future"] = {"a": "anything"}
    rec["unknown_top_level"] = 42
    store = deserialize(rec)
    assert "a" in store


def test_v2_to_v1_projection_uses_dim_mean() -> None:
    store = BeliefStore.from_v2_dict({"a": [0.0, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5]})
    v1 = store.to_v1_dict()
    assert v1["a"] == pytest.approx(sum([0.0, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5]) / 7)


def test_belief_store_from_v1_dict_broadcasts_uniformly() -> None:
    store = BeliefStore.from_v1_dict({"a": 0.3, "b": 0.8})
    assert store.get("a").values == tuple([0.3] * DIM_COUNT)
    assert store.get("b").values == tuple([0.8] * DIM_COUNT)
