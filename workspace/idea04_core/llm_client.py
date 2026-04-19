import json
import os
import time
from collections.abc import Callable
from typing import Any

import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Endpoint / key resolution
#
# Backend selection is delegated to llm_providers.resolve_llm_chat_target().
# Summary:
#   configure_runtime(model_name) is called by the runner once per run.
#   It inspects the model name and config to select:
#     - nvidia    → NVIDIA NIM OpenAI-compatible endpoint + nvidia_key (optional RPM limit)
#     - oversea   → OpenAI-compatible endpoint + oversea_key (gpt-*, o*, oversea_model list)
#     - gptplus5  → OpenAI-compatible endpoint + gptplus5_key (same id rules as oversea)
#     - zhipu     → Zhipu GLM endpoint + KEY
#
# Manual overrides via env vars (take priority over auto-detection):
#   LLM_BACKEND=nvidia|oversea|gptplus5|zhipu
#   LLM_MODEL=<name>      → override resolved model name
#   LLM_API_KEY=<key>     → override API key
#   LLM_BASE_URL=<url>    → override URL (zhipu: full chat URL; oversea/gptplus5/nvidia: base /v1)
#   LLM_USE_SYSTEM_PROXY=1 → use system proxy (default: bypass proxy)
#   ZHIPU_API_KEY=<key>   → legacy env var for GLM key (still honoured)
#   ZHIPU_USE_SYSTEM_PROXY=1 → legacy proxy override (still honoured)
# ---------------------------------------------------------------------------

import re

from .llm_providers import load_llm_json, resolve_llm_chat_target


class ModelDriftError(BaseException):
    """Raised when the LLM provider silently changes the active model.

    Inherits from BaseException (not Exception) so that generic
    ``except Exception`` handlers in method code cannot swallow it and
    let a corrupt run continue writing garbage predictions.
    """


def _model_matches_contract(actual_model: str, intended_model: str) -> bool:
    """Return True when a provider response still honors the intended backbone.

    Some OpenAI-compatible providers return a dated/versioned model id such as
    ``gpt-4.1-mini-2025-04-14`` even when the requested canonical id was
    ``gpt-4.1-mini``. That should be treated as a valid match. Cross-family
    substitutions like ``gpt-4.1-mini`` -> ``gpt-5.1`` must still fail.
    """
    if not actual_model or not intended_model:
        return True
    if actual_model == intended_model:
        return True
    if actual_model.startswith(intended_model + "-"):
        return True
    return False


def _load_llm_config() -> dict[str, Any]:
    return load_llm_json()


# Module-level mutable runtime state (set by configure_runtime)
_runtime: dict[str, Any] = {
    "chat_url": "",
    "api_key": "",
    "model": "",
    "backend": "zhipu",
    "before_request": None,
    "enforce_model": False,   # when True, raise ModelDriftError on provider model mismatch
}

# The model name EXPLICITLY requested by the caller of configure_runtime()
# (i.e. the runner's main_model from the YAML config).  This is set BEFORE
# resolve_llm_chat_target() reads LLM_MODEL, so it always records the *intended*
# backbone even when an env override changes _runtime["model"].
# Used as the ground-truth contract in per-call integrity checks.
_contract_model: str = ""


