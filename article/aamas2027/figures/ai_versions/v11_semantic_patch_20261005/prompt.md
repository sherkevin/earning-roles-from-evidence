# Image edit prompt v11 — close the remaining semantic gaps

Edit the supplied v10 architecture figure in place. Preserve the canvas, layout,
colors, typography, labels, module sizes, and every correct line. Do not redraw
the figure, add a panel, add a legend, or add explanatory prose. Make only the
three corrections below.

## 1. Show that delayed credit reaches the next read

Keep the existing gray dashed `OUTCOME → delayed credit → future state` route and
keep the `future state` marker below `STATE READ`. Add a short gray dashed arrow
from the right side of the `future state` marker upward into the lower-right edge
of the `STATE READ` module. Label this short continuation exactly `next read`.
The continuation means a later read cut in the next episode; it must not enter the
purple current-state rectangle, the `ROLE LEDGER` table, the `seal` box, or the
blue assignment arrow. Do not move the existing marker or feedback route.

## 2. Make exploration an input to a choice that is always sealed

Inside `PEER SELECTOR`, remove the blue fork that makes `explore` and `seal`
appear to be two mutually exclusive outputs. Keep the existing `explore` box as
a small light-blue dashed exploration option connected to the candidate circles
or candidate menu. Draw one clear solid blue path from the candidate choice into
the existing `seal` box, then retain the existing blue `seal → assignment →
OUTCOME` path. The only path to `OUTCOME` must pass through `seal`. Do not remove
the word `explore`; do not add any new selector module or prose.

## 3. Route only producer-owned evidence into ROLE LEDGER

Erase the existing green arrow that leaves the overall right edge of
`ATTRIBUTION`. Draw a short green arrow from the right side of the
`producer-owned` output box into the left side of `ROLE LEDGER`. Keep the
`UNKNOWN` output box in place, but give it no arrow into `ROLE LEDGER`; it remains
an audit-only terminal record. Do not add another ownership category or change
the labels `producer-owned` and `UNKNOWN`.

## Hard checks

- The exact words `future state`, `delayed credit`, and `next read` appear once.
- The exact words `explore` and `seal` remain, but only `seal` leads to `OUTCOME`.
- `UNKNOWN` has no path into `ROLE LEDGER`.
- The historical ledger is never edited by the delayed feedback route.
- All unchanged labels and the central left-to-right flow remain unchanged.
