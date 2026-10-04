from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_contract import BASELINE_ARM_SPECS, validate_contract  # noqa: E402
from peerrolebench_baseline_root_contract import RootRunnerManifest  # noqa: E402
from peerrolebench_canonical_manifest import (  # noqa: E402
    CANONICAL_MANIFEST_VERSION,
    EXPECTED_ARM_NAMES,
    EXPECTED_CELL_CASES,
    EXPECTED_CHANNEL_IDS,
    ASSIGNMENT_SEMANTICS,
    digest,
    build_runtime_stream_values,
    validate_runtime_binding,
    validate_canonical_manifest,
)


def _root() -> dict:
    result = RootRunnerManifest(
        root_id="PIPE3_stream_processing",
        root_commit="d" * 40,
        source_digest="a" * 64,
        generator_digest="b" * 64,
        scorer_digest="c" * 64,
        schedule_digest="d" * 64,
        rng_schedule_digest="e" * 64,
        registry_digest="f" * 64,
        seed_split=(0,),
        arm_names=EXPECTED_ARM_NAMES,
        rng_algorithm="numpy-pcg64",
        visibility_rule="canonical_schedule_prefix_v1",
        max_episode_attempts=4,
        max_api_calls=0,
        max_wall_seconds=60.0,
    ).validate()
    result.update({
        "task_id": "PIPE3_stream_processing",
        "structural_signature": "pipe3-root-v1",
        "authority_kind": "teambench-derived-pinned",
        "split": [0],
        "material_manifest_digest": "1" * 64,
        "task_contract_digest": "2" * 64,
        "adapter_digest": "3" * 64,
        "sandbox_digest": "4" * 64,
        "worker_limits_digest": "5" * 64,
    })
    return result


def _arm_specs() -> tuple[list[dict], dict[str, str]]:
    rows = []
    digests = {}
    for spec in BASELINE_ARM_SPECS:
        row = {
            **spec.__dict__,
            "implementation_digest": digest({"implementation": spec.name, "version": "fixture-v1"}),
            "policy_factory": f"fixture.{spec.name}.Factory",
            "policy_version": "fixture-v1",
            "temperature": 1.0,
            "exploration": 0.1,
            "namespace_digest": digest({"namespace": spec.name}),
        }
        row["spec_digest"] = digest(row)
        rows.append(row)
        digests[spec.name] = row["implementation_digest"]
    return rows, digests


def _channels() -> tuple[list[dict], dict[str, str]]:
    rows = []
    digests = {}
    for channel in EXPECTED_CHANNEL_IDS:
        row = {
            "channel_id": channel,
            "mapping_version": f"{channel}-mapping-v1",
            "implementation_digest": digest({"implementation": channel, "version": "fixture-v1"}),
            "mapping_digest": digest({"mapping": channel, "version": "fixture-v1"}),
        }
        row["channel_digest"] = digest(row)
        rows.append(row)
        digests[channel] = row["implementation_digest"]
    return rows, digests


def _stream() -> tuple[dict, dict[str, str]]:
    values = {
        "ordered_candidate_menu": ["agent-a@v1", "agent-b@v1"],
        "candidate_registry": {"agent-a@v1": "a" * 64, "agent-b@v1": "b" * 64},
        "public_phi": {"schema": "phi-v1", "fields": ["task", "artifact"]},
        "offer_stream": [{"offer_id": "offer-0", "arrival_index": 0}],
        "read_cut_decision": {"read_cut": 0, "decision_index": 1},
        "arrival_schedule": [{"feedback_id": "j0", "arrival_index": 1}],
        "rng_seed_schedule": {"algorithm": "numpy-pcg64", "seeds": [0]},
        "propensity": {"rule": "uniform", "value": 0.5},
        "state_schema": {"version": "state-v1", "bytes_cap": 4096},
        "state_init": {"all_arms": "empty"},
    }
    return values, {key: digest(value) for key, value in values.items()}


