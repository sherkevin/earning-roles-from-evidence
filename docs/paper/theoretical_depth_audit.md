# Theoretical-Depth Audit — EDO paper vs. EMNLP/NeurIPS/ACL Oral / Best-Paper standard

> **Maintainer**: scientist (R48, 2026-04-20). Target bar: EMNLP/NeurIPS/ACL oral / Best Paper, per user directive 2026-04-20 "我们对标的是 NIPS、emnlp、acl 这类顶会的 oral，要有高标准严要求".
>
> **Method**: full-PDF read of 3 benchmark Oral/Best/Outstanding papers (`references/emnlp/`) anchored on **theoretical depth** (provable lemmas, closed-form derivations, irreducibility/convergence claims, falsifiable symbolic claims) rather than empirical depth. Contrast against the current EDO methodology (`article/latex/edo_paper.tex` §3.1–§3.9).
>
> **Update trigger**: any commit that changes §3 Methodology or Appendix E Algorithm 1; any reviewer batch that raises D1 Soundness findings.

---

## 0. Headline — where EDO stands vs. top-venue oral bar

| Dimension | EDO current (R47 state) | Top-venue oral bar | Gap |
|---|---|---|---|
| **Formal definitions** | Types named (e.g. $P_i$, $B_i^t(j)$, $\phi(z)$, $\mathrm{Fit}$, $U^{self/out/split}$), types given | Full function signatures with domain/range + measurability/continuity assumptions | ⚠ medium — needs explicit function-space declarations |
| **Theorems / lemmas / corollaries** | **0** proven | ≥2–3, with proofs | ❌ major |
| **Closed-form derivations** | **0** closed forms given | ≥1 (typically cost-utility trade-off, fixed-point, rank bound, or loss decomposition) | ❌ major |
| **Convergence / fixed-point result** | Implicit (`P_i^{t+1} = (1-μ)P_i^t + μ(·)`) but **no proof that P_i^t converges**, **no stationarity claim**, **no attractor analysis** | Proof of convergence + characterization of fixed-point set | ❌ major |
| **Complexity bounds** | Stage-2 recursion bounds $H_{\max},d_{\max},n_{\max},k_{\max}$ stated but **no complexity theorem** (e.g. "Process($z$) executes $\le f(H_{\max},d_{\max},n_{\max},k_{\max})$ LLM calls") | Closed-form complexity with proof | ❌ major |
| **Falsifiable hypothesis** | Stage-2 agenda §4.4 E1–E5 lists *qualitative* predictions; **no symbolic falsifiable claim** (e.g. "if $\mu \to 0$ then $P_i^t \to P_i^{\infty}$ exists and equals $\mathbb{E}[\cdot]$") | Explicit sym. claims of the form "if X then Y with $p < \alpha$" | ❌ major |
| **Mechanism-isolation theorem** | Prose: §3.9 says "R1/R2/R3 are Stage-2 hooks"; **no formal claim** that "Stage-1 TCPB = degenerate instance of EDO with Split-weight $=-\infty$, Audit $\equiv \mathrm{Accept}$, $B \to c$ via mean-axis fold" | Formal reduction theorem: "Under conditions C, EDO reduces to TCPB" | ⚠ medium (prose exists, formalization missing) |
| **Decentralization formal claim** | Prose: §3.1 "near-homogeneous agents within a fixed role-prior topology"; no **formal decentralization result** (e.g. "no agent has global info; interaction is $k$-local") | Formal $k$-locality claim + proof of locality preservation under updates | ❌ major |
| **Rank / low-rank structure** | None claimed | Common at oral bar (e.g. Backward Lens Lemma 4.1: gradient matrix rank $\le n$) | ❌ major |

**Net assessment**: EDO current § 3 is **framework + restricted prototype + prose motivation**. **It has zero formal theorems, lemmas, or closed-form derivations**. All symbolic equations are *definitions* not *propositions*. Under **P1 Strict ARR SAC lens** (R-FULL-004, R-FULL-011), this is the single largest D1 soundness gap after the undefined-symbols issue (which R47 just fixed via itemize restructure).

---

## 1. Benchmark oral papers — what "theoretical depth" looks like

### 1.1 Backward Lens (EMNLP 2024 Best) — `04_backward_lens_lm_gradients.pdf`

**Subject**: projecting LM gradients into vocabulary space.

