# Official venue and template refresh, 2026-09-26

The target remains AAMAS 2027. The working title and abstract use the official
2027 template, whose downloaded ZIP SHA256 is
`e70e88d36fd96db0777b9d00a1cd0bd1eecbbb28619e9e723dcf207a9bc6ce2a`, identical to
the September 16 archive. [sources.json](sources.json) records the five retained
objects. It preserves local file modification timestamps from the download
cache; these are not claimed to be HTTP response timestamps. Earlier source
objects and their manifest were not overwritten.

Sources verified directly:

- [2027 Main Track call](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/)
  names originality, significance, soundness, reproducibility, clarity, venue
  relevance and appropriate prior work. A MAS contribution must be explicit;
  general language-model improvements alone do not establish the paper's fit.
- [2027 instructions](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/)
  link the downloaded official ZIP. The paper limit remains eight content pages
  plus references; the original style must remain unchanged.
- [2026 instructions](https://cyprusconferences.org/aamas2026/submission-instructions/)
  point to the 2026 ZIP below. The 2026 homepage supplies the same instructions
  page, with no second template link found in the inspected page.

The user also requested this year's template. Its official URL is
`https://cyprusconferences.org/aamas2026/wp-content/uploads/2025/06/AAMAS-2026-Formatting-Instructions-pre-CR.zip`.
The bounded final request returned **HTTP 404** and then timed out downloading
the HTML error page (curl exit 28 after 20 seconds, 270051 bytes received).
This is not a downloaded 2026 template. Earlier attempts likewise found the
link unavailable; no third-party file has been relabeled official. The failure
does not prevent work in the independently verified target-year 2027 template.

## Local build

`python3 scripts/build_aamas2027.py --proposal` now creates the one-page
`article/aamas2027/build/research_proposal.pdf`. Its visible marker is
`INTERNAL PRE-RESULTS PROPOSAL`. The title and 211-word abstract state the
research question and planned tests, without claiming measured effectiveness.
The PDF has no overfull boxes or unresolved references, an empty author metadata
field, and unchanged official class, bibliography style and license graphic.
The source has no citations yet; “no unresolved references” is not a prior-art
completeness claim. Visual inspection confirmed legible, unclipped columns.

The compiler still reports an incomplete `ifx` warning associated with the
official class/metadata path. This warning is retained in verification output;
the package is an internal draft, not a clean submission build. No class file
or layout was modified to suppress it.

The local BasicTeX installation lacked `hyperxmp`. User-mode tlmgr first hit a
mirror checksum mismatch, then reported the package as non-relocatable. A
direct `.sty` request returned an HTML error document, which failed compilation.
The recovery used the official CTAN source distribution from the Tsinghua mirror:
`macros/latex/contrib/hyperxmp/hyperxmp.dtx` and `hyperxmp.ins`; docstrip generated
the package, installed under the user's TeX tree. The generated `.sty` SHA256 is
`24fdc66d629c408d88dd699467446b621a8a726c561d86d580670931f702c86d`.
The local installer copy disabled overwrite prompting; package contents were
generated from upstream, not reimplemented. The original missing `by.pdf` cache
entry was restored byte-for-byte from the already archived official ZIP.

`python3 scripts/build_aamas2027.py --proposal --submission` correctly rejects
the proposal. Template/build validity does not close any scientific gate.
