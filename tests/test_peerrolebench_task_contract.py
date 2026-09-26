"""Engineering contract checks; no candidate execution or scientific results."""
from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import peerrolebench_task_contract as task_contract  # noqa: E402
from peerrolebench_task_contract import (  # noqa: E402
    DIST1_DELIVERY_PATHS, attach_selected_delivery, classify_junit,
    evaluation_record, export_task_materials, load_generated_task,
)


@pytest.mark.parametrize("seed", [0, 1])
def test_cr2_uses_current_generated_text_and_module(seed):
    generated = load_generated_task("CR2_style_enforce", seed)
    contract = export_task_materials(generated)
    producer = contract["agent_payloads"]["producer"]
    assert producer["spec_md"] == generated.spec_md
    assert producer["brief_md"] == generated.brief_md
    assert producer["spec_md"].strip() and producer["brief_md"].strip()
    module = producer["writable_paths"][0]
    assert module in producer["spec_md"] and module in producer["brief_md"]
    assert set(producer["source_files"]) == {module}
    assert contract["manifest"]["dependency"] == "diagnostic_only_no_downstream_task"


def test_dist1_delivery_completes_recipient_material_without_mutating_template():
    generated = load_generated_task("DIST1_queue_race", 1)
    contract = export_task_materials(generated)
    producer, recipient = (contract["agent_payloads"][role] for role in ("producer", "recipient"))
    assert producer["writable_paths"] == list(DIST1_DELIVERY_PATHS)
    assert recipient["writable_paths"] == ["mqueue/consumer.py"]
    assert not recipient["ready_for_dispatch"]
    assert not (set(DIST1_DELIVERY_PATHS) & set(recipient["source_files"]))
    delivery = {path: generated.workspace_files[path] for path in DIST1_DELIVERY_PATHS}
    attached = attach_selected_delivery(recipient, delivery)
    assert attached["ready_for_dispatch"]
    assert attached["source_files"]["mqueue/queue.py"] == delivery["mqueue/queue.py"]
    assert attached["delivery_sha256"]
    assert not recipient["ready_for_dispatch"]
    assert not contract["manifest"]["process_isolation_verified"]


def test_private_material_never_enters_agent_payload():
    generated = load_generated_task("DIST1_queue_race", 0)
    private = "PRIVATE_EVALUATION_SENTINEL"
    poisoned_workspace = dict(generated.workspace_files)
    for path in ("reports/expected.json", "expected.json", "grade.sh", "tests/hidden.py",
                 "mqueue/expected.json", "mqueue/../../reports/score.json"):
        poisoned_workspace[path] = private
    generated = replace(generated, expected={"secret": private}, workspace_files=poisoned_workspace)
    contract = export_task_materials(generated)
    visible = json.dumps(contract["agent_payloads"])
    assert private not in visible
    for payload in contract["agent_payloads"].values():
        assert set(payload["source_files"]) <= {
            *DIST1_DELIVERY_PATHS, "mqueue/consumer.py", "mqueue/config.py", "mqueue/__init__.py",
        }
    assert "reports/expected.json" in contract["manifest"]["excluded_workspace_paths"]
    recipient = contract["agent_payloads"]["recipient"]
    delivery = {path: generated.workspace_files[path] for path in DIST1_DELIVERY_PATHS}
    with pytest.raises(ValueError, match="exactly"):
        attach_selected_delivery(recipient, {**delivery, "reports/expected.json": private})


def test_dist1_seed_repetition_is_detected_without_claiming_independence():
    manifests = [export_task_materials(load_generated_task("DIST1_queue_race", seed))["manifest"]
                 for seed in (0, 1, 8)]
    keys = [item["duplicate_metadata"]["instance_content_sha256"] for item in manifests]
    assert keys[0] == keys[2]
    assert keys[0] != keys[1]
    assert all(not item["duplicate_metadata"]["nonmatching_hash_proves_independence"]
               for item in manifests)


def test_missing_text_or_ambiguous_cr2_source_rejected():
    generated = load_generated_task("CR2_style_enforce", 0)
    with pytest.raises(ValueError, match="nonempty"):
        export_task_materials(replace(generated, spec_md=""))
    with pytest.raises(ValueError, match="exactly one"):
        export_task_materials(replace(generated, workspace_files={**generated.workspace_files, "extra.py": ""}))