def configure_runtime(model_name: str, enforce_model: bool = True) -> None:
    """Configure the active LLM backend from the model name.

    Called once per run by the runner. Sets module-level _runtime so that
    all subsequent call_llm() calls use the correct endpoint and key.

    Args:
        model_name: The intended backbone model (e.g. ``"gpt-4.1-mini"``).
        enforce_model: When True (default), any API response whose ``model``
            field differs from the resolved runtime model will raise
            ``ModelDriftError``, aborting the run immediately.  Set to False
            only for one-off debugging calls.

    Raises:
        RuntimeError: immediately if the LLM_MODEL env var would silently
            redirect to a different model than ``model_name``.  This is the
            startup integrity guard — it prevents a 7 000-sample run from
            writing garbage predictions against the wrong backbone.
    """
    global _runtime, _contract_model
    _contract_model = model_name   # record *intended* model BEFORE env resolution
    cfg = _load_llm_config()
    target = resolve_llm_chat_target(model_name, cfg)
    _runtime["chat_url"] = target.chat_url
    _runtime["api_key"] = target.api_key
    _runtime["model"] = target.model
    _runtime["backend"] = target.provider
    _runtime["before_request"] = target.before_request
    _runtime["enforce_model"] = enforce_model

    # ── Startup integrity guard ────────────────────────────────────────────
    # resolve_llm_chat_target() honours the LLM_MODEL env var, which means
    # configure_runtime("gpt-4.1-mini") silently becomes "gpt-5.1" when
    # LLM_MODEL=gpt-5.1 is set in the shell.  Fail fast here rather than
    # letting thousands of samples write garbage predictions.
    if _runtime["model"] != model_name:
        env_model   = os.environ.get("LLM_MODEL",   "<unset>")
        env_backend = os.environ.get("LLM_BACKEND", "<unset>")
        raise RuntimeError(
            f"[RUNTIME INTEGRITY GUARD] Startup model mismatch: "
            f"config requested '{model_name}' but runtime resolved to "
            f"'{_runtime['model']}'. "
            f"LLM_MODEL={env_model!r}, LLM_BACKEND={env_backend!r}. "
            f"Unset LLM_MODEL (or set it to '{model_name}') before running "
            f"a mainline experiment."
        )


def resolved_model() -> str:
    """Return the currently active model name (after configure_runtime).

    Returns the runtime-configured model if set, otherwise the import-time
    DEFAULT_MODEL fallback.  Always call configure_runtime() before starting
    a run so this reflects the intended backbone.
    """
    return _runtime["model"] or DEFAULT_MODEL


def _get_active_runtime() -> tuple[str, str, str, Callable[[], None] | None]:
    """Return (chat_url, api_key, model, before_request). Lazy-init if unset."""
    if _runtime["chat_url"] and _runtime["api_key"]:
        return (
            _runtime["chat_url"],
            _runtime["api_key"],
            _runtime["model"],
            _runtime.get("before_request"),
        )
    cfg = _load_llm_config()
    model = os.environ.get("LLM_MODEL") or cfg.get("chat_model", "glm-4-flash")
    t = resolve_llm_chat_target(model, cfg)
    return t.chat_url, t.api_key, t.model, t.before_request


