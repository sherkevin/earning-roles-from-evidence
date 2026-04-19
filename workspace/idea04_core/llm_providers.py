"""
LLM provider resolution and light-weight request gating.

configs/llm.json may use three top-level blocks (each with its own base URLs):

  zhipu    — URL, URL1, URL2, KEY, chat_model
  oversea  — base_url, key, models (OpenAI-compatible ids)
  gptplus5 — base_url, key, models (OpenAI-compatible; same routing rules as oversea)
  nvidia   — base_url, key, chat_model, note, max_requests_per_minute,
             route_slash_ids, models (NIM catalog ids; when non-empty, routing uses this list only)

Legacy flat keys are still accepted; see normalize_llm_config().

Environment (same semantics as llm_client):
  LLM_BACKEND   zhipu | oversea | gptplus5 | nvidia
  LLM_MODEL     override model id
  LLM_API_KEY   override API key
  LLM_BASE_URL  oversea/gptplus5/nvidia: base /v1; zhipu: full chat completions URL
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LLM_JSON_PATH = _REPO_ROOT / "configs" / "llm.json"

_NV_LIMITER_LOCK = threading.Lock()
_nvidia_limiter: Any = None
_nvidia_limiter_rpm: int | None = None


def normalize_llm_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Expand nested provider blocks (zhipu / oversea / gptplus5 / nvidia) to flat keys for resolvers.

    If the file is already legacy flat format (no provider objects), returns a copy of ``raw``.
    """
    if not raw:
        return {}
    z_block = raw.get("zhipu")
    o_block = raw.get("oversea")
    g5_block = raw.get("gptplus5")
    n_block = raw.get("nvidia")
    if not (
        isinstance(z_block, dict)
        or isinstance(o_block, dict)
        or isinstance(g5_block, dict)
        or isinstance(n_block, dict)
    ):
        return dict(raw)

    out: dict[str, Any] = {}
    z = z_block if isinstance(z_block, dict) else {}
    out["KEY"] = z.get("KEY", "")
    out["URL"] = z.get("URL", "")
    out["URL1"] = z.get("URL1", "")
    out["URL2"] = z.get("URL2", "")
    out["chat_model"] = z.get("chat_model", "glm-4-flash")

    o = o_block if isinstance(o_block, dict) else {}
    base_o = (o.get("base_url") or o.get("url") or "").strip().rstrip("/")
    out["oversea_url"] = base_o
    out["oversea_key"] = o.get("key", "")
    om = o.get("models")
    out["oversea_model"] = list(om) if isinstance(om, list) else []

    g5 = g5_block if isinstance(g5_block, dict) else {}
    base_g5 = (g5.get("base_url") or g5.get("url") or "").strip().rstrip("/")
    out["gptplus5_url"] = base_g5
    out["gptplus5_key"] = g5.get("key", "")
    g5m = g5.get("models")
    out["gptplus5_model"] = list(g5m) if isinstance(g5m, list) else []
    out["gptplus5_chat_model"] = g5.get("chat_model", "gpt-4.1-mini")

    n = n_block if isinstance(n_block, dict) else {}
    base_n = (n.get("base_url") or n.get("url") or "").strip().rstrip("/")
    out["nvidia_url"] = base_n
    out["nvidia_key"] = n.get("key", "")
    out["nvidia_chat_model"] = n.get("chat_model", "meta/llama-3.1-8b-instruct")
    out["nvidia_note"] = n.get("note", "")
    try:
        out["nvidia_max_requests_per_minute"] = int(n.get("max_requests_per_minute", 40))
    except (TypeError, ValueError):
        out["nvidia_max_requests_per_minute"] = 40
    nm = n.get("models")
    out["nvidia_model"] = list(nm) if isinstance(nm, list) else []
    out["nvidia_route_slash_ids"] = bool(n.get("route_slash_ids", True))

    return out


def load_llm_json(path: Path | str | None = None) -> dict[str, Any]:
    p = Path(path) if path else _LLM_JSON_PATH
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return normalize_llm_config(raw)


def _is_oversea_model(model_name: str, cfg: dict[str, Any]) -> bool:
    if model_name.startswith("gpt-") or model_name.startswith(("o1", "o3", "o4")):
        return True
    if model_name.startswith("chatgpt-"):
        return True
    oversea_list = cfg.get("oversea_model", [])
    if isinstance(oversea_list, list) and model_name in oversea_list:
        return True
    g5_list = cfg.get("gptplus5_model", [])
    if isinstance(g5_list, list) and model_name in g5_list:
        return True
    return False


def _is_nvidia_routable(model_name: str, cfg: dict[str, Any]) -> bool:
    if not (cfg.get("nvidia_key") or os.environ.get("LLM_API_KEY")):
        return False
    listed = cfg.get("nvidia_model")
    if isinstance(listed, list) and len(listed) > 0:
        return model_name in listed
    if cfg.get("nvidia_route_slash_ids", True) and "/" in model_name:
        if _is_oversea_model(model_name, cfg):
            return False
        return True
    return False