**Core theoretical contribution**:
- **Lemma 4.1** (formal statement + proof): *"Given a sequence of inputs of length $n$, a parametric matrix $W$ and a loss function $L$, the gradient $\partial L/\partial W$ produced by a backward pass is a matrix with a rank of $n$ or lower."*
- **Proof by construction**: $\partial L/\partial W = x^\top \cdot \delta$; rank of single outer product $\le 1$; sum of $n$ rank-1 matrices has rank $\le n$; with linear dependencies rank can drop.
- **Corollary-style result**: for the last layer, rank $= 1$ (Appendix A).
- **Mechanism**: "imprint and shift" — formalized as concrete operation on the gradient's $x$-span and $\delta$-span decomposition.

**Pattern**: *one sharp provable claim* ($\mathrm{rank} \le n$) + concrete mechanism name tied to the lemma + empirical verification. The lemma alone is ~5 lines + 10-line proof. Nothing baroque, everything falsifiable.

### 1.2 Explanation-Refiner (EMNLP 2024 Outstanding) — `21_verification_refinement_explanations_theorem_proving.pdf`

**Subject**: neuro-symbolic NLI with LLMs + theorem provers (Isabelle/HOL).

**Core theoretical contribution**:
- **Formal guarantee**: if TP finds a proof of $H \vdash G$ from explanations $E$, then $E$ logically entails $H \Rightarrow G$ — by soundness of Isabelle/HOL.
- **Autoformalization correctness property**: for a human explanation $e$ in natural language, $\mathrm{Formalize}(e)$ yields a FOL formula $\varphi_e$ whose validity can be decided by TP; the formalization error mode is *syntactic* not *semantic* (TP returns "unprovable" not "false-positive proof").
- **Iteration invariant**: at each refinement step, the candidate explanation set is non-decreasing in TP-provability.

**Pattern**: theoretical guarantees **borrowed** from an external formal system (TP soundness) + explicit autoformalization correctness + loop invariant. No new theorems proved by the authors, but the paper is transparent about what guarantees it does and does not carry.

### 1.3 Infini-gram mini (EMNLP 2025 Best) — `01_infinigram_mini_fm_index.pdf`

**Subject**: trillion-token $n$-gram indexing via FM-index.

**Core theoretical contribution**:
- **Space complexity theorem**: FM-index achieves $O(n \log \sigma)$ bits for text of length $n$ over alphabet $\sigma$, compared to $O(n \log n)$ for suffix array.
- **Time complexity**: substring-count query in $O(|P|)$ time using backward search.
- **Concrete numerical proof**: builds a 4TB FM-index over 1.4T tokens (≈ 3 bits/token ratio), achieves 100 ms latency at 99.9% percentile.
- **Practical reduction**: infini-gram ($n$-gram for arbitrary $n$) count query → FM-index backward-search → $O(|P|)$.

**Pattern**: concrete algorithmic result with **proven complexity bounds** (space & time) + **practical empirical verification** that the bounds are realized at scale. Best-Paper because theory is both deep (compressed index) AND realized (4TB built, served, benchmarked).

---

## 2. EDO § 3 — gap analysis line-by-line

### 2.1 §3.1 Problem formulation

**Current**:
- Defines $\mathcal{G} = (\mathcal{A}, \mathcal{E})$ as sparse connected directed graph.
- Task $x = (q, y, C)$, task tree as node list with audit state.

**Gap vs. oral bar**:
1. ❌ **No formal decentralization / $k$-locality definition**. Best-Paper would state: *"agent $a_i$ at time $t$ observes only $\{S_j^{t-1}\}_{j \in \mathcal{N}(i)}$ and $\mathcal{N}(i)$; no agent accesses the full graph $\mathcal{G}$"*, and then prove this invariant is preserved by the three-action policy.
2. ❌ **No formal task-tree grammar**. Task tree is a recursive data structure but its BNF / production rules are not given; reviewers doing §1.5.0 must guess.
3. ⚠ Graph connectedness / edge-cardinality bounds for "sparse" are unspecified.

**Minimal fix** (sprint-scope, < 1 page): add formal decentralization definition + BNF for task-tree.

### 2.2 §3.2 Agent state and personality

**Current**:
- $S_i^t = \{P_i^t, B_i^t, M_i^t, H_i^t, \mathcal{N}(i)\}$ listed.
- $P_i$ is 7-dim vector with named axes (solve/decompose/audit/integrate/explore/efficiency/reliability).

