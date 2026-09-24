"""Zero-LLM vertical slice for the peer-delivery evidence protocol.

This is an integration fixture, not a scientific experiment.  It exercises the
thin protocol we must add around OpenHands SDK:

    DeliveryEnvelope -> ConsumerGate judgment -> actual use/repair -> append-only ledger

The OpenHands SDK is used only for the agent/tool/event loop.  The delivery,
judgment and provenance semantics are implemented here so they cannot be
mistaken for an SDK feature.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, Sequence


RESERVED_PRE_JUDGMENT_KEYS = {"terminal_outcome", "evaluator_score", "gold_answer"}
ALLOWED_JUDGMENTS = {"accept", "reject", "repair", "independent_redo"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DeliveryEnvelope:
    delivery_id: str
    task_id: str
    producer_id: str
    artifact_name: str
    artifact_text: str
    artifact_sha256: str
    source_event_id: str

    @classmethod
    def create(
        cls,
        *,
        delivery_id: str,
        task_id: str,
        producer_id: str,
        artifact_name: str,
        artifact_text: str,
        source_event_id: str,
    ) -> "DeliveryEnvelope":
        return cls(
            delivery_id=delivery_id,
            task_id=task_id,
            producer_id=producer_id,
            artifact_name=artifact_name,
            artifact_text=artifact_text,
            artifact_sha256=sha256_text(artifact_text),
            source_event_id=source_event_id,
        )

    def public_context(self) -> dict[str, Any]:
        """What the recipient may see before acting; no evaluator truth."""

        return {
            "delivery_id": self.delivery_id,
            "task_id": self.task_id,
            "producer_id": self.producer_id,
            "artifact_name": self.artifact_name,
            "artifact_text": self.artifact_text,
            "artifact_sha256": self.artifact_sha256,
            "source_event_id": self.source_event_id,
        }


class AppendOnlyLedger:
    """Hash-chained JSONL ledger with no in-place event mutation."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: list[dict[str, Any]] = []
        self._previous_hash = "GENESIS"

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not event_type or not isinstance(payload, dict):
            raise ValueError("event_type and payload are required")
        row = {
            "seq": len(self.rows),
            "event_type": event_type,
            "payload": payload,
            "previous_hash": self._previous_hash,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        row_hash = sha256_text(canonical_json(row))
        row["record_hash"] = row_hash
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(row) + "\n")
        self.rows.append(row)
        self._previous_hash = row_hash
        return row


class ConsumerGate:
    """Protocol-specific pre-action judgment and post-action use gate."""

    def __init__(self, envelope: DeliveryEnvelope, ledger: AppendOnlyLedger, workdir: Path):
        self.envelope = envelope
        self.ledger = ledger
        self.workdir = workdir
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.judgment: dict[str, Any] | None = None

    def receive(self) -> dict[str, Any]:
        context = self.envelope.public_context()
        leaked = RESERVED_PRE_JUDGMENT_KEYS.intersection(context)
        if leaked:
            raise AssertionError(f"evaluator information leaked before judgment: {sorted(leaked)}")
        self.ledger.append("delivery_visible", {"context": context})
        return context

    def judge(self, *, decision: str, rationale: str, intended_action: str) -> dict[str, Any]:
        if self.judgment is not None:
            raise AssertionError("judgment is immutable and can only be recorded once")
        if decision not in ALLOWED_JUDGMENTS:
            raise ValueError(f"unsupported judgment: {decision}")
        self.judgment = {
            "decision": decision,
            "rationale": rationale,
            "intended_action": intended_action,
        }
        return self.ledger.append(
            "recipient_judgment",
            {
                "delivery_id": self.envelope.delivery_id,
                "consumer_id": "consumer-1",
                "judgment": self.judgment,
                "visible_evidence": [self.envelope.artifact_sha256],
                "terminal_outcome_available": False,
            },
        )

    def apply(self, *, action: str, repair_note: str = "") -> dict[str, Any]:
        if self.judgment is None:
            raise AssertionError("consumer must seal a judgment before acting")
        used = self.judgment["decision"] in {"accept", "repair"}
        if self.judgment["decision"] == "reject":
            used = False
        if self.judgment["decision"] == "independent_redo":
            used = False

        output_text = self.envelope.artifact_text if used else "independent-redo-output"
        if used and self.judgment["decision"] == "repair":
            output_text += f"\n# repair: {repair_note}"
        output_path = self.workdir / "consumer_output.txt"
        output_path.write_text(output_text, encoding="utf-8")
        return self.ledger.append(
            "consumer_action",
            {
                "delivery_id": self.envelope.delivery_id,
                "consumer_id": "consumer-1",
                "action": action,
                "used_artifact": used,
                "artifact_sha256": self.envelope.artifact_sha256 if used else None,
                "repair_note": repair_note,
                "output_sha256": sha256_text(output_text),
                "output_path": str(output_path),
            },
        )


