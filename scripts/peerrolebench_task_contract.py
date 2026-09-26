"""Material and grader-evidence contracts for the TeamBench development slice.

This module never executes candidate code or stages a filesystem sandbox.  It
reuses TeamBench's generators, keeps private evaluation data out of the agent
payloads, and treats missing test coverage separately from incorrect behavior.
These contracts do not qualify a benchmark or demonstrate method efficacy.
"""
from __future__ import annotations

import copy
from collections import Counter
import hashlib
import importlib
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence
import xml.etree.ElementTree as ET


TEAMBENCH = Path(__file__).resolve().parents[1] / "references/benchmark_sources/TeamBench"
TEAMBENCH_SOURCE_COMMIT = "d185aef1916fd86a9ba554d581fd256319a973af"
SUPPORTED_TASKS = {"CR2_style_enforce", "DIST1_queue_race"}
TASK_GENERATORS = {"CR2_style_enforce": "generators/gen_cr2_style_enforce.py",
                   "DIST1_queue_race": "generators/gen_dist1_queue_race.py"}
DIST1_DELIVERY_PATHS = ("mqueue/queue.py", "mqueue/priority.py")
DIST1_SUPPORT_PATHS = ("mqueue/__init__.py", "mqueue/config.py")
CONSUMER_ACTIONS = {"use", "repair", "independent_redo"}


def _digest_files(files: Mapping[str, str | bytes]) -> str:
    digest = hashlib.sha256()
    for path, content in sorted(files.items()):
        for part in (path.encode(), content.encode() if isinstance(content, str) else content):
            digest.update(len(part).to_bytes(8, "big"))
            digest.update(part)
    return digest.hexdigest()


def load_generated_task(task_id: str, seed: int) -> Any:
    """Generate one trusted task in memory; do not call setup_run/write_to_disk."""
    if task_id not in SUPPORTED_TASKS:
        raise ValueError(f"Task has no reviewed material contract: {task_id}")
    root = str(TEAMBENCH)
    if root not in sys.path:
        sys.path.insert(0, root)
    registry = importlib.import_module("generators.registry")
    if Path(registry.__file__).resolve() != TEAMBENCH / "generators/registry.py":
        raise RuntimeError("Another package shadows the reviewed TeamBench generators")
    return registry.get_generator(task_id).generate(seed=seed)


