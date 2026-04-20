"""Patch ReAgent's Agent/agent.py: add missing `Agent` class BEFORE BlackSheep.

Upstream ReAgent has classes `BlackSheep(Agent)`, `Thinker(Agent)`,
`Human(Agent)` that reference `Agent` which is never defined in the module.
We insert a compatibility Agent class between BaseAgent and BlackSheep.
"""
from pathlib import Path

p = Path("/media/data3/dengkw/idea04/external_baselines/reagent/Agent/agent.py")
src = p.read_text(encoding="utf-8")

MARKER = "# ---------- r41b compatibility shim: Agent alias ----------"
if MARKER in src:
    # Remove the (incorrectly appended) prior patch so we can re-insert properly.
    before_marker, _ = src.split(MARKER, 1)
    src = before_marker.rstrip() + "\n"

lines = src.splitlines()
insert_at = None
for i, line in enumerate(lines):
    if line.startswith("class BlackSheep(Agent"):
        insert_at = i
        break
if insert_at is None:
    raise RuntimeError("Could not find `class BlackSheep(Agent` line in agent.py")

AGENT_BLOCK = [
    "",
    "# ---------- r41b compatibility shim: Agent alias ----------",
    "# Upstream ReAgent's moderator2/moderator/blacksheep/thinker/human all do",
    "# `from Agent.agent import Agent` but this class is never defined. We supply",
    "# a thin wrapper over BaseAgent that accepts (name, model) and stores model",
    "# on the instance, so downstream LLM calls can reference self.model.",
    "class Agent(BaseAgent):",
    "    def __init__(self, name: str, model: str = 'gpt-4.1-mini', message_bus=None):",
    "        super().__init__(name=name, message_bus=message_bus)",
    "        self.model = model",
    "    def vote(self, question: str, knowledges: str) -> int:",
    "        return 0  # default: no-revision",
    "    def say(self, message: str):",
    "        print(f'[{self.name}] {message}')",
    "",
]

# Insert before the BlackSheep class
new_lines = lines[:insert_at] + AGENT_BLOCK + lines[insert_at:]
p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
print(f"[r41b_fix_agent] inserted Agent class at line {insert_at+1} (before BlackSheep)")
print(f"[r41b_fix_agent] file now has {len(new_lines)} lines")
