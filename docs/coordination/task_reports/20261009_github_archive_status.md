# GitHub archive and current AAMAS status — 2026-10-09

## Purpose

This report records the complete research snapshot being archived to the configured GitHub
remote `github-archive` (`https://github.com/sherkevin/earning-roles-from-evidence.git`) on
branch `codex/aamas-real-validation-20260922`. It accompanies the code, manuscript, evidence,
experiment logs, figures, PDFs and research notes in the same commit.

## Current scientific state

- Goal: `ACTIVE`, Goal v1.0. The four-arrow chain remains delivery → situated judgment →
  attributable role evidence → future assignment → unseen quality/cost.
- Active research registry: v1.10. Storyline v1.1, method v1.3, benchmark/baseline v1.1 and
  their three evaluation specifications remain the sole active definitions.
- Submission gate: `internal_revision_not_submission_ready`; A-R01 through A-R15 are pending.
- PIPE2 runtime replay: 40 valid receipts, 0 labels, 40 `UNKNOWN`; recipient judgment,
  consumer action and terminal outcome are absent from the receipts. This is an identification
  gap and protocol evidence, not efficacy.
- PIPE2 observation bridge: blocked by handoff semantics. The recipient receives an opaque
  artifact rather than producer source files, and current receipts do not contain typed J/A/Y
  or before/after recipient manifests.
- Baseline parity: 14 zero-call design checks pass, but the manifest is design-only and effect
  estimability is false. The benchmark and baseline remain unfrozen.
- Canonical PDF: `artifacts/aamas2027/main.pdf` is byte-identical to its recorded source,
  SHA-256 `85fdb1f46ce9919de21a28bbd8e51a7b79862de13eec1d7befa98893a0150591`, with 8 body
  pages, 9 total pages, references from page 9, zero overfull boxes and `submission_ready=false`.

## Upload scope

The snapshot includes the current manuscript and Chinese reading copy, figures and versioned
builds, research specifications, task reports, scripts, tests, experiment configurations/raw
logs/summaries, PDFs, and the new research charter/claim/evidence/experiment artifacts. The nine
upstream benchmark repositories are recorded as pinned Git submodules with an archive manifest;
their local uncommitted patch and untracked dataset directory are preserved under
`references/benchmark_sources/LOCAL_CHANGES_20261009/`.

Ignored credentials and `.env` files remain excluded by the repository rules. Four local
operational artifacts are excluded from the archive because they are not research evidence:
`.omo/run-continuation/`, `bookstore.db`, `remote-control-pairing.png`, and `ossutil_output/`.
Their exclusion prevents session state, pairing material and storage-transfer noise from being
published while retaining the research files and status needed for reproducibility.

## Next gate after archive

Complete a versioned PIPE2/PIPE1 handoff descriptor, freeze two structural roots and the
same-information contextual arm, then run one bounded real-API development matrix. Keep every
failed, incomplete or `UNKNOWN` event in JSONL. Scientific claims, result cells and A800 work
remain closed until that matrix and an independent confirmation satisfy the Goal.
