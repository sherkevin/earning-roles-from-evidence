# Actor memory primary-source check

Pinned upstream: `noahshinn/reflexion` at
`218cf0ef1df84b05ce379dd4a8e47f17766733a0`, MIT.
[File hashes and retrieval history](manifest.json) include the failed GitHub CLI
LICENSE fetch and successful raw-primary-host fallback. No source was executed.

- [Original paper](https://arxiv.org/abs/2303.11366v4): language feedback and
  episodic reflection are used without weight updates.
- `hotpotqa_runs/agents.py:301–340`: last-attempt/reflective text enters the next
  agent prompt. Some feedback comes from task correctness; permissions are not
  interchangeable with our private evaluator boundary.
- `programming_runs/reflexion.py:43–78`: executed internal-test feedback enters
  a reflection and revised implementation, within the same problem.

Reusable idea: put legal prior interaction into subsequent generation input.
Not established here: peer routing, unseen-task transfer, our feedback safety,
or our online selector's novelty/effect. Our existing `ActorExperience` can
provide the simplest transcript path; importing the full framework is unnecessary.
