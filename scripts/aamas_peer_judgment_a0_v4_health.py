#!/usr/bin/env python3
"""One separately budgeted real provider health call for A0; run only when authorized."""
from __future__ import annotations

import json
from pathlib import Path
import traceback

import aamas_peer_judgment_a0_v4 as a0
import aamas_real_probe as prior
import aamas_peer_judgment_smoke_v4 as base


def main() -> None:
    cfg = a0.load_config()
    root = a0.ROOT / cfg["preflight"]["paths"]["provider_health"]
    root.mkdir(parents=True, exist_ok=False)
    raw = root / "raw.jsonl"
    secrets = base.Secrets()
    a0.safe_log(secrets)
    result = {"ok": False, "config_sha256": prior.digest(a0.CONFIG),
              "runner_sha256": prior.digest(a0.__file__),
              "health_script_sha256": prior.digest(__file__),
              "llm_api_attempt_cap": 1, "llm_api_attempts": 0,
              "response_sha256": None, "response_text": None, "usage": None,
              "error": None}
    prior.log(raw, "health_config", config_sha256=result["config_sha256"],
              runner_sha256=result["runner_sha256"],
              script_sha256=result["health_script_sha256"],
              provider_name=cfg["provider_name"], model=cfg["model_request"],
              expected_endpoint=cfg["provider_endpoint_expected"], llm_api_attempt_cap=1,
              task_attempts_charged=0)
    try:
        provider = prior.load_provider()
        if provider["base"] != cfg["provider_endpoint_expected"]:
            raise a0.InfrastructureError("Provider endpoint mismatch")
        api = prior.RealAPI(raw, 1)
        response = api.generate([{"role": "user", "content": "Reply with exactly OK."}],
                                max_tokens=32)
        result.update(ok=bool(response.strip()), llm_api_attempts=api.attempts,
                      response_sha256=a0.sha_text(response),
                      response_text=secrets.scrub(response), usage=a0.usage(api))
        if not result["ok"]:
            raise RuntimeError("Provider returned empty health response")
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": secrets.scrub(str(exc)),
                           "traceback": secrets.scrub(traceback.format_exc())}
        prior.log(raw, "health_error", **result["error"])
    finally:
        prior.save(root / "result.json", secrets.scrub(result))
        prior.log(raw, "health_result", **result)
    print(a0.canonical(result))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
