# v8 — semantics-corrected architecture prompt

Status: prompt only; no image generated yet.

This revision preserves the user-provided architecture layout while correcting
the two P0 semantic errors identified in review:

1. `path diff` enters `ATTRIBUTION` separately from the recipient signal;
2. delayed outcome feedback terminates at future selector/state, never at the
   source `ROLE LEDGER`.

It also changes `EARNING ROLES ENGINE` to `EARNING ROLES PROTOCOL`, removes the
binary `accept / revise` assumption, and treats the candidate menu as bounded
selection context rather than a universal task graph.
