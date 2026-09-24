#!/usr/bin/env python3
"""Frozen A0 v4 AppWorld peer-handoff development diagnostic. `check` never calls an LLM.

This is stateless instrumentation, not role learning. A paid `run` requires a
separate provider ping and a zero-LLM native fixture. Do not amend an executed
config or runner: use a new version and preserve the old raw evidence.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import traceback
from typing import Any

import aamas_real_probe as prior
import aamas_peer_judgment_smoke_v4 as base

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aamas2027/peer_judgment_a0_v4.json"
EXPECTED_TASKS = ("2a163ab_1", "afc0fce_1", "6ea6792_1", "60d0b5b_1")
EXPECTED_PAIRS = (("A", "B"), ("B", "C"), ("A", "D"), ("D", "C"))
SOURCE_PIN = "42b5bcf3cd334fee33f0c37c02070a9f5807add5"
READ_ONLY = {"controller_probe", "producer", "consumer_review"}
SECRET_FIELD = base.Secrets.KEY
PROPOSAL_TAG = "proposal"
JUDGMENT_TAG = "judgment"
MAX_PROPOSAL_BYTES = 65536
MAX_JUDGMENT_BYTES = 8192
BASE_LOG = prior.log


class ArtifactInvalid(ValueError):
    pass


class PhaseExhausted(RuntimeError):
    pass


class TransportUnknown(RuntimeError):
    pass


class InfrastructureError(RuntimeError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def json_bytes(value: Any) -> int:
    return len(canonical(value).encode())


def safe_log(secrets: base.Secrets) -> None:
    """RealAPI uses `prior.log`; redact there before anything reaches disk."""
    def redacted(path: Path, event: str, **payload: Any) -> None:
        BASE_LOG(path, event, **secrets.scrub(payload))
    prior.log = redacted


def load_config() -> dict[str, Any]:
    cfg = json.loads(CONFIG.read_text())
    episodes = cfg["episodes_in_order"]
    caps = cfg["attempted_call_caps_per_episode"]
    if (cfg["version"] != 4 or cfg["status"] != "FROZEN_PROSPECTIVE_A0_DEVELOPMENT_DIAGNOSTIC_V4"
            or tuple(row["task_id"] for row in episodes) != EXPECTED_TASKS
            or tuple((row["producer_id"], row["consumer_id"]) for row in episodes) != EXPECTED_PAIRS
            or any(row["family"] != row["task_id"].split("_")[0] for row in episodes)
            or caps != {"producer": 12, "consumer_review": 5, "consumer_action": 7, "total": 24}
            or cfg["global_task_attempt_cap"] != 96
            or cfg["appworld_source_commit"] != SOURCE_PIN
            or cfg["world_seed"] != 100 or cfg["appworld_data_version"] != "0.2.0"
            or cfg["provider_name"] != "内部"
            or cfg["provider_endpoint_expected"] != "https://idealab.alibaba-inc.com/api/code"
            or cfg["model_request"] != "qwen3.8-max" or cfg["temperature"] != 0
            or cfg["max_output_tokens_per_call"] != 8192
            or cfg["online_terminal_feedback"] is not False
            or cfg["role_updates_enabled"] is not False
            or cfg["public_login_guidance"]["apply_equally_to"] != "producer and consumer initial prompts"
            or cfg["exploration_visibility_guidance"]["apply_equally_to"] != "producer and consumer initial prompts"
            or not cfg["producer_seal_guidance"]):
        raise InfrastructureError("A0 contract differs from frozen ID/pair/budget/model contract")
    for version in ("v1", "v2"):
        pinned = cfg[f"supersedes_{version}_pre_execution"]
        older = ROOT / pinned["path"]
        if not older.exists() or prior.digest(older) != pinned["sha256"]:
            raise InfrastructureError(f"Preserved pre-execution {version} config changed")
    for pinned in cfg["v3_completed_run_pins"].values():
        if not isinstance(pinned, dict) or "path" not in pinned:
            continue
        prior_path = ROOT / pinned["path"]
        if not prior_path.exists() or prior.digest(prior_path) != pinned["sha256"]:
            raise InfrastructureError("Completed v3 source/result pin changed")
    size_fixture = cfg["synthetic_size_fixture"]
    if prior.digest(ROOT / size_fixture["path"]) != size_fixture["sha256"]:
        raise InfrastructureError("Synthetic schema-size evidence changed")
    for key in ("protocol", "public_inventory"):
        source = ROOT / cfg[key + "_path"]
        if not source.exists() or prior.digest(source) != cfg[key + "_sha256"]:
            raise InfrastructureError(f"Frozen {key} source hash changed")
    inventory = json.loads((ROOT / cfg["public_inventory_path"]).read_text())
    task_rows = {task["task_id"]: task for family in inventory["families"] for task in family["tasks"]}
    if any(task_rows[row["task_id"]]["public_spec_sha256"] != row["public_spec_sha256"]
           for row in episodes):
        raise InfrastructureError("Frozen public task specification inventory differs")
    out = (ROOT / cfg["output_root"]).resolve()
    if not out.is_relative_to(ROOT / "artifacts/experiments/aamas2027"):
        raise InfrastructureError("Output escaped experiment directory")
    return cfg


def public_path(value: Any, pointer: str) -> Any:
    """Resolve a JSON Pointer; only public result objects enter this function."""
    if pointer == "":
        return value
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ArtifactInvalid("source_refs.path must be a JSON Pointer")
    current = value
    for encoded in pointer[1:].split("/"):
        part = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdecimal() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise ArtifactInvalid("source_refs.path does not exist in cited public result")
    return current


def exact_public_value(actual: Any, declared: Any, kind: str) -> bool:
    if type(actual) in (int, float) and type(declared) in (int, float):
        return abs(float(actual) - float(declared)) < 1e-9
    if type(actual) is type(declared) and actual == declared:
        return True
    return kind == "task_spec" and isinstance(actual, str) and isinstance(declared, str) and declared in actual


def source_ref(ref: Any, sources: dict[str, dict[str, Any]], expected_world: str,
               allow_task_spec: bool = True) -> dict[str, Any]:
    if not isinstance(ref, dict) or set(ref) != {"kind", "source_id", "path", "value"}:
        raise ArtifactInvalid("Each source_ref needs kind, source_id, path, value only")
    kind, identifier = ref["kind"], ref["source_id"]
    if kind not in ("task_spec", "api_observation", "api_doc") or not isinstance(identifier, str):
        raise ArtifactInvalid("Unknown typed public source_ref")
    if kind == "task_spec" and not allow_task_spec:
        raise ArtifactInvalid("task_spec is not an action observation")
    source = sources.get(identifier)
    if source is None or source["kind"] != kind or source["world"] != expected_world:
        raise ArtifactInvalid("source_ref is absent, wrong type, or from another actor/world")
    if kind == "api_observation" and not (source["method"] == "get" and source["app"] not in
                                               ("api_docs", "supervisor", "admin")):
        raise ArtifactInvalid("An action observation must be an actual public task-data GET")
    actual = public_path(source["value"], ref["path"])
    if not exact_public_value(actual, ref["value"], kind):
        raise ArtifactInvalid("source_ref value differs from cited public result")
    return {**copy.deepcopy(ref), "actor": source["actor"], "world": source["world"],
            "step": source["step"], "app": source.get("app"), "api": source.get("api"),
            "method": source.get("method"), "response_sha256": source["response_sha256"]}


def validate_refs(refs: Any, sources: dict[str, dict[str, Any]], world: str,
                  require_data: bool = False) -> list[dict[str, Any]]:
    if not isinstance(refs, list) or not refs or len(refs) > 12:
        raise ArtifactInvalid("Each claim needs 1-12 typed source_refs")
    resolved = [source_ref(ref, sources, world) for ref in refs]
    if require_data and not any(ref["kind"] == "api_observation" for ref in resolved):
        raise ArtifactInvalid("Selection/target/argument must cite actual task-data GET")
    return resolved


def refs_contain_value(refs: list[dict[str, Any]], value: Any) -> bool:
    for ref in refs:
        observed = ref["value"]
        if type(observed) in (int, float) and type(value) in (int, float):
            if abs(float(observed) - float(value)) < 1e-9:
                return True
        elif type(observed) is type(value) and observed == value:
            return True
        elif isinstance(observed, str) and isinstance(value, str) and value and value in observed:
            return True
    return False


def validate_claim(claim: Any, field: str, expected: Any,
                   sources: dict[str, dict[str, Any]], world: str,
                   require_data: bool = True) -> dict[str, Any]:
    if (not isinstance(claim, dict) or set(claim) != {"field", "value", "source_refs", "derivation"}
            or claim["field"] != field or claim["value"] != expected):
        raise ArtifactInvalid(f"Claim missing or mismatched for {field}")
    resolved = validate_refs(claim["source_refs"], sources, world, require_data)
    derivation = claim["derivation"]
    if derivation is not None:
        if (not isinstance(derivation, dict) or set(derivation) != {"expression", "operands"}
                or not isinstance(derivation["expression"], str) or not derivation["expression"].strip()
                or not isinstance(derivation["operands"], list) or not derivation["operands"]):
            raise ArtifactInvalid("Derived claim needs expression and sourced operands")
        operands = []
        for operand in derivation["operands"]:
            if (not isinstance(operand, dict) or set(operand) != {"name", "value", "source_refs"}
                    or not isinstance(operand["name"], str) or not operand["name"]):
                raise ArtifactInvalid("Malformed derived operand")
            operand_refs = validate_refs(operand["source_refs"], sources, world)
            if not refs_contain_value(operand_refs, operand["value"]):
                raise ArtifactInvalid("Derived operand value absent from its cited source")
            operands.append({**operand, "source_refs": operand_refs})
        derivation = {"expression": derivation["expression"], "operands": operands}
    elif not refs_contain_value(resolved, expected):
        raise ArtifactInvalid(f"{field} value absent from cited public source; use sourced derivation")
    return {**claim, "source_refs": resolved, "derivation": derivation}


def validate_proposal(value: Any, sources: dict[str, dict[str, Any]],
                      producer_world: str, secrets: base.Secrets) -> dict[str, Any]:
    if (not isinstance(value, dict)
            or set(value) != {"summary", "candidate_actions", "coverage", "no_action", "uncertainties"}
            or not isinstance(value["summary"], str) or not value["summary"].strip()
            or not isinstance(value["uncertainties"], list)
            or not all(isinstance(x, str) for x in value["uncertainties"])
            or json_bytes(value) > MAX_PROPOSAL_BYTES or secrets.contains(value)):
        raise ArtifactInvalid("Proposal schema/size/credential check failed")
    rows = value["candidate_actions"]
    if not isinstance(rows, list) or len(rows) > 30:
        raise ArtifactInvalid("candidate_actions must be a list of at most 30")
    data_sources = [s for s in sources.values() if s["kind"] == "api_observation"
                    and s["world"] == producer_world]
    if not data_sources:
        raise ArtifactInvalid("Producer needs a real public task-data GET before delivery")
    coverage = value["coverage"]
    if (not isinstance(coverage, dict) or set(coverage) !=
            {"scope", "exhaustive", "pagination_and_stopping_basis", "source_refs"}
            or not isinstance(coverage["scope"], str) or not coverage["scope"].strip()
            or coverage["exhaustive"] not in (True, False, None)
            or not isinstance(coverage["pagination_and_stopping_basis"], str)
            or not coverage["pagination_and_stopping_basis"].strip()):
        raise ArtifactInvalid("Coverage needs scope, exhaustive, stopping basis and public refs")
    coverage = {**coverage, "source_refs": validate_refs(coverage["source_refs"],
                                                         sources, producer_world, True)}
    no_action = value["no_action"]
    if rows and no_action is not None:
        raise ArtifactInvalid("no_action must be null when candidate_actions are present")
    if not rows:
        if (not isinstance(no_action, dict) or set(no_action) != {"reason", "source_refs"}
                or not isinstance(no_action["reason"], str) or not no_action["reason"].strip()):
            raise ArtifactInvalid("Empty candidate_actions requires evidenced no_action")
        no_action = {**no_action, "source_refs": validate_refs(no_action["source_refs"],
                                                                sources, producer_world, True)}
    enriched = []
    seen_ids: set[str] = set()
    for i, row in enumerate(rows):
        if (not isinstance(row, dict) or set(row) !=
                {"action_id", "app", "api", "target", "arguments", "selection_claim", "claims"}
                or row["action_id"] != f"a{i + 1}"
                or row["action_id"] in seen_ids or not isinstance(row["app"], str)
                or not isinstance(row["api"], str) or not isinstance(row["target"], str)
                or not row["target"].strip() or not isinstance(row["arguments"], dict)
                or not row["arguments"] or not isinstance(row["claims"], list)):
            raise ArtifactInvalid("Action row requires sequential ID, public API, target and args")
        seen_ids.add(row["action_id"])
        if any(SECRET_FIELD.search(str(key)) for key in row["arguments"]):
            raise ArtifactInvalid("Credential-bearing action arguments must be supplied by recipient")
        if any(isinstance(x, (dict, list)) for x in row["arguments"].values()):
            raise ArtifactInvalid("Nested action arguments are not supported in A0")
        api_docs = [s for s in sources.values() if s["kind"] == "api_doc" and
                    s["world"] == producer_world and s.get("doc_app") == row["app"] and
                    s.get("doc_api") == row["api"]]
        if not api_docs:
            raise ArtifactInvalid("Every candidate API needs its public show_api_doc observation")
        selection = validate_claim(row["selection_claim"], "selection",
                                   row["selection_claim"].get("value") if isinstance(row["selection_claim"], dict) else None,
                                   sources, producer_world, True)
        claims = row["claims"]
        required = {"target", *(f"arguments.{key}" for key in row["arguments"])}
        by_field = {claim.get("field"): claim for claim in claims if isinstance(claim, dict)}
        if len(by_field) != len(claims) or set(by_field) != required:
            raise ArtifactInvalid("Exactly one claim is required for target and each action argument")
        parsed_claims = [validate_claim(by_field["target"], "target", row["target"],
                                        sources, producer_world, True)]
        for key, arg in row["arguments"].items():
            parsed_claims.append(validate_claim(by_field[f"arguments.{key}"],
                                                f"arguments.{key}", arg,
                                                sources, producer_world,
                                                not isinstance(arg, str) or not any(
                                                    arg in str(s["value"]) for s in sources.values()
                                                    if s["kind"] == "task_spec")))
        enriched.append({**row, "selection_claim": selection, "claims": parsed_claims})
    return {**value, "candidate_actions": enriched, "coverage": coverage, "no_action": no_action,
            "provenance_status": "STRUCTURALLY_VERIFIED_ONLY_SEMANTIC_REVIEW_PENDING"}


def validate_judgment(value: Any, proposal: dict[str, Any],
                      secrets: base.Secrets,
                      steps: list[dict[str, Any]]) -> dict[str, Any]:
    if (not isinstance(value, dict) or set(value) !=
            {"verdict", "planned_action_ids", "review_reason", "planned_repair", "review_source_steps"}
            or value["verdict"] not in ("accept", "repair", "reject", "unknown")
            or not isinstance(value["planned_action_ids"], list)
            or len(set(map(str, value["planned_action_ids"]))) != len(value["planned_action_ids"])
            or not isinstance(value["review_reason"], str) or not value["review_reason"].strip()
            or value["planned_repair"] is not None and not isinstance(value["planned_repair"], str)
            or not isinstance(value["review_source_steps"], list)
            or any(type(x) is not int or x < 1 for x in value["review_source_steps"])
            or json_bytes(value) > MAX_JUDGMENT_BYTES or secrets.contains(value)):
        raise ArtifactInvalid("Pre-action judgment schema/size/credential check failed")
    ids = {row["action_id"] for row in proposal["candidate_actions"]}
    if not set(value["planned_action_ids"]).issubset(ids):
        raise ArtifactInvalid("Judgment planned_action_ids cite unknown proposal rows")
    if value["verdict"] in ("reject", "unknown") and value["planned_action_ids"]:
        raise ArtifactInvalid("Reject/unknown judgment cannot plan to use proposal rows")
    if value["verdict"] == "accept" and ids and not value["planned_action_ids"]:
        raise ArtifactInvalid("Accept judgment must identify intended proposal rows")
    read_steps = {row["step"] for row in steps if row["public_task_data_reads"] > 0}
    if any(step not in read_steps for step in value["review_source_steps"]):
        raise ArtifactInvalid("Review source step must contain an actual successful public task-data GET")
    return value


def api_guard(world: Any, phase: str, actor: str, secrets: base.Secrets,
              raw: Path, deferred: list[tuple[str, dict[str, Any]]],
              context: dict[str, Any], sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Native public API mediation; audit I/O is deferred through SafetyGuard."""
    from appworld.requester import _get_api_name_to_doc

    requester = world.requester
    if not hasattr(requester, "_a0_original_request"):
        requester._a0_original_request = requester.request
        requester._a0_original_verbs = {verb: getattr(requester, "_" + verb)
                                        for verb in ("post", "put", "patch", "delete")}
    original = requester._a0_original_request
    for verb, implementation in requester._a0_original_verbs.items():
        setattr(requester, "_" + verb, implementation)
    audit: list[dict[str, Any]] = []

    def checked(_app_name: str, _api_name: str, **kwargs: Any) -> Any:
        app, api = _app_name, _api_name
        try:
            doc = _get_api_name_to_doc(app, include_private_apis=False)[api]
            method = doc["method"].lower()
            path = doc["path"]
        except Exception as exc:
            deferred.append(("api_denied", {"phase": phase, "app": app,
                                            "api": api, "reason": "not_public_api"}))
            raise InfrastructureError("Unknown public API metadata") from exc
        auth_only = method == "post" and path.endswith("/auth/token")
        if phase in READ_ONLY and method != "get" and not auth_only:
            deferred.append(("write_blocked", {"phase": phase, "app": app,
                                               "api": api, "method": method,
                                               "api_path": path, "actor": actor}))
            raise PermissionError("Read-only actor attempted a task write")
        row = {"phase": phase, "actor": actor, "world": world.experiment_name,
               "step": context.get("step", 0), "app": app, "api": api,
               "origin": context.get("origin", "actor"),
               "method": method, "api_path": path, "arguments": kwargs}
        secrets.observe(kwargs)
        try:
            result = original(app, api, **kwargs)
            secrets.observe(result)
            row["ok"] = True
            row["response"] = secrets.scrub(result)
            row["response_sha256"] = sha_text(canonical(row["response"]))
            row["public_read_observation"] = (method == "get" and app not in
                                              ("api_docs", "supervisor", "admin") and
                                              not (isinstance(result, dict) and
                                                   set(result).intersection({"message", "detail", "error", "errors"})))
            if method == "get" and phase == "producer":
                identifier = f"p{context['step']}.c{len(audit) + 1}"
                kind = "api_doc" if app == "api_docs" else (
                    "api_observation" if row["public_read_observation"] else None)
                if kind == "api_doc" and api != "show_api_doc":
                    kind = None
                if kind:
                    row["source_id"] = identifier
                    sources[identifier] = {"kind": kind, "value": row["response"],
                        "step": context["step"], "actor": actor, "world": world.experiment_name,
                        "app": app, "api": api, "method": method,
                        "response_sha256": row["response_sha256"],
                        "doc_app": kwargs.get("app_name") if api == "show_api_doc" else None,
                        "doc_api": kwargs.get("api_name") if api == "show_api_doc" else None}
            return result
        except Exception as exc:
            row["ok"] = False
            row["public_read_observation"] = False
            row["error_type"] = type(exc).__name__
            raise
        finally:
            audit.append(row)
            deferred.append(("public_api_call", row.copy()))

    requester.request = checked
    if phase in READ_ONLY:
        for verb in ("post", "put", "patch", "delete"):
            old = requester._a0_original_verbs[verb]

            def blocked(url: str, *args: Any, _verb: str = verb,
                        _old: Any = old, **kwargs: Any) -> Any:
                if _verb == "post" and url.endswith("/auth/token"):
                    return _old(url, *args, **kwargs)
                deferred.append(("write_blocked", {"phase": phase, "method": _verb,
                                                   "api_path": url, "actor": actor}))
                raise PermissionError("Direct write transport blocked in read-only phase")

            setattr(requester, "_" + verb, blocked)
    return audit


