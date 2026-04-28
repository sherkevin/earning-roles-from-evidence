# Figure 3 Prompt - Governed Action Loop Detail

> Target: main Method detail figure or front appendix if page budget is tight.
> Width: single-column preferred after Figure 2 carries the full pipeline; two-column only if the paper keeps a separate mechanism spread.
> Reader takeaway: one EDO hop is a local, auditable action loop over task tags, profile tags, note-board memory, tag-gated tools, and audit feedback.
> Evidence status: conceptual mechanism figure; no empirical numbers.
> Governing style: `docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md`.
> Target asset: `artifacts/figures/fig3_action_detail_claude.{svg,pdf,png}`.

---

## 1. Why This Figure Exists

This figure is the detail zoom-in for the mechanism that Figure 2 compresses:

```text
How does one local agent choose, execute, audit, and update a governed action?
```

It should no longer use the old blue pixel-agent style. It must look like the same figure family as Figure 1 and Figure 2: warm off-white paper, terracotta accents, consistent rounded cards, small calm agent nodes, and Claude/Anthropic-like typography.

## 2. Layout

Use a compact single-column mechanism card with one strong reading path:

```text
left: local inputs
center: Agent i decision core
right: governed action menu
bottom: audit + memory/tool update loop
```

Main title:

```text
One-hop governed action loop
```

The figure should feel like a product architecture card, not a dashboard. Prefer sparse cards and chips over dense paragraphs.

## 3. Required Visual Elements

### Local Inputs

Cards:

```text
task packet
agent profile
neighbor belief
NoteBoard memory
tool cards
```

Small chips:

```text
tags
budget
history
trust
facts
failures
cost
risk
schema
```

### Agent i Decision Core

Elements:

```text
Agent i
action envelope
tag-gated selector
score chips: tag fit / history / cost / risk
```

Visual message:

```text
the selector is local and auditable, not a hidden central planner
```

### Governed Action Menu

Action chips:

```text
answer
delegate
split
audit
call tool
update memory
```

Highlight one path:

```text
delegate -> Peer j -> evidence
```

Show "call tool" as an available governed action through a tag gate, but keep "delegate" as the primary highlighted path so the diagram is not overloaded.

### Audit And Update Loop

Elements:

```text
Peer j returns evidence
audit badge: accept / revise / reroute
evidence bundle writes to NoteBoard memory
tag drift chip
reselect tools arrow back to tag-gated selector
```

## 4. Style Rules

Use the same Claude Warm Minimalism family as Figures 1 and 2:

```text
A4 page / outer background: #FFFFFF
warm main card interior: #F4F3EE or #FAF9F5
white sub-cards: #FFFFFF
borders: #B1ADA1
dividers: #E8E6DC
main text: #191817
primary accent: #C15F3C
soft highlight: #F1DFCC
soft tan: #D6B083
```

Typography should follow the current Claude.ai website figure look:

```text
only font family inside the figure: Styrene
titles and headings: Styrene Medium or Styrene Bold
labels and chips: Styrene Regular or Styrene Book
fallbacks: Neue Haas Grotesk, Suisse Int'l, Helvetica Neue, Arial
no serif fonts anywhere in the figure
avoid Inter/Roboto/Google-Sans-looking generic SaaS typography
```

Agent nodes should be simple and consistent. Use identical small warm agent dots or minimal human glyphs inside white circular nodes; do not use blue jackets, pixel sprites, anime, robots, or varied characters.

## 5. Drop-In AI Image Prompt

