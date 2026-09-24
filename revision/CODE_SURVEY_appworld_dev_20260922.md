# Reuse plan for the bounded AppWorld diagnostic

The scientific question requires real task execution and lawful training traces.
The existing official AppWorld runtime already provides both; replacing it with
a toy task generator would weaken the experiment.

- Source: https://github.com/StonyBrookNLP/appworld at
  `42b5bcf3cd334fee33f0c37c02070a9f5807add5`, Apache-2.0 code.
- Reuse `AppWorld`, public task descriptions, sandboxed `execute`, official
  terminal scorer, native train/dev IDs, and official ReAct demonstration prompt.
- Reuse the existing project's B1 logging and fixed 30-call / 2048-output-token
  conventions, but count transport attempts and failures explicitly.
- Existing `run_appworld_b1_530b157_screen.py` fixes three already saturated tasks;
  it cannot answer acquired-capability or interaction questions and will not be
  rerun as the main experiment.
- cc-switch's named provider exposes the Anthropic-compatible idealab endpoint;
  a small transport adapter may be needed to use that verified provider directly
  rather than assuming the local router's origin.
- Public task instructions and native traces may remain protected benchmark
  material. Preserve locally; release a manifest/loader rather than assuming
  permission to redistribute plaintext tasks.

The adapter and diagnostic implement only what the official runtime and current
runner lack: named-provider provenance, bounded paired artifacts, per-attempt
accounting and immutable prospective manifests. No benchmark implementation or
scorer is rewritten.