def flush(raw: Path, deferred: list[tuple[str, dict[str, Any]]]) -> None:
    while deferred:
        event, payload = deferred.pop(0)
        prior.log(raw, event, **payload)


def initial_public_probe(world: Any, phase: str, actor: str, secrets: base.Secrets,
                         raw: Path, deferred: list[tuple[str, dict[str, Any]]],
                         sources: dict[str, dict[str, Any]]) -> str:
    context = {"step": 0, "origin": "controller"}
    audit = api_guard(world, "controller_probe", actor, secrets, raw, deferred, context, sources)
    results = [world.requester.request("supervisor", "show_active_task"),
               world.requester.request("phone", "get_current_date_and_time")]
    flush(raw, deferred)
    payload = secrets.scrub(results)
    digest = sha_text(canonical(payload))
    prior.log(raw, "initial_public_probe", phase=phase, actor=actor,
              world=world.experiment_name, sha256=digest, public_calls=len(audit),
              probe_names=("supervisor.show_active_task", "phone.get_current_date_and_time"))
    return digest


def task_state_hashes(world: Any) -> dict[str, int | None]:
    """Controller-only model hashes; no model records or hashes enter actor prompts."""
    if world.models is None:
        raise InfrastructureError("Local AppWorld model collection unavailable")
    hashes = world.models.model_hashes()
    if not hashes or not all(isinstance(key, str) for key in hashes):
        raise InfrastructureError("Native model_hashes did not return task tables")
    return hashes


