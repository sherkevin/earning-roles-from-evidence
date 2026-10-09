# AI Figure Prompt — v2

## Version

`v2_production_quality_20261004`

This is a targeted production-quality revision of v1. It must preserve the v1
semantics and wording; it is not a structural redesign.

## Input image and role

**Edit target:** `/Users/jingwu/work/earning-roles/article/aamas2027/figures/ai_versions/v1_collabllm_style_20261004/overview_ai.png`.

Preserve the v1 composition, causal direction, colors, numbered steps, and all
exact labels. Improve only print-scale legibility and spacing.

## Prompt

Use case: scientific-educational.

Asset type: a wide, high-resolution AAMAS Figure 1 for a multi-agent systems
paper. Produce a crisp publication-quality raster with a wide 3:1 aspect ratio
and the largest practical output resolution. The image will be inspected at
single-column and full-width conference-paper sizes.

Primary request: keep the exact v1 framework diagram and make it cleaner at
print scale. Do not add modules, icons, characters, legends, metrics, claims,
or decorative elements.

Keep exactly this layout: a small orange `① Situated episode` block on the left;
one visually dominant pale-purple rounded dashed `EARNING ROLES` container in
the center with three horizontal modules; a blue `⑤ Local peer selector` block
on the upper right; a smaller blue `⑥ Later outcome` block below it. Keep the
single left-to-right main path and the one delayed feedback path.

Keep every label verbatim and do not re-render or paraphrase any label:

- `① Situated episode`; `task x_t`; `artifact o_t`; `producer -> recipient`
- `② Recipient use`; `judgment j_t`; `changed paths`
- `③ Ownership gate`; `producer-owned?`; `UNKNOWN if ambiguous`
- `④ Publish`; `versioned evidence`; `+ watermark`
- `⑤ Local peer selector`; `read-cut state -> sealed assignment`; `A`; `B`; `C`; `local menu`
- `⑥ Later outcome`; `quality y_t + complete cost`
- `delivery`; `evidence -> decision`; `after seal`; `delayed credit`; `future read cut`
- `public evidence from recipient use`; `public + attributable + complete -> role evidence`

Production corrections only:

1. Increase the output resolution and keep all strokes and glyphs crisp.
2. Give `changed paths`, `UNKNOWN if ambiguous`, `local menu`, and `delayed credit`
   enough horizontal and vertical breathing room to remain legible after the
   image is scaled down.
3. Move the `future read cut` label slightly upward inside the selector and
   move the gray dashed arrow head slightly away from the selector bottom
   border. It must still clearly enter the future read cut, not the sealed
   assignment and not the central evidence modules.
4. Keep all labels horizontally aligned and prevent any overlap between text,
   borders, arrows, and arrowheads.

Style/constraints: clean editorial best-paper framework figure, white canvas,
flat pastel fills, no gradients, no 3D, no shadows, no logos, no watermark,
no extra text, no red-green-only coding, no screenshot or UI appearance. Keep
the exact v1 orange/green/blue/purple/gray semantic palette.

The result must be visually identical in content to v1, only sharper and more
readable. Do not change the title, causal story, actor identities, or timing
semantics.
