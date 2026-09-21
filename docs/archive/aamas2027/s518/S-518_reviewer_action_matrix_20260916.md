# EMNLP reviews -> AAMAS revision actions

Source: actual author-provided OpenReview review compilation in the repository root, submission 11746, July 2026. Historical internal simulated reviews are not used as external reviewer evidence. Status reflects 2026-09-16 work, not predicted experiment outcomes.

| Issue | Source | Diagnosis / concrete action | Status and acceptance criterion |
|---|---|---|---|
| Dense writing, undefined acronyms, forward-defined notation | AC; 2sxq; Dz77; vJUA | Rebuild around a delegation decision, define one local record and one task type, put implementation identities in a single table | DONE in `article/aamas2027/main.tex`; final prose depends on empirical reconciliation |
| No actual trajectory | F61c | Add recorded HotpotQA failure with split, memory retrieval, REJECT_REROUTE, incorrect terminal acceptance, and observed request usage | DONE; trace JSON preserved in `artifacts/analysis/s518_aamas_audit_20260916/worked_failure_trace.json` |
| HotpotQA .76 vs .43 unexplained | AC; Dz77 | Identify GPT-4.1-mini / n=200 versus Qwen2.5-3B / n=7405; remove cross-population juxtaposition | DONE; manuscript explains boundary, audit reproduces Qwen scores |
| 72-call versus 4-call comparison and missing real costs | AC; F61c; vJUA | Separate variant-specific caps from measured cost; expose HotpotQA 41.72% token increase; shared budget ledger for all model calls/retries | DIAGNOSIS DONE; implementation and matched-budget runs OPEN |
| Largest effect on 2Wiki; tiny HotpotQA effect | AC; F61c; Dz77 | Report exact absolute effect and variant identity; stop calling same-backbone control organization-only isolation | WRITING DONE; fresh held-out result under a shared frozen policy OPEN |
| Only one small headline backbone | AC; Dz77 | Retain 3B as continuity, add materially stronger feasible open-weight model under identical protocol | DESIGNED / NOT RUN |
| QA-only generality, synthetic transfer insufficient | AC; Dz77 | Add externally defined executable non-QA task; prefer a coordination-sensitive task, with pilot feasibility and fixed public ground truth | DESIGNED / NOT RUN; old coding attempts do not close this |
| Missing nearest dynamic role / resource allocation work | AC; vJUA | Read and cite AgentNet, dynamic role assignment, RepuNet, ReAcTree, GPTSwarm, MoRSE; include a simple contextual-bandit alternative | LITERATURE DONE; direct matched comparisons OPEN |
| Many arbitrary constants, no selection procedure | AC; Dz77 | Replace seven-axis weighted story with minimal task-conditioned estimate, cost weight, update rate, and exploration; tune only on development data; freeze sensitivity grid | DESIGN DONE; implementation, sensitivity, and selected values OPEN |
| Neutral / negative controls omitted from central explanation | vJUA | Preserve all-tools, random-tools, no-tool-history, harmful active-audit directions in main/supplement; stop claiming universal necessity | DONE for historical evidence; true single-component interventions OPEN |
| Framework-breadth summary too compressed | vJUA | Prioritize closer comparisons and a method-identity table; retain the old 24-cell matrix as historical secondary evidence, not the new central result | REFRAMED; no need to spend scarce main pages on a weak proxy for conceptual closeness |
| Reproducibility/software availability unclear | F61c; 2sxq; Dz77 | Isolated build, official style hashes, per-input evidence manifest, scorer audit, exact scripts, no invented runtime provenance | PARTIAL; runnable clean release and exact runtime snapshot OPEN |
| No author response during discussion | AC | Put Nov 20--24 rebuttal in calendar; maintain claim/evidence index and prepare point-by-point responses against actual new reviews | RECORDED; no response/submission was sent |

## Additional author-side corrections

| Issue not fully captured by reviews | Action | Status |
|---|---|---|
| Headline policy state resets per task | Remove cross-episode emergence interpretation; specify explicit persistent state and freeze/shuffle/reset controls | CODE AUDIT / REFRAMING DONE; corrected runtime OPEN |
| False fixed-step EMA L2 convergence | Replace with exact finite-n mean/variance and nonzero limiting variance; distinguish conditional rank preservation from convergence | DONE; proofs in main text |
| Cosine scalar reduction does not yield competence-dependent utility | Remove claimed formal reduction | DONE in new draft |
| Audit label can fail to produce claimed transition | Add actual trace; require transition-level tests before running experiments | TRACE DONE; runtime correction OPEN |
| Project scorer not identical to official HotpotQA | Official-function check changes six rows; keep historical score label, rescore both paired sides before official comparison claims | CHECK DONE; all-backend scorer parity OPEN |
| Validation selection and MBPP oracle gating | Treat old repaired configurations as development/history; select deployable baselines before test; keep oracle as upper bound only | DESIGN CORRECTED; fresh confirmation OPEN |

## Closure rule

Writing a remedy does not close an empirical review issue. Mark an OPEN scientific item DONE only after its implementation hash, frozen configuration, raw predictions/request ledger, statistical report, and reconciled manuscript claim are all linked. If a test fails, close it as a measured boundary and revise the claim; do not delete the failed row or silently replace the split.