class _SlidingWindowLimiter:
    """At most `max_events` calls per `window_seconds` (thread-safe)."""

    def __init__(self, max_events: int, window_seconds: float) -> None:
        self.max_events = max_events
        self.window = window_seconds
        self._lock = threading.Lock()
        self._times: list[float] = []

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                self._times = [t for t in self._times if now - t < self.window]
                if len(self._times) < self.max_events:
                    self._times.append(now)
                    return
                wait = self.window - (now - self._times[0]) + 0.001
            time.sleep(max(wait, 0.01))


def _nvidia_before_request(rpm: int) -> Callable[[], None]:
    global _nvidia_limiter, _nvidia_limiter_rpm
    with _NV_LIMITER_LOCK:
        if _nvidia_limiter is None or _nvidia_limiter_rpm != rpm:
            _nvidia_limiter = _SlidingWindowLimiter(max_events=max(1, rpm), window_seconds=60.0)
            _nvidia_limiter_rpm = rpm
        lim = _nvidia_limiter

    def _go() -> None:
        lim.acquire()

    return _go


@dataclass(frozen=True)
class LLMChatTarget:
    provider: str
    chat_url: str
    api_key: str
    model: str
    before_request: Callable[[], None] | None = None


def resolve_llm_chat_target(model_name: str, cfg: dict[str, Any] | None = None) -> LLMChatTarget:
    """Pick provider, URL, key, and model for one chat/completions call."""
    cfg = cfg if cfg is not None else load_llm_json()

    force_backend = os.environ.get("LLM_BACKEND", "").strip().lower()
    override_model = os.environ.get("LLM_MODEL", "").strip()
    effective_model = override_model or model_name

    def oversea_target(m: str) -> LLMChatTarget:
        base_url = (os.environ.get("LLM_BASE_URL") or cfg.get("oversea_url", "")).rstrip("/")
        api_key = os.environ.get("LLM_API_KEY") or cfg.get("oversea_key", "")
        chat_url = f"{base_url}/chat/completions"
        model = m
        if not model or not _is_oversea_model(model, cfg):
            model = "gpt-4.1-mini"
        return LLMChatTarget("oversea", chat_url, api_key, model, None)

    def gptplus5_target(m: str) -> LLMChatTarget:
        base_url = (os.environ.get("LLM_BASE_URL") or cfg.get("gptplus5_url", "")).rstrip("/")
        api_key = os.environ.get("LLM_API_KEY") or cfg.get("gptplus5_key", "")
        chat_url = f"{base_url}/chat/completions"
        model = m
        if not model or not _is_oversea_model(model, cfg):
            model = str(cfg.get("gptplus5_chat_model") or "gpt-4.1-mini")
        return LLMChatTarget("gptplus5", chat_url, api_key, model, None)

    def nvidia_target(m: str) -> LLMChatTarget:
        base_url = (os.environ.get("LLM_BASE_URL") or cfg.get("nvidia_url", "")).rstrip("/")
        api_key = os.environ.get("LLM_API_KEY") or cfg.get("nvidia_key", "")
        chat_url = f"{base_url}/chat/completions"
        model = m
        if force_backend == "nvidia":
            if not model:
                model = str(cfg.get("nvidia_chat_model") or "meta/llama-3.1-8b-instruct")
        elif not model or not _is_nvidia_routable(model, cfg):
            model = str(cfg.get("nvidia_chat_model") or "meta/llama-3.1-8b-instruct")
        rpm = int(cfg.get("nvidia_max_requests_per_minute", 40))
        return LLMChatTarget("nvidia", chat_url, api_key, model, _nvidia_before_request(rpm))

    def zhipu_target(m: str) -> LLMChatTarget:
        chat_url = (
            os.environ.get("LLM_BASE_URL")
            or cfg.get("URL2", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        )
        api_key = (
            os.environ.get("ZHIPU_API_KEY")
            or os.environ.get("LLM_API_KEY")
            or cfg.get("KEY", "")
        )
        model = m
        if not model or model == "gpt-4.1-mini":
            model = str(cfg.get("chat_model", "glm-4-flash"))
        return LLMChatTarget("zhipu", str(chat_url).strip(), api_key, model, None)

    if force_backend == "nvidia":
        return nvidia_target(effective_model)
    if force_backend == "oversea":
        return oversea_target(effective_model)
    if force_backend == "gptplus5":
        return gptplus5_target(effective_model)
    if force_backend == "zhipu":
        return zhipu_target(effective_model)

    if _is_nvidia_routable(effective_model, cfg):
        return nvidia_target(effective_model)
    if _is_oversea_model(effective_model, cfg):
        return oversea_target(effective_model)
    return zhipu_target(effective_model)
