# AAMAS source archive

Downloaded and checked on 2026-09-16 for the AAMAS 2027 reconstruction. [sources.json](sources.json) records 30 downloaded source objects, including their original/resolved URLs, retrieval time, byte count, and SHA256. Extracted text and link files are convenience derivatives of those objects.

The [2026-09-26 venue refresh](venue_refresh_20260926/README.md) separately records
the unchanged official 2027 template, current instructions, failed official
2026 template retrieval, and the compiled pre-results proposal. It does not
overwrite this historical archive or turn the proposal into submission evidence.

- `official/`: AAMAS 2027 homepage, main-track call, instructions, Findings and reciprocal-reviewing policies; AAMAS 2024--2026 proceedings listings and selected awards/program sources.
- `template/aamas_2027_template.zip`: original official LaTeX template archive; `template/official/` is the extracted distribution.
- `papers/`: 12 full PDFs and extracted text, covering recent AAMAS work and close external alternatives. Venue status and award status are distinguished in the positioning memo.
- Additional scorer and bibliographic sources retain their original source URLs in the archive and audit records.
- `q1_novelty/`: additional Q1 published-work audit sources, with a separate [download manifest](q1_novelty/sources.json) and [evidence/version index](q1_novelty/evidence.json). These additions are not counted in the original 30-object manifest. Formal publication status is separated from the inspected author version, and failed downloads remain recorded. LEGOMem's formal AAMAS contribution is an extended abstract; EvoSkillBank is a current COLM 2026 accepted-record/abstract alert, and only a preprint record was verified for EvoFlow.

- `design_lock_20260922/`: historical v5 benchmark/method selection audit, subsequently reopened; includes FlowEvo/PSN/ASI/traditional repair and new skill benchmarks. [sources.json](design_lock_20260922/sources.json) hashes downloads and retains failures; [evidence.json](design_lock_20260922/evidence.json) records the then-inspected scope, pins, decisions and limits. This audit did not execute benchmarks or establish novelty. Its selection labels are historical, not the current execution authority.
- `problem_entry_20260922/`: Q1 v6/v6.1 entry and final-lock audit. [sources.json](problem_entry_20260922/sources.json) preserves 14 downloaded sources, one failed access and one direct-download challenge page; [evidence.json](problem_entry_20260922/evidence.json) distinguishes method inspection, venue records and preprints. Learned assume-guarantee regression verification and probabilistic assumption learning narrow novelty. No new method is locked.
- `benchmark_survey_recent_20260924.md`: project-authored audit of recent agent/multi-agent benchmarks and baselines, including TeamBench, AWS collaboration scenarios and Dynamic Role Assignment. It records the missing full peer-judged role-formation chain, recommended CooperBench extension and minimum matched controls. This is design evidence, not a benchmark lock or positive experiment.

The September 22 GitHub checkpoint publishes the two new source/evidence indexes, not the downloaded third-party HTML/PDF/text caches. Paths inside those manifests refer to the local research cache and may need re-download from their recorded URLs before hash verification on another machine. A challenge payload is not publication text. Project-authored Q1 and contract snapshots under `artifacts/analysis/aamas2027/problem_entry_20260922/` are included in the checkpoint.

Read [REQUIREMENTS.md](../../docs/paper/aamas2027/REQUIREMENTS.md) for deadlines, formatting, scientific standards and the selected-paper comparison, then [AAMAS_TASKS.md](../../docs/coordination/AAMAS_TASKS.md) for gaps and execution. Earlier positioning/venue notes are archived. Official webpages can change after this snapshot; recheck the live instructions before submission.

The source downloader is `scripts/aamas_archive_sources.py`. Downloaded literature is a local research cache; do not include the full PDFs in the anonymous submission ZIP. The working manuscript uses byte-identical copies of the official `aamas.cls`, `ACM-Reference-Format.bst`, and `by.pdf`, verified by `scripts/build_aamas2027.py`.

- `sandbox_runtime_20260926/`: pinned upstream runtime source/license and root-vnode diagnosis. The installed npm dependency is separately pinned in `tools/peerrole-runtime/package-lock.json`; no claim of byte-identical npm rebuild.
- `idealab_thinking_20260926/`: official compatible-Messages documentation plus retrieval provenance. This documents the API field, not independent proof of IdeaLab forwarding; local actual responses supply that narrower evidence. The source was fetched after the disabled-thinking probe and this timing is explicitly retained.

The [N02 analysis](../../docs/research/n02_real_closed_loop_review_20260926.md)
indexes actual API requests, failed attempts and post-hoc diagnostics. Compact
historical fixture artifacts have a [full local inventory](../../experiments/logs/fixture_artifact_index_20260926/manifest.json);
nested fixture workspaces and external cloned repositories stay local. A source
manifest is not a remotely complete experimental artifact bundle.