```text
Create a self-contained single-column academic mechanism figure. Do not rely on any external style guide. The figure should look like a pure white A4 / ACL paper page containing one Claude-style warm mechanism card. The outer canvas/background must be pure white #FFFFFF, not beige or cream, so it blends with the paper. Put the Claude warmth inside the card: use a warm off-white or very light cream main-card interior #F4F3EE or #FAF9F5, pure white sub-cards #FFFFFF, thin warm-grey borders #B1ADA1, subtle divider lines #E8E6DC, deep warm-black text #191817, primary terracotta accent #C15F3C, soft pale terracotta highlight #F1DFCC, and occasional soft tan #D6B083 inside the card only. Use soft rounded corners with 8-12 px radius, extremely subtle shadows, generous whitespace, precise grid alignment, and calm product-architecture spacing. The figure should feel premium, quiet, human-centered, paper-like, warm-inside-card, and consistent with modern Claude.ai website visuals.

Typography must match Claude.ai website figure typography exactly: use Styrene as the only font family for all figure titles, panel headings, labels, chips, and diagram text. Use Styrene Medium or Styrene Bold for the main title and panel headings. Use Styrene Regular or Styrene Book for content labels, chips, and small text. If Styrene is unavailable, use a close grotesk fallback such as Neue Haas Grotesk, Suisse Int'l, Helvetica Neue, or Arial. Do not use serif fonts anywhere in the graphic: no Tiempos, no Anthropic Serif, no Galaxie Copernicus, no editorial serif title accent. Avoid Inter, Roboto, Google Sans, overly rounded startup fonts, condensed tech fonts, and decorative display fonts. Text should have tight but readable tracking, medium/semibold headings, regular/book labels, and generous line spacing.

Figure purpose: show one local EDO decision hop. This is a conceptual mechanism diagram, not a performance chart. It must be readable as a single-column figure in a two-column NLP paper. Do not include empirical numbers, F1/EM/token values, confidence intervals, plots, axes, legends, baseline names, citations, or long paragraphs.

Draw one rounded warm outer card titled exactly "One-hop governed action loop" on the pure white A4 page background, with comfortable white margins around the card. Do not add any subtitle, parenthetical note, font note, style note, or microcopy next to the title. Inside it, use four semantic panels with one clear reading path: "Local inputs", "Agent i", "Action menu", and "Audit and update". Keep all panels visually connected with thin lines and terracotta highlights. Do not write any layout-scaffold zone labels in the visible figure.

Panel title: "Local inputs". Draw five small white cards labeled exactly: "task packet", "agent profile", "neighbor belief", "NoteBoard memory", and "tool cards". Add small chips only where space permits: "tags", "budget", "history", "trust", "facts", "failures", "cost", "risk", and "schema". Use neutral grey for inactive input lines. Use a subtle terracotta accent for the inputs currently selected by Agent i.

Panel title: "Agent i". Draw one simple warm agent node: a white circular node with a thin #B1ADA1 outline, a minimal identical human glyph or dot, and a small terracotta active accent. Do not use blue pixel art. Do not create a smooth full-body avatar. Next to Agent i, draw a card labeled "action envelope" and a card labeled "tag-gated selector". Under the selector, show four tiny score chips labeled exactly "tag fit", "history", "cost", and "risk". Make it clear that the selector belongs locally to Agent i; do not draw a central controller, manager, router, or global planner.

Panel title: "Action menu". Draw six rounded action chips labeled exactly: "answer", "delegate", "split", "audit", "call tool", and "update memory". Keep chips compact and readable. Highlight "delegate" in terracotta as the selected path. Draw a terracotta arrow from Agent i to one peer node labeled "Peer j". Peer j must appear exactly once in the entire figure, in the action-menu area only. Peer j must use the same agent-node style as Agent i, smaller but visually identical. Show "call tool" as an available governed action through a tiny "tag gate" chip connected to a small "tool" card, but do not make it the primary path.

Panel title: "Audit and update". From the single existing Peer j node, draw a returned evidence card labeled "evidence". Do not draw a second Peer j node, second peer avatar, or repeated peer label in the bottom panel. Route the evidence through an audit badge labeled "accept / revise / reroute". Draw a dotted terracotta or warm-grey line from the evidence bundle back to "NoteBoard memory". Draw a small chip labeled "tag drift" and a curved terracotta arrow back to "tag-gated selector" labeled "reselect tools". Keep the bottom loop compact and calm.

Visible text labels must be limited to the labels specified above. Do not invent extra labels, layout-scaffold zone labels, font notes, style notes, parenthetical typography notes, stray letters, duplicate peer labels, duplicated agents, typo labels, fake tool names, or extra method names. Do not include the words "Tiempos", "Anthropic Serif", "optional", "font", or "style" anywhere in the visible figure. Do not vary agent hairstyles, outfits, genders, poses, icon styles, or colors. All figure elements should match the same visual grammar as Figures 1 and 2: white paper background, warm internal card, white rounded sub-cards, thin warm-grey borders, terracotta active paths, simple consistent nodes, and Styrene-only typography.

Output should look like a clean SVG/PDF vector diagram, not a raster poster or screenshot. It should be publication-ready, aligned, minimalist, warm, and readable at academic paper scale.
```

## 6. Acceptance Criteria

1. The figure matches Figure 1 and Figure 2 in palette, typography, card radius, arrow style, and agent-node style.
2. It explains one local decision hop, not the whole paper.
3. It includes note-board memory, tag-gated tool selection, action envelope, audit feedback, and tag-drift reselection.
4. It does not imply a hidden global orchestrator.
5. It contains no empirical numbers, invented method names, duplicate Peer j, stray labels, or old blue pixel-agent styling.