# Legacy module-level aliases (computed at import time for backward compat)
_cfg0 = _load_llm_config()
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY") or _cfg0.get("KEY", "")
ZHIPU_BASE_URL = _cfg0.get("URL2", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
DEFAULT_MODEL = _cfg0.get("chat_model", "glm-4-flash")


def call_llm(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 512,
    retries: int = 3,
) -> dict[str, Any]:
    """Make an LLM API call, routing to the provider configured by configure_runtime().

    Args:
        messages: Chat messages list.
        model: Explicit model name override.  Pass ``None`` (default) to always
            use the model wired by ``configure_runtime()``.  If a non-None
            string is passed and a runtime contract is active, the pre-send
            check will raise ``ModelDriftError`` if it does not match the
            contract.  Only pass an explicit model string in one-off debugging
            scripts where ``configure_runtime()`` has not been called.
        temperature: Sampling temperature.
        max_tokens: Max completion tokens.
        retries: Number of retry attempts on transient errors.
    """
    chat_url, api_key, active_model, before_request = _get_active_runtime()

    # Resolve the effective model.
    # None (the default used by all methods.py call sites) always routes to
    # the runtime-configured model — no fragile string comparison needed.
    if model is None:
        model = _runtime["model"] or active_model or DEFAULT_MODEL

    # Pre-send contract check: compare the model we are about to send against
    # _contract_model (the intended backbone from the runner config), NOT against
    # _runtime["model"] (which may itself have been silently overridden by
    # LLM_MODEL env var).  Using _runtime["model"] as the reference would miss
    # exactly the gpt-5.1 env-override failure this guard is designed to catch.
    intended_model_pre: str = _contract_model or _runtime.get("model", "") or ""
    enforce: bool = bool(_runtime.get("enforce_model", False))
    if enforce and intended_model_pre and model != intended_model_pre:
        raise ModelDriftError(
            f"[RUNTIME INTEGRITY] call_llm() would send model={model!r} but "
            f"runtime contract requires {intended_model_pre!r}. "
            "Possible causes: LLM_MODEL env override, stale DEFAULT_MODEL default, "
            "or explicit model override in caller code. "
            "Run aborted to prevent writing garbage predictions."
        )

    if not api_key:
        raise RuntimeError(
            f"No API key found for backend '{_runtime.get('backend', 'zhipu')}'. "
            "Set ZHIPU_API_KEY (GLM), LLM_API_KEY, or keys in configs/llm.json."
        )

    payload = json.dumps(
        {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    ).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    use_proxy = (
        os.environ.get("LLM_USE_SYSTEM_PROXY", "").strip().lower() in ("1", "true", "yes")
        or os.environ.get("ZHIPU_USE_SYSTEM_PROXY", "").strip().lower() in ("1", "true", "yes")
    )

    for attempt in range(retries):
        try:
            if before_request:
                before_request()
            req = urllib.request.Request(chat_url, data=payload, headers=headers, method="POST")
            if use_proxy:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
            else:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                with opener.open(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

            # Post-response integrity check: verify the provider honoured our model.
            # Compare against _contract_model (runner intent) so that a provider
            # silently upgrading gpt-4.1-mini → gpt-5 would still be caught even
            # if configure_runtime() resolved correctly.
            if enforce and intended_model_pre:
                resp_model: str = result.get("model", "")
                if resp_model and not _model_matches_contract(resp_model, intended_model_pre):
                    raise ModelDriftError(
                        f"[RUNTIME INTEGRITY] Provider returned model={resp_model!r} "
                        f"but intended={intended_model_pre!r}. "
                        "The provider silently changed the active backbone. "
                        "Run aborted to prevent writing garbage predictions."
                    )
            # Inject sent-model metadata into result for per-call log tracing
            result["_sent_model"]    = model
            result["_sent_provider"] = _runtime.get("backend", "unknown")
            return result

        except ModelDriftError:
            raise  # never retry; always propagate immediately
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            # Check if the error body mentions a different model name — this is the
            # "provider rejected gpt-5.x that was silently sent" pattern.
            # Matches both "intended != sent" (caught above) and the case where
            # the provider itself names the offending model in its error body.
            if enforce and intended_model_pre:
                m_err = re.search(r"'([^']+)' model is not supported", body)
                if m_err and m_err.group(1) != intended_model_pre:
                    raise ModelDriftError(
                        f"[RUNTIME INTEGRITY] Provider error references unexpected model "
                        f"{m_err.group(1)!r} (contract={intended_model_pre!r}). "
                        "The provider rejected a request for a backbone different from "
                        "the runner contract. Run aborted."
                    ) from e
            if attempt < retries - 1:
                time.sleep(2**attempt)
            else:
                raise RuntimeError(f"LLM API error {e.code}: {body}")
        except Exception:
            if attempt < retries - 1:
                time.sleep(2**attempt)
            else:
                raise


def extract_text(response: dict[str, Any]) -> str:
    return response["choices"][0]["message"]["content"].strip()


def extract_usage(response: dict[str, Any]) -> dict[str, int] | None:
    """Return provider usage if present (Zhipu GLM-4 / OpenAI style `usage` block)."""
    u = response.get("usage")
    if not isinstance(u, dict):
        return None
    out: dict[str, int] = {}
    for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
        v = u.get(k)
        if v is not None:
            try:
                out[k] = int(v)
            except (TypeError, ValueError):
                pass
    return out or None


def extract_json_block(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON block found in: {text!r}")
    return json.loads(text[start:end])
