#!/usr/bin/env python3
"""Prospective v5 continuation of a sealed AppWorld handoff after safe-code rejection.

This controller makes independent model calls with separate histories and worlds.
It does not learn roles or measure a method advantage. Run only after reviewing
the frozen config. The default command is a no-network contract check.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import traceback
import time
from typing import Any

import aamas_real_probe as prior

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aamas2027/peer_judgment_resume_v5.json"
SOURCE_PIN = "42b5bcf3cd334fee33f0c37c02070a9f5807add5"
READ_PHASES = {"producer", "consumer_review"}
SAFE_IMPORTS = {"json", "math", "re", "decimal", "collections", "itertools", "datetime"}
FORBIDDEN_NAMES = {
    "requester", "world", "appworld", "evaluate_task", "open", "exec", "eval",
    "compile", "__import__", "globals", "locals", "vars", "dir", "getattr",
    "setattr", "delattr", "builtins", "input", "breakpoint", "help", "IPython",
    "get_ipython", "os", "sys", "pathlib", "subprocess", "requests", "urllib",
    "socket", "sqlite3", "shutil", "inspect", "importlib",
}
FORBIDDEN_ATTRS = {"requester", "client", "execute", "evaluate", "save", "load_state"}
PROPOSAL_TAG = "proposal"
JUDGMENT_TAG = "judgment"


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def load_config() -> dict[str, Any]:
    cfg = json.loads(CONFIG.read_text())
    caps = cfg["attempted_call_caps_per_episode"]
    if (cfg["version"] != 5
            or cfg["status"] != "PROSPECTIVE_CONSUMER_RESUME_ONLY"
            or cfg["appworld_source_commit"] != SOURCE_PIN
            or cfg["provider_name"] != "内部"
            or cfg["provider_endpoint_expected"] != "https://idealab.alibaba-inc.com/api/code"
            or cfg["model_request"] != "qwen3.8-max"
            or cfg["temperature"] != 0
            or cfg["native_task_ids_in_order"] != ["3c13f5a_3"]
            or any(type(caps.get(key)) is not int or caps[key] < 0
                   for key in ("producer", "consumer_review", "consumer_action", "total"))
            or caps["producer"] != 0 or caps["consumer_review"] != 7
            or caps["consumer_action"] != 18 or caps["total"] != 25
            or sum(caps[k] for k in ("producer", "consumer_review", "consumer_action")) != caps["total"]
            or caps["total"] * len(cfg["native_task_ids_in_order"]) != cfg["global_attempt_cap"]
            or cfg["max_output_tokens_per_call"] != 1024
            or cfg["world_seed"] != 100):
        raise RuntimeError("Prospective v5 continuation differs from reviewed runner assumptions")
    for name in ("config", "runner_at_execution", "results", "proposal", "raw"):
        path = ROOT / cfg["amends_v4"][name]
        if not path.exists() or prior.digest(path) != cfg["amends_v4"][name + "_sha256"]:
            raise RuntimeError("Preserved v4 evidence hash changed: " + name)
    out = (ROOT / cfg["output_root"]).resolve()
    if not out.is_relative_to(ROOT / "artifacts/experiments/aamas2027"):
        raise RuntimeError("Output root escaped experiment directory")
    return cfg


class Secrets:
    """Capture in-world credential fields before model-visible values are logged."""

    KEY = re.compile(r"(?:password|access[_-]?token|refresh[_-]?token|api[_-]?key|"
                     r"secret|authorization|auth[_-]?token|cookie)", re.I)
    PAIR = re.compile(
        r"(?i)([\"']?(?:password|access[_-]?token|refresh[_-]?token|api[_-]?key|"
        r"secret|authorization|auth[_-]?token|cookie)[\"']?\s*[:=]\s*)"
        r"([\"'])([^\"'\n]+)\2"
    )
    BARE_PAIR = re.compile(
        r"(?i)((?:password|access[_-]?token|refresh[_-]?token|api[_-]?key|"
        r"secret|authorization|auth[_-]?token|cookie)\s*=\s*)([^,\s)]+)"
    )
    BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}")

    def __init__(self) -> None:
        self.values: set[str] = set()

    def observe(self, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if self.KEY.search(str(key)) and isinstance(item, (str, int, float)):
                    secret = str(item)
                    if len(secret) >= 4:
                        self.values.add(secret)
                self.observe(item)
        elif isinstance(value, list):
            for item in value:
                self.observe(item)
        elif isinstance(value, str):
            for match in self.PAIR.finditer(value):
                if len(match.group(3)) >= 4:
                    self.values.add(match.group(3))
            for match in self.BARE_PAIR.finditer(value):
                secret = match.group(2).strip("\"'")
                if len(secret) >= 4:
                    self.values.add(secret)

    def scrub(self, value: Any) -> Any:
        self.observe(value)
        if isinstance(value, dict):
            return {key: "[REDACTED]" if self.KEY.search(str(key)) else self.scrub(item)
                    for key, item in value.items()}
        if isinstance(value, list):
            return [self.scrub(item) for item in value]
        if not isinstance(value, str):
            return value
        output = self.PAIR.sub(lambda m: m.group(1) + m.group(2) + "[REDACTED]" + m.group(2), value)
        output = self.BARE_PAIR.sub(lambda m: m.group(1) + "[REDACTED]", output)
        output = self.BEARER.sub("Bearer [REDACTED]", output)
        for secret in sorted(self.values, key=len, reverse=True):
            output = output.replace(secret, "[REDACTED]")
        return output

    def contains(self, value: Any) -> bool:
        raw = json.dumps(value, ensure_ascii=False)
        return self.scrub(raw) != raw


def install_redacted_logging(secrets: Secrets) -> None:
    native_log = prior.log

    def safe_log(path: Path, event: str, **payload: Any) -> None:
        native_log(path, event, **secrets.scrub(payload))

    prior.log = safe_log


def safe_code(code: str) -> None:
    """Constrain the REPL to public APIs/computation; native SafetyGuard also runs."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError("Model code has invalid syntax") from exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = [item.name.split(".")[0] for item in node.names] if isinstance(node, ast.Import) else [str(node.module).split(".")[0]]
            if any(module not in SAFE_IMPORTS for module in modules):
                raise ValueError("Import outside public computation allowlist")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise ValueError(f"REPL name blocked: {node.id}")
        elif isinstance(node, ast.Attribute) and (node.attr.startswith("_") or node.attr in FORBIDDEN_ATTRS):
            raise ValueError(f"REPL attribute blocked: {node.attr}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            lower = node.value.lower()
            if any(marker in lower for marker in ("ground_truth", "private_data", "evaluation.py", "data/tasks/")):
                raise ValueError("Private benchmark path marker in model code")


def api_guard(world: Any, phase: str, secrets: Secrets, raw: Path,
              deferred_events: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    """Block task writes and defer audit I/O until native SafetyGuard is disabled."""
    from appworld.requester import _get_api_name_to_doc

    audit: list[dict[str, Any]] = []
    requester = world.requester
    if not hasattr(requester, "_pj_original_request"):
        requester._pj_original_request = requester.request
        requester._pj_original_verbs = {
            verb: getattr(requester, "_" + verb)
            for verb in ("post", "put", "patch", "delete")
        }
    original = requester._pj_original_request
    for verb, implementation in requester._pj_original_verbs.items():
        setattr(requester, "_" + verb, implementation)

    def checked(_app_name: str, _api_name: str, **kwargs: Any) -> Any:
        try:
            doc = _get_api_name_to_doc(_app_name, include_private_apis=False)[_api_name]
            method = doc["method"].lower()
            path = doc["path"]
        except Exception as exc:
            deferred_events.append(("api_denied", {"phase": phase, "app": _app_name,
                                                   "api": _api_name,
                                                   "reason": "unknown_public_metadata"}))
            raise RuntimeError("Unknown public API metadata; refusing request") from exc
        credentials_only = method == "post" and path.endswith("/auth/token")
        if phase in READ_PHASES and method != "get" and not credentials_only:
            deferred_events.append(("write_blocked", {"phase": phase, "app": _app_name,
                                                      "api": _api_name, "method": method,
                                                      "api_path": path}))
            raise PermissionError("Read-only actor attempted a task write")
        row = {"phase": phase, "app": _app_name, "api": _api_name,
               "method": method, "api_path": path, "arguments": kwargs}
        secrets.observe(kwargs)
        try:
            result = original(_app_name, _api_name, **kwargs)
            secrets.observe(result)
            row["ok"] = True
            row["public_read_observation"] = (
                method == "get" and _app_name not in ("api_docs", "supervisor", "admin")
                and (not isinstance(result, dict) or
                     bool(result) and not set(result).intersection({"message", "detail", "error", "errors"}))
            )
            if _app_name == "venmo" and _api_name == "create_payment_request":
                row["payment_request_created"] = (
                    isinstance(result, dict) and "payment_request_id" in result)
            return result
        except Exception as exc:
            row["ok"] = False
            row["public_read_observation"] = False
            row["error_type"] = type(exc).__name__
            raise
        finally:
            audit.append(row)
            deferred_events.append(("public_api_call", row.copy()))

    requester.request = checked
    # These are bypasses of requester.request; model code is also AST guarded.
    if phase in READ_PHASES:
        for verb in ("post", "put", "patch", "delete"):
            old = requester._pj_original_verbs[verb]

            def blocked(url: str, *args: Any, _verb: str = verb, _old: Any = old, **kwargs: Any) -> Any:
                if _verb == "post" and url.endswith("/auth/token"):
                    return _old(url, *args, **kwargs)
                deferred_events.append(("write_blocked", {"phase": phase,
                                                          "method": _verb, "api_path": url}))
                raise PermissionError("Direct write transport blocked in read-only phase")

            setattr(requester, "_" + verb, blocked)
    return audit


def flush_guard_events(raw: Path, deferred_events: list[tuple[str, dict[str, Any]]]) -> None:
    """Persist requester events only after world.execute restores native I/O."""
    while deferred_events:
        event, payload = deferred_events.pop(0)
        prior.log(raw, event, **payload)


def render_native_prompt(world: Any, parser: Any, extra: str) -> list[dict[str, str]]:
    if world.task.ground_truth is not None:
        raise RuntimeError("Ground truth loaded into solver world")
    apps = [{"name": key, "description": value}
            for key, value in world.task.app_descriptions.items()]
    prompt = (
        "You are one AI agent using AppWorld's Python REPL to help the supervisor. "
        "For each exploratory turn, reply with exactly one ```python code block; the REPL "
        "output will be returned to you. When instructed to deliver a tagged JSON artifact, "
        "output that artifact instead of code. The REPL retains variables across your own turns. "
        "Access apps only through apis.*. Discover public functions with "
        "apis.api_docs.show_api_descriptions(app_name='APP') and inspect each function with "
        "apis.api_docs.show_api_doc(app_name='APP', api_name='FUNCTION') before calling it. "
        "Credentials, if needed, are available through public supervisor APIs. "
        "Never invent IDs, people, amounts or credentials. Paginate where the API paginates. "
        "Do not access OS files, private benchmark data, evaluator functions or runtime internals. "
        "The file_system app is the user's simulated app, not the host OS.\n\n"
        "Supervisor: " + str(world.task.supervisor) + "\n"
        "Task: " + world.task.instruction + "\n"
        "Available apps: " + json.dumps(apps, ensure_ascii=False, separators=(",", ":")) +
        "\n\n" + extra
    )
    return [{"role": "user", "content": prompt}]


def parse_tag(answer: str, tag: str) -> Any | None:
    matches = re.findall(r"<" + tag + r">\s*(.*?)\s*</" + tag + r">", answer, re.S)
    if not matches:
        return None
    if len(matches) != 1 or "```python" in answer:
        raise ValueError("Ambiguous terminal artifact mixed with executable code")
    return json.loads(matches[0])


def validate_proposal(value: Any, observed_steps: set[int], secrets: Secrets) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"summary", "requests", "uncertainties"}:
        raise ValueError("Invalid proposal schema")
    if not isinstance(value["summary"], str) or not isinstance(value["uncertainties"], list) or not all(isinstance(x, str) for x in value["uncertainties"]):
        raise ValueError("Invalid proposal text")
    rows = value["requests"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 20:
        raise ValueError("Proposal must contain 1-20 requests")
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"recipient_email", "amount_usd", "basis", "source_steps"}:
            raise ValueError("Invalid proposal request schema")
        if (not isinstance(row["recipient_email"], str) or "@" not in row["recipient_email"]
                or type(row["amount_usd"]) not in (int, float) or not 0 < row["amount_usd"] < 100000
                or not isinstance(row["basis"], str) or not isinstance(row["source_steps"], list)
                or not row["source_steps"] or any(type(x) is not int or x not in observed_steps for x in row["source_steps"])):
            raise ValueError("Proposal row lacks grounded recipient, amount or source")
    if len(json.dumps(value, ensure_ascii=False).encode()) > 8192 or secrets.contains(value):
        raise ValueError("Proposal too large or contains credential material")
    return value


def validate_proposal_v2(value: Any, steps: list[dict[str, Any]],
                         secrets: Secrets) -> dict[str, Any]:
    read_steps = {row["step"] for row in steps if row["public_task_data_reads"] > 0}
    if not read_steps:
        raise ValueError("No public task-data read observation yet; inspect the world before proposing")
    proposal = validate_proposal(value, {row["step"] for row in steps}, secrets)
    for row in proposal["requests"]:
        if not read_steps.intersection(row["source_steps"]):
            raise ValueError("Each proposal row must cite a step with an actual public task-data GET")
    return proposal


def validate_judgment(value: Any, secrets: Secrets) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"verdict", "intends_to_use_proposal", "review_reason", "planned_repair"}:
        raise ValueError("Invalid pre-action judgment schema")
    if (value["verdict"] not in ("accept", "rework", "reject", "unknown")
            or type(value["intends_to_use_proposal"]) not in (bool, type(None))
            or (value["verdict"] == "unknown") != (value["intends_to_use_proposal"] is None)
            or not isinstance(value["review_reason"], str)
            or value["planned_repair"] is not None and not isinstance(value["planned_repair"], str)
            or len(json.dumps(value, ensure_ascii=False).encode()) > 4096
            or secrets.contains(value)):
        raise ValueError("Invalid or credential-bearing pre-action judgment")
    return value