def export_task_materials(generated: Any) -> dict[str, Any]:
    """Return agent payload templates plus an operator-only audit manifest.

    The generated spec/brief, not the static template paths, define the current
    instance.  This adapter declares both texts public to both agents; that is
    an explicit change from native Planner/Executor information separation.
    Tests are all withheld here until a public/hidden test split is qualified.
    Only ``agent_payloads`` may be sent to agents; the manifest is for auditing.
    """
    task_id = generated.task_id
    if task_id not in SUPPORTED_TASKS:
        raise ValueError(f"Task has no reviewed material contract: {task_id}")
    if not generated.spec_md.strip() or not generated.brief_md.strip():
        raise ValueError("The current generated instance must have nonempty spec and brief")
    workspace = generated.workspace_files
    if task_id == "DIST1_queue_race":
        delivery_paths = DIST1_DELIVERY_PATHS
        recipient_paths = ("mqueue/consumer.py",)
        support_paths = DIST1_SUPPORT_PATHS
        dependency = "queue_and_priority_delivery_to_consumer_integration"
    else:
        # CR2 generates exactly one top-level module. Never consult expected.json
        # to pick the public source file, and reject ambiguity rather than guess.
        modules = tuple(path for path in workspace if "/" not in path and path.endswith(".py"))
        if len(modules) != 1:
            raise ValueError("CR2 must expose exactly one top-level source module")
        delivery_paths = modules
        recipient_paths = support_paths = ()
        dependency = "diagnostic_only_no_downstream_task"
    public_paths = (*delivery_paths, *recipient_paths, *support_paths)
    for path in public_paths:
        if path not in workspace or not isinstance(workspace[path], str):
            raise ValueError(f"Required public source is missing or non-text: {path}")

    task_text = {"task_id": task_id, "seed": generated.seed,
                 "spec_md": generated.spec_md, "brief_md": generated.brief_md}
    responsibility = {
        "version": "source-responsibility-v1",
        "producer_owned_paths": list(delivery_paths),
        "recipient_owned_paths": list(recipient_paths),
        "read_only_support_paths": list(support_paths),
        "judgment_subject": "selected producer's delivered files, not unfinished recipient-owned work",
        "recipient_integration_rule": (
            "Completing recipient-owned files is the recipient's assigned work under every action. "
            "It is not by itself evidence of producer failure or upstream repair."
        ),
        "permission_rule": (
            "writable_paths describes the current actor's permissions. Repair permissions do not "
            "transfer the original producer/recipient responsibility."
        ),
    }
    producer = {
        **task_text, "role": "producer", "ready_for_dispatch": True,
        "source_files": {path: workspace[path] for path in public_paths},
        "writable_paths": list(delivery_paths), "required_delivery_paths": [],
        "responsibility_contract": copy.deepcopy(responsibility),
    }
    recipient = {
        **task_text, "role": "recipient", "ready_for_dispatch": False,
        "source_files": {path: workspace[path] for path in (*recipient_paths, *support_paths)},
        "writable_paths": list(recipient_paths),
        "required_delivery_paths": list(delivery_paths),
        "responsibility_contract": copy.deepcopy(responsibility),
    }
    instance_files = {f"workspace/{path}": value for path, value in workspace.items()}
    instance_files.update({"spec.md": generated.spec_md, "brief.md": generated.brief_md})
    template_id = f"TeamBench@{TEAMBENCH_SOURCE_COMMIT}/{TASK_GENERATORS[task_id]}"
    structural_root = f"TeamBench@{TEAMBENCH_SOURCE_COMMIT}/{task_id}"
    variant_id = (f"domain-{generated.seed % 8}" if task_id == "DIST1_queue_race"
                  else f"seed-{generated.seed}")
    return {
        "agent_payloads": {"producer": producer, "recipient": recipient},
        "manifest": {
            "schema_version": "peerrolebench-task-materials-v3",
            "task_id": task_id, "seed": generated.seed,
            "source_commit": TEAMBENCH_SOURCE_COMMIT,
            "source_pin_status": "declared_reference; runner must verify checkout before execution",
            "template_id": template_id,
            "structural_root": structural_root,
            "variant": {"seed": generated.seed, "variant_id": variant_id,
                        "independent_task_root": False},
            "dependency": dependency,
            "task_text_source": "GeneratedTask.spec_md/brief_md",
            "spec_visibility": "full_generated_spec_and_brief_to_both_agents",
            "public_source_paths": sorted(public_paths),
            "excluded_workspace_paths": sorted(set(workspace) - set(public_paths)),
            "evaluator_data_in_agent_payload": False,
            "process_isolation_verified": False,
            "benchmark_qualified": False,
            "duplicate_metadata": {
                "task_family_id": task_id,
                "split_group": structural_root,
                "instance_content_sha256": _digest_files(instance_files),
                "meaning": "Identical task texts and workspace bytes, excluding metadata/expected",
                "nonmatching_hash_proves_independence": False,
            },
        },
    }


def attach_selected_delivery(recipient_payload: Mapping[str, Any],
                             delivery: Mapping[str, str]) -> dict[str, Any]:
    """Attach only producer-owned source; caller must verify selection/lineage.

    This checks material shape, not source safety or selection provenance.
    Source is untrusted text and must only be executed in a qualified sandbox.
    """
    if recipient_payload.get("role") != "recipient" or recipient_payload.get("ready_for_dispatch"):
        raise ValueError("Expected a recipient template awaiting a delivery")
    required = set(recipient_payload["required_delivery_paths"])
    if not required or set(delivery) != required:
        raise ValueError("Delivery must contain exactly the contracted producer source paths")
    if not all(isinstance(value, str) for value in delivery.values()):
        raise ValueError("Delivery source must be text")
    result = copy.deepcopy(dict(recipient_payload))
    result["source_files"].update(delivery)
    result["required_delivery_paths"] = []
    result["ready_for_dispatch"] = True
    result["delivery_sha256"] = _digest_files(delivery)
    return result


def prepare_consumer_action(materials: Mapping[str, Any], delivery: Mapping[str, str],
                            action: str) -> dict[str, Any]:
    """Prepare one consumer-owned copy without changing templates or delivery.

    ``materials`` must be the operator-held original export, not agent-supplied
    data. ``use`` permits consumer integration only. ``repair`` permits changes
    to copied producer files too. ``independent_redo`` starts from the original
    public template, but does not erase prior knowledge of the judged delivery.
    Rights depend on action only, never on the experimental condition. The
    runtime must enforce these declared rights; this is not a sandbox.
    """
    if action not in CONSUMER_ACTIONS:
        raise ValueError(f"Unsupported consumer action: {action}")
    template = materials["agent_payloads"]["recipient"]
    result = attach_selected_delivery(template, delivery)
    delivery_paths = set(template["required_delivery_paths"])
    recipient_paths = set(template["writable_paths"])
    if action == "independent_redo":
        original = materials["agent_payloads"]["producer"]["source_files"]
        if set(original) != set(result["source_files"]) or not all(
            isinstance(value, str) for value in original.values()
        ):
            raise ValueError("Original public template must contain exactly the contracted source paths")
        result["source_files"] = copy.deepcopy(dict(original))
    result["writable_paths"] = sorted(recipient_paths if action == "use"
                                     else recipient_paths | delivery_paths)
    result.update({
        "consumer_action": action,
        "action_initialization": ("original_public_template" if action == "independent_redo"
                                  else "selected_delivery_copy"),
        "input_source_sha256": _digest_files(result["source_files"]),
        "prior_delivery_may_have_been_seen": True,
        "independent_redo_is_blinded_control": False,
    })
    return result


