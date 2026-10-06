# v17 AI figure drafts — 2026-10-06

This version follows the project decision to use AI image generation for the three paper figures. It preserves every generated draft and every prompt. These PNGs are **composition and semantic drafts**, not the final submission assets: the professional drawing platform should re-render them with exact typography and export a publication-quality PDF/SVG.

## Figure set

| Figure | One-sentence claim | Drafts | Current review |
|---|---|---|---|
| Figure 1 | Situated use becomes responsibility-scoped evidence before a later assignment is sealed. | `figure1_draft.png` | Strong composition; check exact text and dashed feedback at paper scale. |
| Figure 2 | Episode facts, public evidence, and legal local decisions are separate information lanes. | `figure2_draft.png`, `figure2_draft_v2.png` | v1 had the `project` arrow end at the wrong lane; v2 fixes the semantic endpoint and is preferred. |
| Figure 3 | ArtifactRole and PeerSelect are evaluated separately under matched information and cost contracts. | `figure3_draft.png` | Clear three-panel comparison; replace long top ribbon with typeset text if platform output becomes cramped. |

## Style anchors from the gallery

The prompt set combines three gallery patterns:

- `pipeline`: one directional spine with numbered stages (Figure 1);
- `framework`: aligned lanes/modules with one claim per lane (Figure 2);
- `comparison` + `taxonomy`: separated tracks, matched policies, and endpoint cards (Figure 3).

Reference metadata was read from the local TopConf Figure Gallery `data/figures.json`; the gallery's methodology requires manual visual review after heuristic filtering. We use its recurring conventions: white background, strong hierarchy, limited semantic colors, generous margins, and no decorative 3-D elements.

## Color semantics

- dark navy `#17365D`: text and invariant boundaries;
- blue `#2E5DA1`: selector, sealed assignment, and RARE;
- orange `#F5A623`: situated judgment and ArtifactRole;
- muted green `#4B8B63`: ownership gate, PeerSelect, and safety;
- gray `#B8C0CC`: baseline, audit, or unresolved branch.

## Handoff contract

When platform-rendered versions arrive, add them as `figure{1,2,3}_platform_vN.<ext>` in this directory. Do not overwrite drafts. Verify: exact labels, no crossed arrows, no changed semantics, one-column readability, 300 dpi for PNG or embedded fonts for PDF/SVG. Only after that review should a selected asset replace `article/aamas2027/figures/*.pdf`; the paper must then be rebuilt and rechecked at exactly eight body pages.
