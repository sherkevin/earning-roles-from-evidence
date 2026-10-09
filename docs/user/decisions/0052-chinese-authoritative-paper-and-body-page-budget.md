# ADR 0052 — Chinese-authoritative paper and body-page budget

**Date:** 2026-10-09
**Status:** Accepted by explicit user instruction and maintainer adoption
**Scope:** Current manuscript translation, references, and PDF layout

## Context

The user revised the Chinese manuscript's motivation, terminology, abstract,
and presentation directly. Older English drafts contain wording and omissions
that must not override those revisions. The user now asks to construct the
English main PDF from that Chinese version and explicitly confirms that
bibliographic references do not count toward the body-page budget.

## Decision

`docs/paper/aamas2027/FORMAL_PAPER_ZH.md` is the sole content authority for the
English manuscript in this writing round. English editing may improve idiom,
typesetting, and citation support, but must preserve the Chinese argument,
method, comparisons, responsibility boundaries, and result placeholders.

The body, including the abstract, figures, tables, discussion, limitations,
and conclusion, must occupy no more than eight pages. The target is exactly
eight substantive pages. References begin on a separate subsequent page and
do not count toward the body limit. No body text may be moved into the
reference section to evade that limit.

Supplement references by verifying primary records and attaching them to
specific claims. Compare the number, age, quality, and placement of citations
with relevant AAMAS papers; do not pad to an arbitrary reference count.

The official template, fonts, margins, and layout parameters remain intact.
Equation wrapping and readable table layout are normal editorial operations.
Empirical values without confirmed results remain `xx`.

## Rationale

A single semantic source prevents older phrasing from returning during
translation. Separating body and bibliography matches both the user request
and the official AAMAS 2027 submission instructions. Reference quality depends
on traceable support for the argument, not on copying another paper's count.

## Consequences

The canonical PDF remains `artifacts/aamas2027/main.pdf` under ADR 0050.
Each candidate build preserves its source snapshot and verification record.
Promotion requires a measured eight-page body, separate references, resolved
citations, no overfull boxes, and visual inspection. This writing decision
does not change the research Goal, accepted method decisions, or scientific
submission-gate requirements.

Official source: https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/
