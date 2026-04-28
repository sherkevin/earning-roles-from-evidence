# Artifact Manifest For Current EDO-Frame Draft

Date: 2026-04-28
Owner role: scientist

This manifest prepares the artifact / provenance mapping requested by recent responsible-research reviews. It is a working submission-support document, not a claim that every artifact is final.

## 1. Paper Sources And Builds

| Item | Path | Status | Notes |
|---|---|---|---|
| Main LaTeX source | `article/latex/edo_paper.tex` | active | Current build target. |
| Appendix source | `article/latex/edo_appendix.tex`; `article/latex/edo_appendix_content.tex` | active | Supplementary pseudocode, checklist, and appendix tables. |
| Main PDF | `article/build/edo_paper.pdf` | generated | Latest build verified by `scripts/build_paper.ps1`. |
| Appendix PDF | `article/build/edo_appendix.pdf` | generated / may be file-locked locally | Alternate verification build used `edo_appendix_check.pdf` when the main appendix PDF was locked. |
| Build script | `scripts/build_paper.ps1` | active | Reports page count, main-body page gate, overfull/underfull hboxes. |

## 2. Core Code And Runtime

| Item | Path | Status | Notes |
|---|---|---|---|
| Runner | `workspace/idea04_core/runner.py` | active | Checkpoint/resume, JSONL trace files, metrics writing. |
| Methods | `workspace/idea04_core/methods.py` | active | Internal baselines, Stage-2 chain, EDO-Frame bridge. |
| Contracts | `workspace/idea04_core/contracts.py` | active | Typed packet / trace contracts. |
| EDO-Frame prototype | `codes/edo_frame/` | active prototype | Local NoteBoardMemory, ToolRegistry, ToolSelector, event schemas. |
| EDO-Frame tests | `workspace/idea04_core/test_edo_frame_chain_method.py`; `codes/edo_frame/tests/` | active | Covers bridge behavior and local framework components. |

## 3. Seed Slices And Datasets

| Dataset | Paths | Status | Notes |
|---|---|---|---|
| HotpotQA | `artifacts/seed/hotpotqa_validation_200.jsonl`; `artifacts/seed/hotpotqa_validation_200_seed43.jsonl`; `artifacts/seed/hotpotqa_validation_200_seed44.jsonl` | active | Main HotpotQA slice and disjoint robustness slices. |
| MuSiQue | `artifacts/seed/musique_validation_200.jsonl`; `artifacts/seed/musique_validation_500.jsonl` | active where present | Used for negative local transfer gates. |
| 2WikiMultiHopQA | `artifacts/seed/2wiki_validation_100.jsonl`; `artifacts/seed/2wiki_validation_200.jsonl` | active where present | Official-data seed pack prepared by engineer; local n=50 transfer gate is negative. |

## 4. Main Evidence Artifacts

| Task | Result Doc | Machine Outputs | Paper Use |
|---|---|---|---|
| `E-042` local Phi-4 wave | `docs/engineer/results/E-042_local_open_weight_wave0_20260427.md` | `artifacts/emergence/e042_phi4_wave0_n200_20260427_110027/` | Fragile local diagnostic. |
| `E-045` robustness | `docs/engineer/results/E-045_phi4_multiseed_robustness_20260427.md` | `artifacts/emergence/e045_phi4_multiseed_paired_bootstrap.md` and seed run dirs | Blocks robust local-claim promotion. |
| `E-047` MuSiQue transfer | `docs/engineer/results/E-047_multidataset_local_transfer_20260427.md` | `artifacts/emergence/e047_*` | Negative transfer boundary. |
| `E-050` 2Wiki transfer | `docs/engineer/results/E-050_2wiki_local_transfer_gate_20260428.md` | `artifacts/emergence/e050_phi4_2wiki_transfer_gate_n50_20260428_104856/` | Negative transfer boundary. |
| `E-049` EDO-Frame ablation | `docs/engineer/results/E-049_edo_frame_consumption_layer_ablation_20260427.md` | `artifacts/emergence/e043_step7_step35_full_n200_20260427_143903/` | Causal but non-positive memory/tool evidence. |
| `E-055` mechanism metrics | `docs/engineer/results/E-055_mechanism_metrics_existing_artifacts_20260428.md` | `artifacts/mechanism_metrics/e055_20260428_local/` | Bounded organization metrics; no strong emergence claim. |
| `E-056` sensitivity gate | `docs/engineer/results/E-056_no_paid_sensitivity_gate_20260428.md` | Uses `E-055` and `E-049` artifacts | Bounded negative sensitivity evidence. |

## 5. Known Gaps

- Canonical paid `gpt-4.1-mini` Wave-1 external-baseline matrix remains blocked by `C-027`.
- Final Figure 1 and Figure 3 assets remain blocked by `C-026`.
- A complete hash manifest for every released file should be generated at final packaging time.
- The main paper still cannot claim matched SOTA performance or robust cross-dataset transfer.
