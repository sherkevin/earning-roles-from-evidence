# v9 — Vector production candidate after AI visual exploration

This is an isolated Figure 1 candidate. It is not referenced by
`article/aamas2027/main.tex` and does not replace the active v7 figures.

The layout borrows the structural grammar discovered from the ICML 2025 Best Paper
*CollabLLM: From Passive Responders to Active Collaborators*: small observable
context on the left, one visually dominant central mechanism, a future decision
on the right, and one explicitly delayed feedback edge. The content is original
to the earning-roles paper.

This version is a deterministic vector production pass after three AI-generated
visual candidates. AI v1 supplied the strongest visual hierarchy, but v2 did not
improve raster resolution and v3 introduced a corrupted peer-C glyph and an
orange artifact. The vector pass therefore preserves the v8 semantics while
using embedded TrueType text, larger body labels, and a selector-local
`future read cut` label that does not touch the border.

The candidate is intended to answer one question in 30 seconds:

> How does a recipient's situated use become evidence that changes a later local
> responsibility assignment?

The candidate deliberately omits the detailed field-level contract, the full
baseline matrix, and the crossed event-time constraints. Those belong in the
method and experiment figures/captions.
