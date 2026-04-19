# `artifacts/rebuttals/` — Rebuttal Records

> Created: 2026-04-19 per **U-002-decide ✅** (user batch approval).
> Owner: scientist (writing) + user (final approval before submission).
> Sibling of `artifacts/idea_reviews/` (independent reviewer JSONs).

---

## 1. Purpose

This directory holds the scientist's **rebuttal drafts and final responses** to ARR / EMNLP reviewer feedback after each reviewer batch. It is the **production-side** counterpart to `artifacts/idea_reviews/` (which holds the input reviewer reports themselves).

A rebuttal record exists for two situations:
1. **Internal mock rebuttal** — after our own reviewer-agent batch (`reviewer_<YYYYMMDD>_*`), the scientist drafts a rebuttal to show "if a reviewer raised X, what would we answer?". This is a **paper-quality rehearsal** before the real ARR submission and is required by `four-role-todo-workflow.mdc §11.4 (S-104 step ③)`.
2. **Real ARR / EMNLP rebuttal** — after a real submission cycle, when the meta-review + reviewer comments arrive, the scientist drafts the official rebuttal here, the user reviews + edits + finalizes, then submits via OpenReview.

---

## 2. Directory layout

```
artifacts/rebuttals/
├── README.md                                    ← you are here
├── rebuttal_<YYYYMMDD>_<NN>_<6char-hash>/       ← one folder per rebuttal
│   ├── source_review_id.txt                     ← which reviewer batch this rebuts
│   ├── rebuttal_draft.md                        ← scientist's first draft
│   ├── rebuttal_final.md                        ← user-approved final version
│   ├── changes_made_to_paper.md                 ← what we actually changed in edo_paper.tex
│   └── status.txt                               ← {draft, user_review, finalized, submitted, accepted, rejected}
└── (no aggregated summary file yet; can add `rebuttal_index.jsonl` if multiple rebuttals accumulate)
```

The 6-char hash is a content fingerprint (e.g. SHA-256 first 6 chars of `source_review_id + rebuttal_draft.md`); this prevents accidental name collisions across multiple drafts.

---

## 3. Workflow

### 3.1 Triggering a rebuttal record

A rebuttal record is created when **either**:
- a reviewer batch lands in `artifacts/idea_reviews/reviewer_*` (internal mock), OR
- a real reviewer batch arrives from OpenReview / ARR.

The scientist then runs `S-104` (mandatory 4-step loop in `SCIENTIST_TODO.md §B.4`):
1. Read every weakness / missing experiment / fix-for-8+ from the review.
2. Triage: which feedback to accept vs. reject (with criteria).
3. For accepted feedback → create `S-XXX` fix-TODOs in `SCIENTIST_TODO.md §B.5`.
4. Write `dissent_log` for rejected feedback (in `SCIENTIST_TODO.md §C` AND in this rebuttal's `rebuttal_draft.md`).

### 3.2 Drafting

The scientist creates a new folder `rebuttal_<YYYYMMDD>_<NN>_<6char-hash>/` and writes:
- `source_review_id.txt`: just the reviewer ID (e.g. `reviewer_20260419_163139_01_9e72f7`)
- `rebuttal_draft.md`: full prose rebuttal, organized by reviewer's section numbering (response to weakness 1 / weakness 2 / etc.)
- `changes_made_to_paper.md`: machine-readable diff summary (what edo_paper.tex sections were edited, which `S-XXX` fix-TODOs closed, with commit hashes)
- `status.txt`: `draft`

### 3.3 User review

User reads `rebuttal_draft.md`, makes edits (or asks scientist to revise), eventually approves and renames `status.txt` from `draft` to `user_review`. When user finalizes, `status.txt` becomes `finalized` and `rebuttal_final.md` is created (frozen copy).

### 3.4 Submission

For real ARR rebuttals, user copies `rebuttal_final.md` content into OpenReview. `status.txt` becomes `submitted`. After meta-review verdict lands, `status.txt` is updated to `accepted` or `rejected`, with timestamp.

For internal mocks, `status.txt` jumps directly to `finalized` (no real submission step).

---

## 4. Conventions

- **No new content claims**: per ACL rebuttal rules, rebuttals must NOT introduce new experiments / new methods / new claims. Only clarify existing content. Internal mock rebuttals follow the same rule for honesty in rehearsal.
- **Length**: official ARR rebuttals are limited (typically 1500-3000 words depending on cycle). Internal mock rebuttals follow the same length budget for realism.
- **Tone**: respectful, evidence-based; cite specific paper line / table / equation numbers; never argue with reviewer's preferences (only with factual misreadings).
- **Citation style**: when referencing the paper from rebuttal, use `\S 4.3 / Finding 2` style (matches paper section labels in `article/latex/edo_paper.tex`).

---

## 5. First rebuttal (open)

The first rebuttal that **must** be drafted here is for `reviewer_20260419_163139_01_9e72f7` (P5 oral gatekeeper, overall=4.5, weak_reject). However, this rebuttal is **blocked on `U-011-decide`** (framing pivot decision) because the response strategy depends on whether we choose path (a) "Stage-1 negative result reframing" or path (b) "implement Stage-2 first". Once U-011 is decided, scientist creates `rebuttal_20260419_01_<hash>/` and proceeds.

Tracking ID: `tracking-rebuttal-001` in `SCIENTIST_TODO.md §B.5`.
