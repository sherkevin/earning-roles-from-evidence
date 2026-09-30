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

The initial v1 receipt covers the runner and source-bound boundary tests
(`8 passed`) and the full regression (`309 passed`). The current v2 receipt
adds common RNG-state restoration after a post-sampling failure: its targeted
tests pass (`9 passed`) and the full PeerRoleBench regression passes (`310
passed`). The current structured receipt is
`experiments/logs/n03_pipe3_preflight_mutation_qualification_20260930_v2/`;
the v1 receipt remains immutable. The cases cover read-cut-after-decision,
unavailable offer, unknown candidate, a post-preflight RNG failure, and a
post-sampling attestation failure. Every failure leaves policy, ledger,
selection cache, both manifest chains, and (where the RNG exposes
`bit_generator.state` or `getstate`/`setstate`) the RNG state unchanged. The
success path remains covered.

## Boundary

This is an offline engineering qualification only: zero API calls and zero GPU
jobs, with `scientific_readiness=false`.  The snapshot uses `deepcopy`, so a
future high-throughput runner must measure its overhead.  Custom policies with
external side effects remain outside this qualification.  The next benchmark
gate is still the versioned isolated live runner plus independent histories and
same-information baseline parity.
