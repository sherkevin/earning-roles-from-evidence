# Reference alignment for the AAMAS 2027 draft — 2026-10-09

Scope: a bibliography audit for the paper whose sole content source is
`FORMAL_PAPER_ZH.md`. This adds support for existing claims; it does not introduce
new method claims. The 2026-10-07 survey remains the earlier broad comparison.

## Three official AAMAS exemplars

The award status comes from conference pages, and counts come from the numbered
reference lists in the official proceedings PDFs, not from `.bib` files.

| Sample | Award status | Reference entries | Through 1999 | 2000–09 | 2010–19 | 2020–26 | Undated |
|---|---|---:|---:|---:|---:|---:|---:|
| [Beliefs, Shocks, and the Emergence of Roles in Asset Markets](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p40.pdf) | [AAMAS 2024 Best Paper runner-up](https://www.aamas2024-conference.auckland.ac.nz/awards/best-paper-awards/) | 39 | 7 | 17 | 8 | 7 | 0 |
| [Soft Condorcet Optimization for Ranking of General Agents](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1253.pdf) | [AAMAS 2025 Best Paper](https://aamas2025.org/index.php/conference/awards/best-paper-and-demo-awards/) | 84 | 14 | 8 | 28 | 32 | 2 |
| [Developing Guidelines for Human-LLM Agent Teams](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/JOWO4591.pdf) | [AAMAS 2026 Best Paper](https://cyprusconferences.org/aamas2026/awards/#paper) | 105 | 4 | 23 | 18 | 60 | 0 |

The three papers address different problems: economic agent models, agent
ranking, and human–LLM teams. Their bibliography sizes should therefore not be
treated as a target for an eight-page paper. Their year distributions make a
more useful point: the role/market model draws heavily on older modeling and
economics; the ranking work mixes historical social-choice foundations with
recent optimization; the human–LLM study draws primarily on recent team and
interaction work while retaining older human/agent literature. In the 2025
sample, reference [27] dates to 1785; [41] and [75] say `[n.d.]` and are
counted as undated. All 39/84/105 numbers are contiguous in the PDFs.

The extraction and every per-entry year are in
`research/reference_alignment_20261009/sample_counts.json`. Year was taken as
the first publication year in each numbered reference, with the 1785 and
undated cases inspected manually. PDF-to-text copies are kept beside that JSON
for audit. This is bibliography analysis, not an experiment.

## Seven additions with sentence-level uses

The active BibTeX file had 35 entries at the start of this audit. It now has
42. Each addition supports a proposition already in the Chinese manuscript.

| Cite key | Verified primary record | Appropriate claim / placement |
|---|---|---|
| `wegner1987transactive` | [Springer DOI](https://doi.org/10.1007/978-1-4612-4634-3_9), 1987 chapter by Daniel M. Wegner | Introduction §1, the human-team analogy: collaborators learn who holds which knowledge through interaction. This motivates contextual expertise, not an assertion that agent roles equal human cognition. |
| `lewis2003transactive` | [APA DOI](https://doi.org/10.1037/0021-9010.88.4.587), 2003 field scale by Kyle Lewis | Introduction §1, team expertise as a distributed, measurable social structure. Cite with Wegner if making the human-team analogy; do not imply the paper's RARE metric is Lewis's scale. |
| `malone1994coordination` | [ACM DOI](https://doi.org/10.1145/174666.174668), 1994 article by Thomas W. Malone and Kevin Crowston | Introduction / related work, coordination as managing interdependencies among activities and agents, motivating task-specific division of work. |
| `gerkey2004allocation` | [SAGE DOI](https://doi.org/10.1177/0278364904045564), 2004 article by Brian P. Gerkey and Maja J. Matarić | Related work comparison or §task allocation: task allocation is an established problem with different task and assignment forms. Use as a boundary citation, not as a direct LLM baseline. |
| `teacy2006travos` | [Springer DOI](https://doi.org/10.1007/s10458-006-5952-x), 2006 article by W. T. Luke Teacy et al. | Related work trust/reputation and §limitations: third-party reports can be inaccurate and require reliability handling; supports retaining judgments as observations and checking responsibility separately. |
| `brier1950verification` | [AMS DOI](https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2), 1950 article by Glenn W. Brier | Evaluation RQ1/H1, cite at the first definition of Brier score as a probability forecast score. |
| `guo2017calibration` | [PMLR ICML record](https://proceedings.mlr.press/v70/guo17a.html), 2017 paper by Chuan Guo et al. | Evaluation RQ1, cite near probability calibration/reliability analysis. Its empirical result concerns neural classifiers, so do not claim it validates the present selector. |

The six DOI records above returned matching titles, authors, years and venues
from Crossref; their raw metadata subset is in
`research/reference_alignment_20261009/crossref_verification.json`. Guo et al.
was checked against PMLR's own BibTeX and proceedings page. Three older
entries were later corrected in the targeted final metadata pass below.

## Editorial decision for the build

An entry in `references.bib` does not enter the compiled reference list unless
`main.tex` cites it. Place citations where the listed claim is actually made;
do not add a disconnected citation cluster. The strongest minimum set for the
paper's distinctive argument is Wegner/Lewis for distributed expertise,
Teacy for unreliable reports, Gerkey for assignment, and Brier/Guo for the
stated evaluation. Malone provides the broader coordination framing if space
permits. The bibliography may occupy pages after the eight body pages under
the user's page-count requirement.

## Final active-citation audit

At the time of this check, `main.tex` cites **all 42** unique keys in
`references.bib`: no undefined key and no uncited BibTeX entry. Distinct keys
per main section are below; a key cited in two sections is counted in both.

| Main section | Distinct keys | Citation commands |
|---|---:|---:|
| Introduction | 5 | 3 |
| Related Work and Positioning | 27 | 20 |
| Problem Formulation | 0 | 0 |
| Earning Roles | 0 | 0 |
| Benchmarks and Baselines | 10 | 4 |
| Experimental Questions and Matrix | 2 | 2 |
| Results; Discussion and Limitations; Conclusion | 0 | 0 |

The 42 active references span 1950–2026: **3 through 1999, 5 from
2000–2009, 6 from 2010–2019, and 28 from 2020–2026**. Exact year counts and
per-section keys are in `research/reference_alignment_20261009/manuscript_citation_distribution.json`.
The distribution concentrates neighboring work in Related Work and benchmark
sources in Benchmarks and Baselines; method definitions and placeholder results
do not need decorative citations.

A PDF-text scan of numeric citation groups in the three official examples
shows where authors use the literature. These are approximate location counts,
not unique-paper counts: a repeated citation appears again, numeric ranges are
one group, and non-reference bracketed numbers may be included. The raw lines
and section boundaries are in `research/reference_alignment_20261009/sample_section_citation_markers.json`.

| Official sample | Introduction | Background / related work | Method / design | Evaluation / simulation | Discussion / conclusion |
|---|---:|---:|---:|---:|---:|
| 2024 roles runner-up | 17 | 7 preliminaries | 0 market model | 6 simulation | 0 conclusion |
| 2025 ranking winner | 17 | 21 background | 9 method | 9 empirical evaluation | 6 discussion |
| 2026 human–LLM teams winner | 19 | 31 related work | 30 across overview and phases 1–2 | 3 phase-3 evaluation | 17 discussion |

The 2024 paper uses prior economics and modeling literature chiefly in the
introduction and preliminaries, then cites a few sources during simulation;
its own market-model section has no bracketed citations. The 2025 paper cites
social-choice and ranking literature most densely in background while
connecting method, evaluation and discussion to prior work. The 2026 paper
places the largest concentration in related work, with further citations in
guideline development and discussion. Placement should follow the claim's
role, rather than an even distribution across sections.

## Targeted correction of existing metadata

The three corrections below preserve the pre-existing citation keys. They
were made after the initial seven additions and after the running build had
already read the prior BibTeX. A subsequent build should pick them up.

| Key | Before | Verified final record / change |
|---|---|---|
| `wu2023autogen` | 2023 arXiv text inside an `@inproceedings` entry; singular “Conversation” title | [COLM 2024 accepted-paper list](https://colmweb.org/2024/AcceptedPapers.html) links the [official OpenReview record](https://openreview.net/forum?id=BAakY1hNKS): title ends **“Conversations”**, same authors, conference publication in 2024. Updated title, venue, year and URL. |
| `yao2024taubench` | 2024 arXiv preprint | [ICLR 2025 proceedings PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/1b126cc38b8638e07bef37e7b2bb72bf-Paper-Conference.pdf) and [OpenReview record](https://openreview.net/forum?id=roNSXZpUDN): same four authors and title, conference publication in 2025. Updated type, venue, year and URL; normalized the TeX `\tau` command. |
| `sabater2002reputation` | `@inproceedings` with the AAMAS proceedings title in the `journal` field | The [ACM DOI](https://doi.org/10.1145/544741.544854) identifies the 2002 AAMAS paper, pages 475–482. Moved the proceedings title to `booktitle`; all factual fields and the key are unchanged. |

The original TeamBench entry remains labeled arXiv; a locally available
submitted manuscript alone is not evidence of conference acceptance. This is
a targeted metadata audit, not fresh DOI-by-DOI verification of all 35
earlier entries.