def _cells() -> list[dict]:
    rows = []
    for channel in EXPECTED_CHANNEL_IDS:
        for case in EXPECTED_CELL_CASES:
            row = {
                "cell_id": f"{channel}:{case}",
                "channel_id": channel,
                "case": case,
                "expected_disposition": {
                    "positive": "eligible_update",
                    "unknown": "unknown_no_update",
                    "late": "preflight_rejection",
                    "duplicate": "preflight_rejection",
                    "mutation": "preflight_rejection",
                }[case],
                "independent_unit": "episode",
                "episode_count": 1,
                "seed_split": [0],
                "expected_runner_started": case == "positive",
                "expected_updates": 1 if case == "positive" else 0,
            }
            row["cell_digest"] = digest(row)
            rows.append(row)
    return rows


def _manifest() -> dict:
    arm_specs, arm_digests = _arm_specs()
    channels, channel_digests = _channels()
    stream, stream_digests = _stream()
    result = {
        "manifest_version": CANONICAL_MANIFEST_VERSION,
        "root": _root(),
        "contract": validate_contract(),
        "arm_specs": arm_specs,
        "arm_implementation_digests": arm_digests,
        "channels": channels,
        "channel_implementation_digests": channel_digests,
        "stream": stream,
        "stream_digests": stream_digests,
        "cells": _cells(),
        "execution": {
            "unknown_rule": "unknown_no_update_with_reason",
            "selected_only": True,
            "cost_mode": "offline_unmeasured",
            "cost_schema_digest": digest({"cost_fields": list(validate_contract()["cost_fields"])}),
            "history_schema_digest": digest({"history": "state-v1"}),
            "assignment_semantics": ASSIGNMENT_SEMANTICS,
            "negative_cell_contract_digest": digest({"expected_dispositions": {
                "positive": "eligible_update",
                "unknown": "unknown_no_update",
                "late": "preflight_rejection",
                "duplicate": "preflight_rejection",
                "mutation": "preflight_rejection",
            }}),
            "denominator_preservation": True,
        },
        "analysis_plan_digest": digest({"plan": "registered-before-run", "version": "v1"}),
        "closest_published": {
            "status": "blocked_required",
            "placeholder": True,
            "reason": "faithful public adapter and independent receipt are not qualified",
        },
        "status": "engineering_matrix",
    }
    result["manifest_digest"] = digest(result)
    return result


def test_runtime_stream_builder_projects_public_runner_inputs_only():
    sys.path.insert(0, str(ROOT / "tests"))
    from test_peerrolebench_policy_matrix_runner import _registry  # noqa: E402
    from peerrolebench_policy_matrix_runner_v1 import fixture_case  # noqa: E402

    offers, schedule, _ = fixture_case("recipient_only")
    stream = build_runtime_stream_values(offers, schedule, _registry())
    assert set(stream) == {
        "ordered_candidate_menu", "candidate_registry", "public_phi",
        "offer_stream", "read_cut_decision", "arrival_schedule",
        "rng_seed_schedule", "propensity", "state_schema", "state_init",
    }
    assert stream["candidate_registry"] == [entry.payload() for entry in _registry()]
    assert any(row["public_rows"] for row in stream["offer_stream"])
    assert "future_outcome" not in stream
    assert all("scorer" not in str(value).lower() for value in stream.values())


def test_valid_engineering_manifest_is_accepted():
    manifest = _manifest()
    result = validate_canonical_manifest(manifest)
    assert result["valid"] is True
    assert result["root_manifest_digest"] == manifest["root"]["manifest_digest"]


def test_missing_channel_is_rejected():
    manifest = _manifest()
    del manifest["channels"][1]
    manifest["manifest_digest"] = digest({key: value for key, value in manifest.items() if key != "manifest_digest"})
    with pytest.raises(ValueError, match="three channel adapters"):
        validate_canonical_manifest(manifest)


def test_arm_implementation_mutation_is_rejected_before_runner():
    manifest = _manifest()
    manifest["arm_specs"][0]["implementation_digest"] = "1" * 64
    with pytest.raises(ValueError, match="spec_digest mismatch"):
        validate_canonical_manifest(manifest)


def test_phi_or_stream_digest_mutation_is_rejected():
    manifest = _manifest()
    manifest["stream"]["public_phi"]["fields"].append("future_outcome")
    with pytest.raises(ValueError, match="stream_digests.public_phi mismatch"):
        validate_canonical_manifest(manifest)


def test_missing_closest_published_placeholder_is_rejected():
    manifest = _manifest()
    del manifest["closest_published"]
    with pytest.raises(ValueError, match="missing fields"):
        validate_canonical_manifest(manifest)


