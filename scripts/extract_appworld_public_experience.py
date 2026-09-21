from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

INTERACTION_RE = re.compile(
    r"### Environment Interaction (\d+)\n-+\n"
    r"```python\n(.*?)\n```\n\n```\n(.*?)\n```",
    re.DOTALL,
)

SENSITIVE_KEYS = {
    "password", "access_token", "token", "email", "username",
    "phone_number", "card_number", "verification_code",
}


def iter_api_calls(code: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    calls: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Attribute)
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "apis"
        ):
            continue
        calls.append({
            "app": func.value.attr,
            "action": func.attr,
            "keyword_args": [kw.arg for kw in node.keywords if kw.arg],
            "positional_arg_count": len(node.args),
            "lineno": getattr(node, "lineno", None),
        })
    return sorted(calls, key=lambda item: (item["lineno"] is None, item["lineno"] or 0))


def load_api_doc(root: Path, app: str, action: str) -> dict[str, Any] | None:
    path = root / "data" / "api_docs" / "standard" / f"{app}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get(action)


def abstract_call(root: Path, call: dict[str, Any]) -> dict[str, Any]:
    doc = load_api_doc(root, call["app"], call["action"])
    params: list[dict[str, Any]] = []
    if doc:
        for item in doc.get("parameters", []):
            name = item.get("name")
            params.append({
                "name": name,
                "required": bool(item.get("required")),
                "binding": (
                    "<retrieve fresh from current task/context>"
                    if name in SENSITIVE_KEYS
                    else "<bind from current task or prior step>"
                ),
            })
    return {
        "app": call["app"],
        "action": call["action"],
        "description": doc.get("description") if doc else None,
        "parameters": params,
        "observed_keyword_args": call["keyword_args"],
        "observed_positional_arg_count": call["positional_arg_count"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--appworld-root", required=True)
    ap.add_argument("--run-task-dir", required=True)
    ap.add_argument("--source-task-id", required=True)
    ap.add_argument("--allow-app", action="append", required=True)
    ap.add_argument(
        "--allow-action", action="append",
        help="Optional exact app.action whitelist; repeat as needed.",
    )
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-text", required=True)
    args = ap.parse_args()

    root = Path(args.appworld_root)
    run_dir = Path(args.run_task_dir)
    trace_path = run_dir / "logs" / "environment_io.md"
    text = trace_path.read_text(encoding="utf-8", errors="replace")

    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    allowed = set(args.allow_app)
    allowed_actions = set(args.allow_action or [])

    for match in INTERACTION_RE.finditer(text):
        step = int(match.group(1))
        code = match.group(2)
        observation = match.group(3)
        # Public runtime feedback only. Never inspect evaluator/private truth here.
        if observation.lstrip().startswith("Execution failed."):
            continue
        for call in iter_api_calls(code):
            if call["app"] not in allowed:
                continue
            key = (call["app"], call["action"])
            if allowed_actions and f"{key[0]}.{key[1]}" not in allowed_actions:
                continue
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "source_step": step,
                "public_runtime_status": "execution_block_succeeded",
                "interface": abstract_call(root, call),
            })

    payload = {
        "source_task_id": args.source_task_id,
        "source_trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "allowed_apps": sorted(allowed),
        "allowed_actions": sorted(allowed_actions),
        "evaluator_private_truth_used": False,
        "records": records,
        "boundary": (
            "Derived only from the worker's own execution trace and public runtime "
            "success/failure. Concrete credentials, tokens and entity values are not retained."
        ),
    }

    lines = [
        "Validated private experience from earlier completed interactions:",
        "Use only when relevant. Re-bind all task-specific values in the current world.",
    ]
    for rec in records:
        iface = rec["interface"]
        required = [p["name"] for p in iface["parameters"] if p["required"]]
        lines.append(
            f"- {iface['app']}.{iface['action']}: "
            f"{iface.get('description') or 'validated API'} "
            f"Required parameters: {required or 'none'}."
        )
    lines.append(
        "This is scoped interface evidence, not an answer or a complete plan for the current task."
    )

    out_json = Path(args.out_json)
    out_text = Path(args.out_text)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_text.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    out_text.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "records": len(records),
        "apps": sorted(allowed),
        "out_json": str(out_json),
        "out_text": str(out_text),
    }, indent=2))


if __name__ == "__main__":
    main()