def generate_with_retry(api: Any, messages: list[dict[str, str]], raw: Path,
                        max_tokens: int, state: dict[str, Any]) -> str:
    service_retries = 0
    while True:
        try:
            return api.generate(messages, max_tokens=max_tokens)
        except Exception as exc:
            timed_out = (isinstance(exc, TimeoutError)
                         or isinstance(getattr(exc, "reason", None), TimeoutError))
            if (timed_out and not state["timeout_retry_used"]
                    and state["world_execute_count"] == 0 and api.attempts < api.max_attempts):
                state["timeout_retry_used"] = True
                prior.log(raw, "transport_backoff", seconds=2, error_type="TimeoutError",
                          retry_kind="one_pre_world_timeout", charged_attempts=api.attempts)
                time.sleep(2)
                continue
            code = getattr(exc, "code", None)
            if code not in (429, 503) or service_retries >= 2 or api.attempts >= api.max_attempts:
                raise
            delay = (1, 2)[service_retries]
            service_retries += 1
            prior.log(raw, "transport_backoff", seconds=delay, status=code,
                      retry_index=service_retries, retry_kind="service",
                      charged_attempts=api.attempts)
            time.sleep(delay)


def phase_loop(world: Any, parser: Any, api: Any, messages: list[dict[str, str]],
               raw: Path, phase: str, terminal_tag: str | None, max_tokens: int,
               secrets: Secrets, audit: list[dict[str, Any]], state: dict[str, Any],
               validator: Any | None = None,
               deferred_events: list[tuple[str, dict[str, Any]]] | None = None
               ) -> tuple[Any | None, list[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []
    while api.attempts < api.max_attempts:
        answer = generate_with_retry(api, messages, raw, max_tokens, state)
        try:
            terminal = parse_tag(answer, terminal_tag) if terminal_tag else None
        except (ValueError, json.JSONDecodeError) as exc:
            if terminal_tag is None:
                raise
            state["validation_rejections"][phase] += 1
            prior.log(raw, "artifact_rejected", phase=phase, attempted_call=api.attempts,
                      error_type=type(exc).__name__, reason="malformed_terminal_artifact")
            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content":
                f"Validation error: malformed <{terminal_tag}> JSON or mixed executable code. "
                "Revise using only actual public observations. The rejected response consumed "
                "one model call; repair uses the remaining phase budget."})
            continue
        if terminal is not None:
            try:
                if validator is not None:
                    terminal = validator(terminal, steps)
            except ValueError as exc:
                state["validation_rejections"][phase] += 1
                reason = str(exc)
                prior.log(raw, "artifact_rejected", phase=phase, attempted_call=api.attempts,
                          error_type=type(exc).__name__, reason=reason, public_steps=len(steps))
                messages.append({"role": "assistant", "content": answer})
                messages.append({"role": "user", "content":
                    "Validation error: " + reason + ". Inspect public task data if needed, "
                    "then revise using only actual observed step numbers. The rejected response "
                    "consumed one model call and repair must fit the remaining phase budget."})
                continue
            prior.log(raw, "phase_artifact", phase=phase, artifact=terminal)
            messages.append({"role": "assistant", "content": answer})
            return terminal, steps
        code, fixed = parser.extract_code_and_fix_content(answer)
        if not code.strip():
            if terminal_tag is None:
                raise ValueError(f"{phase} response had no code or terminal artifact")
            state["validation_rejections"][phase] += 1
            prior.log(raw, "artifact_rejected", phase=phase, attempted_call=api.attempts,
                      reason="no_executable_code_or_terminal_artifact")
            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content":
                f"Validation error: provide public read code or a valid <{terminal_tag}> JSON artifact. "
                "This response consumed a model call; repair uses the remaining phase budget."})
            continue
        try:
            safe_code(code)
        except ValueError as exc:
            state["validation_rejections"].setdefault(phase, 0)
            state["validation_rejections"][phase] += 1
            reason = str(exc)
            prior.log(raw, "code_rejected", phase=phase, attempted_call=api.attempts,
                      reason=reason, executed=False)
            messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content":
                "Validation error: " + reason + ". The AppWorld `apis` object is already "
                "available in the REPL; do not import it. Use only public apis.* functions "
                "or emit the requested JSON artifact. This response consumed one call; "
                "continue within the remaining budget."})
            continue
        before = len(audit)
        observation = world.execute(code)
        if deferred_events is not None:
            flush_guard_events(raw, deferred_events)
        state["world_execute_count"] += 1
        if "Usage of the following function is not allowed: pathlib.Path.mkdir" in observation:
            raise RuntimeError("Native public API failed on runner I/O inside SafetyGuard")
        if "Unknown public API metadata" in observation:
            raise PermissionError("Unknown public API metadata inside REPL")
        if "Read-only actor attempted a task write" in observation or "Direct write transport blocked" in observation:
            raise PermissionError("Read-only API violation inside REPL")
        row = {"step": len(steps) + 1, "code": code, "observation": observation,
               "api_calls": len(audit) - before,
               "public_task_data_reads": sum(bool(call.get("public_read_observation"))
                                             for call in audit[before:])}
        steps.append(row)
        prior.log(raw, "environment_observation", phase=phase, **row)
        messages.append({"role": "assistant", "content": fixed + "\n\n"})
        messages.append({"role": "user", "content": "Output:\n```\n" + observation + "\n```\n\n"})
        if phase == "consumer_action" and world.task_completed():
            prior.log(raw, "native_task_completed", phase=phase)
            return None, steps
    if phase == "consumer_action":
        prior.log(raw, "policy_stopped", phase=phase, reason="action_call_budget")
        return None, steps
    raise RuntimeError(f"{phase} model call budget exhausted before terminal condition")