def test_live_status_with_blocked_closest_published_is_rejected():
    manifest = _manifest()
    manifest["status"] = "live"
    manifest["manifest_digest"] = digest({key: value for key, value in manifest.items() if key != "manifest_digest"})
    with pytest.raises(ValueError, match="live/baseline_frozen"):
        validate_canonical_manifest(manifest)


def test_cell_expected_update_mutation_is_rejected():
    manifest = _manifest()
    manifest["cells"][0]["expected_disposition"] = "ignored"
    with pytest.raises(ValueError, match="expected_disposition mismatch"):
        validate_canonical_manifest(manifest)


def test_bad_envelope_digest_is_rejected():
    manifest = _manifest()
    manifest["manifest_digest"] = "0" * 64
    with pytest.raises(ValueError, match="manifest_digest mismatch"):
        validate_canonical_manifest(manifest)


def test_root_metadata_is_required_and_digest_validated():
    manifest = _manifest()
    del manifest["root"]["task_id"]
    with pytest.raises(ValueError, match="root missing fields"):
        validate_canonical_manifest(manifest)
    manifest = _manifest()
    manifest["root"]["adapter_digest"] = "bad"
    with pytest.raises(ValueError, match="root.adapter_digest"):
        validate_canonical_manifest(manifest)


def test_policy_fields_and_execution_extension_are_required():
    manifest = _manifest()
    del manifest["arm_specs"][0]["policy_factory"]
    with pytest.raises(ValueError, match="policy_factory"):
        validate_canonical_manifest(manifest)
    manifest = _manifest()
    manifest["arm_specs"][0]["exploration"] = 1.0
    with pytest.raises(ValueError, match="exploration"):
        validate_canonical_manifest(manifest)
    manifest = _manifest()
    manifest["execution"]["selected_only"] = False
    with pytest.raises(ValueError, match="selected_only"):
        validate_canonical_manifest(manifest)


def test_execution_cost_and_negative_cell_digests_are_bound():
    manifest = _manifest()
    manifest["execution"]["cost_schema_digest"] = "0" * 64
    with pytest.raises(ValueError, match="cost_schema_digest"):
        validate_canonical_manifest(manifest)
    manifest = _manifest()
    manifest["execution"]["negative_cell_contract_digest"] = "0" * 64
    with pytest.raises(ValueError, match="negative_cell_contract_digest"):
        validate_canonical_manifest(manifest)


def test_cell_runner_expectations_follow_positive_case():
    manifest = _manifest()
    manifest["cells"][0]["expected_runner_started"] = False
    with pytest.raises(ValueError, match="expected_runner_started"):
        validate_canonical_manifest(manifest)
    manifest = _manifest()
    manifest["cells"][1]["expected_updates"] = 1
    with pytest.raises(ValueError, match="expected_updates"):
        validate_canonical_manifest(manifest)


def test_runtime_binding_accepts_exact_sealed_values():
    manifest = _manifest()
    result = validate_runtime_binding(
        manifest,
        root_commit=manifest["root"]["root_commit"],
        registry_digest=manifest["root"]["registry_digest"],
        schedule_digest=manifest["root"]["schedule_digest"],
        rng_schedule_digest=manifest["root"]["rng_schedule_digest"],
        stream_values=manifest["stream"],
    )
    assert result["bound"] is True


def test_runtime_binding_rejects_root_or_stream_mutation():
    manifest = _manifest()
    with pytest.raises(ValueError, match="runtime registry_digest"):
        validate_runtime_binding(
            manifest,
            root_commit=manifest["root"]["root_commit"],
            registry_digest="0" * 64,
            schedule_digest=manifest["root"]["schedule_digest"],
            rng_schedule_digest=manifest["root"]["rng_schedule_digest"],
            stream_values=manifest["stream"],
        )
    manifest = _manifest()
    values = dict(manifest["stream"])
    values["public_phi"] = {"future_outcome": True}
    with pytest.raises(ValueError, match="runtime stream digest mismatch: public_phi"):
        validate_runtime_binding(
            manifest,
            root_commit=manifest["root"]["root_commit"],
            registry_digest=manifest["root"]["registry_digest"],
            schedule_digest=manifest["root"]["schedule_digest"],
            rng_schedule_digest=manifest["root"]["rng_schedule_digest"],
            stream_values=values,
        )
