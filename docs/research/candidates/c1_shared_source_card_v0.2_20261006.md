# Candidate card — sealed shared source, typed denominators, and policy binding

Date: 2026-10-06
Status: `CANDIDATE / DESIGN_ONLY / NOT RUN`
Supersedes: `c1_shared_source_card_v0.1_20261006.md` as the next development candidate
Goal change requested: `false`

## Why v0.1 is insufficient

The v0.1 projection seam rejected one-arm mutations, but an independent review found
that it did not reject a coordinated mutation of every projected row: it did not
recompute the source receipt or arm projection digests. Its source digest could also
be self-created from the candidate input. Finally, source costs were copied to each
row without a source-level allocation rule, and `PENDING_ATTRIBUTION`/`UNKNOWN` did
not fully constrain the episode and target states.

These are identification and accounting defects. They do not justify another live
API call.

## v0.2 contract

The v2 seam in `scripts/peerrolebench_shared_source_v2.py` requires:

1. an external source-manifest digest, embedded provenance fingerprints for artifact,
   contract, registry, scorer, prompt and raw response, and an explicit
   `policy_invariant` marker;
2. canonical source-digest recomputation that excludes only seal metadata, plus
   recomputation of every arm projection digest;
3. typed state: `ELIGIBLE` means complete source and `ITT_AND_ELIGIBLE`,
   `PENDING_ATTRIBUTION` means complete source stopped before target and `ITT_ONLY`,
   and `UNKNOWN` means incomplete source stopped before target and `ITT_ONLY`;
4. a source-level cost ledger that counts source acquisition once and sums target
   cost separately, rejecting inconsistent or duplicated source cost IDs;
5. a contract-only selection binding containing policy decision/native selection IDs,
   candidate registry and input digests, chosen candidate, propensity and a binding
   digest. This bridge must be connected to the real runner before live comparison.

The source receipt is still shared evidence. This card estimates policy behavior
conditional on that fixed source; it cannot be used to claim a total end-to-end effect
until source acquisition and independent histories are separately evaluated.

## Zero-call qualification

The v2 qualification contains ten cases: valid external seal; coordinated nested
action, delivery and projection-digest mutations; namespace/seal mutations; typed
pending and unknown denominator states; valid selection binding; and a selection
binding mutation. All ten pass in
[`n03_shared_source_qualification_20261006_v3`](../../experiments/logs/n03_shared_source_qualification_20261006_v3/summary.json).

The qualification uses a fixed synthetic external-manifest digest to test the
contract. It makes no LLM call, launches no GPU job, invokes no native grader and
sets `scientific_claim_allowed=false`. A real card must replace this fixture with
the frozen artifact/contract/scorer manifest and retain the manifest hash in the
execution receipt.

## Remaining release gates

Before a bounded live comparison, the runner must bind the v2 selection contract to
the native ledger, record independent target assignments/outcomes, implement the
source/target cost allocation in its aggregate report, and prove that the source
manifest is generated before policy execution. The final scientific comparison still
requires independent roots, independent histories and the same-information baseline
matrix; this candidate does not alter the active benchmark or Goal.
