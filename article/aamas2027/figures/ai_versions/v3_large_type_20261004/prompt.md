# AI Figure Prompt — v3

## Version

`v3_large_type_20261004`

This is the last AI-generation attempt for this figure. It is a readability
revision only; do not redesign the framework.

## Input image and role

**Edit target:** `/Users/jingwu/work/earning-roles/article/aamas2027/figures/ai_versions/v1_collabllm_style_20261004/overview_ai.png`.

Preserve the exact v1 content, ordering, colors, labels, actor identities,
arrows, and timing. Only improve print-scale typography and spacing.

## Prompt

Use case: scientific-educational.

Asset type: a clean, wide, publication-quality AAMAS Figure 1. Render a
three-to-one landscape framework diagram on a pure white canvas. The final
figure will be reduced substantially in a two-column paper, so body labels
must be large, dark, crisp, and readable at print size.

Keep the same single visual sentence and the same composition as v1:

`Situated episode -> EARNING ROLES -> Local peer selector -> Later outcome`,
with a gray dashed `delayed credit` arrow returning from the later outcome to
`future read cut` inside the selector.

Keep all exact labels verbatim, with no spelling changes, additions, or
deletions:

`① Situated episode`, `task x_t`, `artifact o_t`, `producer -> recipient`,
`② Recipient use`, `judgment j_t`, `changed paths`, `③ Ownership gate`,
`producer-owned?`, `UNKNOWN if ambiguous`, `④ Publish`, `versioned evidence`,
`+ watermark`, `⑤ Local peer selector`, `read-cut state -> sealed assignment`,
`A`, `B`, `C`, `local menu`, `⑥ Later outcome`, `quality y_t + complete cost`,
`delivery`, `evidence -> decision`, `after seal`, `delayed credit`,
`future read cut`, `public evidence from recipient use`, and
`public + attributable + complete -> role evidence`.

Typography correction: enlarge every small body label by roughly 25 percent,
especially `changed paths`, `UNKNOWN if ambiguous`, `local menu`, `delayed
credit`, and `future read cut`. Keep enough horizontal space by making the
three inner modules slightly wider and reducing only empty whitespace. Do not
shrink the central container title or the numbered step markers.

Spacing correction: move `future read cut` farther inside the selector, above
its lower border; move the gray dashed arrowhead farther below that label;
keep the gray arrow clearly entering the future read cut and never the sealed
assignment. Keep the blue `after seal` arrow separate from the gray delayed
arrow.

Style: restrained best-paper framework figure, flat pastel fills, consistent
thin strokes, high-contrast sans-serif type, no gradients, no shadows, no
icons, no people, no robots, no legend, no metrics, no watermark, no extra
text, no red-green-only encoding, no overlap, and no arrows through labels.

The result must contain exactly the v1 semantic content, with larger and more
legible typography. This is not permission to invent a new architecture.
