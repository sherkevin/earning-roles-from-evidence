# Meta-Team reuse audit for peer-judged roles

Status: primary paper and pinned repository inspected; **no baseline was run**.
The machine-readable repository snapshot, file URLs, timestamps, hashes, and
license check are in [upstream_metadata.json](upstream_metadata.json). The
repository was at commit `36dc85d9dc2219d292fa180f347479738a84acb2`
(2026-07-25 commit date) when checked on 2026-09-23. This is **not** claimed
to be the paper-publication implementation. The primary paper is
[Meta-Team v1](https://arxiv.org/html/2605.29790v1), cached at
`../acquisition_followup_20260922/metateam_v1.html`.

## What the primary sources establish

- The [paper's Section 3](https://arxiv.org/html/2605.29790v1#S3) already
  defines post-task communication about how one agent's output affected a
  downstream agent. Thus “learn from another agent's judgment” and
  “coevolve roles and collaboration” are not novel on their own.
- The [L2 prompt](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/prompts/reflection/l2_communication.md)
  has direct collaborators discuss concrete handoff problems, or skip
  discussion when things went smoothly. Each may still record observations.
  Its profile has `reliability`, `strengths`, `weaknesses`, communication style,
  and notes. It asks for general patterns, not one-off case reports.
- The [profile writer](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/tools/reflection.py#L275)
  merges YAML observations into per-agent teammate profiles;
  [collaboration notes](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/tools/reflection.py#L573)
  are saved separately. [Agent initialization](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/agent.py#L100)
  loads these and the [system prompt](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/agent.py#L150)
  exposes them on later tasks.
- [Runner](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/runner.py#L578)
  also supplies teammate insights to recruited agents. In the full system a
  Chairman recruits agents, L1 revises individual prompts/skills, and L3
  revises team structure. A peer-profile-only port is not the full Meta-Team.
- [Reflection context](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/reflection_runner.py#L733)
  includes final output and validation when available. Giving that signal to
  only one comparison arm would be an information leak, not a fair result.
- The repository has no AppWorld adapter or AppWorld task data. Its included
  split files target other benchmarks; they cannot supply our role-learning
  trajectories. The reusable pieces here are the reflection protocol, profile
  state semantics, and experiment scaffold, not a ready AppWorld baseline.

The exact L2 prompt and key implementation files were already cached, with
matching hashes, under `../acquisition_followup_20260922/`; this audit reuses
those files rather than duplicating them. Only the two small dependency files
are copied here for implementation planning. The public repository has no
detected `LICENSE`, `COPYING`, or `NOTICE` file, and GitHub reports no license.
These references are for internal inspection; do not copy upstream code into
the distributable experimental runtime without permission or a verified
license.

## Actionable baseline design

1. **Controlled L2 adaptation (first comparison):** keep the same AppWorld
   producer/consumer controller, task order, candidate agents, model, public
   observations, message history, and API budgets in both arms. After a task,
   let directly interacting peers create Meta-Team-style qualitative profiles
   and collaboration notes from the same allowed evidence. Load those notes on
   later tasks and record whether they change *which agent is entrusted with a
   role*. Reimplement this component independently and label it “Meta-Team L2
   adaptation”, not a full reproduction.
2. **Full-framework comparison (separate):** if the paper later needs to claim
   improvement over complete Meta-Team, port an AppWorld adapter and its tool
   safety interface into the pinned upstream framework, keep its Chairman and
   L1/L2/L3 phases, and run matched model, data split, feedback timing, and
   inference budget. Report architecture and cost differences rather than
   silently treating the L2 adaptation as the whole framework.
3. **Evidence parity:** decide before running whether training agents may see
   official post-task validation. Either both arms receive identical train-only
   validation, or neither does. Test labels and hidden evaluators must never
   enter a later test prompt. Both arms must receive the same public consumer
   judgment/use/repair messages, and all evidence must be timestamped before
   any future assignment.
4. **Learning endpoint:** the current single producer/consumer witness cannot
   test role learning. Add at least two plausible producers for a future role,
   then measure later assignment quality and downstream task outcome, with
   per-task choices and profile updates preserved. Separate accepted/used
   proposals from official task success and actor-specific execution errors.

This comparator is strong precisely because Meta-Team already records peer
observations and changes later behavior. A new method needs a specific,
measurable gain beyond qualitative teammate profiles, not a renamed L2 phase.
