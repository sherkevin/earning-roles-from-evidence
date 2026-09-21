# AAMAS source archive

Downloaded and checked on 2026-09-16 for the AAMAS 2027 reconstruction. [sources.json](sources.json) records 30 downloaded source objects, including their original/resolved URLs, retrieval time, byte count, and SHA256. Extracted text and link files are convenience derivatives of those objects.

- `official/`: AAMAS 2027 homepage, main-track call, instructions, Findings and reciprocal-reviewing policies; AAMAS 2024--2026 proceedings listings and selected awards/program sources.
- `template/aamas_2027_template.zip`: original official LaTeX template archive; `template/official/` is the extracted distribution.
- `papers/`: 12 full PDFs and extracted text, covering recent AAMAS work and close external alternatives. Venue status and award status are distinguished in the positioning memo.
- Additional scorer and bibliographic sources retain their original source URLs in the archive and audit records.
- `q1_novelty/`: additional Q1 published-work audit sources, with a separate [download manifest](q1_novelty/sources.json) and [evidence/version index](q1_novelty/evidence.json). These additions are not counted in the original 30-object manifest. Formal publication status is separated from the inspected author version, and failed downloads remain recorded. LEGOMem's formal AAMAS contribution is an extended abstract; EvoSkillBank is a current COLM 2026 accepted-record/abstract alert, and only a preprint record was verified for EvoFlow.

Read [REQUIREMENTS.md](../../docs/paper/aamas2027/REQUIREMENTS.md) for deadlines, formatting, scientific standards and the selected-paper comparison, then [AAMAS_TASKS.md](../../docs/coordination/AAMAS_TASKS.md) for gaps and execution. Earlier positioning/venue notes are archived. Official webpages can change after this snapshot; recheck the live instructions before submission.

The source downloader is `scripts/aamas_archive_sources.py`. Downloaded literature is a local research cache; do not include the full PDFs in the anonymous submission ZIP. The working manuscript uses byte-identical copies of the official `aamas.cls`, `ACM-Reference-Format.bst`, and `by.pdf`, verified by `scripts/build_aamas2027.py`.
