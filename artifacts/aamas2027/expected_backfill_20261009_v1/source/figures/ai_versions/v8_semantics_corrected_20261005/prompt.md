# Image2.5 Prompt — v8 Semantics-Corrected Architecture Figure

Create a new publication-quality AAMAS/ICML/NeurIPS method architecture figure
from the supplied architecture draft. Preserve the strong wide composition,
white canvas, left-to-right reading order, restrained pastel palette, and
central dominant enclosure. Correct the scientific semantics and keep labels
short. This is an architecture figure, not a prose flowchart.

## Main reading path

Show this causal path:

`candidate menu → situated episode → recipient signal + execution trace → attribution gate → public role evidence → read-cut selector → sealed assignment → later outcome`

The delayed outcome must affect only the future selector/policy state. It must
never modify the source evidence record.

## Four visual regions

### 1. Candidate menu (left)
Use a pale green rounded card titled exactly `CANDIDATE MENU`. Show three small
peer circles labelled `A`, `B`, `C` and a small task circle labelled `task`.
Use light, non-causal dotted links only; do not draw this as a mandatory graph
shared by every benchmark track. Do not use the title `LOCAL PEERS`.

### 2. Situated episode (left-center)
Use an orange rounded card titled exactly `SITUATED EPISODE`. Inside it show
three compact objects in one row:

`PRODUCER` → `artifact` → `RECIPIENT`

Under `RECIPIENT`, show a small execution trace object with exactly two labels:
`use` and `path diff`. The path-diff object must have a visible thin gray arrow
entering the central `ATTRIBUTION` module. The recipient signal must have a
separate orange arrow entering `JUDGMENT`.

### 3. Central protocol (dominant)
Use a large pale-purple rounded dashed enclosure titled exactly
`EARNING ROLES PROTOCOL`. Do not use `ENGINE`, `MODEL`, or `PERSISTENT ROLE STATE`.
Inside, place four aligned modules:

1. `JUDGMENT` with the one small label `recipient signal`;
2. `ATTRIBUTION` with a split gate labelled `producer-owned` and `UNKNOWN`;
3. `ROLE LEDGER` with a compact three-column table labelled `peer`, `role`,
   `evidence`, plus a tiny version stamp `v_t` or watermark mark;
4. `STATE READ` with the small label `read-cut`.

The `ATTRIBUTION` module must receive two visible inputs: the judgment signal and
execution/path evidence. Do not imply that attribution is inferred from the
judgment alone. The ledger represents a public, versioned evidence record; it is
not rewritten by later outcome feedback.

### 4. Future selection and outcome (right)
Use a blue rounded card titled `PEER SELECTOR`. Inside show `A`, `B`, `C` with
small probability bars, a branch labelled `explore`, a lock labelled `sealed`,
and a compact output label `assignment`.
Below it, use a blue card titled `OUTCOME` with two labels `quality` and `cost`.

## Arrows

Use only these distinct, non-crossing arrows:

- orange `artifact` arrow: PRODUCER → artifact → RECIPIENT;
- orange `recipient signal` arrow: RECIPIENT/use → JUDGMENT;
- thin gray `path evidence` arrow: path diff → ATTRIBUTION;
- green arrow: JUDGMENT + path evidence → ATTRIBUTION → ROLE LEDGER;
- purple arrow: ROLE LEDGER → STATE READ/read-cut → PEER SELECTOR;
- blue dashed arrow: sealed → assignment → OUTCOME;
- gray dashed arrow labelled `delayed credit`: OUTCOME → a small future-state
  marker next to STATE READ or PEER SELECTOR. It must visibly stop at `future`
  or `next state`, never at ROLE LEDGER and never at the source evidence table.

Do not draw a return arrow into `ROLE LEDGER`. Do not draw a single arrow from
JUDGMENT directly to ROLE LEDGER that bypasses ATTRIBUTION.

## Style and constraints

Use crisp neutral sans-serif typography, consistent thin strokes, generous
whitespace, and flat editorial colors. Preserve the architecture-level detail
of a strong conference framework figure: participants, intermediate artifact,
execution trace, gate, evidence table, read-cut state, selection probabilities,
and delayed future update.

Keep text horizontal and readable at two-column print size. Do not add prose,
paragraphs, equations, metrics, icons of people or robots, logos, watermarks,
claims, or labels not explicitly requested. Do not imply that the selector graph
is shared by all task tracks. Do not imply that later outcome edits a historical
RoleEvidence record. Do not use `accept / revise` as a binary judgment label.
