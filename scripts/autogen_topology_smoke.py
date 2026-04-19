import argparse
import asyncio
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from autogen_core import AgentId, DefaultInterventionHandler, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, rpc


@dataclass
class RouteMessage:
    task_id: str
    question: str
    path: list[str]
    hops_left: int


@dataclass
class SmokeResult:
    topology: str
    start_node: str
    final_node: str
    final_path: list[str]
    allowed_edges: list[list[str]]
    observed_edges: list[list[str]]
    violations: list[list[str]]
    send_count: int
    checks: dict[str, bool]


class RoutingLogIntervention(DefaultInterventionHandler):
    def __init__(self) -> None:
        self.send_events: list[dict[str, str]] = []

    async def on_send(self, message: Any, *, message_context: MessageContext, recipient: AgentId) -> Any:
        sender_type = "external" if message_context.sender is None else message_context.sender.type
        self.send_events.append(
            {
                "sender_type": sender_type,
                "recipient_type": recipient.type,
                "message_type": type(message).__name__,
            }
        )
        return message


class TopologyNode(RoutedAgent):
    def __init__(self, node_name: str, neighbor_names: list[str]) -> None:
        super().__init__(f"Topology node {node_name}")
        self.node_name = node_name
        self.neighbor_names = set(neighbor_names)

    @rpc
    async def on_route(self, message: RouteMessage, _ctx: MessageContext) -> RouteMessage:
        message.path.append(self.node_name)
        if message.hops_left <= 0 or not self.neighbor_names:
            return message

        next_node = sorted(self.neighbor_names)[0]
        message.hops_left -= 1
        return await self.send_message(
            message,
            recipient=AgentId(type=f"node.{next_node}", key="default"),
        )


def build_adjacency(topology: str) -> dict[str, list[str]]:
    if topology == "chain":
        return {
            "decomposer": ["evidence_seeker"],
            "evidence_seeker": ["verifier"],
            "verifier": ["synthesizer"],
            "synthesizer": [],
        }
    if topology == "star":
        return {
            "decomposer": ["evidence_seeker", "verifier", "synthesizer"],
            "evidence_seeker": ["decomposer"],
            "verifier": ["decomposer"],
            "synthesizer": ["decomposer"],
        }
    raise ValueError(f"Unsupported topology: {topology}")


async def run_smoke(topology: str) -> SmokeResult:
    adjacency = build_adjacency(topology)
    intervention = RoutingLogIntervention()
    runtime = SingleThreadedAgentRuntime(intervention_handlers=[intervention])

    for node_name, neighbors in adjacency.items():
        await TopologyNode.register(
            runtime,
            type=f"node.{node_name}",
            factory=lambda node_name=node_name, neighbors=neighbors: TopologyNode(node_name=node_name, neighbor_names=neighbors),
        )

    start_node = "decomposer"
    runtime.start()
    final_msg = await runtime.send_message(
        RouteMessage(
            task_id="smoke-task-001",
            question="Who discovered penicillin and when?",
            path=[],
            hops_left=3,
        ),
        recipient=AgentId(type=f"node.{start_node}", key="default"),
    )
    await runtime.stop_when_idle()
    await runtime.close()

    allowed_edges = {(f"node.{source}", f"node.{target}") for source, targets in adjacency.items() for target in targets}
    observed_edges: list[list[str]] = []
    violations: list[list[str]] = []

    for event in intervention.send_events:
        sender_type = event["sender_type"]
        recipient_type = event["recipient_type"]
        if sender_type == "external":
            continue
        observed_edges.append([sender_type, recipient_type])
        if (sender_type, recipient_type) not in allowed_edges:
            violations.append([sender_type, recipient_type])

    return SmokeResult(
        topology=topology,
        start_node=start_node,
        final_node=final_msg.path[-1] if final_msg.path else "",
        final_path=final_msg.path,
        allowed_edges=sorted([[src, dst] for src, dst in allowed_edges]),
        observed_edges=observed_edges,
        violations=violations,
        send_count=len(intervention.send_events),
        checks={
            "path_non_empty": len(final_msg.path) > 0,
            "no_topology_violation": len(violations) == 0,
            "messages_intercepted": len(intervention.send_events) > 0,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoGen fixed-topology smoke test.")
    parser.add_argument("--topology", choices=["chain", "star"], default="chain")
    parser.add_argument("--output", default="artifacts/round0/autogen_smoke_result.json")
    args = parser.parse_args()

    result = asyncio.run(run_smoke(topology=args.topology))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")

    if not all(result.checks.values()):
        raise SystemExit(f"Smoke checks failed: {result.checks}")

    print(f"Smoke succeeded for topology={result.topology}")
    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
