# AAMAS paper artifacts

`main.pdf` is the only current paper PDF. It is promoted from a versioned
child directory only after the build, page rendering, and review checks pass.

Child directories preserve candidate and historical PDFs for rollback and
audit. They are not parallel main manuscripts. The active LaTeX workspace is
under `article/aamas2027/build/`; its intermediate files are not the canonical
artifact. See [ADR 0050](../../docs/user/decisions/0050-canonical-main-pdf-and-versioned-builds.md).