def validate_consumer_result(action_payload: Mapping[str, Any],
                             source_files: Mapping[str, str]) -> dict[str, Any]:
    """Validate a returned full source snapshot against operator-held rights.

    The caller retains the prepared input privately and supplies only the agent
    output files as ``source_files``. This validates returned material; a later
    sandbox must separately prevent forbidden transient writes and reads.
    """
    if action_payload.get("consumer_action") not in CONSUMER_ACTIONS:
        raise ValueError("Expected an operator-prepared consumer action")
    initial = action_payload["source_files"]
    if set(source_files) != set(initial):
        raise ValueError("Consumer result must contain exactly the contracted source paths")
    if not all(isinstance(value, str) for value in source_files.values()):
        raise ValueError("Consumer result source must be text")
    if _digest_files(initial) != action_payload["input_source_sha256"]:
        raise ValueError("Operator-held initial source has changed")
    changed = sorted(path for path in initial if initial[path] != source_files[path])
    if set(changed) - set(action_payload["writable_paths"]):
        raise ValueError("Consumer result changed read-only source files")
    return {
        "consumer_action": action_payload["consumer_action"],
        "source_files": copy.deepcopy(dict(source_files)),
        "input_source_sha256": action_payload["input_source_sha256"],
        "output_source_sha256": _digest_files(source_files),
        "delivery_sha256": action_payload["delivery_sha256"],
        "changed_paths": changed,
        "action_initialization": action_payload["action_initialization"],
        "prior_delivery_may_have_been_seen": True,
        "independent_redo_is_blinded_control": False,
    }