@pytest.mark.parametrize("xml,classification,label,counts", [
    ('<testsuite tests="1"><testcase name="ok"/></testsuite>', "passed", 1, (1, 1, 0, 0, 0)),
    ('<testsuite tests="1"><testcase name="bad"><failure/></testcase></testsuite>', "failed", 0, (1, 0, 1, 0, 0)),
    ('<testsuite tests="1"><testcase><skipped/></testcase></testsuite>', "skipped", None, (1, 0, 0, 1, 0)),
    ('<testsuite tests="2"><testcase/><testcase><skipped/></testcase></testsuite>', "skipped", None, (2, 1, 0, 1, 0)),
    ('<testsuite tests="1"><testcase><error/></testcase></testsuite>', "error", None, (1, 0, 0, 0, 1)),
    ('<testsuite tests="0"/>', "zero-tests", None, (0, 0, 0, 0, 0)),
    ('<testsuite>', "malformed", None, (0, 0, 0, 0, 0)),
    ('<unrelated/>', "malformed", None, (0, 0, 0, 0, 0)),
])
def test_junit_classifies_observed_testcases(xml, classification, label, counts):
    result = classify_junit(xml)
    assert result["classification"] == classification
    assert result["label"] == label
    assert tuple(result["counts"].values()) == counts
    if classification not in {"passed", "failed"}:
        assert result["status"] == "UNKNOWN"


def test_nested_namespaced_suites_do_not_double_count():
    xml = ('<testsuites xmlns="urn:junit" tests="2"><testsuite tests="2">'
           '<testsuite tests="1"><testcase name="a"/></testsuite>'
           '<testsuite tests="1"><testcase name="b"/></testsuite>'
           '</testsuite></testsuites>')
    result = classify_junit(xml)
    assert result["classification"] == "passed"
    assert result["counts"]["total"] == 2


def test_all_skipped_native_success_is_preserved_but_not_a_positive_label():
    native = {"pass": True, "secondary": {"partial_score": 1.0}}
    record = evaluation_record(native, '<testsuite tests="1"><testcase><skipped/></testcase></testsuite>')
    assert record["native_score"] == native
    assert record["test_evidence"]["all_skipped"]
    assert record["test_evidence"]["label"] is None
    record["native_score"]["secondary"]["partial_score"] = 0
    assert native["secondary"]["partial_score"] == 1.0


def test_skipped_case_is_not_a_negative_label_but_actual_failure_remains_negative():
    result = classify_junit('<testsuite tests="2"><testcase><skipped/></testcase>'
                            '<testcase><failure/></testcase></testsuite>', process_exit_code=1)
    assert result["classification"] == "failed"
    assert result["counts"]["failed"] == result["counts"]["skipped"] == 1
    assert not result["coverage_complete"]


@pytest.mark.parametrize("run_status,classification", [
    ({"timed_out": True}, "timeout"),
    ({"infrastructure_error": "Missing pytest-timeout"}, "error"),
    ({"process_exit_code": 3}, "error"),
    ({"process_exit_code": 1}, "error"),
])
def test_process_failure_overrides_success_xml(run_status, classification):
    result = classify_junit('<testsuite tests="1"><testcase/></testsuite>', **run_status)
    assert result["classification"] == classification
    assert result["status"] == "UNKNOWN" and result["label"] is None
    assert result["counts"]["passed"] == 1


def test_collection_error_and_missing_case_evidence_cannot_pass():
    assert classify_junit('<testsuite tests="0" errors="1"/>')["classification"] == "error"
    assert classify_junit('<testsuite tests="2"/>')["classification"] == "malformed"
    assert classify_junit('<testsuite tests="1" failures="1"><testcase/></testsuite>')["classification"] == "malformed"
    assert classify_junit(None, timed_out=True)["classification"] == "timeout"


