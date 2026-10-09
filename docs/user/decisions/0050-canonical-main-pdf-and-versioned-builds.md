# ADR 0050 — Canonical main PDF and versioned builds

**Date:** 2026-10-07
**Status:** Accepted
**Scope:** `earning-roles` paper artifacts

**Reconfirmed:** 2026-10-08. The user explicitly requires completed collaborator
versions to be merged into the master, which lives one level above iteration
directories. This confirmation preserves the existing decision.

## Context

The paper has several historical PDF builds, because each layout and figure
round was compiled into a separate directory. Those files are useful for
rollback and audit, but exposing more than one current-looking PDF makes it
unclear which manuscript is the source of truth.

## Decision

`artifacts/aamas2027/main.pdf` is the only canonical current paper PDF.

Each candidate round may be compiled under a versioned child directory such as
`artifacts/aamas2027/hierarchy_density_20261007_v51_v52/`, but that file is a
candidate or historical snapshot until it passes the paper-page checks. After a
round passes, its PDF is copied to the parent `main.pdf`, and the copy operation,
source hash, build hash, and review status are recorded in that round's receipt.

Before promotion, the chosen changes must be merged into `article/aamas2027/main.tex`
and its source dependencies. The primary maintainer performs the final merge and
promotion; collaborators retain their own versioned drafts. A completed paper
revision includes both source integration and master PDF synchronization.

The active LaTeX build remains under `article/aamas2027/build/`; its output is
an implementation workspace, not a second canonical paper. Historical PDFs are
not deleted, because they are evidence of prior decisions and provide rollback,
but documentation must label them as historical or candidate rather than as
the main manuscript.

## Promotion requirements

Promotion to the parent `main.pdf` requires the current source hash, compiled
PDF hash, page-count/References check, citation and overfull checks, actual page
render review, and an explicit task report. Figure changes must also retain the
prompt/image/hash lineage and the independent figure review.

This decision controls artifact identity only. It does not open the scientific
submission gate, change the Goal, or turn an internal pre-results manuscript
into a submission-ready paper.

## Consequences

Readers and tools use one stable path for the current paper. Versioned folders
remain auditable and reversible. A new figure or text round must be promoted
explicitly; merely compiling a PDF in a new directory does not make it current.
