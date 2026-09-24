from pathlib import Path
import json
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.local import LocalEnvironment
from minisweagent.models.test_models import DeterministicToolcallModel, make_toolcall_output

OUT = Path(__file__).resolve().parent
cmd1 = "printf proposal-v1"
cmd2 = "printf 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\\naccepted'"
def tc(call_id: str, command: str):
    return [{"id": call_id, "type": "function", "function": {"name": "bash", "arguments": json.dumps({"command": command})}}]
outputs = [
    make_toolcall_output("producer delivery", tc("call-1", cmd1), [{"command": cmd1, "tool_call_id": "call-1"}]),
    make_toolcall_output("finish", tc("call-2", cmd2), [{"command": cmd2, "tool_call_id": "call-2"}]),
]
model = DeterministicToolcallModel(outputs=outputs)
agent = DefaultAgent(
    model=model,
    env=LocalEnvironment(),
    system_template="You are a bounded test agent.",
    instance_template="{{task}}",
    step_limit=4,
    cost_limit=10,
)
info = agent.run("record and submit one proposal")
traj = agent.serialize()
(OUT / "trajectory.json").write_text(json.dumps(traj, indent=2), encoding="utf-8")
summary = {
    "exit_status": info.get("exit_status"),
    "submission": info.get("submission"),
    "api_calls": agent.n_calls,
    "trajectory_messages": len(agent.messages),
    "tool_observations": sum(1 for msg in agent.messages if msg.get("role") == "tool"),
}
(OUT / "result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
with (OUT / "raw.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps({"event":"completed","summary":summary}, ensure_ascii=False)+"\n")
print(json.dumps(summary, indent=2))
