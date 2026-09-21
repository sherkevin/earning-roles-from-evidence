# OfficeBench B0 structural audit

Summary:

{
  "officebench_commit": "b978b808667c32b52ce19a67ce1def1de9ae02b7",
  "instances": 300,
  "families": 167,
  "family_counts": {
    "1": 22,
    "2": 46,
    "3": 99
  },
  "instance_counts": {
    "1": 93,
    "2": 95,
    "3": 112
  },
  "cross_level_exact_duplicate_groups": 1,
  "three_app_families": 99,
  "eligible_extension_families": 33,
  "eligible_fraction": 0.3333,
  "contain_ge_070": 43,
  "contain_ge_080": 32,
  "candidate_added_op_counts": {
    "email.read": 5,
    "email.send": 9,
    "reason.check": 2,
    "word.write": 4,
    "calendar.create": 8,
    "pdf.write": 8,
    "calendar.read": 1,
    "image.write": 2,
    "reason.aggregate": 2,
    "excel.write": 3,
    "pdf.read": 6,
    "word.read": 2,
    "reason.summarize": 3,
    "reason.filter": 1
  },
  "lower_op_support": {
    "fs.rename": 8,
    "excel.write": 20,
    "excel.read": 19,
    "reason.aggregate": 14,
    "reason.check": 2,
    "word.write": 12,
    "pdf.read": 15,
    "pdf.write": 8,
    "image.read": 10,
    "image.write": 5,
    "word.read": 6,
    "email.send": 8,
    "email.read": 12,
    "reason.summarize": 6,
    "calendar.create": 8,
    "calendar.read": 9,
    "reason.filter": 2
  },
  "thresholds": {
    "contain": 0.7,
    "cosine": 0.42
  },
  "note": "Zero-inference heuristic structural audit. Eligible rows require manual semantic validation before a frozen split."
}

## High-confidence candidate extensions

- 3-59 <- 2-19 | added=excel.write,pdf.read,pdf.write | contain=1.00, cosine=0.96
- 3-25 <- 2-6 | added=image.write,pdf.write,word.write | contain=1.00, cosine=0.95
- 3-12 <- 2-1 | added=email.read,email.send | contain=1.00, cosine=0.93
- 3-50 <- 2-15 | added=image.write | contain=1.00, cosine=0.92
- 3-51 <- 2-15 | added=email.send | contain=1.00, cosine=0.91
- 3-43 <- 2-12 | added=email.send | contain=1.00, cosine=0.89
- 3-76 <- 2-31 | added=email.send | contain=1.00, cosine=0.84
- 3-23 <- 2-6 | added=calendar.create,calendar.read | contain=1.00, cosine=0.78
- 3-17 <- 2-3 | added=email.read | contain=1.00, cosine=0.76
- 3-24 <- 2-7 | added=calendar.create | contain=1.00, cosine=0.71
- 3-52 <- 2-16 | added=calendar.create,email.send | contain=1.00, cosine=0.58
- 3-71 <- 2-27 | added=pdf.write | contain=1.00, cosine=0.58
- 3-74 <- 2-29 | added=excel.write | contain=0.90, cosine=0.89
- 3-96 <- 2-43 | added=word.read,word.write | contain=0.89, cosine=0.85
- 3-26 <- 2-7 | added=email.read | contain=0.89, cosine=0.75
- 3-35 <- 2-10 | added=reason.aggregate | contain=0.88, cosine=0.66
- 3-36 <- 2-10 | added=calendar.create,reason.aggregate | contain=0.88, cosine=0.65
- 3-93 <- 2-40 | added=pdf.read,pdf.write | contain=0.86, cosine=0.91
- 3-62 <- 2-22 | added=pdf.read,pdf.write | contain=0.86, cosine=0.88
- 3-69 <- 2-24 | added=excel.write,pdf.read,word.read | contain=0.83, cosine=0.87
- 3-19 <- 2-5 | added=email.send,reason.check,word.write | contain=0.78, cosine=0.76
- 3-20 <- 2-5 | added=calendar.create,pdf.write,reason.check,word.write | contain=0.78, cosine=0.69
- 3-95 <- 2-42 | added=reason.summarize | contain=0.77, cosine=0.73
- 3-97 <- 2-48 | added=pdf.read,pdf.write,reason.summarize | contain=0.75, cosine=0.59
- 3-54 <- 2-18 | added=email.send | contain=0.71, cosine=0.64
- 3-100 <- 2-50 | added=email.send | contain=0.67, cosine=0.63
- 3-40 <- 2-11 | added=calendar.create | contain=0.67, cosine=0.60
- 3-75 <- 2-30 | added=email.read,pdf.read | contain=0.67, cosine=0.45
- 3-27 <- 2-8 | added=email.read,email.send | contain=0.55, cosine=0.64
- 3-78 <- 2-32 | added=reason.summarize | contain=0.50, cosine=0.71
- 3-79 <- 2-32 | added=calendar.create | contain=0.50, cosine=0.66
- 3-28 <- 2-8 | added=calendar.create | contain=0.45, cosine=0.60
- 3-83 <- 1-6 | added=pdf.write,reason.filter | contain=0.25, cosine=0.60

## Curated B0 verdict

**B0 PASS for a restricted, evaluator-reviewed compositional subset; OfficeBench is not yet benchmark-locked.**

Manual review retained 15 parent-to-extension relations across 12 distinct base families. Every retained pair shares at least one byte-identical relevant input artifact between parent and child. The added output roles cover calendar, email, Excel, image, PDF, and Word. Three base families (2-7, 2-15, 2-29) each have two different held-out extensions, enabling sibling-composition tests rather than only one linear continuation.

The frozen reviewed manifest is `curated_pairs.json`. Its parent/child tasks, input hashes, added output role, and exclusions are explicit. The earlier 33-row heuristic candidate list is discovery evidence only and must not be used directly as an experiment split.

### Exclusion policy

Known cross-level duplicates are not unseen compositions. Tasks with task/evaluator disagreement, missing verification of a claim-critical requested output, inconsistent source modality/path, or known upstream correction PRs are excluded from the core set. Examples include 3-43, 3-70, 3-97, 3-99, and the duplicated 2-13/3-45 family.

### Scientific boundary

B0 establishes that OfficeBench contains a natural, public, programmatically evaluated parent/extension structure sufficient to construct a non-synthetic compositional transfer slice. It does **not** show that local models can solve the slice, that task exposure creates measurable worker differentiation, or that evidence-conditioned rebinding helps. Those are B1 and later A-T03/A-T04/A-T06 gates.
