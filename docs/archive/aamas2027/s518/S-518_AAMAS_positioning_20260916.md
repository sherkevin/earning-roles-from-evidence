# AAMAS positioning: what the project should contribute

## Decision

Rebuild the paper around **when accepted contributions deserve future delegation authority**. The proposed title is **When Should an Agent Earn Delegation? Evidence, Reputation, and Coordination in Language-Agent Teams**. Retain EDO as the principle; retire EDO-Frame/TCPB/Stage-2/focused/adaptive as competing scientific concepts in the main story. Keep their exact implementation names only where reproducibility requires them.

The current work belongs most naturally in AAMAS 2027 GAAI. Its path to a stronger submission is a falsifiable coordination result, not a longer catalogue of components or a stronger claim of universal reasoning performance.

## Independent diagnosis beyond the reviewers

The reviewers correctly identify unreadable notation, weak cost controls, limited backbones/tasks, and missing close baselines. There is a deeper problem: the paper's central explanatory claim and its best measured implementation are different objects.

1. **The headline router does not demonstrate cross-task learning.** `workspace/idea04_core/runner.py:63` retains competence only for two scalar calibration methods. Other methods initialize state inside `_process_one`, including fresh belief stores for task-tree execution. The adaptive selection function in `methods.py:2186` uses question type and dataset hints. The historical performance improvement can therefore arise without a persistent organizational state.
2. **The initial roles are not operationally homogeneous.** The runner starts with named decomposer/evidence-seeker/verifier/synthesizer nodes and default competence; the appendix describes role-specific prompt suffixes. A shared backbone is not a role-free initial condition. The revised experiment needs identical worker prompts and separate controls for structural versus prompt heterogeneity.
3. **Accepted is not correct, and logged is not enforced.** The actual `hotpotqa-0000` trace in the frame matrix logs `REJECT_REROUTE`, then answers locally and incorrectly. This is an implementation-contract discrepancy worth fixing before a theory of auditing is claimed. One trace demonstrates existence, not prevalence.
4. **The EMA convergence statement is wrong.** For independent noise with variance sigma squared and fixed positive step mu, the limit variance is `mu * sigma_squared / (2 - mu)`. The old L2-convergence assertion must be removed. The revised draft states and proves the exact elementary mean/variance result, without claiming a new stochastic-approximation theorem.
5. **The stated scalar reduction is not an algebraic consequence.** A cosine similarity of two positive nonzero scalars equals one. It does not become the varying competence score used by the historical weighted routing formula. The reduction was an implementation analogy, not a demonstrated equivalence; remove its theorem-like presentation.
6. **The official scorer claim is inaccurate.** The project scorer differs from HotpotQA's official normalization/special-answer handling. The same router outputs change from F1 0.432403 to 0.432275 under the official function, with six changed rows. This small difference does not invalidate the whole score, but it makes exact scorer parity an open gate.
7. **Repeated validation repair weakens confirmatory interpretation.** The recorded v2/v3/v6 router changes and many MBPP repairs use observed residuals. Current numbers remain legitimate historical/development observations, but resubmission needs frozen selection and fresh evaluation. A bootstrap does not undo adaptive model selection.
8. **The old MBPP promotion criterion conflates a deployable comparator with an oracle.** Per-task best-of-baselines using test outcomes is an oracle upper bound. Failure against it does not prove inferiority to the strongest fixed deployable baseline. It also does not rescue repeatedly tuned MBPP results as fresh transfer evidence. Keep both statements separate.

The historical source snapshot may differ from today's uncommitted runtime. Findings about current code and findings about preserved traces are explicitly distinct until runtime hashes are reconciled.

## What the existing evidence does support

The offline audit reproduces all 24,815 headline predictions under the project scorer and verifies unique identifiers. MuSiQue and 2Wiki paired means were also reproduced from available comparator predictions. HotpotQA's original direct-baseline file is absent at its archived path, so its paired interval is checked against the archived bootstrap rather than a fresh recomputation.

- HotpotQA: 0.432403 F1; delta over archived direct agent 0.004470; 41.72% more recorded tokens per example.
- MuSiQue: 0.338877 F1; delta over AgentVerse adaptation 0.012980.
- 2Wiki: 0.554537 F1; delta over final debate adaptation 0.085668.
- The frame component matrix supports configuration-level gains and a harmful memory-removal setting. All-tools, random-tools, and no-tool-history interventions are neutral at their archived uncertainty. Isolated active audit is harmful relative to its parent.

These are useful observations about particular protocols. They do not establish equal-budget utility, universal superiority, persistent role formation, or necessity of each component.

## Recent AAMAS papers: evidence for fit, not a recipe for acceptance

Selection method: inspect the 2024--2026 official proceedings, the official awards records, and papers near delegation, reputation, adaptive partner selection, trees, and LLM coordination. The sample is purposive, not a representative survey of every accepted/rejected paper. It cannot estimate acceptance probability or identify a causal preference of reviewers. Full PDFs and extracted text are archived locally with hashes.