@pytest.mark.parametrize("action", ["use", "repair", "independent_redo"])
def test_consumer_action_permissions_and_starting_materials(action):
    generated = load_generated_task("DIST1_queue_race", 1)
    materials = export_task_materials(generated)
    original = json.loads(json.dumps(materials))
    delivery = {path: f"# delivered {path}\n" for path in DIST1_DELIVERY_PATHS}
    original_delivery = dict(delivery)
    payload = task_contract.prepare_consumer_action(materials, delivery, action)
    expected_writable = {"mqueue/consumer.py"}
    if action != "use":
        expected_writable.update(DIST1_DELIVERY_PATHS)
    assert set(payload["writable_paths"]) == expected_writable
    for path in DIST1_DELIVERY_PATHS:
        expected_source = generated.workspace_files[path] if action == "independent_redo" else delivery[path]
        assert payload["source_files"][path] == expected_source
    assert payload["consumer_action"] == action
    assert payload["prior_delivery_may_have_been_seen"]
    assert not payload["independent_redo_is_blinded_control"]
    assert payload["action_initialization"] == (
        "original_public_template" if action == "independent_redo" else "selected_delivery_copy"
    )
    assert payload["delivery_sha256"] == attach_selected_delivery(
        materials["agent_payloads"]["recipient"], delivery
    )["delivery_sha256"]
    payload["source_files"]["mqueue/consumer.py"] = "changed consumer copy"
    payload["source_files"]["mqueue/queue.py"] = "changed queue copy"
    assert materials == original
    assert delivery == original_delivery


@pytest.mark.parametrize("action", ["use", "repair", "independent_redo"])
def test_consumer_result_validates_action_writes_and_readonly_support(action):
    generated = load_generated_task("DIST1_queue_race", 0)
    materials = export_task_materials(generated)
    delivery = {path: f"# selected {path}\n" for path in DIST1_DELIVERY_PATHS}
    payload = task_contract.prepare_consumer_action(materials, delivery, action)
    output = dict(payload["source_files"])
    output["mqueue/consumer.py"] = "# consumer integration\n"
    record = task_contract.validate_consumer_result(payload, output)
    assert record["changed_paths"] == ["mqueue/consumer.py"]
    assert record["output_source_sha256"] != record["input_source_sha256"]
    assert record["delivery_sha256"] == payload["delivery_sha256"]
    output["mqueue/queue.py"] = "# repaired queue\n"
    if action == "use":
        with pytest.raises(ValueError, match="read-only"):
            task_contract.validate_consumer_result(payload, output)
    else:
        assert "mqueue/queue.py" in task_contract.validate_consumer_result(payload, output)["changed_paths"]
    output = dict(payload["source_files"])
    output["mqueue/config.py"] = "CAPACITY = 1000000000\n"
    with pytest.raises(ValueError, match="read-only"):
        task_contract.validate_consumer_result(payload, output)
    output = {**payload["source_files"], "reports/expected.json": "secret"}
    with pytest.raises(ValueError, match="exactly"):
        task_contract.validate_consumer_result(payload, output)


def test_action_rights_are_not_chosen_by_experiment_condition():
    generated = load_generated_task("DIST1_queue_race", 0)
    delivery = {path: generated.workspace_files[path] for path in DIST1_DELIVERY_PATHS}
    permissions = []
    for condition in ("no_update", "terminal_only", "situated_judgment", "contextual_bandit"):
        materials = export_task_materials(generated)
        materials["manifest"]["experiment_condition"] = condition
        permissions.append(task_contract.prepare_consumer_action(materials, delivery, "repair")["writable_paths"])
    assert all(paths == permissions[0] for paths in permissions)


def test_consumer_action_rejects_unknown_action_and_extra_delivery_path():
    generated = load_generated_task("DIST1_queue_race", 0)
    materials = export_task_materials(generated)
    delivery = {path: generated.workspace_files[path] for path in DIST1_DELIVERY_PATHS}
    with pytest.raises(ValueError, match="action"):
        task_contract.prepare_consumer_action(materials, delivery, "pretend_use")
    with pytest.raises(ValueError, match="exactly"):
        task_contract.prepare_consumer_action(materials, {**delivery, "../private.py": "secret"}, "repair")