**Gap**:
1. ❌ **No type signature**: is $P_i^t \in \mathbb{R}^7$, $[0,1]^7$, or $\Delta^6$ (simplex)? Normalization / constraint space not stated.
2. ❌ **No dimension-choice justification**: why 7 axes? Why these 7? Ablation over axis choice would be ideal but absent.
3. ❌ **No falsifiable identifiability claim**: are the 7 axes linearly independent? If two of them collapse under real data (e.g. decompose ≡ integrate) — is that a failure or expected?

**Minimal fix**: state type $P_i^t \in [0,1]^7$ explicitly + "axes chosen to cover observed interaction modes; future work will ablate".

### 2.3 §3.3 Task signatures and local utility

**Current**:
- $\phi(z) \in \mathbb{R}^7$ with 7 named axes (need_decompose / ...).
- $\mathrm{Fit}(P, \phi) = \langle P, \phi \rangle / (\|P\|\|\phi\|) \in [0,1]$.
- Three utility functions $U^{self/out/split}$ as linear combinations of Fit and cost/risk terms.

**Gap**:
1. ❌ **$\mathrm{Fit}$ range claim** $\in [0,1]$ is incorrect when $P \cdot \phi$ can be negative (cosine similarity is in $[-1, 1]$). Either constrain $P, \phi \in \mathbb{R}_{\ge 0}^7$ or change range. This is an **actual sign-error-class bug** a P1 Strict reviewer should flag; R-FULL-011 didn't flag it because P1 focused on undefined symbols.
2. ❌ **No proof of optimality of $\pi_i(z) = \arg\max$**. Why argmax the three utility branches? Expected utility = optimal under what utility model? For stochastic settings, should be expected utility over belief $B_i$.
3. ❌ **No closed-form of utility trade-off frontier**. Given cost/risk, the Pareto frontier in $(F_1, \text{tokens})$ space is not derived. Figure 4 empirically shows TCPB is Pareto-dominated; a *theoretical* result saying "the utility function admits a Pareto frontier characterized by $\lambda_c, \lambda_r$" would strengthen.

**Minimal fix**: correct range for $\mathrm{Fit}$ (add clip or non-negative constraint), add 1-paragraph optimality argument under a stated utility axiom.

### 2.4 §3.4 Recursive upstream audit

**Current**:
- Prose: acceptance obligation, 4-class decision (accept / reject+redo / reject+reroute / reject+resplit).
- Delegation tree semantics.

**Gap**:
1. ❌ **No Markov / semi-Markov formalization**. The audit loop is effectively a stochastic game. Is it a POMDP? MDP? What is the state / action / reward / transition?
2. ❌ **No guarantee that audit decision is tractable**. With $k_{\max}=3, d_{\max}=3$ recursion bounds, branching factor could be exponential. What's the per-query LLM-call complexity?
3. ❌ **No information-theoretic argument**. Why does *recursive* audit dominate *terminal* audit? Best-Paper version: a claim like "recursive audit provides $\Omega(H)$ more bits of feedback than terminal audit, enabling faster credit assignment by factor $H$".

**Minimal fix** (Stage-2-scope): state the audit loop as a depth-limited POMDP + complexity bound on Process($z$) calls.

### 2.5 §3.5 Personality-tag update

**Current**:
- EMA-style update $P_i^{t+1} = \mathrm{clip}((1-\mu)P_i^t + \mu(\eta_{\mathrm{loc}}\text{LocalValue}_i - \eta_{\mathrm{rew}}\text{ReworkPenalty}_i + \eta_{\mathrm{trm}}\text{TerminalValue}_i))$.
- Numeric values $(\eta_{\mathrm{loc}},\eta_{\mathrm{trm}},\eta_{\mathrm{rew}},\mu) = (0.06, 0.10, 0.10, 0.5)$.

**Gap**:
1. ❌ **No convergence result**. Does $P_i^t$ converge as $t \to \infty$ under stationary environment? To what? This is the **single most critical missing theorem**: any reviewer will ask *"what does peer-calibration converge to?"*.
2. ❌ **No stability result**. EMA with $\mu = 0.5$ is highly responsive to recent events — is the update stable or does it oscillate under adversarial / pathological rework signals?
3. ❌ **No bias / efficiency trade-off**. $\mu$ controls bias-variance: smaller $\mu$ = lower variance but slower adaptation. Top-venue version would characterize this trade-off in closed form.

**Minimal fix** (this is the highest-value single theorem for EDO): prove $P_i^t$ is a **supermartingale** under stationarity (or a related stochastic stability result), yielding a fixed-point $P_i^\infty$ interpretable as time-averaged socially observed value.

