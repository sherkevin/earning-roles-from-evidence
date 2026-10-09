# Image2.5 Patch Prompt — Correct the Remaining Geometry in the Latest Figure

Edit the supplied latest figure in place. This is a surgical correction pass.
Preserve the canvas, card positions, colors, typography, module sizes, all
existing labels, and all correct arrows. Do not redraw the figure from scratch.
Do not add a caption, legend, paragraph, icon, character, or new panel.

The input is the latest figure with the title `EARNING ROLES PROTOCOL` and the
left card title `PEER CONTEXT`.

## 1. Remove the causal-looking edge in PEER CONTEXT

Inside `PEER CONTEXT`, change only the orange A-to-B connection into a light
gray dotted context link with no arrowhead. Keep A, B, C, and `task` in their
current positions and keep the other dotted context links. Do not change the
orange `PRODUCER → artifact → RECIPIENT` flow in `SITUATED EPISODE`.

## 2. Replace the incorrect delayed-feedback route

Erase the entire gray dashed feedback route that currently rises from
`OUTCOME` and ends at the bottom of `ROLE LEDGER`. Remove its arrowhead as well.
It must not touch the ledger or the historical `evidence` row.

Draw one new gray dashed arrow from the bottom edge of `OUTCOME` toward a small
outlined marker labelled exactly `future state`. Put this marker below the
lower-right outside edge of `STATE READ`, clearly separated from the purple
state rectangle. The arrow may travel left along the bottom margin and then turn
up into this marker, but it must never touch `ROLE LEDGER`, `ATTRIBUTION`, the
current state rectangle, the selector's `seal`, or the blue assignment arrow.
Put the exact label `delayed credit` beside this new dashed arrow. This is a
selected-only delayed signal for a future selector state.

## 3. Add the three missing small labels

Add only these short labels, with the same small dark typography as nearby labels:

- `v_t` at the upper-right corner of the `ROLE LEDGER` table;
- `read-cut` inside the `STATE READ` module, above or beside its purple state
  rectangle;
- `assignment` beside the blue arrow from `PEER SELECTOR` down to `OUTCOME`.

Keep each label legible and unobtrusive. Do not add definitions or explanatory
sentences.

## 4. Preserve the existing evidence path

Keep the existing gray `path evidence` line from `path diff` to the left side of
`ATTRIBUTION`. It may cross only the `ATTRIBUTION` boundary at its final arrowhead;
it must not cross any other module, border, or existing arrow.

## Hard acceptance checks

- No orange arrow remains inside `PEER CONTEXT`.
- No gray dashed arrow enters or points to `ROLE LEDGER`.
- The words `future state`, `delayed credit`, `v_t`, `read-cut`, and `assignment`
  are all present exactly once.
- The central flow and every unchanged label remain unchanged.
- Do not introduce any new text beyond the five exact labels above.
