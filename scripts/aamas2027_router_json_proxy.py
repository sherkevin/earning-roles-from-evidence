#!/usr/bin/env python3
"""Loopback-only adapter from Codex router SSE to ordinary Responses JSON.

The user's local Codex router at 127.0.0.1:8317 intentionally emits
Responses API events as SSE even for non-streaming requests. AppWorld's
pinned OpenAI SDK expects a JSON Response object for stream=False.

This adapter changes transport only:
  AppWorld -> http://127.0.0.1:8318/v1/responses
           -> http://127.0.0.1:8317/v1/responses
It never stores or resolves the upstream provider credential.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def completed_response_from_sse(raw: str) -> dict:
    """Extract the final Response object from a Responses SSE transcript."""
    for block in reversed(raw.split("\n\n")):
        event = None
        data_lines: list[str] = []
        for line in block.splitlines():
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
        if event != "response.completed" or not data_lines:
            continue
        payload = json.loads("\n".join(data_lines))
        response = payload.get("response")
        if not isinstance(response, dict):
            raise ValueError("response.completed did not contain a response object")
        return response
    raise ValueError("No response.completed event found in upstream SSE")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    upstream = "http://127.0.0.1:8317"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[router-json-proxy] {self.address_string()} {fmt % args}")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, b'{"status":"ok"}\n', "application/json")
            return
        if self.path != "/v1/models":
            self._send(404, b'{"error":"not found"}\n', "application/json")
            return
        try:
            with urllib.request.urlopen(self.upstream + self.path, timeout=15) as response:
                body = response.read()
                self._send(response.status, body, response.headers.get_content_type())
        except Exception as exc:
            body = json.dumps({"error": str(exc)}).encode()
            self._send(502, body, "application/json")

    def do_POST(self) -> None:
        if self.path != "/v1/responses":
            self._send(404, b'{"error":"not found"}\n', "application/json")
            return
        length = int(self.headers.get("Content-Length", "0"))
        request_body = self.rfile.read(length)
        headers = {"Content-Type": "application/json"}
        if authorization := self.headers.get("Authorization"):
            headers["Authorization"] = authorization
        request = urllib.request.Request(
            self.upstream + self.path,
            data=request_body,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                raw = response.read().decode("utf-8", "replace")
                if response.headers.get_content_type() == "text/event-stream":
                    payload = completed_response_from_sse(raw)
                    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                    self._send(response.status, body, "application/json")
                else:
                    self._send(
                        response.status,
                        raw.encode("utf-8"),
                        response.headers.get_content_type(),
                    )
        except urllib.error.HTTPError as exc:
            self._send(
                exc.code,
                exc.read(),
                exc.headers.get_content_type() or "application/json",
            )
        except Exception as exc:
            body = json.dumps(
                {"error": {"message": str(exc), "type": type(exc).__name__}}
            ).encode("utf-8")
            self._send(502, body, "application/json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8318)
    parser.add_argument("--upstream", default="http://127.0.0.1:8317")
    args = parser.parse_args()
    Handler.upstream = args.upstream.rstrip("/")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(
        f"[router-json-proxy] listening on http://127.0.0.1:{args.port}; "
        f"upstream={Handler.upstream}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