def usage(api: Any) -> dict[str, Any]:
    return {"attempts": api.attempts, "tokens": api.usage,
            "unknown_usage_attempts": api.unknown_usage_attempts,
            "api_errors": api.errors, "error_codes": api.error_codes,
            "returned_models": api.returned_models, "api_seconds": api.seconds}


def actual_use(proposal: dict[str, Any], action_calls: list[dict[str, Any]]) -> dict[str, Any]:
    writes = [row for row in action_calls if row["app"] == "venmo" and
              row["api"] == "create_payment_request"]

    def same_amount(value: Any, expected: float) -> bool:
        try:
            return abs(float(value) - expected) < 0.005
        except (TypeError, ValueError, OverflowError):
            return False

    matches, successful_matches, changed, missing = [], [], [], []
    for index, proposed in enumerate(proposal["requests"]):
        candidates = [row for row in writes if str(row["arguments"].get("user_email", "")).casefold() == proposed["recipient_email"].casefold()]
        exact = [row for row in candidates if same_amount(row["arguments"].get("amount"), proposed["amount_usd"])]
        if exact:
            matches.append(index)
            if any(row.get("payment_request_created") for row in exact):
                successful_matches.append(index)
        elif candidates:
            changed.append({"proposal_index": index, "actual_amounts": [row["arguments"].get("amount") for row in candidates]})
        else:
            missing.append(index)
    proposed_emails = {row["recipient_email"].casefold() for row in proposal["requests"]}
    extras = [row["arguments"].get("user_email") for row in writes
              if str(row["arguments"].get("user_email", "")).casefold() not in proposed_emails]
    return {"exact_proposal_rows_actually_actioned": matches,
            "exact_proposal_rows_successfully_created": successful_matches,
            "proposal_rows_reworked_in_action": changed,
            "proposal_rows_not_actioned": missing,
            "extra_action_recipients": extras,
            "proposal_actually_used": bool(matches),
            "proposal_successfully_applied": bool(successful_matches),
            "repair_or_rejection_recorded": bool(changed or missing or extras),
            "attribution_limit": "Request matching supports use evidence but does not prove the proposal caused the action."}