def _sdk_tools(gate: ConsumerGate):
    """Build OpenHands SDK tools lazily so protocol classes remain dependency-free."""

    from openhands.sdk.tool import Action, Observation, Tool, ToolDefinition, ToolExecutor, register_tool
    from pydantic import Field

    class ReceiveAction(Action):
        request: str = Field(default="show_delivery")

    class ReceiveObservation(Observation):
        result: str

        @property
        def to_llm_content(self) -> Sequence[Any]:
            from openhands.sdk.llm import TextContent

            return [TextContent(text=self.result)]

    class ReceiveExecutor(ToolExecutor[ReceiveAction, ReceiveObservation]):
        def __call__(self, action: ReceiveAction, conversation=None) -> ReceiveObservation:
            return ReceiveObservation(result=canonical_json(gate.receive()))

    class ReceiveTool(ToolDefinition[ReceiveAction, ReceiveObservation]):
        name: ClassVar[str] = "receive_delivery"

        @classmethod
        def create(cls, conv_state=None, *, executor: ToolExecutor, **params):
            return [
                cls(
                    description="Expose the bounded producer delivery before any action.",
                    action_type=ReceiveAction,
                    observation_type=ReceiveObservation,
                    executor=executor,
                )
            ]

    class JudgeAction(Action):
        decision: str
        rationale: str
        intended_action: str

    class JudgeExecutor(ToolExecutor[JudgeAction, ReceiveObservation]):
        def __call__(self, action: JudgeAction, conversation=None) -> ReceiveObservation:
            row = gate.judge(
                decision=action.decision,
                rationale=action.rationale,
                intended_action=action.intended_action,
            )
            return ReceiveObservation(result=canonical_json(row["payload"]))

    class JudgeTool(ToolDefinition[JudgeAction, ReceiveObservation]):
        name: ClassVar[str] = "judge_delivery"

        @classmethod
        def create(cls, conv_state=None, *, executor: ToolExecutor, **params):
            return [
                cls(
                    description="Seal one recipient judgment before use.",
                    action_type=JudgeAction,
                    observation_type=ReceiveObservation,
                    executor=executor,
                )
            ]

    class ApplyAction(Action):
        action: str
        repair_note: str = ""

    class ApplyExecutor(ToolExecutor[ApplyAction, ReceiveObservation]):
        def __call__(self, action: ApplyAction, conversation=None) -> ReceiveObservation:
            row = gate.apply(action=action.action, repair_note=action.repair_note)
            return ReceiveObservation(result=canonical_json(row["payload"]))

    class ApplyTool(ToolDefinition[ApplyAction, ReceiveObservation]):
        name: ClassVar[str] = "apply_delivery"

        @classmethod
        def create(cls, conv_state=None, *, executor: ToolExecutor, **params):
            return [
                cls(
                    description="Use or repair the delivered artifact after judgment.",
                    action_type=ApplyAction,
                    observation_type=ReceiveObservation,
                    executor=executor,
                )
            ]

    tools = [
        ReceiveTool.create(executor=ReceiveExecutor())[0],
        JudgeTool.create(executor=JudgeExecutor())[0],
        ApplyTool.create(executor=ApplyExecutor())[0],
    ]
    for tool in tools:
        register_tool(tool.name, tool)
    return [Tool(name=tool.name) for tool in tools]


