#!/usr/bin/env python3
"""One real recipient-judgment API call for the TeamBench adapter.

The prompt contains only public task text, a candidate id/version, a workspace
digest, and a short diff summary.  It intentionally excludes reports,
expected.json, the grader, and terminal scores.  This is an interface smoke,
not an efficacy measurement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import aamas_real_probe as prior  # noqa: E402


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("response did not contain a JSON object")
    value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("response JSON is not an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "experiments" / "logs" /
                                                    "peerrolebench_real_judgment_20260925"))
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.jsonl"
    task_text = (
        "Repair the generated Python helper module so its public class, function, "
        "imports, type hints, and docstrings follow the stated style rubric."
    )
    prompt = f"""You are a recipient agent judging a peer artifact before execution.

Task description:
{task_text}

Candidate metadata:
- candidate_id: peer_02_repair
- producer_version: fixture-v1
- artifact_sha256: {'a' * 64}
- visible_changed_files: test_helpers.py
- visible_diff_summary: renamed public symbols to snake_case/PascalCase, sorted stdlib imports, added annotations and docstrings

You cannot see the grader, expected labels, reports, or any terminal score.
Return JSON only with this schema:
{{"decision":"accept|accept_with_rework|reject_redo|reject_reroute", "predicted_score":0.0, "confidence":0.0, "rubric_flags":["..."], "rationale":"..."}}
"""
    config = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider_name": "内部",
        "model": "qwen3.8-max",
        "temperature": 0,
        "max_tokens": 512,
        "prompt_sha256": digest(prompt),
        "terminal_feedback_visible": False,
        "reports_visible": False,
        "real_api_call_count": 0,
    }
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    # Python on this host is linked against LibreSSL and fails the direct
    # Idealab TLS handshake; curl is the supported direct transport here.  We
    # still load the same named cc-switch provider and make one real request.
    provider = prior.load_provider()
    started = time.monotonic()
    response: dict = {"event": "probe_start", "prompt_sha256": digest(prompt)}
    try:
        request = {
            "model": "qwen3.8-max",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0,
            "stream": False,
        }
        with raw.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "request_start",
                "provider": {k: v for k, v in provider.items() if k != "secret"},
                "model": request["model"],
                "max_tokens": request["max_tokens"],
                "temperature": request["temperature"],
                "prompt_sha256": digest(prompt),
                "prompt_characters": len(prompt),
            }, ensure_ascii=False) + "\n")
        request_path = out / "request.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
        proc = subprocess.run(
            [
                "curl", "--silent", "--show-error", "--fail-with-body",
                "--max-time", "120", "-H", "Content-Type: application/json",
                "-H", "Authorization: Bearer " + provider["secret"],
                "-H", "anthropic-version: 2023-06-01",
                "--data-binary", "@" + str(request_path),
                provider["base"] + "/v1/messages",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        request_path.unlink(missing_ok=True)
        if proc.returncode != 0:
            raise RuntimeError("curl failed: " + proc.stderr.strip()[:500])
        result = json.loads(proc.stdout)
        text = "\n".join(
            block.get("text", "") for block in result.get("content", [])
            if block.get("type") == "text"
        )
        if not text.strip():
            raise RuntimeError("successful response had no text content")
        parsed = extract_json(text)
        allowed = {"accept", "accept_with_rework", "reject_redo", "reject_reroute"}
        if parsed.get("decision") not in allowed:
            raise ValueError("invalid decision label")
        if not 0.0 <= float(parsed.get("predicted_score")) <= 1.0:
            raise ValueError("predicted_score outside [0,1]")
        if not 0.0 <= float(parsed.get("confidence")) <= 1.0:
            raise ValueError("confidence outside [0,1]")
        response.update({
            "event": "real_api_success",
            "response_text": text,
            "parsed_judgment": parsed,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "attempts": 1,
            "usage": result.get("usage", {}),
            "errors": 0,
            "returned_models": [result.get("model")],
        })
        config["real_api_call_count"] = 1
        (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        with raw.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(response, ensure_ascii=False) + "\n")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        response.update({
            "event": "real_api_failure",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "attempts": 1,
            "usage": {},
            "errors": 1,
            "returned_models": [],
        })
        with raw.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(response, ensure_ascii=False) + "\n")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
