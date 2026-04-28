# Figure 2 Prompt - Detailed Double-Column EDO-Frame Pipeline

> Target: main Method architecture figure.
> Width: **two-column**.
> Reader takeaway: EDO-Frame is a locally organized, audited, memory/tool-governed pipeline, not a central planner or loose group chat.
> Evidence status: conceptual architecture; no empirical numbers.
> Governing style: `docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md`.
> Target asset: `artifacts/figures/fig2_edo_frame_pipeline_claude.{svg,pdf,png}`.

---

## 1. Why This Figure Exists

Figure 2 is the primary method figure. It should answer:

```text
How does an input task move through EDO-Frame, and where do delegation, memory, tools, audit, and reproducibility logs appear?
```

This figure should be more detailed than Figure 1 and should be given two-column space in the main paper. Figure 1 is now only a compact single-column comparison teaser.

## 2. Visual Reference And Style

Use the Claude Warm Minimalism style in:

```text
docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md
```

Use `docs/references/架构图/image4.png` as a structural reference:

```text
left side: large rounded warm workbench / stage
right side: repeated small mechanism diagrams
overall: paper-like background, warm tan / terracotta accents, tiny agents, generous whitespace
```

Do not copy `image4.png` literally. Translate its structure into the EDO-Frame pipeline.

## 3. Layout

Use a two-column landscape architecture layout with two major regions:

```text
Left 60%: "(a) Local EDO society" large warm workbench
Right 40%: "(b) Governed action cycle" stacked mini-mechanisms
Bottom full width: "(c) Logged evidence trail"
```

Canvas:

```text
wide two-column paper figure
pure white A4 page background #FFFFFF
warm rounded card interiors #F4F3EE or #FAF9F5
white sub-cards / chips #FFFFFF
terracotta accent #C15F3C
neutral grey #B1ADA1
deep text #191817
```

Main title:

```text
EDO-Frame pipeline: local organization, governed tools, auditable evidence
```

Keep the title short and visually quiet.

## 4. Left Region - Local EDO Society Workbench

Panel title:

```text
(a) Local EDO society
```

Visual structure:

```text
large rounded warm workbench card, inspired by image4.png
inside it, 4 identical tiny EDO agents arranged on a sparse local graph
agents sit in small white circular nodes
node labels: i, j, m, r
no extra stray node labels
```

Required elements:

```text
input task card on far left: "question + context"
task-tag chips: "decompose", "verify", "integrate"
budget chip: "hop budget"
four local agent nodes in a sparse graph
small local-view halos around each agent
solid terracotta arrows = delegation / forward action
dashed terracotta arrows = audit return
one small note-board card: "NoteBoard memory"
one small tool card: "Tag-gated tools"
one small envelope card: "Action schema"
one small shield/check card: "Audit"
```

Composition:

```text
input task card enters the workbench from left
agents are centered, not all-to-all
memory/tool/audit/action cards are around the graph perimeter, not central commanders
no large controller node
no central planner
no hierarchy that looks like a manager controlling all agents
```

The left region should communicate "local organization forms inside a constrained workbench."

## 5. Right Region - Governed Action Cycle Mini-Diagrams

Panel title:

```text
(b) Governed action cycle
```

Use four stacked mini-diagrams or a 2x2 grid, similar to the repeated small diagrams in `image4.png`.

Mini-diagram 1:

```text
Read local state
agent node reads task tags + local memory
```

Mini-diagram 2:

```text
Choose action
three tiny action chips: do / outsource / split
selected chip highlighted in terracotta
```

Mini-diagram 3:

```text
Use governed tools
agent connects to tool card only through tag gate
```

Mini-diagram 4:

```text
Audit and update
downstream response returns through audit shield
belief / persona tag chip updates
```

Right-region visual grammar:

```text
each mini-diagram is a white rounded card
use same tiny agent icon in each card
use thin neutral arrows for inactive paths
use terracotta for active selected path
avoid dense text
```

## 6. Bottom Rail - Reproducible Evidence Trail