def sanitize_native_logs(native_dir: Path, secrets: Secrets) -> None:
    if not native_dir.exists():
        return
    for log_dir in native_dir.glob("tasks/*/logs"):
        for path in log_dir.rglob("*"):
            if path.is_file() and path.suffix in (".json", ".jsonl", ".txt", ".log", ".md"):
                raw = path.read_text(errors="replace")
                cleaned = secrets.scrub(raw)
                if raw != cleaned:
                    path.write_text(cleaned)


def install_native_log_scrubber(world: Any, native_dir: Path, secrets: Secrets) -> None:
    native_save_logs = world.save_logs

    def safe_save_logs() -> None:
        native_save_logs()
        sanitize_native_logs(native_dir, secrets)

    world.save_logs = safe_save_logs


def v4_first_consumer_response(cfg: dict[str, Any]) -> str:
    """Read the one rejected consumer turn from hash-pinned v4 evidence."""
    rows = [json.loads(line) for line in
            (ROOT / cfg["amends_v4"]["raw"]).read_text().splitlines()]
    sealed = [index for index, row in enumerate(rows)
              if row["event"] == "producer_sealed"]
    if len(sealed) != 1:
        raise RuntimeError("Expected exactly one v4 sealed producer artifact")
    later = rows[sealed[0] + 1:]
    starts = [row for row in later if row["event"] == "request_start"]
    responses = [row for row in later if row["event"] == "response"]
    observations = [row for row in later if row["event"] == "environment_observation"]
    prompt_rows = [row for row in later if row["event"] == "initial_prompt"
                   and row["payload"]["phase"] == "consumer_review"]
    if (len(starts) != 1 or len(responses) != 1 or observations
            or len(prompt_rows) != 1 or starts[0]["payload"]["attempt"] != 1
            or responses[0]["payload"]["attempt"] != 1
            or prompt_rows[0]["payload"]["prompt_sha256"] !=
               cfg["amends_v4"]["consumer_initial_prompt_sha256"]):
        raise RuntimeError("v4 consumer continuation boundary differs from contract")
    blocks = responses[0]["payload"]["response"].get("content", [])
    answer = "\n".join(block.get("text", "") for block in blocks
                       if block.get("type") == "text")
    if (sha_text(answer) != cfg["amends_v4"]["consumer_first_text_sha256"]
            or "[REDACTED]" in answer or "import apis" not in answer):
        raise RuntimeError("v4 rejected answer changed or was redacted")
    return answer