### 2.6 §3.6 TCPB prototype & §3.7 Why separation matters

**Current**:
- Explicit reduction: Split-weight $-\infty$, Audit $\equiv$ Accept, $B \to c$ via mean-axis fold.
- Weighted utility formula $0.55 c[j] + 0.20 \mathrm{accept}(j) + 0.10 \mathrm{forward\_bias}(j) - \lambda_a \mathrm{audit}(z)$ with concrete weights.

**Gap**:
1. ⚠ Reduction from EDO to TCPB is given in prose but not as a **formal reduction theorem**: e.g. "Let $\mathcal{E}_{\mathrm{EDO}}$ be the EDO execution schema; let $\mathcal{E}_{\mathrm{TCPB}}$ be the TCPB schema. Under conditions $C_1, C_2, C_3$ (Split-disabled, Audit $\equiv$ Accept, $B \to c$ via mean-axis fold), $\mathcal{E}_{\mathrm{TCPB}}$ is the degenerate instance of $\mathcal{E}_{\mathrm{EDO}}$."
2. ❌ **Weights 0.55/0.20/0.10 justification**: why these specific values? §B2 says "hand-set priors, not searched" which is honest but weakens D1. Minimal fix: either add a 2-line sensitivity argument ("results stable within ±0.05 of each weight" — we already have partial evidence from §4.5 ±2× sweep) or explicitly state "these are hyperparameters, a Stage-2 sensitivity sweep is the falsifiability plan."

### 2.7 §3.9 Stage-2 roadmap

**Current**:
- Lists R1/R2/R3 as Stage-2 hooks.
- Cross-references Algorithm 1 lines for each.

**Gap**:
1. ❌ **No per-hook prediction symbolic claim**. "R1 split on 4-hop MuSiQue: $\Delta F_1 > 0$ with $p < 0.05$ under 3-seed paired bootstrap" would be a falsifiable symbolic prediction. Current version just lists the mechanisms.
2. ❌ **Why these three and not others**: R1/R2/R3 chosen why? Any formal argument (e.g. "these are the minimal hooks that recover full-EDO from TCPB")?

---

## 3. Minimal sprint-scope theoretical fixes (T-35, post-R47)

Prioritized by (impact on D1 cap) × (cost in page budget + eng time):

| # | Fix | D1 impact | Cost | Status | Ticket |
|---|---|---|---|---|---|
| T-1 | **Fit range correction**: clip / non-negative constraint, 2 lines | +0.3 on D1 (closes P1-obvious sign-bug) | 5 min | ⏳ | S-165 |
| T-2 | **Formal decentralization statement** ($k$-locality invariant), 3 lines in §3.1 | +0.3 on D1 (decentralization claim now formal) | 15 min | ⏳ | S-166 |
| T-3 | **Personality-tag EMA convergence theorem** under stationarity: either cite Robbins-Monro stochastic-approximation result OR prove $P_i^t$ is a bounded-variation sequence with martingale-like structure, in-paper (≤ 0.25 page) or Appendix F | **+0.5 to +1.0 on D1** (single largest D1 lift) | 45-60 min (borrow from RM literature + write) | ⏳ | S-167 |
| T-4 | **TCPB-as-EDO-reduction theorem**, 4 lines in §3.6 | +0.3 on D1 (formal reduction replaces prose) | 15 min | ⏳ | S-168 |
| T-5 | **Process($z$) complexity bound** $\le H_{\max} \cdot k_{\max}^{d_{\max}}$ with Stage-2 restriction proof, 3 lines in §3.4 / Appendix E | +0.3 on D1 + closes complexity-theorem gap | 15 min | ⏳ | S-169 |
| T-6 | **Symbolic Stage-2 hypothesis list** (R1/R2/R3 each with predicted sign + expected effect size), replaces §3.9 qualitative list | +0.2 on D5 + D4 (falsifiable plan) | 20 min | ⏳ | S-170 |

**Total sprint-scope time**: 1.5–2 hours. **Total expected D1 lift**: +1.5 to +2.0 (from current 4.5 sub-5 → 6.0–6.5 band 6, unlocks D1+0.5 cap permanently).

**Combined with R47 (Symbol Glossary itemize) + E-017 fullval + E-014 canonical ablation + E-018 external SOTA + MuSiQue + Figure 1 vector**, sprint-path overall projection:
- R-FULL-010/011 state: 3.5–4.0
- With sprint data inflow only (no T-1..T-6): 5.8–6.2 borderline
- **With sprint data + T-1..T-6 theorems**: **6.3–6.8 comfortable accept**
- Still below Best-Paper 8.5 by ≈ 1.7 gap → Best-Paper track needs real novel mechanism result.

