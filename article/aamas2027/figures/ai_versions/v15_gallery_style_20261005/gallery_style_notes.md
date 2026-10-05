# Figure 1 v15: gallery-grounded style notes

## Why this pass exists

Figure 1 v14 is semantically readable, but its pastel panels, gradients, repeated rounded cards, and large clip-art-like icons make it look like a product infographic. The top-conference samples in the local gallery use a different visual grammar: the figure is a compact explanation of a mechanism, not a collection of UI cards.

## Reference set inspected

- `AAAI 2024 — ProAgent: Building Proactive Cooperative Agents with Large Language Models` (`/tmp/topconf_agent_samples/119_aaai_2024.jpg`)
- `AAAI 2025 — MAPF-GPT: Imitation Learning for Multi-Agent Pathfinding at Scale` (`/tmp/topconf_agent_samples/243_aaai_2025.jpg`)
- `NeurIPS 2025 — A-LAMP: Agentic LLM-Based Framework for Automated MDP Modeling and Policy Generation` (`/tmp/topconf_agent_samples/3144_neurips_2025.jpg`)
- `NeurIPS 2025 — Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?` (`/tmp/topconf_agent_samples/3186_neurips_2025.jpg`)
- `NeurIPS 2025 — AgentBreeder: Mitigating the AI Safety Risks of Multi-Agent Scaffolds via Self-Improvement` (`/tmp/topconf_agent_samples/3478_neurips_2025.jpg`)
- `AAAI 2024 — Repair Is Nearly Generation` (`/tmp/topconf_arch_samples/09_aaai_2023_pipeline.jpg`, gallery metadata labels it as a pipeline exemplar)

## Observable visual rules

1. Use a white or near-white page background. Separate regions with whitespace, a thin rule, or one restrained dashed boundary; do not tint every region with a gradient.
2. Give the main mechanism one visual spine. The samples use a small number of strong arrows and a clear reading direction; they do not place every noun in its own card.
3. Use one dominant dark ink color and at most two or three muted accents. Color should encode a relation or stage, not decorate every object.
4. Use consistent thin strokes and mostly flat fills. Avoid glow, bevels, drop shadows, glossy 3-D cylinders, emoji, and stock-illustration icons.
5. Keep labels short and typographic. A label should identify a state, operation, or signal (`judge`, `ledger`, `read`, `assign`), while the caption explains the semantics. Do not turn the figure into a paragraph of boxed text.
6. Use a small legend only when a color or line style is reused. The samples do not repeat the same explanatory prose inside multiple panels.
7. Preserve semantic hierarchy: situated episode on the left, protocol spine in the center, selection and delayed outcome on the right. The visual treatment should make the causal path obvious before a reader reads individual labels.

## v15 acceptance checks

- At a two-column PDF width, the mechanism remains legible without zooming.
- No more than one top-level panel boundary encloses the protocol spine; peer context, episode, and outcome can be lightweight side annotations.
- No gradient fill, glow, bevel, or cartoon/stock icon remains.
- The causal path `producer -> artifact -> recipient signal -> judgment -> attribution -> ledger -> state read -> selector -> outcome -> later read` is visible from arrows and position alone.
- Exact semantic anchors retained: `P`, `R`, `JUDGE`, `OWN/UNK`, `LEDGER`, `v_t`, `READ`, `EXPLORE`, `SEAL`, `ASSIGN`, `QUALITY`, `COST`, `FUTURE`.
- If the generated edit corrupts labels or arrow direction, preserve it as a failed candidate and do not promote it.
