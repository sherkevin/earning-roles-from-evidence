# AI Figure Prompt — v1

## Version

`v1_collabllm_style_20261004`

One prompt corresponds to one generated image. This prompt is retained before generation so the image can be regenerated or compared with later versions.

## Input images and roles

1. **Reference image:** `/Users/jingwu/Documents/Codex/2026-09-27/new-chat/topconf-paper-figure-gallery/images/icml/final/icml2025-0242.jpg` — use only as a high-level reference for the visual grammar of a best-paper framework figure: one horizontal reading direction, one visually dominant central mechanism, numbered steps, sparse labeled arrows, and a clean white canvas. Do not copy its text, characters, icons, or exact layout.
2. **Semantic reference:** `/Users/jingwu/work/earning-roles/article/aamas2027/figures/versions/v8_collabllm_framework_20261004/overview.png` — use only to preserve the intended earning-roles semantics and arrow destinations. Do not preserve its typography or drawing style.

## Prompt

Use case: scientific-educational.

Asset type: a wide landscape Figure 1 for an AAMAS multi-agent systems paper. The figure must look like a polished top machine-learning conference framework figure, not a software flowchart, poster, dashboard, or presentation slide.

Primary request: create an original, publication-quality framework diagram for a method called **Earning Roles**. The single visual sentence is: **a recipient's situated use becomes public evidence that changes who receives the next responsibility**.

Scene/backdrop: a pure white paper canvas, wide 3:1 composition, generous whitespace, no outer frame, no page decoration.

Composition/framing: left-to-right reading order. Place a small orange “Situated episode” block on the left, one large central pale-purple rounded dashed container occupying the visual center, a blue “Local peer selector” block on the upper right, and a smaller blue “Later outcome” block below it. The central container must clearly dominate the image and be the only large mechanism enclosure.

Central mechanism: inside the central container, place exactly three compact modules in one horizontal row. The modules are numbered and connected left to right:

- `② Recipient use` with the two lines `judgment j_t` and `changed paths`;
- `③ Ownership gate` with the two lines `producer-owned?` and `UNKNOWN if ambiguous`;
- `④ Publish` with the two lines `versioned evidence` and `+ watermark`.

The central container title is exactly `EARNING ROLES`. Its subtitle is exactly `public evidence from recipient use`. A small quiet sentence below the modules is exactly `public + attributable + complete -> role evidence`.

External objects and exact labels:

- Left block title: `① Situated episode`; lines: `task x_t`, `artifact o_t`, and `producer -> recipient`.
- Upper-right block title: `⑤ Local peer selector`; line: `read-cut state -> sealed assignment`; show three small outlined peer circles labeled exactly `A`, `B`, and `C`, followed by `local menu`.
- Lower-right block title: `⑥ Later outcome`; line: `quality y_t + complete cost`.

Arrows and timing: an orange solid arrow labeled exactly `delivery` goes from the left block into the central mechanism. A blue solid arrow labeled exactly `evidence -> decision` goes from the central mechanism to the upper-right selector. A blue dashed arrow labeled exactly `after seal` goes from the selector down to the later outcome. A gray dashed arrow labeled exactly `delayed credit` goes from the later outcome back upward into a small label inside the selector reading exactly `future read cut`. This gray delayed arrow must not enter the central evidence modules and must not touch the sealed-assignment text.

Style/medium: clean editorial vector-like scientific infographic with subtle rounded cards, thin consistent strokes, crisp sans-serif typography, restrained pastel fills, and strong hierarchy. The design should feel like a carefully typeset ICML/NeurIPS/AAMAS best-paper Figure 1, with visual polish coming from spacing, alignment, and hierarchy rather than decoration.

Color palette: orange for the situated episode and recipient-use path; green for responsibility gate and evidence publication; deep blue for future selection and outcomes; muted purple for the central mechanism enclosure; neutral dark gray for delayed feedback and explanatory text. At most five semantic colors. Keep the figure readable in grayscale and do not rely on red versus green.

Text (verbatim): render every quoted label exactly as written above, with normal ASCII subscripts such as `x_t`, `o_t`, `j_t`, and `y_t`. Use no additional words, numbers, legends, logos, citations, watermarks, or invented metrics. All text must be sharp, legible, and horizontally aligned.

Constraints: preserve the exact causal and temporal direction; keep the central mechanism visually dominant; leave enough whitespace around every label; use one main reading path; make arrows terminate at named objects; keep the image original rather than copying the reference.

Avoid: garbled or misspelled text, overlapping labels, extra panels, people or robot illustrations, decorative agent icons, gradients, 3D effects, shadows, glossy UI styling, screenshots, dense equations, tiny unreadable prose, red-green-only encoding, arrows crossing through text, arrows that loop into the wrong module, and any claim such as “better”, “SOTA”, “online learning”, or percentage improvement.

## Execution provenance

- Generator: built-in Codex image generation tool (not the CLI fallback).
- Reference attached to the generation call: the local semantic candidate `article/aamas2027/figures/versions/v8_collabllm_framework_20261004/overview.png`.
- The gallery reference was inspected visually and specified in the prompt, but its external path could not be attached to the generation call because the image tool denied access outside the workspace.
- Generated asset: `overview_ai.png` in this directory.