def response_receipts(rows: list[dict[str, Any]]) -> str:
    receipts = []
    for row in rows:
        if row.get("source_id") and row.get("ok"):
            value = canonical(row.get("response"))
            receipts.append({"source_id": row["source_id"], "app": row["app"],
                             "api": row["api"], "response_sha256": row["response_sha256"],
                             "response": value[:12000], "truncated": len(value) > 12000})
    return "\nPublic source receipts (JSON Pointer paths refer to response):\n" + canonical(receipts)


def generate_with_retry(api: prior.RealAPI, messages: list[dict[str, str]],
                        raw: Path, cfg: dict[str, Any], state: dict[str, Any]) -> str:
    retries = 0
    # RealAPI serializes this request with json.dumps before sending it. Keep a
    # byte-level snapshot so retries cannot silently include a changed history.
    request = {"model": cfg["model_request"], "messages": messages,
               "max_tokens": cfg["max_output_tokens_per_call"],
               "temperature": cfg["temperature"], "stream": False}
    request_bytes = json.dumps(request).encode()
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    world_count = state["world_execute_count"]
    while True:
        before_attempt = api.attempts
        before_log_bytes = raw.stat().st_size if raw.exists() else 0
        try:
            return api.generate(messages, max_tokens=cfg["max_output_tokens_per_call"])
        except Exception as exc:
            if json.dumps(request).encode() != request_bytes or state["world_execute_count"] != world_count:
                raise TransportUnknown("Request messages or world state changed during failed call") from exc
            events = [json.loads(line) for line in raw.read_bytes()[before_log_bytes:].splitlines()]
            response_returned = any(row.get("event") == "response" for row in events)
            one_attempt_charged = api.attempts == before_attempt + 1
            timed_out = isinstance(exc, TimeoutError) or isinstance(getattr(exc, "reason", None), TimeoutError)
            if (timed_out and not response_returned and one_attempt_charged
                    and not state["timeout_retry_used"] and api.attempts < api.max_attempts):
                state["timeout_retry_used"] = True
                prior.log(raw, "transport_backoff", retry_kind="same_request_unreturned_timeout",
                          request_sha256=request_hash, response_returned=False,
                          world_execute_count_before=world_count,
                          world_execute_count_after=state["world_execute_count"],
                          messages_unchanged=True, seconds=2, charged_attempts=api.attempts)
                time.sleep(2)
                continue
            code = getattr(exc, "code", None)
            if (code in (429, 503) and not response_returned and one_attempt_charged
                    and retries < 2 and api.attempts < api.max_attempts):
                delay = (1, 2)[retries]
                retries += 1
                prior.log(raw, "transport_backoff", retry_kind="service", status=code,
                          request_sha256=request_hash, response_returned=False,
                          messages_unchanged=True, seconds=delay, retry_index=retries,
                          charged_attempts=api.attempts)
                time.sleep(delay)
                continue
            raise TransportUnknown(f"{type(exc).__name__}: {exc}") from exc