| Paper and status | What was actually studied | Implication for this project |
|---|---|---|
| [Beliefs, Shocks, and the Emergence of Roles in Asset Markets](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p40.pdf), AAMAS 2024 full paper; best-paper finalist in the official awards PDF | Roles measured through trade networks, with interventions on shocks and heterogeneous beliefs | Show observable allocation structure and intervene on its cause; do not infer roles from labels. |
| [LLM-Powered Hierarchical Language Agent for Real-time Human-AI Coordination](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p1219.pdf), AAMAS 2024 full paper | Hierarchical execution in Overcooked; responsiveness and human coordination are central | Measure the deployment constraint, including latency, rather than only answer F1. |
| [Soft Condorcet Optimization for Ranking of General Agents](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1253.pdf), AAMAS 2025 best paper | A precise ranking objective connected to social choice and evaluated empirically | A narrow, well-defined object can be stronger than a large framework; connect analysis to a real decision. |
| [Curiosity-Driven Partner Selection Accelerates Convention Emergence in Language Games](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1282.pdf), AAMAS 2025 full paper; finalist listed in conference program | History-dependent partner choice, graph structure, and speed of convention formation | Make the causal chain history -> allocation -> coordination performance visible. |
| [SCMRAG](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p50.pdf), AAMAS 2025 full paper | Agentic multihop retrieval with correction and multiple datasets | QA is not out of scope by itself; the distinct agent mechanism must be clear. |
| [Reputation as a Solution to Cooperation Collapse in LLM-based MASs](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UEHN4980.pdf), AAMAS 2026 full paper; student-paper nominee | Direct/gossip reputation and network evolution in cooperation settings | Reputation in LLM teams is prior work. Differentiate task-conditioned delegation value and noisy audit attribution. |
| [Defection at First Sight](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/IBSZ1473.pdf), AAMAS 2026 full paper; best-paper nominee | Partner choice without initial opponent information, with sequentially learned behavior | Cold start and limited local information must be actual restrictions, not slogans. |
| [ReAcTree](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UCGT7089.pdf), AAMAS 2026 full paper | Agent trees, control flow, episodic/working memory, embodied planning across models | Tree + memory is not enough novelty. This is both close prior work and a candidate non-QA comparison. |
| [Developing Guidelines for Human-LLM Agent Teams](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/JOWO4591.pdf), AAMAS 2026 best paper | Guidelines grounded in a literature review and expert studies | AAMAS has no single preferred method type; the rigor must match the claimed contribution. |

Award status was checked separately from paper contents. The 2024 awards PDF lists finalists and says winners will be announced later; this audit does not promote a finalist to winner. Award examples are not evidence that copying their writing style will cause acceptance.

## Closest alternatives and novelty boundary

| Alternative | Why it is close | Required comparison or exact distinction |
|---|---|---|
| [AgentNet, NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html) | Decentralized evolving task routing and specialization | Direct implementation baseline with matched local model/tools/budget, or a documented faithful adaptation. EDO cannot claim to originate decentralized emergent organization. |
| [Dynamic Role Assignment, 2026 preprint](https://arxiv.org/abs/2601.17152) | Proposal and peer-review selection of workers before debate | Charge meta-debate selection cost; compare to updating reputation from completed downstream contributions. It is a preprint, not established here as an AAMAS paper. |
| [GPTSwarm, ICML 2024](https://proceedings.mlr.press/v235/zhuge24a.html) | Optimization of agent computation/communication graphs | Separate offline graph-optimization cost and information from online local learning. |
| [MoRSE, August 2026 preprint](https://arxiv.org/abs/2608.09251) | Role--subtask specialization and credit assignment | Cite as a recent trained-specialization alternative; do not silently compare its trained experts to untrained shared workers. |
| RepuNet / classical reputation / cost-aware bandits | Outcomes alter later partner selection | Include a simple non-LLM selection rule; show what task-local audit attribution adds beyond ordinary success-rate tracking. |

The current revised protocol is deliberately minimal and is not yet a strong novelty claim on its own. Its candidate contribution is the combination of a measurable delegation question, an audit-quality failure analysis, and controlled empirical identification. If the experiments show only that a generic bandit works, say so and redesign the contribution rather than inventing a new acronym.

## Proposed contribution and rejection-sensitive tests

**Claim candidate:** Under a fixed execution interface and inference budget, accurately attributed local acceptance records improve later delegation and support faster recovery when worker suitability changes.

The decisive causal chain is:

`accepted/rejected contribution -> persistent edge/task-type estimate -> different executor allocation -> higher held-out team utility at the same budget`.

Each arrow needs an observable check. The theory explains that audit acceptance preserves true competence order only under informative, worker-independent noise within comparable task categories. This yields a useful failure prediction: permissive or worker-biased auditing can concentrate authority on the wrong workers. The fixed-step variance formula explains why updates should be assessed as noisy tracking rather than convergence to stable personalities.

Keep memory and reputation separate. Freeze or shuffle reputation while preserving retrieved facts and tool affordances. Transfer task-conditioned records, scramble worker identities, and swap capabilities; these interventions distinguish useful learned allocation from prompt specialization and static routing heuristics. If no effect survives, a carefully supported negative result about the limits of evidence-derived organization is a legitimate outcome, not a reason to hide the controls.

## Writing decisions already implemented

- Introduction begins with a delegation decision and the distinction between acceptance and competence.
- Define the observable role through allocation, not a seven-axis personality metaphor.
- Present one minimal protocol; give implementation-to-evidence identity in one table.
- Replace the incorrect convergence statement with short, fully proved conditional results.
- Preserve historical QA values but label the scorer, dataset-specific variants, selection history, and incomplete costs.
- Show neutral/harmful controls and a real failed audit; remove the claim that all mechanisms are independently necessary.
- Move literature from generic model/orchestration background to close MAS alternatives.
- Keep prospective experiment descriptions explicit until real results exist. The draft is visibly internal and the release guard remains closed.

This is a substantive first reconstruction, not a completed new empirical paper. The fastest credible route to AAMAS is to close the experiment gates in the companion handoff, not to remove the internal labels or inflate the historical conclusions.
