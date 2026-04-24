"""openai_compat_shim — redirect MAD's legacy ``openai==0.27.6`` calls to newapi.

MAD (Du et al. 2024, ``llm_multiagent_debate``) uses the legacy
``openai.ChatCompletion.create(...)`` API style, with an implicit reliance on
``openai.api_key`` + ``openai.api_base`` module-level globals.  Our project's
canonical LLM endpoint is now ``newapi`` (``xh.v1api.cc``) per
``configs/llm.json`` (set as PRIMARY 2026-04-20 per U-EXEC-001).

Importing this shim **before** any MAD module reconfigures ``openai`` globals so
that the rest of MAD's code paths transparently route to our endpoint, without
us having to monkeypatch any MAD source file.

Usage in any MAD-derived script (gen_math.py, gen_gsm.py, etc.)::

    # MUST be the first line — before ``import openai`` lower in the file.
    from openai_compat_shim import shim_active, RESOLVED_MODEL  # noqa: F401
    ...
    completion = openai.ChatCompletion.create(
        model=RESOLVED_MODEL,   # NOT "gpt-3.5-turbo-0301" anymore
        messages=...,
        n=1,
    )

If a script passes a stale ``model="gpt-3.5-turbo-..."``, the optional helper
``coerce_model(model_name)`` swaps it to ``RESOLVED_MODEL`` per the project's
canonical-backbone rule (per ``experiment.md §1.3``: gpt-4.1-mini for mainline).

This shim is **isolated to ``external_baselines/mad/``**; it does NOT touch the
production code path under ``workspace/idea04_core/``.  Per ENGINEER_TODO
[u_018_mad_landed_20260420] E-016 ticket spec C-3, MAD adapter work must NOT
monkeypatch the global ``openai`` package in a way that pollutes our
``llm_client.py`` Stage-1 pipeline (which uses ``urllib`` directly, not the
``openai`` package, so this shim is doubly safe).

Forensic dispatch source: ENGINEER_TODO [E-017_migration_landed_ack_20260420]
sub-block "Hold/Defer items".
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Locate configs/llm.json — search up from this file until we find idea04 root.
# ---------------------------------------------------------------------------
_THIS = Path(__file__).resolve()


def _locate_idea04_root() -> Path:
    """Walk upward looking for the canonical configs/llm.json marker."""
    for ancestor in [_THIS] + list(_THIS.parents):
        candidate = ancestor / "configs" / "llm.json"
        if candidate.is_file():
            return ancestor
    raise RuntimeError(
        f"openai_compat_shim: could not locate configs/llm.json from {_THIS}; "
        "expected ancestor /media/data3/dengkw/idea04/ on server."
    )


_REPO_ROOT = _locate_idea04_root()
_LLM_JSON = _REPO_ROOT / "configs" / "llm.json"


def _ensure_v1_suffix(base_url: str) -> str:
    base = (base_url or "").strip().rstrip("/")
    if not base:
        return base
    if base.endswith("/v1") or "/v1/" in base:
        return base
    return base + "/v1"


def _load_newapi_creds() -> tuple[str, str, str]:
    """Return (base_url_with_v1, api_key, canonical_model)."""
    cfg: dict[str, Any] = json.loads(_LLM_JSON.read_text(encoding="utf-8"))
    na = cfg.get("newapi", {})
    if not (isinstance(na, dict) and na.get("base_url") and na.get("key")):
        raise RuntimeError(
            f"openai_compat_shim: configs/llm.json has no usable 'newapi' "
            f"block (got: {sorted(na.keys()) if isinstance(na, dict) else type(na).__name__})"
        )
    status = str(na.get("_status", "")).upper()
    if not status.startswith("PRIMARY"):
        # Soft warn — we still proceed, but flag because non-PRIMARY = mid-rotation
        print(
            f"[mad_shim] WARN: newapi._status = {status!r} (expected PRIMARY); "
            "proceeding anyway. If you see ModelDriftError, check configs/llm.json.",
            file=sys.stderr,
        )
    return (
        _ensure_v1_suffix(str(na["base_url"])),
        str(na["key"]),
        str(na.get("chat_model") or "gpt-4.1-mini"),
    )


_BASE_URL, _API_KEY, RESOLVED_MODEL = _load_newapi_creds()


# ---------------------------------------------------------------------------
# Apply the global redirect.  Done at import time so subsequent ``import openai``
# statements in MAD scripts pick up the new defaults.
# ---------------------------------------------------------------------------
import openai  # noqa: E402

openai.api_key = _API_KEY
openai.api_base = _BASE_URL

shim_active: bool = True

# Public alias for callers that want the canonical model name as a constant.
__all__ = ["shim_active", "RESOLVED_MODEL", "coerce_model"]


def coerce_model(model_name: str | None) -> str:
    """Replace any legacy ``gpt-3.5-...`` etc. with the project's canonical backbone.

    Called by patched MAD scripts to avoid silently sending a stale model id
    that is either no longer available on newapi or that violates the
    canonical-backbone rule in ``experiment.md §1.3``.
    """
    if not model_name:
        return RESOLVED_MODEL
    if model_name.startswith(("gpt-3.5", "gpt-4o-mini", "deepseek-")):
        return RESOLVED_MODEL
    if model_name.startswith("gpt-4.1-mini"):
        return RESOLVED_MODEL
    # any other explicit override (e.g. "gpt-4.1") — pass through as-is so
    # the caller's intent is honoured; downstream ModelDriftError will catch
    # any cross-family substitution at the response layer.
    return model_name


print(
    f"[mad_shim] Redirected openai.api_base = {_BASE_URL} "
    f"(canonical model: {RESOLVED_MODEL})",
    file=sys.stderr,
)