def phase_loop(world: Any, parser: Any, api: prior.RealAPI,
               messages: list[dict[str, str]], raw: Path, phase: str,
               terminal_tag: str | None, cfg: dict[str, Any], secrets: base.Secrets,
               audit: list[dict[str, Any]], deferred: list[tuple[str, dict[str, Any]]],
               context: dict[str, Any], state: dict[str, Any],
               validator: Any | None = None) -> tuple[Any | None, list[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []
    while api.attempts < api.max_attempts:
        answer = generate_with_retry(api, messages, raw, cfg, state)
        terminal: Any | None = None
        if terminal_tag:
            try:
                terminal = base.parse_tag(answer, terminal_tag)
            except (ValueError, json.JSONDecodeError) as exc:
                state["validation_rejections"][phase] += 1
                prior.log(raw, "artifact_rejected", phase=phase, attempt=api.attempts,
                          error_type=type(exc).__name__, reason="malformed_tagged_json")
                messages += [{"role": "assistant", "content": answer}, {"role": "user", "content":
                    f"Validation error: emit one well-formed <{terminal_tag}> JSON artifact or public Python code. "
                    "This attempt was charged; use only remaining calls."}]
                continue
        if terminal is not None:
            try:
                terminal = validator(terminal, steps) if validator else terminal
            except (ArtifactInvalid, ValueError) as exc:
                state["validation_rejections"][phase] += 1
                reason = secrets.scrub(str(exc))
                prior.log(raw, "artifact_rejected", phase=phase, attempt=api.attempts,
                          reason=reason)
                messages += [{"role": "assistant", "content": answer}, {"role": "user", "content":
                    "Validation error: " + reason + ". Repair using only your public observations. "
                    "The rejected response was charged to this phase."}]
                continue
            prior.log(raw, "phase_artifact", phase=phase, artifact=terminal)
            messages.append({"role": "assistant", "content": answer})
            return terminal, steps
        code, fixed = parser.extract_code_and_fix_content(answer)
        if not code.strip():
            state["validation_rejections"][phase] += 1
            prior.log(raw, "code_rejected", phase=phase, attempt=api.attempts,
                      reason="missing_python_code_or_terminal_artifact")
            messages += [{"role": "assistant", "content": answer}, {"role": "user", "content":
                "Validation error: provide one public ```python code block" +
                (f" or <{terminal_tag}> JSON." if terminal_tag else ".") +
                " This response was charged."}]
            continue
        try:
            base.safe_code(code)
        except ValueError as exc:
            state["validation_rejections"][phase] += 1
            prior.log(raw, "code_rejected", phase=phase, attempt=api.attempts,
                      reason=str(exc))
            messages += [{"role": "assistant", "content": answer}, {"role": "user", "content":
                "Validation error: " + str(exc) + ". Use the existing apis object and public APIs. "
                "This response was charged."}]
            continue
        before = len(audit)
        context["step"] = len(steps) + 1
        observation = world.execute(code)
        flush(raw, deferred)
        state["world_execute_count"] += 1
        if "Usage of the following function is not allowed: pathlib.Path.mkdir" in observation:
            raise InfrastructureError("Native public API failed on runner I/O inside SafetyGuard")
        if "Unknown public API metadata" in observation:
            raise InfrastructureError("Unknown public API metadata inside REPL")
        new_calls = audit[before:]
        row = {"step": context["step"], "code": code, "observation": observation,
               "api_calls": len(new_calls),
               "source_ids": [call["source_id"] for call in new_calls if call.get("source_id")],
               "public_task_data_reads": sum(bool(call.get("public_read_observation"))
                                             for call in new_calls)}
        steps.append(row)
        prior.log(raw, "environment_observation", phase=phase, **row)
        messages.append({"role": "assistant", "content": fixed + "\n\n"})
        feedback = "Output:\n```\n" + observation + "\n```\n"
        if phase == "producer":
            feedback += response_receipts(new_calls)
        if "Read-only actor attempted a task write" in observation or "Direct write transport blocked" in observation:
            prior.log(raw, "read_only_write_rejected", phase=phase, step=context["step"])
            feedback += "\nThis write was blocked; remain read-only in this phase."
        messages.append({"role": "user", "content": feedback})
        if phase == "consumer_action":
            context["origin"] = "controller"
            completed = world.task_completed()
            flush(raw, deferred)
            context["origin"] = "actor"
            if completed:
                prior.log(raw, "native_task_completed", phase=phase)
                return None, steps
    if phase == "consumer_action":
        state["action_budget_exhausted"] = True
        prior.log(raw, "phase_exhausted", phase=phase, attempts=api.attempts,
                  world_steps=len(steps), status="UNKNOWN")
        return None, steps
    raise PhaseExhausted(f"{phase} attempted-call cap exhausted after {len(steps)} world steps")


def usage(api: prior.RealAPI) -> dict[str, Any]:
    return {"attempts": api.attempts, "tokens": api.usage,
            "unknown_usage_attempts": api.unknown_usage_attempts,
            "api_errors": api.errors, "error_codes": api.error_codes,
            "returned_models": api.returned_models, "api_seconds": api.seconds}


def equivalent(a: Any, b: Any) -> bool:
    if type(a) in (int, float) and type(b) in (int, float):
        return abs(float(a) - float(b)) < 0.005
    return a == b


def material_args(arguments: dict[str, Any]) -> dict[str, Any]:
    """Only credentials and AppWorld's call-wrapper flag are non-material."""
    return {key: value for key, value in arguments.items()
            if not SECRET_FIELD.search(key) and key != "raise_on_failure"}


def actual_use(proposal: dict[str, Any], action_calls: list[dict[str, Any]],
               judgment: dict[str, Any], secrets: base.Secrets) -> dict[str, Any]:
    finalization_calls = [call for call in action_calls if call["app"] == "supervisor" and
                          call["api"] == "complete_task"]
    writes = [call for call in action_calls if call.get("origin") == "actor" and
              call["method"] != "get" and
              not call["api_path"].endswith("/auth/token") and
              not (call["app"] == "supervisor" and call["api"] == "complete_task")]
    attempted, confirmed, unmatched = [], [], []
    matched_call_ids: set[int] = set()
    for row in proposal["candidate_actions"]:
        candidates = [(i, call) for i, call in enumerate(writes)
                      if i not in matched_call_ids and
                      call["app"] == row["app"] and call["api"] == row["api"] and
                      set(material_args(call["arguments"])) == set(row["arguments"]) and
                      all(equivalent(material_args(call["arguments"])[key], value)
                          for key, value in row["arguments"].items())]
        if candidates:
            attempted.append(row["action_id"])
            matched_call_ids.add(candidates[0][0])
            call = candidates[0][1]
            if call.get("ok") and not (isinstance(call.get("response"), dict) and
                                       set(call["response"]).intersection({"error", "errors", "detail"})):
                confirmed.append(row["action_id"])
        else:
            unmatched.append(row["action_id"])
    extra = [{"app": call["app"], "api": call["api"], "arguments": secrets.scrub(call["arguments"]),
              "ok": call.get("ok"), "source_id": call.get("source_id")}
             for i, call in enumerate(writes) if i not in matched_call_ids]
    return {"planned_action_ids": judgment["planned_action_ids"],
            "matched_attempted_action_ids": attempted,
            "matched_api_success_action_ids": confirmed,
            "confirmed_state_transition_action_ids": [],
            "confirmed_state_transition_status": "NOT_ESTABLISHED_BY_GENERIC_A0_AUDIT",
            "not_matched_action_ids": unmatched,
            "extra_or_modified_write_calls": extra,
            "all_action_write_calls": secrets.scrub(writes),
            "consumer_finalization_calls": [{"attempted": True, "ok": call.get("ok"),
                "answer_was_non_null": call["arguments"].get("answer") is not None,
                "answer_type": type(call["arguments"].get("answer")).__name__}
                for call in finalization_calls],
            "consumer_finalization_error": "UNDETERMINED_PUBLIC_TRACE_REVIEW_REQUIRED",
            "attempted_match_is_causal_proof": False,
            "api_success_is_official_state_transition_proof": False,
            "interpretation": "Exact non-secret API argument match is behavioral use evidence only. API success and official state transition remain distinct; evaluator is offline."}


def seal_json(path: Path, value: Any, secrets: base.Secrets) -> str:
    if secrets.contains(value):
        raise InfrastructureError("Credential appeared in sealed artifact")
    prior.save(path, value)
    return prior.digest(path)


def episode(job: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    out = ROOT / cfg["output_root"]
    manifest = json.loads((out / "source_manifest.json").read_text())
    if (prior.digest(__file__) != manifest["runner_sha256"] or
            prior.digest(CONFIG) != manifest["config_sha256"] or
            prior.digest(out / "runner_at_execution.py") != manifest["runner_sha256"]):
        raise InfrastructureError("A0 runner/config differs from prospective snapshot")
    if job not in cfg["episodes_in_order"]:
        raise InfrastructureError("Task not in frozen A0 sequence")
    task_id = job["task_id"]
    directory = out / "episodes" / task_id
    directory.mkdir(parents=True, exist_ok=False)
    raw = directory / "raw.jsonl"
    secrets = base.Secrets()
    safe_log(secrets)
    started = prior.mono()
    config_hash = prior.digest(CONFIG)
    suffix = sha_text("peer-a0-v4:" + task_id + ":" + config_hash)[:18]
    worlds = {"producer": "pa0_prod_" + suffix, "consumer": "pa0_cons_" + suffix}
    native_dirs = {name: prior.APP / "experiments/outputs" / name for name in worlds.values()}
    deferred: list[tuple[str, dict[str, Any]]] = []
    apis: dict[str, prior.RealAPI] = {}
    result: dict[str, Any] = {**job, "status": "UNKNOWN", "error": None,
        "infrastructure_error_category": None, "global_stop": False,
        "official_final_success": None, "usd_cost": None,
        "valid_complete_observation_chain": False, "worlds": worlds}
    state = {"world_execute_count": 0, "timeout_retry_used": False,
             "action_budget_exhausted": False, "last_phase": None,
             "validation_rejections": {"producer": 0, "consumer_review": 0,
                                       "consumer_action": 0}}
    prior.log(raw, "episode_config", task_id=task_id, pair=[job["producer_id"],job["consumer_id"]],
              config_sha256=config_hash, runner_sha256=prior.digest(__file__),
              appworld_commit=SOURCE_PIN, data_version=cfg["appworld_data_version"],
              seed=cfg["world_seed"], model=cfg["model_request"],
              caps=cfg["attempted_call_caps_per_episode"],
              stateless_a0=True, role_updates_enabled=False,
              command=sys.argv, project_git_head=subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              host=platform.node(), python=sys.version,
              no_ground_truth_in_solver=True, usd_cost=None)
    try:
        if any(path.exists() for path in native_dirs.values()):
            raise InfrastructureError("Refuse native-output overwrite")
        AppWorld, parser = prior.initialize_runtime()
        provider = prior.load_provider()
        if provider["base"] != cfg["provider_endpoint_expected"]:
            raise InfrastructureError("Provider endpoint mismatch")
        prior.log(raw, "runtime_versions", provider={k:v for k,v in provider.items() if k != "secret"},
                  package_versions={name: importlib.metadata.version(name)
                                    for name in ("appworld", "openai", "freezegun", "jinja2")})
        source_spec = {"instruction": None, "supervisor": None}
        sources: dict[str, dict[str, Any]] = {}
        producer_probe: str | None = None
        with AppWorld(task_id=task_id, experiment_name=worlds["producer"],
                      load_ground_truth=False, random_seed=cfg["world_seed"],
                      raise_on_extra_parameters=True) as producer:
            if (producer.task.ground_truth is not None or not producer.raise_on_unsafe_execution
                    or producer.task.db_version != cfg["appworld_data_version"]):
                raise InfrastructureError("Unsafe producer world or ground truth loaded")
            base.install_native_log_scrubber(producer, native_dirs[worlds["producer"]], secrets)
            producer_initial_hashes = task_state_hashes(producer)
            prior.log(raw, "controller_initial_task_state", phase="producer",
                      actor=job["producer_id"],
                      model_hashes_sha256=sha_text(canonical(producer_initial_hashes)),
                      model_count=len(producer_initial_hashes), model_hashes=producer_initial_hashes,
                      never_actor_visible=True)
            source_spec = {"instruction": producer.task.instruction,
                           "supervisor": str(producer.task.supervisor)}
            sources["task_spec"] = {"kind": "task_spec", "value": source_spec,
                "step": None, "actor": job["producer_id"], "world": worlds["producer"],
                "method": None, "response_sha256": sha_text(canonical(source_spec))}
            producer_probe = initial_public_probe(producer, "producer", job["producer_id"],
                                                   secrets, raw, deferred, sources)
            context = {"step": 0}
            producer_audit = api_guard(producer, "producer", job["producer_id"], secrets,
                                       raw, deferred, context, sources)
            producer_messages = base.render_native_prompt(producer, parser,
                "You are the PRODUCER. Inspect only public APIs/GETs; do not write or complete the task. "
                "The recipient receives only your sealed proposal, not your private REPL or transcript. "
                "Find every qualifying target; inspect pagination and ordering for 'all' and 'last'. "
                "After public reading, emit exactly <proposal>{JSON}</proposal>, never executable code together with JSON. "
                "Keys: summary, candidate_actions (0-30), coverage, no_action (null unless no actions), uncertainties. "
                "Each action: action_id a1,a2,...; app, api, target (string), arguments (non-secret API args), "
                "selection_claim, claims. selection_claim and each claims row: field, value, source_refs, "
                "derivation (null or {expression, operands}). Required claim fields are target and "
                "arguments.KEY for each argument; selection_claim.field is selection. "
                "Each source_ref has kind (task_spec/api_observation/api_doc), source_id, JSON Pointer path, "
                "value copied exactly from the public source. Task-spec literals may be substrings of /instruction. "
                "For every derived value, including selection decisions not literally present in one field, "
                "state an explicit expression/reason and sourced operands; never fabricate a source. "
                "coverage: {scope, exhaustive (true/false/null), pagination_and_stopping_basis, source_refs}. "
                "When no actions qualify, provide no_action:{reason,source_refs}. "
                "Only the controller receipts supply valid pSTEP.cCALL source IDs and public response JSON. "
                "Cite task_spec for instruction literals and api_doc for API signatures. "
                "No credentials in proposal. Mark unknown completeness honestly. "
                + cfg["public_login_guidance"]["text"] + " "
                + cfg["exploration_visibility_guidance"]["text"] + " "
                + cfg["producer_seal_guidance"])
            prior.log(raw, "initial_prompt", phase="producer",
                      prompt_sha256=sha_text(producer_messages[-1]["content"]),
                      prompt_characters=len(producer_messages[-1]["content"]))
            apis["producer"] = prior.RealAPI(raw, cfg["attempted_call_caps_per_episode"]["producer"])
            state["last_phase"] = "producer"
            proposal, producer_steps = phase_loop(producer, parser, apis["producer"],
                producer_messages, raw, "producer", PROPOSAL_TAG, cfg, secrets,
                producer_audit, deferred, context, state,
                lambda artifact, _: validate_proposal(artifact, sources, worlds["producer"], secrets))
            if any(call["method"] != "get" and not call["api_path"].endswith("/auth/token")
                   for call in producer_audit):
                raise InfrastructureError("Producer task-state write detected")
            producer_after_hashes = task_state_hashes(producer)
            changed_models = [name for name in producer_initial_hashes
                              if producer_initial_hashes[name] != producer_after_hashes.get(name)]
            prior.log(raw, "controller_producer_state_after_read", changed_models=changed_models,
                      initial_sha256=sha_text(canonical(producer_initial_hashes)),
                      after_sha256=sha_text(canonical(producer_after_hashes)),
                      task_state_write_count=0, never_actor_visible=True)
            if changed_models:
                raise InfrastructureError("Producer read phase changed task model state")
            proposal_hash = seal_json(directory / "proposal.json", proposal, secrets)
            prior.log(raw, "producer_sealed", proposal_sha256=proposal_hash,
                      source_count=len(sources), public_steps=len(producer_steps),
                      public_api_calls=len(producer_audit), task_state_write_count=0)
            producer.save()
        base.sanitize_native_logs(native_dirs[worlds["producer"]], secrets)

        with AppWorld(task_id=task_id, experiment_name=worlds["consumer"],
                      load_ground_truth=False, random_seed=cfg["world_seed"],
                      raise_on_extra_parameters=True) as consumer:
            if (consumer.task.ground_truth is not None or not consumer.raise_on_unsafe_execution
                    or consumer.task.db_version != cfg["appworld_data_version"]):
                raise InfrastructureError("Unsafe consumer world or ground truth loaded")
            base.install_native_log_scrubber(consumer, native_dirs[worlds["consumer"]], secrets)
            consumer_initial_hashes = task_state_hashes(consumer)
            prior.log(raw, "controller_initial_task_state", phase="consumer",
                      actor=job["consumer_id"],
                      model_hashes_sha256=sha_text(canonical(consumer_initial_hashes)),
                      model_count=len(consumer_initial_hashes), model_hashes=consumer_initial_hashes,
                      never_actor_visible=True)
            if consumer_initial_hashes != producer_initial_hashes:
                raise InfrastructureError("Producer/consumer initial task model state mismatch")
            consumer_probe = initial_public_probe(consumer, "consumer", job["consumer_id"],
                                                   secrets, raw, deferred, sources)
            if consumer_probe != producer_probe or consumer.task.instruction != source_spec["instruction"]:
                raise InfrastructureError("Producer/consumer initial public state mismatch")
            prior.log(raw, "initial_task_state_equal", probe_sha256=consumer_probe,
                      model_hashes_sha256=sha_text(canonical(consumer_initial_hashes)),
                      limitation="Native model hashes are controller-only and not actor-visible")
            context = {"step": 0}
            review_audit = api_guard(consumer, "consumer_review", job["consumer_id"],
                                     secrets, raw, deferred, context, sources)
            consumer_messages = base.render_native_prompt(consumer, parser,
                "You are the independent CONSUMER. Only this sealed delivery crosses from the producer: "
                "<delivered_proposal>" + canonical(proposal) + "</delivered_proposal>. "
                "Use only public read APIs and computation before judgment; verify as needed. "
                "Then emit exactly <judgment>{JSON}</judgment> outside code fences, with keys "
                "verdict (accept/repair/reject/unknown), planned_action_ids (proposal IDs you intend to use), "
                "review_reason, planned_repair (string/null), review_source_steps (your read step numbers). "
                "The judgment is sealed before writes. No producer transcript, secret, evaluator, or hidden answer is available. "
                + cfg["public_login_guidance"]["text"] + " "
                + cfg["exploration_visibility_guidance"]["text"])
            prior.log(raw, "initial_prompt", phase="consumer_review",
                      prompt_sha256=sha_text(consumer_messages[-1]["content"]),
                      prompt_characters=len(consumer_messages[-1]["content"]))
            apis["consumer_review"] = prior.RealAPI(raw, cfg["attempted_call_caps_per_episode"]["consumer_review"])
            state["last_phase"] = "consumer_review"
            judgment, review_steps = phase_loop(consumer, parser, apis["consumer_review"],
                consumer_messages, raw, "consumer_review", JUDGMENT_TAG, cfg, secrets,
                review_audit, deferred, context, state,
                lambda artifact, steps: validate_judgment(artifact, proposal, secrets, steps))
            judgment_hash = seal_json(directory / "pre_action_judgment.json", judgment, secrets)
            prior.log(raw, "pre_action_judgment_sealed", judgment_sha256=judgment_hash,
                      judgment=judgment, review_steps=len(review_steps), review_api_calls=len(review_audit))
            context = {"step": 0}
            before_action_hashes = task_state_hashes(consumer)
            prior.log(raw, "controller_pre_action_task_state",
                      model_hashes_sha256=sha_text(canonical(before_action_hashes)),
                      model_hashes=before_action_hashes, never_actor_visible=True)
            if before_action_hashes != consumer_initial_hashes:
                raise InfrastructureError("Consumer review read phase changed task model state")
            action_audit = api_guard(consumer, "consumer_action", job["consumer_id"],
                                     secrets, raw, deferred, context, sources)
            consumer_messages.append({"role": "user", "content":
                "Your judgment is sealed. You may now execute public write APIs, inspect and repair as needed, "
                "and finish the supervisor's task. Complete no-answer tasks with an empty/null answer if required. "
                "Do not inspect private evaluator data. Your actual calls are audited separately from your intention."})
            apis["consumer_action"] = prior.RealAPI(raw, cfg["attempted_call_caps_per_episode"]["consumer_action"])
            state["last_phase"] = "consumer_action"
            _, action_steps = phase_loop(consumer, parser, apis["consumer_action"],
                consumer_messages, raw, "consumer_action", None, cfg, secrets,
                action_audit, deferred, context, state)
            action_stop = "budget_exhausted_unknown" if state["action_budget_exhausted"] else "task_completed"
            context["origin"] = "controller"
            completed = consumer.task_completed()
            flush(raw, deferred)
            context["origin"] = "actor"
            after_action_hashes = task_state_hashes(consumer)
            changed_action_models = sorted(name for name in before_action_hashes
                                           if before_action_hashes[name] != after_action_hashes.get(name))
            prior.log(raw, "controller_post_action_task_state",
                      model_hashes_sha256=sha_text(canonical(after_action_hashes)),
                      changed_models=changed_action_models,
                      never_actor_visible=True)
            consumer.save()
            use = actual_use(proposal, action_audit, judgment, secrets)
            use["controller_changed_task_models"] = changed_action_models
            use["controller_any_state_change_witness"] = bool(changed_action_models)
            use["controller_nonfinalization_changed_models"] = [
                name for name in changed_action_models if not name.startswith("supervisor.")]
            use["controller_task_action_change_witness"] = bool(
                use["controller_nonfinalization_changed_models"])
            use["per_action_state_transition_attribution"] = "UNKNOWN_GENERIC_MODEL_HASH_ONLY"
            use["consumer_action_stop"] = action_stop
            use["consumer_task_completed"] = completed
            use["action_world_steps"] = len(action_steps)
            use["review_world_steps"] = len(review_steps)
            use["review_api_calls"] = len(review_audit)
            use["action_api_calls"] = sum(call.get("origin") == "actor" for call in action_audit)
            use["controller_completion_probe_calls"] = sum(
                call.get("origin") == "controller" for call in action_audit)
            use["action_public_reads"] = sum(bool(call.get("public_read_observation"))
                                             for call in action_audit if call.get("origin") == "actor")
            use_hash = seal_json(directory / "actual_use.json", use, secrets)
            prior.log(raw, "consumer_action_sealed", actual_use_sha256=use_hash,
                      task_completed=completed, action_stop=action_stop)
            role_event = {"task_id": task_id, "family": job["family"],
                "producer_id": job["producer_id"], "consumer_id": job["consumer_id"],
                "producer_world": worlds["producer"], "consumer_world": worlds["consumer"],
                "deliverable_sha256": proposal_hash,
                "public_source_ids": sorted(sources),
                "pre_action_judgment_sha256": judgment_hash,
                "actual_use_sha256": use_hash,
                "public_runtime_outcome": {"task_completed": completed,
                                           "action_stop": action_stop},
                "uncertainties": proposal["uncertainties"],
                "repair_cost_observed": {"review_attempts": apis["consumer_review"].attempts,
                                          "review_world_steps": len(review_steps),
                                          "review_api_calls": len(review_audit),
                                          "action_extra_or_modified_writes": len(use["extra_or_modified_write_calls"])},
                "role_update": None,
                "responsibility_attribution": "UNDETERMINED_PENDING_PUBLIC_TRACE_REVIEW",
                "method_claim": "NONE_A0_STATELESS"}
            event_hash = seal_json(directory / "role_event.json", role_event, secrets)
            prior.log(raw, "role_event_sealed", role_event_sha256=event_hash,
                      role_update_enabled=False)
            complete_chain = bool(completed and not state["action_budget_exhausted"])
            result.update(status="ACTOR_SEALED" if not state["action_budget_exhausted"] else
                          "ACTOR_SEALED_ACTION_CAP_UNKNOWN", task_completed=completed,
                          action_stop=action_stop, proposal_sha256=proposal_hash,
                          judgment_sha256=judgment_hash, actual_use_sha256=use_hash,
                          role_event_sha256=event_hash,
                          valid_complete_observation_chain=complete_chain,
                          complete_chain_rule=cfg["complete_observation_chain_rule"],
                          producer_public_steps=len(producer_steps),
                          producer_public_api_calls=len(producer_audit),
                          consumer_review_steps=len(review_steps),
                          consumer_review_api_calls=len(review_audit),
                          consumer_action_api_calls=use["action_api_calls"],
                          controller_completion_probe_calls=use["controller_completion_probe_calls"])
        base.sanitize_native_logs(native_dirs[worlds["consumer"]], secrets)

        # No import of evaluator exists above this sealed boundary.
        from appworld.evaluator import evaluate_task
        evaluation = evaluate_task(task_id=task_id, experiment_name=worlds["consumer"],
                                   suppress_errors=True, save_report=True).to_dict(stats_only=False)
        prior.save(directory / "evaluator_only.json", secrets.scrub(evaluation))
        result.update(status="SCORED", official_final_success=bool(evaluation["success"]),
                      official_passes=len(evaluation["passes"]),
                      official_failures=len(evaluation["failures"]))
        prior.log(raw, "offline_evaluation", success=result["official_final_success"],
                  passes=result["official_passes"], failures=result["official_failures"],
                  never_actor_visible=True)
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": secrets.scrub(str(exc)),
                           "traceback": secrets.scrub(traceback.format_exc())}
        result["status"] = "UNKNOWN"
        result["stop_reason"] = secrets.scrub(str(exc))
        result["stop_phase"] = state["last_phase"]
        if isinstance(exc, (InfrastructureError, PermissionError)):
            result["infrastructure_error_category"] = (
                "native_guard_or_public_api" if "SafetyGuard" in str(exc) else
                "world_state_mismatch" if "state mismatch" in str(exc) else
                "producer_write_violation" if "write" in str(exc).lower() else
                "infrastructure_contract")
            result["global_stop"] = True
        elif isinstance(exc, TransportUnknown):
            result["infrastructure_error_category"] = "provider_transport"
        elif isinstance(exc, PhaseExhausted):
            result["infrastructure_error_category"] = None
        elif isinstance(exc, ArtifactInvalid):
            result["infrastructure_error_category"] = None
        else:
            result["infrastructure_error_category"] = "unexpected_" + type(exc).__name__
            result["global_stop"] = True
        prior.log(raw, "episode_error", **result["error"],
                  status=result["status"], category=result["infrastructure_error_category"],
                  global_stop=result["global_stop"])
        try:
            from appworld import AppWorld
            AppWorld.close_all()
        except Exception:
            pass
    finally:
        flush(raw, deferred)
        for native in native_dirs.values():
            base.sanitize_native_logs(native, secrets)
        result["phase_costs"] = {phase: usage(api) for phase, api in apis.items()}
        result["attempted_task_calls"] = sum(api.attempts for api in apis.values())
        result["world_execute_count"] = state["world_execute_count"]
        result["validation_rejections"] = state["validation_rejections"]
        result["action_budget_exhausted"] = state["action_budget_exhausted"]
        result["timeout_retry_used"] = state["timeout_retry_used"]
        result["wall_seconds"] = prior.mono() - started
        prior.save(directory / "result.json", secrets.scrub(result))
        prior.log(raw, "episode_result", **result)
    return result


def run_all(cfg: dict[str, Any]) -> None:
    preflight = cfg["preflight"]["paths"]
    prerequisites = {}
    for key in ("native_fixture", "provider_health"):
        path = ROOT / preflight[key] / "result.json"
        if not path.exists():
            raise InfrastructureError(f"Missing required separate {key} preflight result")
        evidence = json.loads(path.read_text())
        if (evidence.get("config_sha256") != prior.digest(CONFIG)
                or evidence.get("runner_sha256") != prior.digest(__file__)
                or evidence.get("ok") is not True):
            raise InfrastructureError(f"{key} preflight failed or refers to different config")
        prerequisites[key] = {"result_path": str(path.relative_to(ROOT)),
                              "sha256": prior.digest(path)}
    out = ROOT / cfg["output_root"]
    out.mkdir(parents=True, exist_ok=False)
    prior.save(out / "frozen_config.json", cfg)
    runner_bytes = Path(__file__).read_bytes()
    (out / "runner_at_execution.py").write_bytes(runner_bytes)
    dependency_versions = {name: importlib.metadata.version(name)
                           for name in ("appworld", "openai", "freezegun", "jinja2")}
    prior.save(out / "source_manifest.json", {"runner_sha256": hashlib.sha256(runner_bytes).hexdigest(),
        "config_sha256": prior.digest(CONFIG), "protocol_sha256": cfg["protocol_sha256"],
        "public_inventory_sha256": cfg["public_inventory_sha256"],
        "preflight": prerequisites, "development_only": True,
        "python": sys.version, "dependency_versions": dependency_versions,
        "appworld_source_commit": cfg["appworld_source_commit"],
        "appworld_data_version": cfg["appworld_data_version"],
        "task_attempt_reservation": cfg["global_task_attempt_cap"]})
    raw = out / "run_raw.jsonl"
    prior.log(raw, "run_reserved", episodes=cfg["episodes_in_order"],
              config_sha256=prior.digest(CONFIG), runner_sha256=prior.digest(__file__),
              global_attempt_cap=cfg["global_task_attempt_cap"],
              task_attempts_so_far=0, preflight=prerequisites)
    results: list[dict[str, Any]] = []
    consecutive_category: str | None = None
    consecutive_count = 0
    for job in cfg["episodes_in_order"]:
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    "_episode", job["task_id"]], cwd=ROOT, check=False)
        result_path = out / "episodes" / job["task_id"] / "result.json"
        if not result_path.exists():
            prior.log(raw, "child_result_missing", task_id=job["task_id"],
                      returncode=completed.returncode, category="child_result_missing")
            break
        row = json.loads(result_path.read_text())
        results.append(row)
        prior.save(out / "partial_results.json", results)
        total = sum(item["attempted_task_calls"] for item in results)
        prior.log(raw, "episode_collected", task_id=job["task_id"], status=row["status"],
                  attempted_task_calls=row["attempted_task_calls"],
                  cumulative_attempts=total, result_sha256=prior.digest(result_path))
        if total > cfg["global_task_attempt_cap"]:
            raise InfrastructureError("Global A0 attempted-call cap exceeded")
        category = row.get("infrastructure_error_category")
        if category and category == consecutive_category:
            consecutive_count += 1
        elif category:
            consecutive_category, consecutive_count = category, 1
        else:
            consecutive_category, consecutive_count = None, 0
        if row["global_stop"] or consecutive_count >= 2:
            prior.log(raw, "run_stopped", reason="global_stop_or_repeated_infrastructure",
                      category=category, consecutive_count=consecutive_count)
            break
    complete = sum(bool(r["valid_complete_observation_chain"]) for r in results)
    summary = {"status": "A0_DEVELOPMENT_DIAGNOSTIC", "attempted_ids": [r["task_id"] for r in results],
        "unstarted_ids": [j["task_id"] for j in cfg["episodes_in_order"][len(results):]],
        "task_llm_attempts": sum(r["attempted_task_calls"] for r in results),
        "preflight_llm_attempts_separate": 1,
        "complete_observation_chains": complete,
        "A1_observation_gate": "eligible_to_design_A1" if len(results) == 4 and complete >= 3 else
                                "stop_or_incomplete_A0",
        "no_role_update_or_method_claim": True, "no_confirmation_claim": True,
        "results": results}
    prior.save(out / "results.json", summary)
    prior.log(raw, "run_final", summary_sha256=prior.digest(out / "results.json"),
              complete_observation_chains=complete, gate=summary["A1_observation_gate"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "run", "_episode"), nargs="?", default="check")
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()
    cfg = load_config()
    if args.command == "check":
        base.safe_code("print(apis.api_docs.show_app_descriptions())")
        print(canonical({"status": "contract_ok_no_llm_calls", "config_sha256": prior.digest(CONFIG),
                         "ordered_ids": [j["task_id"] for j in cfg["episodes_in_order"]],
                         "attempt_caps": cfg["attempted_call_caps_per_episode"]}))
    elif args.command == "run":
        if args.task_id:
            parser.error("run cannot override the frozen task sequence")
        run_all(cfg)
    else:
        jobs = [job for job in cfg["episodes_in_order"] if job["task_id"] == args.task_id]
        if len(jobs) != 1:
            parser.error("Internal episode task is outside the frozen population")
        row = episode(jobs[0], cfg)
        print(canonical({"task_id": row["task_id"], "status": row["status"],
                         "attempted_task_calls": row["attempted_task_calls"]}))


if __name__ == "__main__":
    main()
