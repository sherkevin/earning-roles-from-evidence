from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar, Sequence

from openhands.sdk.agent import Agent
from openhands.sdk.conversation import Conversation
from openhands.sdk.event import ActionEvent, Event, ObservationEvent
from openhands.sdk.llm import Message, MessageToolCall, TextContent
from openhands.sdk.testing import TestLLM
from openhands.sdk.tool import Action, Observation, Tool, ToolDefinition, ToolExecutor, register_tool

OUT = Path(__file__).resolve().parent


class EchoAction(Action):
    command: str


class EchoObservation(Observation):
    result: str

    @property
    def to_llm_content(self) -> Sequence[TextContent]:
        return [TextContent(text=self.result)]


class EchoExecutor(ToolExecutor[EchoAction, EchoObservation]):
    def __call__(self, action: EchoAction, conversation=None) -> EchoObservation:
        return EchoObservation(result=f"accepted:{action.command}")


class EchoTool(ToolDefinition[EchoAction, EchoObservation]):
    name: ClassVar[str] = "echo_delivery"

    @classmethod
    def create(cls, conv_state=None, *, executor: ToolExecutor, **params):
        return [
            cls(
                description="Record one bounded delivery event.",
                action_type=EchoAction,
                observation_type=EchoObservation,
                executor=executor,
            )
        ]


def main() -> None:
    raw = OUT / "raw.jsonl"
    events: list[dict] = []

    def callback(event: Event) -> None:
        row = {"event_type": type(event).__name__, "event_id": str(event.id)}
        if isinstance(event, ActionEvent):
            row["tool_name"] = event.tool_name
            row["action"] = event.action.model_dump() if event.action else None
        if isinstance(event, ObservationEvent):
            row["tool_name"] = event.tool_name
            row["action_id"] = str(event.action_id)
            row["observation"] = event.observation.model_dump() if event.observation else None
        events.append(row)
        with raw.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"event": "callback", "payload": row}, ensure_ascii=False) + "\n")

    scripted = TestLLM.from_messages(
        [
            Message(
                role="assistant",
                content=[TextContent(text="")],
                tool_calls=[
                    MessageToolCall(
                        id="call_delivery_1",
                        name="echo_delivery",
                        arguments='{"command":"proposal-v1"}',
                        origin="completion",
                    )
                ],
            ),
            Message(role="assistant", content=[TextContent(text="Delivery complete.")]),
        ],
        model="scripted-no-network",
    )
    register_tool("echo_delivery", EchoTool.create(executor=EchoExecutor())[0])
    agent = Agent(llm=scripted, tools=[Tool(name="echo_delivery")])
    conversation = Conversation(
        agent=agent,
        workspace=OUT / "workspace",
        persistence_dir=OUT / "persistence",
        callbacks=[callback],
        max_iteration_per_run=4,
        delete_on_close=False,
    )
    conversation.send_message("Submit one proposal and stop.")
    conversation.run()

    summary = {
        "event_count": len(events),
        "event_types": [e["event_type"] for e in events],
        "action_events": sum(e["event_type"] == "ActionEvent" for e in events),
        "observation_events": sum(e["event_type"] == "ObservationEvent" for e in events),
        "conversation_status": str(conversation.state.execution_status),
        "persistence_dir": str(OUT / "persistence"),
    }
    (OUT / "result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