@pytest.mark.parametrize("task_id", ["DIST1_queue_race", "CR2_style_enforce"])
def test_all_seeds_share_pinned_structural_root(task_id):
    manifests = [export_task_materials(load_generated_task(task_id, seed))["manifest"] for seed in (0, 1, 8)]
    assert len({item["structural_root"] for item in manifests}) == 1
    assert len({item["template_id"] for item in manifests}) == 1
    for item in manifests:
        assert item["source_commit"] == "d185aef1916fd86a9ba554d581fd256319a973af"
        assert item["source_commit"] in item["template_id"]
        assert item["duplicate_metadata"]["split_group"] == item["structural_root"]
        assert not item["variant"]["independent_task_root"]
    if task_id == "DIST1_queue_race":
        assert manifests[0]["variant"]["variant_id"] == manifests[2]["variant"]["variant_id"]
        assert manifests[0]["variant"]["variant_id"] != manifests[1]["variant"]["variant_id"]


def test_required_junit_inventory_missing_case_is_unknown_even_when_present_case_passes():
    xml = '<testsuite tests="1"><testcase classname="consumer" name="success"/></testsuite>'
    result = classify_junit(xml, required_test_ids=["consumer::success", "consumer::failure_retry"])
    assert result["classification"] == "missing-tests"
    assert result["status"] == "UNKNOWN" and result["label"] is None
    assert result["missing_test_ids"] == ["consumer::failure_retry"]
    assert result["observed_coverage_complete"]
    assert not result["coverage_complete"]


def test_no_inventory_cannot_claim_complete_coverage():
    xml = '<testsuite tests="1"><testcase classname="consumer" name="success"/></testsuite>'
    result = classify_junit(xml)
    assert result["classification"] == "passed"
    assert result["observed_coverage_complete"]
    assert not result["coverage_complete"]
    assert not result["required_inventory_provided"]


def test_required_junit_inventory_matches_classname_and_name_not_bare_name():
    xml = ('<testsuite tests="2"><testcase classname="queue" name="success"/>'
           '<testcase classname="consumer" name="success"/></testsuite>')
    result = classify_junit(xml, required_test_ids=["consumer::success", "queue::success"])
    assert result["status"] == "PASS" and result["label"] == 1
    assert result["coverage_complete"]
    assert result["missing_test_ids"] == []
    assert {case["test_id"] for case in result["cases"]} == {"queue::success", "consumer::success"}


def test_duplicate_required_testcase_identity_is_unknown():
    xml = ('<testsuite tests="2"><testcase classname="consumer" name="success"/>'
           '<testcase classname="consumer" name="success"/></testsuite>')
    result = classify_junit(xml, required_test_ids=["consumer::success"])
    assert result["classification"] == "duplicate-tests"
    assert result["status"] == "UNKNOWN" and not result["coverage_complete"]
    assert result["duplicate_test_ids"] == ["consumer::success"]


def test_missing_required_case_does_not_hide_present_failures_but_does_not_label_complete_task():
    xml = '<testsuite tests="1"><testcase classname="consumer" name="bad"><failure/></testcase></testsuite>'
    result = classify_junit(xml, required_test_ids=["consumer::bad", "consumer::other"], process_exit_code=1)
    assert result["status"] == "UNKNOWN" and result["label"] is None
    assert result["counts"]["failed"] == 1
    assert result["cases"][0]["status"] == "failed"


def test_skipped_required_case_does_not_establish_coverage():
    xml = '<testsuite tests="1"><testcase classname="consumer" name="retry"><skipped/></testcase></testsuite>'
    result = classify_junit(xml, required_test_ids=["consumer::retry"])
    assert result["classification"] == "skipped" and result["label"] is None
    assert not result["coverage_complete"]


@pytest.mark.parametrize("inventory", [[], "consumer::ok", ["consumer::ok", "consumer::ok"], ["ok"], ["consumer::"]])
def test_invalid_required_inventory_is_rejected(inventory):
    with pytest.raises(ValueError, match="required_test_ids"):
        classify_junit('<testsuite tests="1"><testcase name="ok"/></testsuite>', required_test_ids=inventory)


def test_evaluation_record_preserves_native_score_when_inventory_is_incomplete():
    record = evaluation_record({"pass": True}, '<testsuite tests="1"><testcase classname="queue" name="ok"/></testsuite>',
                               required_test_ids=["queue::ok", "consumer::ok"])
    assert record["native_score"] == {"pass": True}
    assert record["test_evidence"]["status"] == "UNKNOWN"
