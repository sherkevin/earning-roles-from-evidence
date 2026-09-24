# 0006 — Study peer-judged role formation, not package replacement

Status: Accepted author research-direction decision, 2026-09-23. Complements [0005](0005-retain-peer-judged-role-learning.md); does not establish an algorithm or result.

## Context

The project originally asks how agents, starting without assigned expert roles, develop useful responsibilities through actual collaboration: one agent delivers work, its real upstream owner or downstream consumer judges and uses it, and later task outcomes may correct that judgment. The judged agent's role and future responsibilities should change. Agents also learn from the work they receive, and useful workflows arise from how they work together.

Q1 v5 instead considered rebinding an existing workflow after an agent's execution package changed; Q1 v6.1 considered qualifying an updated package against a workflow's handoff requirements. These candidates treated workflow structure and its executors as separable enough to make replacement and compatibility the headline decision. Their own reviews found the mechanism and novelty incomplete, and R0–R3 did not validate them as online multi-agent learning.

## Decision

The paper's active research direction is the **original peer-judged role-formation problem**. An agent and the workflow it participates in are treated as jointly shaped by their collaboration history. We do not make arbitrary replacement of a workflow participant by an independently updated package, nor cheap qualification of that replacement, the primary Q1 or a prerequisite for this paper.

The scientific loop to operationalize is: real dependent work → actual collaborator's situated judgment of the delivered contribution and repair/use → correction from later task evidence where lawful → role evidence about the judged agent → changed future responsibility within evolving collaboration. Private skill/memory and workflow evolution remain the setting and possible consequences; their full learning algorithms are not automatically additional contribution claims.

This is a project framing and a choice of research question, not a universal assertion that compatibility regressions never occur. Prior v5/v6.1 analyses and experiments remain historical evidence and may inform controls or limitations, without governing active method selection.

## Rationale

The author's objection is that the replacement/compatibility question does not capture how agents and their workflows naturally develop together in this project. It is weaker than the original problem and risks building a paper around an artificial intervention. Narrowing an uncalibrated global persona was justified; replacing the consumer-judgment mechanism with package qualification was not.

## Consequences

- Retire v5/v6.1 conditional adoption and their old/new-package witness, transferable qualification and cheaper-retesting gates as **main-paper** requirements. Preserve records without rewriting historical outcomes.
- Rewrite active G0–G6 around one executable judgment-to-role update, real producer/consumer observations, judge reliability, later assignment and a fair same-information comparison with task-specific trust, raw acceptance and pooled selection.
- Keep workflow as a first-class evolving record of dependencies and collaboration. Test whether role evidence helps within that evolution; do not claim workflow composition or skill acquisition independently improves results without a separate intervention.
- Design a small real-API multi-agent development test after the observation/update rule and controls are specified. Existing R0–R3 diagnostics do not answer this Q1.
