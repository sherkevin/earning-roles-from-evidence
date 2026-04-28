# Claude Warm Minimalism Figure Style

> Created: 2026-04-27
> Owner: scientist
> Scope: publication figure style direction for EDO conceptual / architecture figures.
> Local reference: `docs/references/架构图/image4.png`.

---

## 1. Style Name

Use **Claude Warm Minimalism** for the next render pass.

The figures should feel like the Claude.ai website translated into academic paper diagrams: warm, calm, precise, premium, paper-like, and human-centered. The style should be more like a refined notebook / product architecture diagram than a game UI, cyberpunk dashboard, or generic SaaS infographic.

## 2. Overall Aesthetic

```text
Warm Minimalism.
Sleek, thoughtful, human-centered, premium paper-like.
Generous whitespace.
Clean lines.
Soft rounded corners, border-radius 8-12 px.
Extremely subtle soft shadows.
No heavy decoration.
Calm, professional, warm, approachable, high-end.
```

The closest local reference is `image4.png`: a large rounded warm stage/workbench on the left and repeated small mechanism diagrams on the right. Use that clarity and warmth, but make it cleaner and more academic.

## 3. Core Palette

```text
A4 page / outer background: #FFFFFF
Warm card interior: #F4F3EE
Very light warm card interior: #FAF9F5
Pure white sub-cards / chips: #FFFFFF
Primary accent: #C15F3C
Neutral grey: #B1ADA1
Main text: #191817
Light divider / subtle background: #E8E6DC
Soft warm tan fill: #D6B083
Soft pale highlight: #F1DFCC
```

Use a pure white outer canvas so the figure sits naturally on an A4 / ACL paper page. Put the Claude warmth inside rounded cards and panels, not in the page background. Use the terracotta accent `#C15F3C` for key routing lines, highlighted nodes, stage markers, active bars, and important callouts. Use neutral grey for inactive or comparison flows. Avoid cold blues, neon colors, saturated purple, and bright green unless there is a strong semantic reason.

## 4. Typography

Claude.ai website figures / illustrations use a consistent Styrene typography system:

```text
Primary font family for all figure titles, labels, chips, and diagram text: Styrene.
Figure titles / headings: Styrene Medium or Styrene Bold.
Figure content / labels / chip text / axis text: Styrene Regular or Styrene Book.
Fallbacks only if Styrene is unavailable: Neue Haas Grotesk, Suisse Int'l, Helvetica Neue, Arial.
No serif fonts inside figures: do not use Tiempos, Anthropic Serif, Galaxie Copernicus, or editorial serif title accents.
Avoid generic Inter/Roboto/Google-Sans-looking typography when trying to match Claude.
Headings: Styrene Medium/Bold, tight but readable tracking, dark #191817.
Labels and chips: Styrene Regular/Book, high readability.
Line height: generous, around 1.35-1.5.
Labels: short and crisp.
No dense paragraphs inside figures.
```

## 5. Figure Components

Use:

```text
rounded cards
thin warm grey borders
paper-like stage panels
tiny human agent sprites only when needed
small document cards
small tool/memory/audit chips
simple arrow lines
repeated mini-mechanism panels
```

Do not use:

```text
3D objects
neon glow
heavy gradients
dark dashboards
cold blue/purple palettes
decorative backgrounds
fake numeric charts
logo-like product icons
large paragraphs
```

## 6. Agent Icon Direction

Agents may remain tiny pixel-style humans, but they should be softened into the warm paper aesthetic:

```text
tiny consistent human sprites
same silhouette, same pose, same scale
warm neutral clothing with one terracotta active accent
white or pale circular node backing
thin #B1ADA1 outline
no anime variation
no robots
no different hairstyles / genders / outfits across nodes
```

Figure 1 can use abstract dots/cards instead of detailed human sprites if the single-column layout becomes crowded.

Figure 2 should use tiny consistent agents because it is the method pipeline.

## 7. Layout Rules

1. Prefer strong grids and precise alignment.
2. Leave generous breathing space around every group.
3. Use one primary reading direction per figure.
4. Use repeated visual grammar: same node shape, same arrow type, same card radius.
5. Use small labels with high contrast; if the image model cannot render text reliably, reserve clean label spaces for manual vector labels.

## 8. Master Prompt Snippet

Paste this at the beginning of Figure 1 / Figure 2 render prompts:

```text
Create a clean academic architecture figure that looks like a white A4 paper page containing one or more Claude-style warm cards. The outer canvas/background must be pure white #FFFFFF so it blends with an ACL/EMNLP paper page. Put warmth inside the cards: warm card interiors #F4F3EE or #FAF9F5, pure white sub-cards #FFFFFF, thin warm-grey borders #B1ADA1, subtle dividers #E8E6DC, deep warm-black text #191817, primary terracotta accent #C15F3C, generous whitespace, soft rounded corners (8-12 px), and extremely subtle shadows. Typography must be fully consistent with Claude.ai figure typography: use Styrene for all figure titles, headings, labels, chips, and diagram text. Use Styrene Medium/Bold for titles and headings; use Styrene Regular/Book for labels and content. If Styrene is unavailable, use a close grotesk fallback such as Neue Haas Grotesk, Suisse Int'l, Helvetica Neue, or Arial. Do not use serif fonts anywhere inside the figure: no Tiempos, Anthropic Serif, Galaxie Copernicus, or editorial serif title accent. Avoid generic Inter/Roboto/Google-Sans-looking typography, overly rounded startup fonts, and cold technical display fonts. The figure should feel premium, calm, human-centered, and paper-like, similar to Claude.ai official visual identity. Avoid cold blues/purples, neon, 3D, dark dashboard styling, heavy gradients, decorative textures, fake numbers, and crowded text. Use short readable labels only. Output as a clean SVG/PDF-style vector diagram suitable for an academic paper.
```

## 9. Drop-In Prompt Rule

The user copies only the fenced `Drop-In AI Image Prompt` block into the image-generation input box. Therefore every drop-in prompt must be fully self-contained:

```text
include the full style palette
include typography and spacing rules
include exact layout structure
include all required labels
include all negative constraints
include width / paper-scale requirement
do not rely on this style file being pasted with it
```

Context above a drop-in prompt is for humans only. The fenced drop-in prompt is the actual production artifact.

## 10. Per-Figure Width Policy

```text
Figure 1: single-column, compact comparison / teaser.
Figure 2: two-column, detailed method pipeline and primary architecture.
Figure 3: mechanism zoom-in in the same Claude Warm Minimalism style; keep only if it remains in the main paper.
```
