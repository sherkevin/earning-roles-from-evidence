# Figure 1 — Conceptual diagram prompt (USER to render)

> Owner: **user** (per 2026-04-19 协作约定: 概念图 / 示意图归用户绘制).
> Scientist responsibility: provide a complete prompt + acceptance criteria + a textual fallback so the user (or an AI image tool) can produce the asset without further clarification.
> Target asset: `workspace/autogen/dotnet/website/articles/paper/figures/fig1_3action_policy.{pdf,svg,png}` (final delivery dir per 2026-04-19 user instruction; a copy goes into `artifacts/figures/` for in-doc preview).
> Final caption / paper insertion is `S-010` and is blocked on this asset landing.

---

## 1. What the figure must convey

Figure 1 is the **single conceptual schematic** for the EDO long-paper method. A reviewer who looks at it for 5 seconds must be able to read off three things:

1. The **three primitive actions** an agent picks among on every received task: `do_self`, `outsource(neighbor)`, `split(subtasks)`.
2. The **recursive acceptance ladder**: when agent `a` outsources to `b`, `b` later returns a candidate result and `a` must `accept / accept_with_note / reject_reroute / reject_resplit` it. If `b` itself outsourced to `c` first, then `b` accepted `c` before returning upward.
3. The **distinction between full EDO** (sparse graph + arbitrary task tree) and the **TCPB Stage-1 prototype** (chain topology + linear handoff). The viewer should see in one glance that EDO is the superset and that the prototype lives inside a fixed `decomposer → evidence_seeker → verifier → synthesizer` chain.

A reader should NOT have to read §3 prose to understand which arrow is "outsource" vs "audit return" vs "split".

---

## 2. Layout specification (single column, ~3.3in wide × ~2.5in tall, vector format)

The figure is **two stacked panels**, separated by a thin horizontal rule. Both panels share x-axis width.

### Panel A (top, ~60% of vertical space): Full EDO on a sparse graph with a recursive task tree

* Five circular agent nodes, near-homogeneous (all same shape and color), labeled `A`, `B`, `C`, `D`, `E`. Place them so the visible-edge graph forms a **sparse, connected, non-trivial topology** (e.g., A–B, A–C, B–C, B–D, C–E). Use thin gray lines for visibility edges (these are *who can see whom*, not delegation flow).
* On agent `A`, show the **incoming root task** as a small rounded rectangle labeled `task z`.
* From `A`, show the **three-action policy** as a vertically stacked decision callout next to `A`:
  * `do_self` (small icon: gear) — leads to a small green "answer" leaf attached to A.
  * `outsource(B)` (small icon: arrow) — solid colored arrow from A → B labeled `outsource(z)`.
  * `split(z → {z₁,z₂})` (small icon: branching tree) — shows two child task rectangles `z₁`, `z₂` attached to A; `z₁` is then `outsourced(C)` and `z₂` is `do_self` at A.
* From `B → D`, draw another `outsource(z)` arrow (so we have a 2-hop delegation chain A→B→D for the "recursion" intuition).
* Draw the **return / audit arrows** with a *different visual style* (dashed, opposite direction, with small "audit" label):
  * D → B (dashed, label `accept?`)
  * B → A (dashed, label `accept?`)
  * C → A (dashed, label `accept?` for the split-child path)
* In the bottom-right of Panel A, place a tiny legend swatch:
  * solid arrow = `outsource / split delegation`
  * dashed arrow = `recursive acceptance audit`
  * green leaf = `final accepted answer`

### Panel B (bottom, ~40% of vertical space): TCPB Stage-1 prototype on a fixed chain

* Four square nodes in a left-to-right chain, labeled `decomposer → evidence_seeker → verifier → synthesizer`. Use the same node color as Panel A (homogeneous color scheme).
* Solid arrows pointing rightward labeled `forward (outsource only)`.
* No `split` arrows (since the prototype has no split).
* No dashed audit arrows (since terminal-only update has no per-hop upstream rejection).
* A small green leaf next to `synthesizer` labeled `final answer + terminal F1 update`.
* A subtle dashed feedback arrow from `synthesizer` back to `decomposer` labeled **`scalar competence update (TCPB)`** to indicate the post-sample update goes only to the accepting node.

A 2-line caption underneath the panel border (NOT inside the figure): "Top: EDO theoretical action space. Bottom: the restricted Stage-1 instantiation actually executed in this submission."

---

## 3. Visual / aesthetic constraints (must satisfy these)

