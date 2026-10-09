# Image2.5 Prompt — v7 Rich Architecture Figure

Generate a new Figure 1 from scratch for a multi-agent systems paper. Use the
attached top-conference framework figures only as visual grammar references. The
result must look like a method architecture, not a six-box process chart and not
a poster. Preserve a clear left-to-right time direction and one lower delayed
feedback loop.

## Composition

Wide 16:6 white paper canvas. Organize the figure into three aligned horizontal
bands and four vertical stages:

### Stage 1 — local team context (left)
Show a small local peer graph with three colored circular nodes `A`, `B`, `C`, a
small task node `task`, and one highlighted producer-to-recipient edge. Label the
stage only `LOCAL PEERS`. Do not draw human or robot characters.

### Stage 2 — situated episode (left-center)
Show two compact role cards, `PRODUCER` and `RECIPIENT`, connected by an orange
artifact arrow. Between them show a small artifact card labelled `artifact`.
Under the recipient card show a compact execution trace with two short rows:
`use` and `path diff`. Label the stage only `SITUATED EPISODE`.

### Stage 3 — central method architecture (dominant)
Place the largest pale-purple dashed enclosure in the center with the exact title
`EARNING ROLES ENGINE`. Inside, use four clearly separated submodules connected
left to right:

1. `JUDGMENT` — a small score/tag card labelled `accept / revise`;
2. `ATTRIBUTION` — a gate icon or split with labels `owned` and `unknown`;
3. `ROLE LEDGER` — a compact versioned table with rows `peer`, `role`, `evidence`;
4. `STATE READ` — a small read-cut vector feeding the selector.

Use only those labels. Do not add explanations, equations, or paragraphs inside
the enclosure. The engine should visibly transform recipient evidence into a
persistent role state.

### Stage 4 — next assignment and outcome (right)
At upper right, show a blue module titled `PEER SELECTOR` with a small probability
bar or three weighted circles `A`, `B`, `C`, plus a compact branch labelled
`explore` and a blue lock labelled `seal`. Directly below, show a blue module titled
`OUTCOME` with the two labels `quality` and `cost`.

## Connections

Use distinct, non-crossing arrows with visible arrowheads:

- orange: `artifact` → recipient `use` → `JUDGMENT`;
- green: `JUDGMENT` → `ATTRIBUTION` → `ROLE LEDGER`;
- purple: `ROLE LEDGER` → `STATE READ` → `PEER SELECTOR`;
- blue dashed: `seal` → `OUTCOME`;
- gray dashed, delayed: `OUTCOME` → `ROLE LEDGER` / future state.

The main reading path must be obvious without reading every label. The delayed
arrow must never enter the producer card or bypass attribution.

## Style

Use a restrained top-conference scientific-figure style: crisp sans-serif text,
consistent thin strokes, flat pastel fills, subtle rounded rectangles, small
vector-like data objects, strong alignment, generous whitespace, no gradients,
no 3-D, no shadows, no decorative icons, no logos, no watermark, no dashboard UI.
Keep all text horizontal and legible at two-column print size. Use color plus
layout plus arrow style so the figure remains interpretable in grayscale.

Do not copy any reference image. Do not add any text not explicitly listed in
this prompt. Do not turn the figure into a circular workflow. Do not include
claims such as better, SOTA, online learning, or numerical improvements.
