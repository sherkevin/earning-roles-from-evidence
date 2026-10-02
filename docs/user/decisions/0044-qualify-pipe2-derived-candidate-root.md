# ADR 0044 — Qualify PIPE2 CSV-writer derived root as the next candidate

- **Status**: Accepted
- **Date**: 2026-10-03
- **Scope**: PIPE2 second-root candidate qualification
- **Supersedes**: none; it narrows the execution choice recorded in the PIPE2 authority-option reports

## Context

The pinned TeamBench `PIPE2_data_pipeline` generator writes comma-separated rows by joining
fields. Four seeded instances (`1,4,6,9`) therefore produce an undeclared `null` CSV column
when a value contains a comma. The pinned runtime correctly refuses to emit labels for those
fixtures. A prior zero-call probe showed that standard CSV serialization preserves the logical
ETL rows and repairs this data-shape defect, but the probe had not been made into a reproducible
loader.

## Decision

Use `pipe2-csv-writer-v1` as the **next candidate derived root** for zero-call qualification.
The candidate is defined by:

1. TeamBench commit `d185aef1916fd86a9ba554d581fd256319a973af` and the pinned generator hash;
2. a hash-locked adapter that changes only CSV serialization (QUOTE_MINIMAL, LF, doubled quotes);
3. a hash-only recipe with per-seed source/expected digests and root digest;
4. explicit preservation of the old pinned receipts and an explicit
   `CANDIDATE_DERIVED_ROOT`/`benchmark_qualified=false` status.

The candidate may proceed through shape, ownership, delivery, adoption and responsibility-aware
zero-call qualification. This decision does **not** activate it as the benchmark, freeze a
scientific split, authorize LLM/A800 efficacy runs, or alter the active benchmark/baseline
document. Activation requires a later versioned benchmark decision after situated judgment,
later assignment/outcome, independent histories and same-information baseline parity pass.

## Rationale

The overlay repairs an observable fixture contract without silently rewriting the pinned source,
and its recipe makes every byte derivable and auditable. It is therefore a better next engineering
route than discarding malformed seeds or treating a valid subset as an independent root. Keeping
the status non-active prevents an engineering pass from being misreported as scientific evidence.

## Consequences

- Existing pinned v8/v9 and shape-audit receipts remain immutable historical evidence.
- New derived receipts must record zero LLM/GPU calls, candidate code/sandbox status, recipe/root
  digest and the non-scientific boundary.
- Any later promotion must create a new benchmark-baseline document version and a new decision;
  it cannot be inferred from this candidate qualification.
