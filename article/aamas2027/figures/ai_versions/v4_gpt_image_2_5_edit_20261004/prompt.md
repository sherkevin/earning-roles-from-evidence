# AI Figure Prompt — v4 (explicit GPT Image 2.5)

## Version

`v4_gpt_image_2_5_edit_20261004`

This version is generated through the explicit `gpt-image-2.5` image API. The
prompt and source image are retained so this version can be reproduced and
compared with later revisions.

## Source image

Edit this supplied image as the sole visual source:
`article/aamas2027/figures/ai_versions/v1_collabllm_style_20261004/overview_ai.png`.
Preserve its wide 3:1 composition, left-to-right causal story, flat pastel
palette, and all module positions. Do not crop, rotate, or replace the layout.

## Prompt

Create the final publication-quality framework figure for an AAMAS multi-agent
systems paper. This is a precise typography and spacing pass over the supplied
framework diagram, not a new illustration.

The visual sentence must remain exactly:
`Situated episode -> EARNING ROLES -> Local peer selector -> Later outcome`,
with a gray dashed `delayed credit` arrow returning from the later outcome to
`future read cut` inside the selector. Preserve the central mechanism as the
single dominant object.

Keep exactly these labels, with exact spelling, punctuation, capitalization,
and ASCII symbols. Do not add, remove, paraphrase, or invent any text:

- `① Situated episode`; `task x_t`; `artifact o_t`; `producer -> recipient`
- `② Recipient use`; `judgment j_t`; `changed paths`
- `③ Ownership gate`; `producer-owned?`; `UNKNOWN if ambiguous`
- `④ Publish`; `versioned evidence`; `+ watermark`
- `⑤ Local peer selector`; `read-cut state -> sealed assignment`; `A`; `B`; `C`; `local menu`
- `⑥ Later outcome`; `quality y_t + complete cost`
- `delivery`; `evidence -> decision`; `after seal`; `delayed credit`; `future read cut`
- `public evidence from recipient use`; `public + attributable + complete -> role evidence`

Typography requirements:
- Use a crisp, neutral sans-serif suitable for a two-column conference paper.
- Make every body label large enough to remain readable after reduction; give
  `changed paths`, `UNKNOWN if ambiguous`, `local menu`, `delayed credit`, and
  `future read cut` extra whitespace.
- Keep all text horizontal, aligned to its card, and fully inside its card.
- Preserve the title `EARNING ROLES` as the strongest typographic element.

Geometry requirements:
- Keep the orange episode card on the left, the pale-purple dashed mechanism
  enclosure in the center, and the blue selector/outcome cards on the right.
- Keep the three central modules in one horizontal row.
- Keep the orange `delivery`, blue `evidence -> decision`, blue dashed `after seal`,
  and gray dashed `delayed credit` arrows distinct and non-crossing.
- The gray delayed arrow must terminate at `future read cut`, above the selector
  bottom border; it must never touch `read-cut state -> sealed assignment`, the
  central modules, or any other label.
- Use consistent thin strokes, clean rounded cards, generous white space, and
  a restrained five-color palette. Keep the figure readable in grayscale.

Quality constraints:
- Flat editorial scientific infographic; polished ICML/NeurIPS/AAMAS framework
  figure; no poster, dashboard, software screenshot, or decorative clip art.
- No gradients, 3-D effects, shadows, people, robots, logos, watermark, legend,
  metrics, claims, or extra symbols.
- Do not change the causal semantics or actor identities.
- If any generated glyph is uncertain, use the exact plain ASCII label from the
  list above rather than a decorative substitute.
