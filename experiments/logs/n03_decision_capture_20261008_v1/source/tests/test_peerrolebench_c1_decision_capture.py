"""Zero-call checks for persisted C1 pre-execution inputs; no efficacy claim."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_baseline_policies import ContextualTrustPolicy, NoUpdatePolicy  # noqa: E402
from peerrolebench_c1_pipe3_bounded_live import (  # noqa: E402
    _features, _prepare_context, _run_parent_source, _select_source,
    load_decision_capture, save_decision_capture,
)
from peerrolebench_pipe3_full_chain_qualification import registry  # noqa: E402
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, _digest  # noqa: E402
from peerrolebench_role_evidence_selection import (  # noqa: E402
    commit_role_evidence_selection, preview_role_evidence_selection_with_public_judgment,
)
from test_peerrolebench_role_evidence_selection import _source  # noqa: E402


def _source_capture(tmp_path: Path):
    boundary = Pipe3SelectionBoundary(NoUpdatePolicy(), registry())
    seal = _select_source(boundary, "no_update", _features(), 0, namespace="parent")
    path = tmp_path / "preexecution_capture.json"
    digest = save_decision_capture(path, seal, boundary)
    return boundary, seal, path, digest


def _write_tamper(path: Path, mutate):
    receipt = json.loads(path.read_text(encoding="utf-8"))
    mutate(receipt)
    body = dict(receipt)
    body.pop("capture_digest")
    receipt["capture_digest"] = _digest(body)
    path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")


def test_parent_capture_precedes_episode_failure_and_remains_reloadable(tmp_path, monkeypatch):
    def fail_later(**_kwargs):
        raise RuntimeError("episode stopped after selection")

    monkeypatch.setattr("peerrolebench_c1_pipe3_bounded_live._run_episode", fail_later)
    with pytest.raises(RuntimeError, match="after selection"):
        _run_parent_source(tmp_path, {}, _prepare_context())
    path = tmp_path / "parent_source" / "decision_0" / "preexecution_capture.json"
    before = path.read_bytes()
    assert load_decision_capture(path) == _features()["peer-b@v1"]
    assert path.read_bytes() == before


def test_capture_is_immutable_and_does_not_alias_later_policy_or_ledger(tmp_path):
    boundary, seal, path, _ = _source_capture(tmp_path)
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        save_decision_capture(path, seal, boundary)
    boundary.policy.updates = 7
    boundary.ledger.record_task_start("PIPE3_stream_processing", 0)
    assert path.read_bytes() == before
    assert load_decision_capture(path, ledger_events=boundary.ledger.events) == _features()["peer-b@v1"]


@pytest.mark.parametrize("mutation", [
    lambda r: r["sidecar"]["captured_features"][r["selected_key"]].__setitem__(0, 0.25),
    lambda r: r["attestation"].__setitem__("policy_input_digest", "0" * 64),
    lambda r: r["sidecar"]["candidates"].reverse(),
    lambda r: r["feedback_offer"]["candidate_keys"].reverse(),
    lambda r: r["sidecar"]["captured_features"].pop(r["selected_key"]),
    lambda r: r["sidecar"]["captured_features"].__setitem__(r["selected_key"], []),
])
def test_tampered_selection_inputs_fail_closed(tmp_path, mutation):
    boundary, _seal, path, _ = _source_capture(tmp_path)
    _write_tamper(path, mutation)
    with pytest.raises(ValueError):
        load_decision_capture(path, ledger_events=boundary.ledger.events)


def test_external_native_prefix_mismatch_fails(tmp_path):
    boundary, _seal, path, _ = _source_capture(tmp_path)
    wrong = [dict(boundary.ledger.events[0], record_hash="0" * 64)]
    with pytest.raises(ValueError, match="independent native ledger"):
        load_decision_capture(path, ledger_events=wrong)


def test_target_capture_binds_role_read_and_overlay(tmp_path):
    boundary = Pipe3SelectionBoundary(ContextualTrustPolicy(), registry())
    role_offer, feedback_offer = _source(boundary)
    common = dict(
        assignment_id="as1", native_selection_id="s1", selector_id="peer-a",
        rng=np.random.default_rng(7), state_version="state", encoder_version="encoder",
        feature_schema="pipe3", policy_version="contextual-v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=1.0,
        decision_index=1, captured_features={"peer-b@v1": (1.0, 0.0), "peer-c@v1": (0.0, 1.0)},
    )
    plan, overlay = preview_role_evidence_selection_with_public_judgment(
        boundary, role_offer=role_offer, feedback_offer=feedback_offer,
        base_scores=(0.0, 0.0), read_cut=1, **common,
    )
    seal = commit_role_evidence_selection(
        boundary, plan=plan, role_offer=role_offer, feedback_offer=feedback_offer,
    )
    path = tmp_path / "target.json"
    save_decision_capture(path, seal, boundary, role_offer=role_offer, overlay=overlay,
                          parent_capture_digest="a" * 64)
    expected = dict(seal.decision_sidecar.captured_features)[seal.policy_selection.chosen.key]
    assert load_decision_capture(path, ledger_events=boundary.ledger.events,
                                 parent_capture_digest="a" * 64) == expected
    _write_tamper(path, lambda r: r["role_read"].__setitem__("attestation_digest", "0" * 64))
    with pytest.raises(ValueError, match="role-evidence read"):
        load_decision_capture(path, ledger_events=boundary.ledger.events,
                              parent_capture_digest="a" * 64)
