# ADR 0051 — Archive the complete research snapshot to GitHub

- **Status:** Accepted
- **Date:** 2026-10-09
- **Scope:** Repository archival and reproducibility

## Context

The AAMAS project has accumulated manuscript revisions, benchmark and baseline audits, figures,
PDF provenance, experiment logs and protocol qualifications across a large working tree. The
current scientific gate is still closed, so the archive must preserve both progress and open
blockers. A local session file, pairing image, SQLite cache and OSS transfer report are
operational state rather than research evidence.

## Decision

Push the current research snapshot, including source, docs, logs, figures, PDFs, benchmark
source snapshots and the dated status report, to the configured GitHub archive remote on the
current branch. Respect `.gitignore` for credentials and `.env` files. Exclude only the four
operational paths listed in the status report: `.omo/run-continuation/`, `bookstore.db`,
`remote-control-pairing.png` and `ossutil_output/`.

## Rationale

This preserves the evidence needed to continue the paper and makes the closed submission gate,
`UNKNOWN` results and unresolved benchmark/baseline work visible alongside the implementation.
Publishing local credentials or session material would add no reproducibility value.

## Consequences

The GitHub branch is a recoverable research snapshot rather than a submission-ready release.
The status report is the reference for the archived scientific state. Future experiments must
append raw evidence and update the report or a new task report before changing submission claims.