def classify_consumer_changes(materials: Mapping[str, Any],
                              validated_result: Mapping[str, Any]) -> dict[str, Any]:
    """Attribute observed file edits to task ownership, not a declared action.

    This is a descriptive measurement only: changing an upstream file does not
    prove the producer caused a defect, and no change does not prove correctness.
    Keep declared repair separate from the consumer's assigned integration work.
    """
    producer_owned = set(materials["agent_payloads"]["producer"]["writable_paths"])
    consumer_owned = set(materials["agent_payloads"]["recipient"]["writable_paths"])
    if producer_owned & consumer_owned:
        raise ValueError("Ownership must be disjoint for this change classification")
    changed = set(validated_result["changed_paths"])
    if changed - producer_owned - consumer_owned:
        raise ValueError("Observed edit lies outside contracted responsibility paths")
    upstream = sorted(changed & producer_owned)
    integration = sorted(changed & consumer_owned)
    action = validated_result["consumer_action"]
    return {
        "measurement_version": "ownership-change-classification-v1",
        "declared_action": action,
        "producer_owned_paths_changed": upstream,
        "consumer_owned_paths_changed": integration,
        "observed_upstream_revision": bool(upstream),
        "observed_consumer_integration": bool(integration),
        "declared_repair_without_upstream_change": action == "repair" and not upstream,
        "producer_defect_proven": False,
        "producer_correctness_measured": False,
        "marginal_repair_cost_identified": False,
    }


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def classify_junit(xml_text: str | bytes | None, *, process_exit_code: int | None = None,
                   timed_out: bool = False, infrastructure_error: str | None = None,
                   required_test_ids: Sequence[str] | None = None) -> dict[str, Any]:
    """Classify testcase evidence independently of the native aggregate score.

    A skipped test is uncovered, never a failed test. A positive label requires
    at least one actual testcase and complete observed coverage. Error, timeout,
    malformed reports, and zero tests are UNKNOWN. Callers must pass externally
    known infrastructure failures; a generic JUnit <failure> cannot reveal their
    cause. Counts are testcase counts, not sums of nested suite attributes.
    Inventory ids are ``classname::name`` from trusted, predeclared tests; keep
    parameter suffixes verbatim. Missing required cases or duplicate identities
    make the task label UNKNOWN. Without an inventory PASS/FAIL describes only
    observed cases and ``coverage_complete`` is always false.
    """
    required: tuple[str, ...] | None = None
    if required_test_ids is not None:
        if isinstance(required_test_ids, (str, bytes)):
            raise ValueError("required_test_ids must be a nonempty sequence of classname::name ids")
        required = tuple(required_test_ids)
        if not required or not all(
            isinstance(test_id, str) and "::" in test_id and test_id.rsplit("::", 1)[1]
            for test_id in required
        ) or len(set(required)) != len(required):
            raise ValueError("required_test_ids must contain unique, nonempty classname::name ids")
    counts = dict(total=0, passed=0, failed=0, skipped=0, error=0)
    cases: list[dict[str, str]] = []
    issues: list[str] = []
    malformed = False
    suite_errors = False
    try:
        if not xml_text:
            raise ValueError("Missing JUnit XML")
        root = ET.fromstring(xml_text)
        if _tag(root) not in {"testsuite", "testsuites"}:
            raise ValueError("JUnit root must be testsuite or testsuites")
        for case in (node for node in root.iter() if _tag(node) == "testcase"):
            outcomes = {_tag(child) for child in case}
            outcome = next((name for name in ("error", "failure", "skipped") if name in outcomes), "passed")
            status = "failed" if outcome == "failure" else outcome
            counts[status] += 1
            counts["total"] += 1
            name, classname = case.get("name", ""), case.get("classname", "")
            cases.append({"name": name, "classname": classname,
                          "test_id": f"{classname}::{name}", "status": status})
        for suite in (node for node in root.iter() if _tag(node) in {"testsuite", "testsuites"}):
            child_cases = [node for node in suite.iter() if _tag(node) == "testcase"]
            declared = suite.get("tests")
            if declared is not None and int(declared) != len(child_cases):
                raise ValueError("Declared test count differs from actual testcase evidence")
            for attribute, outcome_tag in (("failures", "failure"), ("skipped", "skipped")):
                if attribute in suite.attrib and int(suite.attrib[attribute]) != sum(
                    any(_tag(child) == outcome_tag for child in case) for case in child_cases
                ):
                    raise ValueError(f"Declared {attribute} count differs from testcase evidence")
            if any(_tag(child) == "error" for child in suite):
                suite_errors = True
            declared_errors = int(suite.get("errors", "0"))
            if declared_errors < 0:
                raise ValueError("Declared error count cannot be negative")
            if declared_errors > sum(
                any(_tag(child) == "error" for child in case) for case in child_cases
            ):
                suite_errors = True
    except (ET.ParseError, ValueError, TypeError) as exc:
        malformed = True
        issues.append(str(exc))

    identity_counts = Counter(case["test_id"] for case in cases)
    missing = sorted(set(required or ()) - set(identity_counts))
    duplicates = sorted(test_id for test_id, count in identity_counts.items() if count > 1)
    observed_complete = bool(counts["total"]) and not (
        malformed or counts["error"] or suite_errors or counts["skipped"] or timed_out
        or infrastructure_error or process_exit_code not in (None, 0, 1)
        or (process_exit_code == 1 and not counts["failed"])
    )
    if timed_out:
        classification = "timeout"
        issues.append("Grader process timed out")
    elif infrastructure_error:
        classification = "error"
        issues.append(infrastructure_error)
    elif malformed:
        classification = "malformed"
    elif counts["error"] or suite_errors:
        classification = "error"
    elif process_exit_code not in (None, 0, 1):
        classification = "error"
        issues.append(f"Unexpected grader exit code: {process_exit_code}")
    elif process_exit_code == 1 and not counts["failed"]:
        classification = "error"
        issues.append("Nonzero grader exit without an observed assertion failure")
    elif not counts["total"]:
        classification = "zero-tests"
    elif required is not None and duplicates:
        classification = "duplicate-tests"
        issues.append("Duplicate testcase identities cannot establish unique coverage")
    elif missing:
        classification = "missing-tests"
        issues.append("Missing required testcase evidence")
    elif counts["failed"]:
        classification = "failed"
    elif counts["skipped"]:
        classification = "skipped"
    else:
        classification = "passed"
    status = {"passed": "PASS", "failed": "FAIL"}.get(classification, "UNKNOWN")
    return {
        "classification": classification, "status": status,
        "label": {"PASS": 1, "FAIL": 0}.get(status),
        "counts": counts, "cases": cases,
        "all_skipped": counts["total"] > 0 and counts["skipped"] == counts["total"],
        "required_inventory_provided": required is not None,
        "required_test_ids": list(required) if required is not None else None,
        "missing_test_ids": missing,
        "duplicate_test_ids": duplicates,
        "observed_coverage_complete": observed_complete,
        "coverage_complete": required is not None and observed_complete and not missing
            and not duplicates and classification in {"passed", "failed"},
        "process_exit_code": process_exit_code, "issues": issues,
    }


def evaluation_record(native_score: Mapping[str, Any], junit_xml: str | bytes | None,
                      **run_status: Any) -> dict[str, Any]:
    """Keep the unmodified native score beside independently classified tests."""
    return {"native_score": copy.deepcopy(dict(native_score)),
            "test_evidence": classify_junit(junit_xml, **run_status)}