Panel title:

```text
(c) Logged evidence trail
```

Draw a thin full-width rail under both main regions.

Log cards:

```text
routing traces
handoff packets
memory events
tool events
audit events
metrics
```

Final output cards on the right end:

```text
answer
evidence bundle
caveats
run provenance
```

Connect the left workbench and right action-cycle region down to the rail with thin neutral vertical lines. This should show that every action produces an auditable artifact trail.

## 7. Agent And Icon Rules

Use tiny consistent human-agent icons only where helpful. They should fit the Claude warm paper aesthetic:

```text
same silhouette everywhere
same pose everywhere
same scale everywhere
warm neutral clothing
terracotta node/accent for EDO active agents
white circular node backing
thin #B1ADA1 outline
```

Forbidden:

```text
different hairstyles / genders / outfits
robots
anime characters
smooth vector avatar mixed with pixel avatar
duplicate "Peer j"
stray label "k"
typo labels such as "compac chips"
```

If the model cannot render tiny text correctly, leave reserved label space and render shapes cleanly; labels can be added manually later.

## 8. Drop-In AI Image Prompt

```text
Create a self-contained two-column academic architecture figure. Do not rely on any external style guide. The figure should look like a pure white A4 / ACL paper page containing several Claude-style warm cards. The outer canvas/background must be pure white #FFFFFF, not beige or cream, so it blends with the paper. Put the Claude warmth inside the cards and panels: use warm off-white or very light cream card interiors #F4F3EE or #FAF9F5, pure white sub-cards/chips #FFFFFF, thin warm-grey borders #B1ADA1, subtle divider lines #E8E6DC, deep warm-black text #191817, and one primary accent color #C15F3C (warm terracotta orange). Optional warm supporting fills inside cards only: pale terracotta #F1DFCC and soft tan #D6B083. Use soft rounded corners with 8-12 px border radius, extremely subtle soft shadows, generous whitespace, and precise alignment.

Typography must match Claude.ai website figure typography exactly: use Styrene as the only font family for all figure titles, panel headings, mini-card titles, chips, labels, and diagram text. Use Styrene Medium or Styrene Bold for the main title and panel headings. Use Styrene Regular or Styrene Book for content labels, chips, and small text. If Styrene is unavailable, use a close grotesk fallback such as Neue Haas Grotesk, Suisse Int'l, Helvetica Neue, or Arial. Do not use serif fonts anywhere in the graphic: no Tiempos, no Anthropic Serif, no Galaxie Copernicus, no editorial serif title accent. Avoid Inter, Roboto, Google Sans, overly rounded startup fonts, cold technical display fonts, 3D effects, glossy gradients, dark dashboards, decorative textures, busy backgrounds, product logos, fake numeric results, leaderboard bars, dense paragraphs, and tiny unreadable text. The feeling should be premium, calm, warm-inside-cards, human-centered, paper-like, and suitable for an EMNLP/ACL academic paper.

Structural inspiration: use the same kind of composition as a warm architecture diagram with a large rounded workbench on the left and repeated small mechanism diagrams on the right. Do not copy any existing image literally; create an original EDO-Frame pipeline figure. The figure must be detailed enough to justify two-column width in a paper, but it must still feel spacious, aligned, and calm.

Main title: "EDO-Frame pipeline: local organization, governed tools, auditable evidence". Place the full figure on a white page with comfortable white margins. Use a wide landscape two-column layout made of warm Claude-style cards with three regions:

1. Left 60%: large rounded workbench panel titled "(a) Local EDO society".
2. Right 40%: stacked or 2x2 mini-card panel titled "(b) Governed action cycle".
3. Bottom full width: thin artifact rail titled "(c) Logged evidence trail".

LEFT REGION DETAILS. Draw a large rounded warm workbench card, paper-like and calm, with a pale tan top accent or soft terracotta border. The only visible title for this panel is "(a) Local EDO society"; do not add any design-scaffold label. On the far left inside the panel, place an input document card labeled "question + context". Add four small chips near it: "decompose", "verify", "integrate", and "hop budget". The task card flows into a sparse local society of exactly four tiny identical EDO agent nodes labeled only "i", "j", "m", and "r". Put each agent in a white circular node with a thin #B1ADA1 outline and a terracotta active accent #C15F3C. Use the same tiny human-agent icon or the same simple agent dot for all four nodes: same silhouette, same pose, same scale, same clothing/style, no variation. Arrange the four nodes as a sparse graph, not all-to-all. Use solid terracotta arrows for delegation / forward action. Use dashed terracotta arrows for audit return. Add small pale local-view halos around agents.

Around the local graph perimeter, place exactly four module cards: "NoteBoard memory", "Tag-gated tools", "Action schema", and "Audit". The module cards should be white or pale warm cards with thin grey borders and small terracotta icons. They are not agents and must not look like a central commander. Place them around the graph perimeter, not above everything as a manager. There must be no large controller node, no global planner, and no all-seeing orchestrator. The message of the left region is: local organization forms inside a constrained workbench.

RIGHT REGION DETAILS. Draw one right-side panel titled "(b) Governed action cycle"; do not repeat this title elsewhere above, below, or inside the panel. Inside it, draw four small white rounded mini-diagram cards in a stacked column or 2x2 grid, visually like repeated mechanism diagrams. Each card uses the same tiny agent icon/dot style as the left region. Use neutral grey #B1ADA1 for inactive paths and terracotta #C15F3C for selected/active paths.

Mini-card 1 title: "Read local state". Show one agent reading task tags plus note-board memory.
Mini-card 2 title: "Choose action". Show three small action chips labeled "do", "outsource", and "split"; highlight one selected chip in terracotta.
Mini-card 3 title: "Use governed tools". Show the agent connected to a tool card only through a small tag gate. The visible labels should be "tag gate" and "tools".
Mini-card 4 title: "Audit and update". Show a downstream response returning through an audit shield, then updating a small "persona tag" chip.

BOTTOM RAIL DETAILS. Draw a thin rail spanning the full width under both the workbench and the action-cycle panel. Title it "(c) Logged evidence trail". Place six small log cards on the rail labeled exactly: "routing traces", "handoff packets", "memory events", "tool events", "audit events", and "metrics". At the far right end, show four output cards labeled "answer", "evidence bundle", "caveats", and "run provenance". Connect the left workbench and right action-cycle panel down to the rail with thin neutral vertical lines. The message of the bottom rail is that every action creates an auditable artifact trail, not that the mechanism has already produced positive empirical validation.

Visible text labels should be short and limited to the labels listed above. Do not add empirical numbers, F1/EM/token values, confidence intervals, axes, plots, legends, baseline names, paper citations, product names, or long explanatory text. Do not include method names such as MA-RAG, ReAgent, MAD, AutoGen, or ChatEval. Do not add fake leaderboard bars or any result chart. This is a conceptual method architecture figure.

Agent/icon constraints: no sprite inconsistency, no different hairstyles, no different genders, no different outfits, no different poses, no robots, no anime characters, no smooth vector avatar mixed with pixel avatar. Do not create a fifth agent. Do not create stray letters such as "k". Do not duplicate "Peer j". Do not use typo labels such as "compac chips". Do not make NoteBoard memory, Tag-gated tools, Action schema, or Audit look like extra agents.

Output should look like a clean SVG/PDF vector diagram, not a screenshot or raster poster. It should be publication-ready, aligned, minimalist, warm, detailed enough for a two-column method figure, and readable at academic paper scale.
```

## 9. Acceptance Criteria

1. Figure 2 is clearly the main method architecture figure and deserves two-column width.
2. The left workbench shows local organization without central orchestration.
3. The right mini-diagrams make the governed action cycle legible.
4. The bottom rail makes reproducibility / logging visible.
5. The palette and spacing match Claude Warm Minimalism.
6. No empirical numbers or fake result claims appear.
7. No sprite inconsistency, duplicate peer labels, stray letters, or typo labels appear.
