# Figure 1 Prompt - Single-Column Paradigm Comparison

> Target: introduction visual teaser / compact related-method contrast.
> Width: **single-column**.
> Reader takeaway: EDO is not a larger group chat, static role chain, or central planner; it is a local organization-forming framework.
> Evidence status: conceptual comparison only; no empirical numbers.
> Governing style: `docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md`.
> Target asset: `artifacts/figures/fig1_paradigm_comparison_claude.{svg,pdf,png}`.

---

## 1. Why This Figure Exists

This figure gives reviewers a fast visual answer to:

```text
How is EDO different from common multi-agent or agent-tool systems?
```

It should compare paradigms, not performance. Exact baseline scores belong in result plots/tables generated from artifacts. Because this is now a single-column figure, it must be compact and calm, not a full visual survey.

## 2. Layout

Use a **vertical single-column comparison card** with four compact rows, not five horizontal columns.

Panel title:

```text
Where EDO differs
```

Rows:

```text
1. Single call
2. Fixed role chain
3. Central planner / debate
4. EDO-Frame
```

Each row should contain:

```text
left: small icon or mini schematic
middle: paradigm label
right: one short limitation / distinction phrase
```

### Row 1: Single Call

Visual:

```text
one neutral document card flowing to one neutral agent dot and one answer card
```

Right phrase:

```text
single shared context
```

### Row 2: Fixed Role Chain

```text
four small neutral dots in a rigid vertical or horizontal chain
thin grey arrows only
```

Right phrase:

```text
roles known in advance
```

### Row 3: Central Planner / Debate

```text
one larger neutral controller dot above three smaller dots
or three dots around a speech bubble
keep this row simple; do not draw a large architecture
```

Right phrase:

```text
global / conversational control
```

### Row 4: EDO-Frame

Visual:

```text
three or four warm terracotta-accent dots in a sparse local graph
one tiny note-board chip
one tiny audit loop arrow
one tiny tool chip
```

Right phrase:

```text
organization forms locally
```

Highlight:

```text
Use a light terracotta border or pale #F1DFCC row background for EDO-Frame only.
Keep all other rows neutral.
```

## 3. Style Constraints

Use Claude Warm Minimalism:

```text
A4 page / outer background #FFFFFF
warm rounded main card #F4F3EE or #FAF9F5
white sub-cards / row chips #FFFFFF
thin #B1ADA1 borders
main text #191817
key EDO accent #C15F3C
subtle dividers #E8E6DC
generous whitespace
Styrene-only typography: Styrene Medium/Bold for title, Styrene Regular/Book for labels and chips
no serif fonts anywhere in the figure
```

Do not use the old five-column blue pixel-agent layout. Do not include method names such as MA-RAG, ReAgent, MAD, AutoGen, or ChatEval. Do not include numbers. Do not over-render people; abstract dots/cards are acceptable for this single-column teaser.

## 4. Drop-In AI Image Prompt

```text
Create a self-contained single-column academic paper figure. Do not rely on any external style guide. The figure should look like a pure white A4 / ACL paper page containing a Claude-style warm card. The outer canvas/background must be pure white #FFFFFF, not beige or cream, so it blends with the paper. Put the Claude warmth inside the central card: use a warm off-white or very light cream card interior #F4F3EE or #FAF9F5, pure white sub-cards #FFFFFF, thin warm-grey borders #B1ADA1, subtle divider lines #E8E6DC, deep warm-black text #191817, and one primary accent color #C15F3C (warm terracotta orange). Use soft rounded corners with 8-12 px border radius, extremely subtle soft shadows, generous whitespace, and precise grid alignment.

Typography must match Claude.ai website figure typography exactly: use Styrene as the only font family for all titles, headings, row labels, chips, and diagram text. Use Styrene Medium or Styrene Bold for the title and row labels. Use Styrene Regular or Styrene Book for content labels and right-side phrases. If Styrene is unavailable, use a close grotesk fallback such as Neue Haas Grotesk, Suisse Int'l, Helvetica Neue, or Arial. Do not use serif fonts anywhere in the graphic: no Tiempos, no Anthropic Serif, no Galaxie Copernicus, no editorial serif title accent. Avoid Inter, Roboto, Google Sans, overly rounded startup fonts, cold technical display fonts, 3D effects, glossy gradients, dark dashboards, decorative textures, product logos, fake numeric results, leaderboard bars, dense paragraphs, and tiny unreadable text. The feeling should be premium, calm, warm-inside-card, human-centered, paper-like, and suitable for an EMNLP/ACL academic paper.

Figure purpose: compact paradigm comparison only. This is not the main method pipeline and not a performance chart. The final figure must fit a single column in a two-column academic paper. Keep it compact, calm, and readable when scaled down.

Draw one vertical rounded comparison card titled "Where EDO differs". Place it on the pure white A4 page background with comfortable white margins around the card. The main card itself should have a warm Claude-style interior (#F4F3EE or #FAF9F5) and a thin warm-grey border. Inside it, place white or very pale sub-cards/rows. The card contains four horizontal rows separated by subtle #E8E6DC divider lines. Each row has exactly three zones: left = tiny mini-schematic, middle = short paradigm label, right = one short distinction phrase. Use abstract dots, document cards, arrows, and chips rather than detailed characters. If tiny agents are used, keep them as identical simple dots or tiny consistent human icons; do not vary hairstyles, clothing, gender, pose, or icon style.

Row 1 label: "Single call". Left mini-schematic: one neutral document card flows through one neutral agent dot to one answer card. Use neutral grey #B1ADA1 for the arrow and node. Right phrase: "single shared context".

Row 2 label: "Fixed role chain". Left mini-schematic: four small neutral dots in a rigid chain with thin grey arrows. No feedback loops, no branches. Right phrase: "roles known in advance".

Row 3 label: "Planner / debate". Left mini-schematic: either one larger neutral controller dot above three smaller dots, or three dots around one simple speech bubble. Keep this row minimal; do not draw a full architecture. Right phrase: "global / conversational control".

Row 4 label: "EDO-Frame". Highlight this row only with a pale terracotta fill #F1DFCC or a thin terracotta border #C15F3C. Left mini-schematic: three or four terracotta-accent dots in a sparse local graph, plus one tiny note-board chip, one tiny audit loop arrow, and one tiny tool chip. Use terracotta #C15F3C for active EDO edges and highlights. Right phrase: "organization forms locally".

Typography and label rules: use only these visible text labels: "Where EDO differs", "Single call", "Fixed role chain", "Planner / debate", "EDO-Frame", "single shared context", "roles known in advance", "global / conversational control", and "organization forms locally". Do not add method names such as MA-RAG, ReAgent, MAD, AutoGen, ChatEval, or paper citations. Do not add empirical numbers, F1/EM/token values, confidence intervals, axes, plots, or legends. Do not include long explanatory text. Leave enough margin around all rows so the figure feels spacious.

Output should look like a clean SVG/PDF vector diagram, not a screenshot or raster poster. It should be publication-ready, aligned, minimalist, warm, and readable as a single-column academic figure.
```

## 5. Acceptance Criteria

1. The figure is legible as a single-column paper figure.
2. It distinguishes EDO from common paradigms without becoming the full method diagram.
3. It uses Claude Warm Minimalism and terracotta accents.
4. It contains no empirical claims, numbers, or invented baseline names.