def run_fixture(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "fixture_id": "reuse2_openhands_protocol_20260924",
        "paid_api": False,
        "model": "openhands.sdk.testing.TestLLM",
        "task_id": "click-smoke-task-2800-fixture",
        "producer_id": "producer-1",
        "consumer_id": "consumer-1",
        "terminal_outcome_exposed_before_judgment": False,
    }
    (output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    ledger = AppendOnlyLedger(output_dir / "ledger.jsonl")
    envelope = DeliveryEnvelope.create(
        delivery_id="delivery-1",
        task_id=config["task_id"],
        producer_id=config["producer_id"],
        artifact_name="feature.patch",
        artifact_text="def feature():\n    return 'producer-v1'\n",
        source_event_id="producer-action-1",
    )
    ledger.append("producer_delivery", {"envelope": asdict(envelope)})
    gate = ConsumerGate(envelope, ledger, output_dir / "consumer_workspace")

    # Import the pinned runtime only for the agent/tool/event loop.
    from openhands.sdk.agent import Agent
    from openhands.sdk.conversation import Conversation
    from openhands.sdk.event import ActionEvent, Event, ObservationEvent
    from openhands.sdk.llm import Message, MessageToolCall, TextContent
    from openhands.sdk.testing import TestLLM

    tools = _sdk_tools(gate)
    scripted = TestLLM.from_messages(
        [
            Message(
                role="assistant",
                content=[TextContent(text="")],
                tool_calls=[
                    MessageToolCall(
                        id="call_receive",
                        name="receive_delivery",
                        arguments='{"request":"show_delivery"}',
                        origin="completion",
                    )
                ],
            ),
            Message(
                role="assistant",
                content=[TextContent(text="")],
                tool_calls=[
                    MessageToolCall(
                        id="call_judge",
                        name="judge_delivery",
                        arguments=json.dumps(
                            {
                                "decision": "accept",
                                "rationale": "artifact matches the requested feature contract",
                                "intended_action": "use_delivery",
                            }
                        ),
                        origin="completion",
                    )
                ],
            ),
            Message(
                role="assistant",
                content=[TextContent(text="")],
                tool_calls=[
                    MessageToolCall(
                        id="call_apply",
                        name="apply_delivery",
                        arguments='{"action":"integrate_patch","repair_note":""}',
                        origin="completion",
                    )
                ],
            ),
            Message(role="assistant", content=[TextContent(text="handoff complete")]),
        ],
        model="scripted-no-network",
    )

    callback_events: list[dict[str, Any]] = []

    def callback(event: Event) -> None:
        row: dict[str, Any] = {"event_type": type(event).__name__, "event_id": str(event.id)}
        if isinstance(event, ActionEvent):
            row["tool_name"] = event.tool_name
        if isinstance(event, ObservationEvent):
            row["tool_name"] = event.tool_name
            row["action_id"] = str(event.action_id)
        callback_events.append(row)
        with (output_dir / "openhands_events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(row) + "\n")

    workspace = output_dir / "agent_workspace"
    conversation = Conversation(
        agent=Agent(llm=scripted, tools=tools),
        workspace=workspace,
        persistence_dir=output_dir / "persistence",
        callbacks=[callback],
        max_iteration_per_run=8,
        delete_on_close=False,
    )
    conversation.send_message(
        "Receive the delivery, seal a recipient judgment before acting, then use it and stop."
    )
    conversation.run()

    result = {
        "fixture_id": config["fixture_id"],
        "conversation_status": str(conversation.state.execution_status),
        "callback_event_count": len(callback_events),
        "ledger_event_types": [row["event_type"] for row in ledger.rows],
        "ledger_event_count": len(ledger.rows),
        "ledger_final_hash": ledger.rows[-1]["record_hash"] if ledger.rows else None,
        "judgment_before_action": [
            row["event_type"] for row in ledger.rows
        ].index("recipient_judgment") < [row["event_type"] for row in ledger.rows].index("consumer_action"),
        "terminal_outcome_exposed_before_judgment": config[
            "terminal_outcome_exposed_before_judgment"
        ],
        "consumer_output_exists": (output_dir / "consumer_workspace/consumer_output.txt").exists(),
        "paid_api": False,
    }
    (output_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/experiments/aamas2027/reuse2_openhands_protocol_20260924"),
    )
    args = parser.parse_args()
    result = run_fixture(args.output_dir)
    print(json.dumps(result, indent=2))
    return 0 if result["conversation_status"].endswith("FINISHED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
