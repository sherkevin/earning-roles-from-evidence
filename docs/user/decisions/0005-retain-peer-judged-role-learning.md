# 0005 — Retain roles learned from others' judgments

Status: Accepted as a research-scope constraint from the author's explicit correction, 2026-09-23. This status does **not** certify scientific novelty, a particular algorithm or a result.

## Context

The [original idea](../../../idea.md) defines an agent's social role through value it delivers to another agent, who accepts, reworks or rejects the deliverable. In a chain `a → b → c`, `b` judges `c` and `a` judges `b`; terminal outcomes can later correct mistaken local acceptance. The judged agent was meant to accumulate an operational role/persona from these events, visible to future collaborators.

Subsequent simplifications changed the object. The [current manuscript](../../../article/aamas2027/main.tex) keeps an upstream-acceptance question but updates only a delegator's binary acceptance estimate for a neighbor; it does not implement a role state learned by the judged agent from multiple collaborators. [Q1 v6.1](../../scientist/analysis/AAMAS_Q1_worker_differences.md) instead studies package qualification against workflow handoff requirements. The assistant's later proposed Q1 further folded judgment into generic contribution evidence and centered role matching. The author correctly identified that the original innovation line had disappeared from the proposed method.

## Decision

Any main Q1/method candidate for this paper must explicitly retain **learning roles from other agents' situated judgments of delivered work** as a research object. “Judgment” means evaluation by the actual task owner or downstream consumer of what the contribution enabled and what repair it required; a self-declared role, generic detached LLM judge, terminal-only reward or uncalibrated pass-rate table is not an adequate substitution.

The candidate causal loop is: real delivery → consumer's recorded acceptance/use/rework judgment → independently checked correction where available → attributable role evidence about the producer → changed future responsibility. The exact evidence representation, calibration rule, sharing scope and routing policy are still open scientific/design questions. Skill acquisition and workflow composition remain part of the broader project but must not obscure identification of this loop.

## Rationale

This restores the project's distinctive question and prevents a convenient infrastructure or baseline from replacing it silently. It also creates a falsifiable distinction between an agent's own answer quality, a consumer's opinion and the value of giving that agent a future responsibility.

Task-specific trust, contextual peer calibration, reputation and credit-guided role evolution are prior art; therefore the decision to retain the question is **not** a priority claim. A useful paper still needs a specific executable judgment-to-role rule and evidence that it changes outcomes beyond strong same-information alternatives.

## Consequences

- Reopen G0's story/method alignment around this loop. Do not lock a Q1 centered only on handoff qualification or ordinary matching as if it preserved the original mechanism.
- Keep the distinction between the delegator's local belief about a peer and any role evidence/profile accumulated by the judged agent. How to aggregate or expose such evidence remains to be specified.
- Compare any concrete rule with self-report, terminal-only reward, raw acceptance rates, contextual trust/bandit and same-information program controls. Record judge error, task difficulty, selection bias, real downstream use, repair cost and all judgment overhead.
- R0–R3 are real diagnostics but did not test this loop; they neither verify nor falsify it. A new real multi-agent development test needs actual independent producers and consumers, not relabeled segments of a single-agent program.
- If no distinguishable rule or reliable observation protocol can be built, narrow the paper honestly rather than treating this decision as proof of an innovation.
