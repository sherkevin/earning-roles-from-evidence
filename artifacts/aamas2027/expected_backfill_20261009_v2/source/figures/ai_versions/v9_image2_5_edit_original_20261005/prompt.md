# Image2.5 Edit Prompt — v9 Original Architecture Correction

Edit the supplied image **in place**. Preserve the original canvas size, aspect
ratio, white background, card positions, colors, stroke widths, typography,
spacing, arrow style, and every label that is not explicitly listed below.
Do not redraw the figure from scratch. Do not simplify it. Do not add a legend,
caption, paragraph, icon, character, or new panel.

The source image is the architecture diagram titled `本地协作与角色账本流程图`.
Make only the following surgical changes.

## 1. Correct the central title

Change the central dashed-container title:

`EARNING ROLES ENGINE` → `EARNING ROLES PROTOCOL`

Keep the same position, font size, color, and enclosure geometry. Do not add the
word model, persistent, online, or any other title.

## 2. Make the left peer card a bounded peer context

Change the left card title:

`LOCAL PEERS` → `PEER CONTEXT`

Keep the circles `A`, `B`, `C`, and `task` in the same positions. Keep their
colors. Change only the connecting lines inside this card to light gray dotted
context links, so they do not look like a mandatory causal graph shared by every
task track. Do not add arrows from this card to the episode card. The right-hand
`PEER SELECTOR` remains the only module that represents the candidate set and
selection decision; do not create a second candidate-menu label in the left card.

## 3. Correct the recipient signal label

Inside the `JUDGMENT` module, replace:

`accept / revise` → `recipient signal`

Keep the `JUDGMENT` module size and position unchanged.

## 4. Show that attribution uses execution evidence as well as judgment

Keep the existing orange recipient-to-judgment arrow.
Add one thin gray arrow from the existing `path diff` object under `RECIPIENT`
to the left side of the `ATTRIBUTION` module. Label this short arrow exactly:

`path evidence`

The new gray arrow must be visibly separate from the orange judgment arrow. It
must enter `ATTRIBUTION`, not `JUDGMENT` and not `ROLE LEDGER`.

Inside `ATTRIBUTION`, change the two output labels to:

`owned` → `producer-owned`
`unknown` → `UNKNOWN`

Do not add any further ownership categories to the image.

## 5. Mark the public role evidence record as versioned

Keep the existing `ROLE LEDGER` table with rows/columns `peer`, `role`, and
`evidence`. Add a tiny unobtrusive version mark `v_t` at the table's upper-right
corner, like a record version stamp. Do not change the table into a paragraph and
do not add field definitions.

## 6. Clarify the state read and assignment output

Inside `STATE READ`, add the short label:

`read-cut`

Near the blue arrow leaving `PEER SELECTOR` toward `OUTCOME`, add the short label:

`assignment`

Keep the existing `explore` and lock/seal visuals and all peer circles.

## 7. Redirect delayed feedback to the future state

This is the most important geometry edit.

Erase only the existing gray dashed delayed arrow segment that rises from
`OUTCOME` and terminates at the bottom of `ROLE LEDGER`.

Draw a new gray dashed arrow starting from the bottom of `OUTCOME`, travelling
upward, and terminating at one small marker labelled exactly:

`future state`

Place this marker at the lower-right outside edge of `STATE READ`, below and
visibly separated from the existing `read-cut` label. This is the only allowed
endpoint; do not place it at `PEER SELECTOR`, on the `seal` visual, or on the
assignment arrow. Place the label `delayed credit` beside the new gray dashed
arrow. The new arrow must never touch or enter the `ROLE LEDGER` table, the
historical `evidence` row, the current `read-cut`, the `seal`, or the central
`ATTRIBUTION` module. It represents a delayed selected-only signal for a future
selector/policy state, not an edit to a source evidence record.

## 8. Constrain the path-evidence routing

Route the new gray `path evidence` arrow along the open space below the
`JUDGMENT` module, then turn upward into the left side of `ATTRIBUTION`. It must
not cross the `JUDGMENT` box, any module border, the orange recipient-to-judgment
arrow, the `ROLE LEDGER`, or any other existing arrow. The figure keeps the short
label `path evidence`; the caption will define that path evidence is evaluated
together with the producer contract and ownership rule.

## Hard preservation constraints

Do not change the left-to-right reading order:

`PEER CONTEXT | SITUATED EPISODE → JUDGMENT → ATTRIBUTION → ROLE LEDGER → STATE READ → PEER SELECTOR → OUTCOME`

The vertical bar means that `PEER CONTEXT` is contextual input shown alongside the
episode; do not draw a causal arrow from it to `SITUATED EPISODE`.

Do not add `accept`, `revise`, `reject`, equations, metrics, explanations,
claims, or new agent types. Do not remove `producer`, `recipient`, `artifact`,
`use`, `path diff`, `peer`, `role`, `evidence`, `quality`, or `cost`. Do not move
any unchanged box. Keep the final image as a clean, high-resolution scientific
architecture figure suitable for later vector tracing.