def episode(task_id: str, cfg: dict[str, Any]) -> dict[str, Any]:
    if task_id not in cfg["native_task_ids_in_order"]:
        raise ValueError("Task outside prospective population")
    out_root = ROOT / cfg["output_root"]
    manifest_path = out_root / "source_manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("Missing prospective v5 source snapshot")
    manifest = json.loads(manifest_path.read_text())
    if (prior.digest(__file__) != manifest["runner_sha256"]
            or prior.digest(CONFIG) != manifest["config_sha256"]
            or prior.digest(out_root / "runner_at_execution.py") != manifest["runner_sha256"]):
        raise RuntimeError("v5 runner/config differs from frozen execution snapshot")
    episode_dir = out_root / "episodes" / task_id
    episode_dir.mkdir(parents=True, exist_ok=False)
    raw = episode_dir / "raw.jsonl"
    secrets = Secrets()
    install_redacted_logging(secrets)
    started = prior.mono()
    suffix = sha_text(f"peerjudgment-v5:{task_id}:{prior.digest(CONFIG)}")[:18]
    experiments = {"consumer": "pj5_cons_" + suffix}
    native_dirs = {key: prior.APP / "experiments/outputs" / name for key, name in experiments.items()}
    result: dict[str, Any] = {"task_id": task_id, "status": "INVALID", "global_stop": False,
                              "experiment_names": experiments, "error": None,
                              "official_final_success": None, "usd_cost": None}
    apis: dict[str, Any] = {}
    deferred_events: list[tuple[str, dict[str, Any]]] = []
    state: dict[str, Any] = {"timeout_retry_used": False,
                             "world_execute_count": cfg["amends_v4"]["world_execute_count"],
                             "validation_rejections": {"consumer_review": 0,
                                                       "consumer_action": 0}}
    preexisting_native = {native for native in native_dirs.values() if native.exists()}
    try:
        if preexisting_native:
            raise RuntimeError(f"Refuse native-output overwrite: {sorted(map(str, preexisting_native))}")
        proposal = json.loads((ROOT / cfg["amends_v4"]["proposal"]).read_text())
        first_answer = v4_first_consumer_response(cfg)
        if secrets.contains(proposal):
            raise RuntimeError("Credential appeared in inherited producer artifact")
        prior.save(episode_dir / "proposal_from_v4.json", proposal)
        if prior.digest(episode_dir / "proposal_from_v4.json") != cfg["amends_v4"]["proposal_sha256"]:
            raise RuntimeError("Inherited proposal copy differs from v4 sealed artifact")
        AppWorld, parser = prior.initialize_runtime()
        provider = prior.load_provider()
        if provider["base"] != cfg["provider_endpoint_expected"]:
            raise RuntimeError("Provider endpoint mismatch")
        versions = {name: importlib.metadata.version(name)
                    for name in ("appworld", "openai", "freezegun", "jinja2")}
        prior.log(raw, "episode_config", task_id=task_id, config_sha256=prior.digest(CONFIG),
                  script_sha256=prior.digest(__file__), prompt_mode="v4_compact_consumer_resume",
                  appworld_commit=SOURCE_PIN, project_git_head=subprocess.check_output(
                      ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  provider={key: value for key, value in provider.items() if key != "secret"},
                  model=cfg["model_request"], temperature=cfg["temperature"],
                  seed=cfg["world_seed"], caps=cfg["attempted_call_caps_per_episode"],
                  amendment_version=cfg["version"], v4_results_sha256=cfg["amends_v4"]["results_sha256"],
                  inherited_proposal_sha256=cfg["amends_v4"]["proposal_sha256"],
                  inherited_consumer_response_sha256=cfg["amends_v4"]["consumer_first_text_sha256"],
                  timeout_retry_rule=cfg["transport_rule"]["timeout"],
                  validation_repair_rule=cfg["validation_repair_rule"],
                  host=platform.node(), python=sys.version, package_versions=versions,
                  command=sys.argv, evaluator_loaded_in_solver=False, usd_cost=None)

        with AppWorld(task_id=task_id, experiment_name=experiments["consumer"],
                      load_ground_truth=False, random_seed=cfg["world_seed"],
                      raise_on_extra_parameters=True) as consumer:
            install_native_log_scrubber(consumer, native_dirs["consumer"], secrets)
            review_audit = api_guard(consumer, "consumer_review", secrets, raw,
                                     deferred_events)
            consumer_messages = render_native_prompt(consumer, parser,
                "You are the independent CONSUMER. A producer in a separate world delivered "
                "only this proposal: <delivered_proposal>" + json.dumps(proposal, ensure_ascii=False) +
                "</delivered_proposal>. You may inspect your own public world before judging. "
                "For now, use only public read APIs and ordinary Python; no task writes, files "
                "or runtime internals. Before any write, emit exactly <judgment>{JSON}</judgment> "
                "outside any code fence with verdict (accept/rework/reject/unknown), "
                "intends_to_use_proposal (boolean or null), review_reason (public evidence), "
                "planned_repair (string or null). Your judgment is sealed before action.")
            if sha_text(consumer_messages[-1]["content"]) != cfg["amends_v4"]["consumer_initial_prompt_sha256"]:
                raise RuntimeError("Reconstructed consumer prompt differs from v4")
            prior.log(raw, "initial_prompt", phase="consumer_review",
                      prompt_sha256=sha_text(consumer_messages[-1]["content"]),
                      prompt_characters=len(consumer_messages[-1]["content"]))
            consumer_messages.append({"role": "assistant", "content": first_answer})
            consumer_messages.append({"role": "user", "content": cfg["repair_feedback"]})
            prior.log(raw, "inherited_rejected_consumer_turn",
                      source_raw_sha256=cfg["amends_v4"]["raw_sha256"],
                      response_sha256=sha_text(first_answer),
                      inherited_review_attempts=1, inherited_world_executes=0,
                      feedback=cfg["repair_feedback"])
            apis["consumer_review"] = prior.RealAPI(raw, cfg["attempted_call_caps_per_episode"]["consumer_review"])
            judgment_raw, review_steps = phase_loop(
                consumer, parser, apis["consumer_review"], consumer_messages, raw,
                "consumer_review", JUDGMENT_TAG, cfg["max_output_tokens_per_call"],
                secrets, review_audit, state,
                lambda value, steps: validate_judgment(value, secrets), deferred_events)
            judgment = judgment_raw
            prior.save(episode_dir / "pre_action_judgment.json", judgment)
            prior.log(raw, "pre_action_judgment_sealed", judgment=judgment,
                      judgment_sha256=prior.digest(episode_dir / "pre_action_judgment.json"),
                      public_review_steps=len(review_steps), public_review_api_calls=len(review_audit))
            # Gate changes after the judgment is durable. The same consumer keeps its
            # own conversation and REPL; producer variables never enter this world.
            action_audit = api_guard(consumer, "consumer_action", secrets, raw,
                                     deferred_events)
            consumer_messages.append({"role": "user", "content":
                "Your pre-action judgment is recorded. You may now act on your own world "
                "using public APIs. Complete the supervisor's task. Continue to inspect "
                "and repair as needed. Do not access private evaluator information."})
            apis["consumer_action"] = prior.RealAPI(raw, cfg["attempted_call_caps_per_episode"]["consumer_action"])
            _, action_steps = phase_loop(
                consumer, parser, apis["consumer_action"], consumer_messages, raw,
                "consumer_action", None, cfg["max_output_tokens_per_call"],
                secrets, action_audit, state, deferred_events=deferred_events)
            completed = consumer.task_completed()
            consumer.save()
            use = actual_use(proposal, action_audit)
            if secrets.contains(use):
                raise RuntimeError("Credential appeared in computed use record")
            prior.save(episode_dir / "actual_use.json", use)
            prior.log(raw, "consumer_action_sealed", actual_use=use,
                      actual_use_sha256=prior.digest(episode_dir / "actual_use.json"),
                      action_steps=len(action_steps), public_action_api_calls=len(action_audit))
            result.update(status="EXECUTED", valid_independent_handoff=True,
                          pre_action_judgment_recorded=True,
                          task_completed=completed,
                          action_stop_reason="supervisor_completed" if completed else "budget_exhausted",
                          **use)
        sanitize_native_logs(native_dirs["consumer"], secrets)

        # The evaluator is imported only after producer and consumer have closed.
        from appworld.evaluator import evaluate_task
        evaluation = evaluate_task(task_id=task_id, experiment_name=experiments["consumer"],
                                   suppress_errors=True, save_report=True).to_dict(stats_only=False)
        prior.save(episode_dir / "evaluator_only.json", secrets.scrub(evaluation))
        result.update(status="SCORED", official_final_success=bool(evaluation["success"]),
                      passed_assertions=len(evaluation["passes"]),
                      failed_assertions=len(evaluation["failures"]))
        prior.log(raw, "offline_evaluation", official_final_success=result["official_final_success"],
                  passed_assertions=result["passed_assertions"], failed_assertions=result["failed_assertions"])
    except Exception as exc:
        message = str(exc)
        result["error"] = {"type": type(exc).__name__, "message": secrets.scrub(message),
                           "traceback": secrets.scrub(traceback.format_exc())}
        result["global_stop"] = any(marker in message for marker in (
            "Provider endpoint", "named cc-switch provider", "AppWorld source pin",
            "Ground truth loaded", "Read-only API violation", "task mutation",
            "Unknown public API metadata", "Credential appeared", "native-output overwrite",
            "Native public API failed on runner I/O"))
        prior.log(raw, "episode_error", **result["error"], global_stop=result["global_stop"])
        try:
            from appworld import AppWorld
            AppWorld.close_all()
        except Exception:
            pass
    finally:
        flush_guard_events(raw, deferred_events)
        for native in native_dirs.values():
            if native not in preexisting_native:
                sanitize_native_logs(native, secrets)
        result["phase_costs"] = {key: usage(api) for key, api in apis.items()}
        result["validation_rejections"] = state["validation_rejections"]
        result["timeout_retry_used"] = state["timeout_retry_used"]
        result["world_execute_count"] = state["world_execute_count"]
        result["new_world_execute_count"] = (state["world_execute_count"]
                                             - cfg["amends_v4"]["world_execute_count"])
        result["inherited_review_attempts"] = 1
        result["inherited_producer_attempts"] = cfg["amends_v4"]["producer_attempts"]
        result["attempted_calls"] = sum(api.attempts for api in apis.values())
        result["wall_seconds"] = prior.mono() - started
        prior.save(episode_dir / "result.json", secrets.scrub(result))
        prior.log(raw, "episode_result", **result)
    return result


def run_all(cfg: dict[str, Any]) -> None:
    root = ROOT / cfg["output_root"]
    root.mkdir(parents=True, exist_ok=False)
    prior.save(root / "frozen_config.json", cfg)
    source = Path(__file__).read_bytes()
    (root / "runner_at_execution.py").write_bytes(source)
    prior.save(root / "source_manifest.json", {
        "runner_sha256": hashlib.sha256(source).hexdigest(),
        "config_sha256": prior.digest(CONFIG),
        "v4_runner_at_execution_sha256": cfg["amends_v4"]["runner_at_execution_sha256"],
        "v4_results_sha256": cfg["amends_v4"]["results_sha256"],
        "v4_proposal_sha256": cfg["amends_v4"]["proposal_sha256"],
        "development_only": True,
    })
    results = []
    for task_id in cfg["native_task_ids_in_order"]:
        # AppWorld freezes process-global time; each episode is a fresh process.
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    "_episode", task_id], cwd=ROOT, check=False)
        result_path = root / "episodes" / task_id / "result.json"
        if not result_path.exists():
            raise RuntimeError(f"Episode process ended without result: {task_id} exit={completed.returncode}")
        result = json.loads(result_path.read_text())
        results.append(result)
        prior.save(root / "partial_results.json", results)
        if result["global_stop"]:
            break
    prior.save(root / "results.json", {"task_ids_attempted": [r["task_id"] for r in results],
                                        "results": results, "no_confirmation_claim": True})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "run", "_episode"), nargs="?", default="check")
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()
    cfg = load_config()
    if args.command == "check":
        safe_code("print(apis.api_docs.show_app_descriptions())")
        print(json.dumps({"status": "contract_ok_no_api_calls", "config_sha256": prior.digest(CONFIG),
                          "tasks": cfg["native_task_ids_in_order"]}))
    elif args.command == "run":
        if args.task_id:
            parser.error("run does not accept a task override")
        run_all(cfg)
    else:
        if args.task_id not in cfg["native_task_ids_in_order"]:
            parser.error("Internal episode task outside frozen population")
        result = episode(args.task_id, cfg)
        print(json.dumps({"task_id": args.task_id, "status": result["status"],
                          "global_stop": result["global_stop"]}))


if __name__ == "__main__":
    main()
