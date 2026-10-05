# v13 edit prompt — convert explanatory boxes into an architecture diagram

Edit `input_v12.png` while preserving its clean AAMAS paper-figure style,
canvas proportions, left-to-right composition, pastel section colors, and all
causal arrow directions. This is a semantic simplification pass, not a new
workflow.

The current image is too textual: many small rounded rectangles merely frame
sentences. Replace those explanatory sentences with compact visual tokens and
short labels. The figure must read as a system architecture at a glance; the
caption carries the definitions.

Keep exactly five top-level regions and their order:

1. `PEER CONTEXT`: retain four colored circular peer/task nodes and light gray
   undirected dotted context edges. Keep only the title and node labels `A`,
   `B`, `C`, `task`.
2. `SITUATED EPISODE`: show three large nodes `P`, a small document/artifact
   icon, and `R`, joined by one orange arrow chain. Under `R`, replace the
   current two-line text box with two tiny green icons: a hand/use symbol and a
   path-diff symbol. Do not write explanatory sentences.
3. `EARNING ROLES PROTOCOL`: retain four compact stages in one horizontal
   pipeline. Label only `JUDGE`, `GATE`, `LEDGER`, and `READ`. Inside them use
   symbols and at most one short token each: a speech/check icon for the
   recipient signal; a split gate with green `OWN` and gray `UNK`; a ledger
   stack with `v_t`; and a small read-cut slider. Remove the current nested
   prose boxes `recipient signal`, `producer-owned`, `UNKNOWN`, `peer`, `role`,
   `evidence`, and `read-cut` as sentences. `OWN` must feed the ledger; `UNK`
   must terminate as audit-only with no ledger arrow. A thin gray path-evidence
   line may enter the gate.
4. `PEER SELECTOR`: show a compact candidate cluster of three peer dots, a
   dashed magnifier/branch icon labelled `EXPLORE`, then a solid blue lock icon
   labelled `SEAL`, followed by a single blue downward arrow labelled
   `ASSIGN`. Only `SEAL` reaches the outcome. Avoid duplicate candidate menus or
   explanatory text.
5. `OUTCOME`: show two simple metric icons, a gauge/check for quality and a
   coin/clock for cost, with labels `QUALITY` and `COST` only.

Preserve the protocol semantics exactly. The gray dashed feedback must leave
the outcome, pass through a small dashed node labelled `FUTURE`, and enter the
bottom edge of the `READ` stage at `NEXT READ`; it must never enter the current
ledger, current read state, gate, seal, or assignment. Keep `DELAYED` as the
only feedback label. Keep peer-context links descriptive and non-causal.

Typography rules: one consistent sans-serif, bold uppercase for stage titles,
small uppercase for node labels, no paragraph text, no sentences, no tiny table
rows, no duplicate labels, and generous whitespace. Use color and line style
to encode observation (orange), attributable evidence (green), selection and
outcome (blue), and delayed feedback (gray dashed). Do not add any new stage,
algorithm name, metric, or claim. Keep all arrows clean, non-overlapping, and
inside the canvas. The result should look like a compact top-conference system
architecture figure, not a collection of text cards.
