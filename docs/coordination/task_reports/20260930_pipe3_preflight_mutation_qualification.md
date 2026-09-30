# Task report — PIPE3 preflight-before-mutation qualification (2026-09-30)

## Scope

The versioned PIPE3 selection boundary previously appended the public offer,
consumed feedback, and sampled a policy decision before constructing the
attestation.  A late read-cut, availability, menu, or policy/ledger error
could therefore leave a partial policy or manifest update.  This task audits
that boundary without calling an API, executing task code, or using a GPU.

## Change

`Pipe3SelectionBoundary.choose_and_seal` now performs a preflight pass before
mutating any policy, native ledger, selection cache, or manifest.  It checks
role and selector identity, duplicate episode/event IDs, task start ordering,
version and time fields, integer watermarks, `read_cut <= decision_index`,
offer availability, candidate/base-score alignment, feature vectors, and the
selected-only feedback binding.  A transaction snapshot is retained around
the mutation path so an error that can only be observed after sampling (for
example a custom RNG or a future ledger invariant) restores the same mutable
objects and re-raises the original error.

## Evidence

The targeted runner and source-bound boundary tests pass (`8 passed`), and the
full PeerRoleBench regression passes (`309 passed`).  The structured receipt is
`experiments/logs/n03_pipe3_preflight_mutation_qualification_20260930/`.
It covers read-cut-after-decision, unavailable offer, unknown candidate, and a
post-preflight RNG failure; every failure leaves policy, ledger, selection
cache, and both manifest chains unchanged.  The success path remains covered.

## Boundary

This is an offline engineering qualification only: zero API calls and zero GPU
jobs, with `scientific_readiness=false`.  The snapshot uses `deepcopy`, so a
future high-throughput runner must measure its overhead.  Custom policies with
external side effects remain outside this qualification.  The next benchmark
gate is still the versioned isolated live runner plus independent histories and
same-information baseline parity.