| Constraint | Rationale |
|---|---|
| **Vector format**: deliver `.pdf` (preferred) or `.svg`; `.png` only as fallback / preview | ACL `\includegraphics{...}` requires vector for clean compile; rasterized figures get partial credit deduction |
| Black + ≤ 2 accent colors (suggested: `#2c5fab` blue for solid arrows, `#d8332e` red for audit dashed arrows, `#5e9b5e` green for final answer leaves) | EMNLP camera-ready printing is reliably distinguishable in 4-color and color-blind safe |
| No prose blocks inside the image — only single-token labels (`outsource`, `accept?`, `do_self`, `split`, `decomposer` etc.) | LaTeX caption owns the prose; image must read at 50% scale |
| Sans-serif font (Helvetica / Arial / Roboto); ≥ 8 pt at final scale | ACL legibility requirement |
| All node labels horizontally readable (no rotated text) | ARR reviewer accessibility |
| Single-column width: 3.3 in × ≤ 3.0 in | Don't span both columns; we want it to flow with §3.4 prose |

---

## 4. AI-image-tool prompt (drop-in for ChatGPT image / Midjourney / SVG-aware tools)

> **Render a 2-panel academic schematic, single column width (3.3 in × 2.5 in total), in vector style with white background. Top panel (~60% height): five identical small circular agent nodes labeled A B C D E forming a sparse undirected visibility graph (edges A–B, A–C, B–C, B–D, C–E shown as thin gray lines). Show task delegation flow with three colored solid arrows: A→B labeled "outsource(z)", B→D labeled "outsource(z)", and a small branching schematic from A showing "split(z → z₁, z₂)" with z₁ flowing to C and z₂ kept at A as "do_self". Show recursive acceptance audit as red dashed arrows in the reverse direction: D→B, B→A, C→A all labeled "accept?". Add a small green leaf icon at A labeled "final answer". Bottom panel (~40% height, separated by a thin horizontal rule): four identical square nodes in a left-to-right chain labeled "decomposer", "evidence_seeker", "verifier", "synthesizer" connected by blue solid arrows labeled "forward". A small green leaf at the synthesizer labeled "final answer + terminal F1 update". A red dashed feedback arrow from synthesizer back to decomposer labeled "scalar competence update (TCPB)". Use sans-serif font ≥ 8pt. No prose blocks inside the image. Tiny legend in the bottom-right of the top panel: solid blue = outsource/split delegation; red dashed = recursive acceptance audit; green leaf = final accepted answer. Style should look like a clean ICML/EMNLP Figure 1, monochrome with two accent colors only (blue #2c5fab, red #d8332e, green #5e9b5e). Output as SVG or PDF.**

---

## 5. Acceptance criteria (so the user knows when the deliverable is "done")

| Check | Pass if |
|---|---|
| File format | `.pdf` or `.svg` (vector); `.png` 300+ dpi as fallback |
| File location | `workspace/autogen/dotnet/website/articles/paper/figures/fig1_3action_policy.{pdf,svg,png}` AND `artifacts/figures/fig1_3action_policy.{pdf,svg,png}` (mirror copy for in-doc preview) |
| Read-time | A reviewer who has *not* read §3 can identify the three primitive actions and the audit return arrows in ≤ 10 seconds |
| Both panels | Both Panel A (full EDO sparse graph + task tree) and Panel B (TCPB chain prototype) are present |
| Color discipline | ≤ 2 accent colors + black + green leaf; no rainbow palettes |
| Single-column width | Final rendered file fits 3.3 in width without truncation in `\includegraphics[width=\columnwidth]{fig1_3action_policy}` |
| No identifying info | No "we" / "our" / project name / GitHub URL / author hints inside the image (anonymization compliance per `docs/demand.md §2`) |

---

## 6. Once the asset lands

* Notify the scientist (drop a line in `docs/coordination/SCIENTIST_TODO.md § D` revision record).
* `S-010` will then unblock: scientist embeds via `\includegraphics{...}` in the LaTeX paper after `S-013`, and writes the final caption referencing both panels.
* If only `.png` is delivered (raster only), scientist re-flags `U-009-decide` and asks user whether to (a) re-render as vector or (b) accept raster + `\includegraphics{...}` width-only embedding.

---

## 7. Failure modes to avoid (common pitfalls when AI tools generate this kind of figure)

* **Multiple colors per node** — agents must look identical to convey "near-homogeneous"; the only allowed asymmetry is graph position.
* **Curved arrows mixed with straight arrows** — pick one style for delegation (solid straight), one for audit (dashed straight or slight curve consistently in one direction).
* **Inline equations or paragraph captions inside the image** — captions go in LaTeX, not the figure.
* **Drop shadows / 3-D bevel / gradient fill** — academic figures use flat 2-D vector strokes only.
* **Clip-art-style icons** (e.g., cartoon robot for the agents) — use plain geometric shapes (circles for full EDO panel, squares for the prototype panel) to make the homogeneity visually obvious.