---

## 4. Best-Paper-track additional theoretical fixes (post-ARR, 2–3 month agenda)

Only reachable if user elects (b) in U-023-decide. These are **not optional** for Best-Paper 8.5 bar:

| # | Fix | Ticket |
|---|---|---|
| T-Best-1 | **Stage-2 R2 audit information-theoretic lower bound**: formal result that recursive audit provides $\Omega(H)$ bits of credit-assignment signal vs. terminal audit's $O(1)$ | S-171 (post-ARR) |
| T-Best-2 | **Emergent-specialization entropy theorem**: under persona-tag update + $k$-local interaction, show that agent-axis specialization entropy decreases monotonically (analog of clustering in graph signal processing) | S-172 (post-ARR) |
| T-Best-3 | **Original novel mechanism with provable advantage vs MAD / AutoGen / MA-RAG** on multi-hop QA: e.g. "R2 recursive audit is provably more sample-efficient than MAD debate for credit-assignment in $H$-hop QA by factor $\Omega(H)$, provided audit decisions are at least $1/2+\epsilon$ accurate" | S-173 (post-ARR) — **this is the missing "original mechanistic breakthrough" that 8.5 requires** |

Without at least one of T-Best-1/-2/-3 proven + empirically verified, Best-Paper 8.5 is **structurally unreachable** regardless of polish effort.

---

## 5. Cross-reference — which reviewer finding maps to which gap

| Reviewer batch | Finding | Addressed by |
|---|---|---|
| R-FULL-001..007 | "undefined symbols" | R47 (Symbol Glossary itemize) |
| R-FULL-011 | D1=4.5 sub-5 cap on ≥10 undefined forms | R47 (same) + T-1/T-4 |
| R-FULL-002/004 (D1<6 P1 strict) | "insufficient formalization of belief update + audit" | T-3 (EMA convergence) + T-5 (complexity bound) |
| R-FULL-001 D3 cap at 4 (MAD overlap risk) | "TCPB not empirically isolated from MAD" | T-Best-3 (provable-advantage theorem) + E-015+E-016 empirical |
| R-FULL-009/010 (Best-Paper structural) | "missing mechanistic novelty claim" | T-Best-1/-2/-3 |

---

## 6. Recommended immediate action (this session, non-blocking E-017 resume)

1. **S-165 Fit range correction** (5 min) — fix Fit formula sign-range bug.
2. **S-166 formal decentralization statement** (15 min) — 3-line inline in §3.1.
3. **S-167 Personality-tag EMA convergence theorem** (45-60 min) — 0.2-0.25 page inline in §3.5 or Appendix F; cite Robbins-Monro (1951) for technique.
4. **S-168 TCPB-as-EDO-reduction theorem** (15 min) — 4-line formal statement in §3.6.
5. **S-169 Process($z$) complexity bound** (15 min) — 3 lines in Algorithm 1 / §3.4.
6. **S-170 Stage-2 symbolic-hypothesis list** (20 min) — rewrite §3.9.

**Total**: ~2 hours scientist self-exec; quota-independent; does not touch code; inline LaTeX edits only.

**Expected impact on next R-FULL-012**: weighted_pre_cap lift from ~4.975 to ~5.5–5.8; overall floor from 4.0 to 4.5; D1 from 4.5 to 6.0 (breaks D1 cap permanently).

---

## 7. Maintenance

**Refresh trigger**:
- Any commit touching `article/latex/edo_paper.tex §3` subsections or Appendix E.
- Any new reviewer batch raising new D1 findings.
- Any successful landing of T-1..T-6 (update status column, bump D1 impact estimate).

**Owned by**: scientist (single editor).
**Related files**:
- `docs/paper/best_paper_structural_audit.md` (§11.5 structural compliance counterpart).
- `docs/paper/benchmark_inventory.md` (baseline+dataset counterpart).
- `docs/coordination/SCIENTIST_TODO.md §B.5` (S-165..S-170 sprint-scope, S-171..S-173 Best-Paper-track).
- Benchmark papers analyzed: `references/emnlp/2024/best/04_backward_lens_lm_gradients.pdf`, `references/emnlp/2024/outstanding/21_verification_refinement_explanations_theorem_proving.pdf`, `references/emnlp/2025/best/01_infinigram_mini_fm_index.pdf`.
