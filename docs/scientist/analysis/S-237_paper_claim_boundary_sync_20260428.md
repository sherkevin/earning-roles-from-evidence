# S-237 Paper Claim Boundary Sync After R-FULL-027 / Negative Evidence

Date: 2026-04-28
Author role: scientist

## 1. Purpose

`S-236` accepted `R-FULL-027` as a valid BP-EXPERIMENTS cap and updated the review with newly landed engineer artifacts:

- `E-044`: negative SmolLM3-3B smaller-backbone control;
- `E-047`: negative MuSiQue transfer;
- `E-049`: causal but non-positive EDO-Frame consumption-layer ablation;
- `E-045`: multi-seed Phi-4 robustness remains inconclusive because pooled CI crosses zero.

`S-237` syncs those facts into the paper so the manuscript does not overclaim local emergence, transfer, or governed memory/tool benefits.

## 2. Paper Edits

Edited `article/latex/edo_paper.tex`:

1. Abstract now calls the Phi-4 result a fragile capability-boundary signal and names the mixed/negative follow-up checks.
2. Contribution bullet now says the local gain weakens under multi-seed and transfer checks.
3. Governed memory/tool subsection now states that consumption-layer ablations affect answers but are not beneficial.
4. Figure 3 caption now frames the action loop as auditable infrastructure with non-positive ablation evidence.
5. Table 2 caption now warns that follow-up pooling weakens the single-seed gain into a candidate signal.
6. Findings now explicitly record that MuSiQue and SmolLM3 controls are negative.
7. Conclusion was compressed and claim-bounded.
8. Limitations now state that follow-up checks are mixed or negative rather than confirmatory.

## 3. Verification

Build command:

```powershell
powershell -ExecutionPolicy Bypass -File "scripts/build_paper.ps1"
```

Final build result after clearing locked stale intermediates:

```text
[OK]   build succeeded
[INFO] PDF pages (incl. Limitations + Refs): 10
[INFO] Main body ends on page 8 (Limitations on page 8, 98 preceding lines): COMPLIANT
[INFO] Overfull hboxes: 0   Underfull hboxes: 32
[PDF ] D:\Codes\idea04\article\build\edo_paper.pdf (12920.8 KB)
```

Additional grep check:

```text
rg "robust|universal|consistently|SOTA|state-of-the-art|improves performance|beneficial|generalise|generalize|positive local" article/latex/edo_paper.tex
```

The remaining hits are claim-bounded contexts such as "not a universal performance claim", "negative rather than confirmatory", "robust to backbone change" for the fixed safety gate, and explicit non-generalisation language.

ReadLints was run on the edited paper, the new S-236 triage document, and `SCIENTIST_TODO.md`; no linter errors were reported.

## 4. Scientific Verdict

The paper is now more honest but not stronger. It should be evaluated as:

- a clear framework paper with an executable Stage-1 reduction;
- a negative strong-backbone result;
- a fragile local Phi-4 candidate signal;
- negative transfer / smaller-backbone controls;
- causal-but-non-positive memory/tool ablation evidence.

This reduces overclaim risk for the next review. It does not solve the BP-EXPERIMENTS cap because external baselines, broader datasets, sensitivity sweeps, and stronger statistical closure remain missing or parked.

## 5. Status

`S-237` is complete.
