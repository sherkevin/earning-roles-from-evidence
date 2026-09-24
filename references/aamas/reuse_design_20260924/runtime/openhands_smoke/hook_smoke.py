from __future__ import annotations
import json
from pathlib import Path
from openhands.sdk.hooks import HookConfig, HookDefinition, HookManager, HookMatcher
from openhands.sdk.hooks.types import HookEventType

OUT = Path(__file__).resolve().parent
cmd = "python3 -c 'import json,sys; e=json.load(sys.stdin); print(json.dumps({\"decision\":\"allow\",\"reason\":e.get(\"tool_name\",\"none\")}))'"
config = HookConfig(
    pre_tool_use=[HookMatcher(matcher="echo_delivery", hooks=[HookDefinition(command=cmd)])],
    post_tool_use=[HookMatcher(matcher="echo_delivery", hooks=[HookDefinition(command=cmd)])],
)
manager = HookManager(config=config, working_dir=str(OUT))
pre_continue, pre_results = manager.run_pre_tool_use("echo_delivery", {"command":"proposal-v1"})
post_results = manager.run_post_tool_use("echo_delivery", {"command":"proposal-v1"}, {"result":"accepted"})
summary = {
    "pre_continue": pre_continue,
    "pre": [r.model_dump() for r in pre_results],
    "post": [r.model_dump() for r in post_results],
    "hook_event_types": [HookEventType.PRE_TOOL_USE.value, HookEventType.POST_TOOL_USE.value],
}
(OUT / "hook_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
with (OUT / "raw.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps({"event":"hook_smoke_completed","summary":summary}, ensure_ascii=False)+"\n")
print(json.dumps(summary, indent=2))
