# AI Figure Prompt — v5 (Codex built-in image generation)

## Version

`v5_builtin_tool_revision_20261004`

This version deliberately uses the Codex built-in image generation tool. The
model identity is not exposed by that tool, so this version must be described as
“built-in image generation; model undisclosed”.

## Edit target

Use the supplied v1 framework image as the visual source. Preserve its wide
landscape layout and its meaning, but produce a cleaner, more refined
publication figure.

## Prompt

Edit the supplied image into a polished, high-end AAMAS/ICML/NeurIPS research
framework figure. Keep the same white canvas, wide horizontal reading order,
central pale-purple dashed EARNING ROLES container, orange situated episode on
the left, and blue selector plus later outcome on the right. The single story
must remain:

Situated episode -> EARNING ROLES -> Local peer selector -> Later outcome,
with delayed credit returning from Later outcome to future read cut.

Preserve exactly these labels and render them sharply, with no spelling changes,
extra words, invented symbols, or missing labels:

① Situated episode
 task x_t
 artifact o_t
 producer -> recipient
 delivery

EARNING ROLES
 public evidence from recipient use

② Recipient use
 judgment j_t
 changed paths

③ Ownership gate
 producer-owned?
 UNKNOWN if ambiguous

④ Publish
 versioned evidence
 + watermark

public + attributable + complete -> role evidence

evidence -> decision
⑤ Local peer selector
 read-cut state -> sealed assignment
 A   B   C   local menu
 future read cut
after seal
⑥ Later outcome
 quality y_t + complete cost
delayed credit

Typography and layout: use a precise neutral sans-serif; make body text large
and readable after reduction to a two-column paper; align text to cards; keep
consistent margins, line heights, and stroke widths; give future read cut and
delayed credit generous space. The central container is the visual focus, but
its internal three modules should remain balanced and uncluttered.

Keep arrows separate and causally correct: orange delivery into the mechanism;
blue evidence -> decision into the selector; blue dashed after seal down to
later outcome; gray dashed delayed credit upward into future read cut. Never let
an arrow cross a label, touch the wrong box, or enter the central modules from
the delayed-credit path.

Use flat restrained pastel colors, no gradients, no 3-D, no shadows, no people,
robots, icons, logos, watermark, legend, dashboard styling, or decorative
illustrations. This is a scientific paper figure, not a poster or product UI.
Do not redesign the architecture and do not add claims such as better, SOTA,
online learning, or percentage improvement.
