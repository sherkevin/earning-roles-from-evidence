# Figure 1 — Conceptual diagram prompt (USER to render)

> Owner: **user** (per 2026-04-19 协作约定: 概念图 / 示意图归用户绘制).
> Version history: v1 (2026-04-19, R1 commit) → **v2 (2026-04-20, R11 commit)** — upgraded to highlight Stage-2 R1/R2/R3 mechanisms + module-swap design (per S-119 in `SCIENTIST_TODO §B.5`).
> Scientist responsibility: provide a complete prompt + acceptance criteria + a textual fallback so the user (or an AI image tool) can produce the asset without further clarification.
> Target asset: `artifacts/figures/fig1_3action_policy.{pdf,svg,png}` (vector preferred; copy paths in §5).
> Final caption / paper insertion is `S-010` and is blocked on this asset landing.
> Tracking row: `USER_TODO.md §B.2 U-EXEC-004`.

---

## 0. What changed in v2 vs v1

| Aspect | v1 (2026-04-19) | v2 (2026-04-20) |
|---|---|---|
| Action vocabulary | `do_self / outsource(neighbor) / split(subtasks)` | **same** — three primitive actions are stable |
| Panel A purpose | "Full EDO" abstract framework | **same** but now also annotates which mechanism is **R1 / R2 / R3** of the Stage-2 sprint |
| Panel B purpose | TCPB Stage-1 prototype (degenerate chain) | **same** — preserved as the "what we ran in Stage-1" anchor |
| **NEW Panel C** | (absent) | **module-swap call-out** showing R3 → AutoGen `select_speaker` and R2 → ChatEval `MetaReviewer` (closes reviewer R-FULL-001 fatal #3) |
| Color palette | 2 accents (blue / red) + green leaf | **same** plus optional purple `#7d3aa8` for swap-into-host arrows in Panel C |
| Aspect ratio | 3.3 × 2.5 in (single column, 2 stacked panels) | **3.3 × 3.4 in** (single column, 3 stacked panels) — taller to accommodate Panel C; still single column |

If you produced a v1 image already, **do not throw it away** — keep it as `fig1_3action_policy_v1.{pdf,svg,png}` for legacy comparison. v2 replaces v1 in the paper.

---

## 1. What the figure must convey (v2)

Figure 1 is the **single conceptual schematic** for the EDO long-paper method. A reviewer who looks at it for 5 seconds must be able to read off **four** things:

1. The **three primitive actions** an agent picks among on every received task: `do_self`, `outsource(neighbor)`, `split(subtasks)` — Panel A.
2. The **recursive acceptance ladder**: when agent `a` outsources to `b`, `b` later returns a candidate result and `a` must `accept / accept_with_note / reject_reroute / reject_resplit` it. If `b` itself outsourced to `c` first, then `b` accepted `c` before returning upward — Panel A.
3. The **distinction between full EDO** (Panel A: sparse graph + arbitrary task tree + R1 split + R2 audit + R3 vector belief) and the **TCPB Stage-1 prototype** (Panel B: chain topology + linear handoff + scalar competence). The viewer should see in one glance that EDO is the superset and that the prototype lives inside a fixed `decomposer → evidence_seeker → verifier → synthesizer` chain.
4. **NEW (v2): module-swap design** (Panel C) — our R3 vector-belief routing drops into AutoGen `GroupChatManager.select_speaker`; our R2 audit decision drops into ChatEval `MetaReviewer.aggregate`. This is the experimental anchor for the §4.x external-baseline comparison (closes reviewer R-FULL-001 fatal #3).

A reader should NOT have to read §3 prose to understand which arrow is "outsource" vs "audit return" vs "split"; nor should they need to read §4 to understand which of our mechanisms swaps into which external host's component.

---

## 2. Layout specification (single column, ~3.3in wide × ~3.4in tall, vector format)

The figure is **three stacked panels**, separated by thin horizontal rules. All panels share x-axis width.

### Panel A (top, ~45% of vertical space): Full EDO on a sparse graph with a recursive task tree

* Five circular agent nodes, near-homogeneous (all same shape and color), labeled `A`, `B`, `C`, `D`, `E`. Place them so the visible-edge graph forms a **sparse, connected, non-trivial topology** (e.g., A–B, A–C, B–C, B–D, C–E). Use thin gray lines for visibility edges (these are *who can see whom*, not delegation flow).
* On agent `A`, show the **incoming root task** as a small rounded rectangle labeled `task z`.
* From `A`, show the **three-action policy** as a vertically stacked decision callout next to `A` — **annotate each action with the corresponding R-mechanism tag**:
  * `do_self` (small icon: gear) — leads to a small green "answer" leaf attached to A.
  * `outsource(B)` (small icon: arrow) — solid colored arrow from A → B labeled `outsource(z)`. **Annotate as "R3 vector-belief routing"** (small italic label below the arrow). The neighbor `B` is selected because `B_A^t(B)` (vector belief over B's competence) maximises `U_i^{out}`.
  * `split(z → {z₁,z₂})` (small icon: branching tree) — shows two child task rectangles `z₁`, `z₂` attached to A; `z₁` is then `outsourced(C)` and `z₂` is `do_self` at A. **Annotate as "R1 split-and-recurse"** (small italic label).
* From `B → D`, draw another `outsource(z)` arrow (so we have a 2-hop delegation chain A→B→D for the "recursion" intuition).
* Draw the **return / audit arrows** with a *different visual style* (dashed, opposite direction, with small "audit" label). **Annotate the audit ladder as "R2 audit"** (single italic label near the dashed arrows, not per-arrow):
  * D → B (dashed, label `accept?`)
  * B → A (dashed, label `accept?`)
  * C → A (dashed, label `accept?` for the split-child path)
* In the bottom-right of Panel A, place a tiny legend swatch:
  * solid blue arrow = `outsource / split delegation`
  * red dashed arrow = `R2 recursive acceptance audit`
  * green leaf = `final accepted answer`
  * italic label `R1` / `R2` / `R3` = Stage-2 mechanism this part of the diagram instantiates

### Panel B (middle, ~25% of vertical space): TCPB Stage-1 prototype on a fixed chain

* Four square nodes in a left-to-right chain, labeled `decomposer → evidence_seeker → verifier → synthesizer`. Use the same node color as Panel A (homogeneous color scheme).
* Solid arrows pointing rightward labeled `forward (outsource only)`.
* No `split` arrows (since the prototype has no split). **Add a tiny grey strikeout or dashed-out `split` icon** above the chain with a "Stage-2 only" label, to make the gap between Panel A and Panel B visually unmistakable.
* No dashed audit arrows (since terminal-only update has no per-hop upstream rejection). **Add a tiny grey strikeout or dashed-out red `audit?` arrow** with "Stage-2 only" label.
* A small green leaf next to `synthesizer` labeled `final answer + terminal F1 update`.
* A subtle dashed feedback arrow from `synthesizer` back to `decomposer` labeled **`scalar competence update (TCPB)`** to indicate the post-sample update goes only to the accepting node. **Add italic label "R3 → scalar fallback"** next to this arrow.

### Panel C (bottom, ~30% of vertical space): Module-swap design — drop our mechanisms into external hosts (NEW in v2)

This panel is the **experimental anchor** that makes the §4.x external-baseline comparison legible to a reviewer in a single glance.

Two side-by-side mini-diagrams (left half and right half of Panel C, separated by a thin vertical rule):

**Left half — SWAP-1: R3 → AutoGen.**
* Draw a small box labeled `AutoGen GroupChatManager` (use a distinct outline style — dashed border — to mark it as a third-party host).
* Inside the box, draw a tiny `select_speaker()` callout.
* Draw a purple (`#7d3aa8`) hollow arrow pointing INTO the `select_speaker()` callout, labeled `our R3 vector belief Bᵢᵗ(j)`.
* Above the box, label `Host: AutoGen (Wu et al. 2024)`.
* Below the box, label `Swap target: select_speaker`.

**Right half — SWAP-3: R2 → ChatEval.**
* Draw a small box labeled `ChatEval MetaReviewer` (dashed border, same third-party outline style).
* Inside the box, draw a tiny `aggregate()` callout.
* Draw a purple hollow arrow pointing INTO the `aggregate()` callout, labeled `our R2 audit decision`.
* Above the box, label `Host: ChatEval (Chan et al. 2024)`.
* Below the box, label `Swap target: MetaReviewer.aggregate`.

A 1-line italic caption underneath Panel C: "Module-swap experiments (§4.x): our mechanisms drop in as controlled replacements for the host's decision component, holding everything else constant."

---

## 3. Visual / aesthetic constraints (v2 unchanged from v1 except color palette)

| Constraint | Rationale |
|---|---|
| **Vector format**: deliver `.pdf` (preferred) or `.svg`; `.png` only as fallback / preview | ACL `\includegraphics{...}` requires vector for clean compile; rasterized figures get partial credit deduction |
| Black + ≤ 3 accent colors (suggested: `#2c5fab` blue for solid arrows, `#d8332e` red for audit dashed arrows, `#5e9b5e` green for final answer leaves, **`#7d3aa8` purple for module-swap arrows in Panel C**) | EMNLP camera-ready printing is reliably distinguishable in 4-color and color-blind safe |
| No prose blocks inside the image — only single-token labels (`outsource`, `accept?`, `do_self`, `split`, `decomposer`, `R1`, `R2`, `R3`, `select_speaker`, `aggregate` etc.) | LaTeX caption owns the prose; image must read at 50% scale |
| Sans-serif font (Helvetica / Arial / Roboto); ≥ 8 pt at final scale (italic-ised R-mechanism tags can be 7 pt) | ACL legibility requirement |
| All node labels horizontally readable (no rotated text) | ARR reviewer accessibility |
| Single-column width: 3.3 in × ≤ 3.5 in (height extended from 3.0 to ~3.4 to accommodate Panel C) | Don't span both columns; Panel C trades ~0.4 in vertical for closing reviewer fatal #3 |

---

## 4. AI-image-tool prompt (drop-in for ChatGPT image / Midjourney / SVG-aware tools)

> **Render a 3-panel academic schematic, single column width (3.3 in × 3.4 in total), in vector style with white background. Top panel A (~45% height): five identical small circular agent nodes labeled A B C D E forming a sparse undirected visibility graph (edges A–B, A–C, B–C, B–D, C–E shown as thin gray lines). Show task delegation flow with three colored solid blue arrows: A→B labeled "outsource(z) — R3" in italic, B→D labeled "outsource(z)", and a small branching schematic from A showing "split(z → z₁, z₂) — R1" with z₁ flowing to C and z₂ kept at A as "do_self". Show recursive acceptance audit as red dashed arrows in the reverse direction labeled "R2 audit ladder": D→B, B→A, C→A all labeled "accept?". Add a small green leaf icon at A labeled "final answer". Middle panel B (~25% height, separated by a thin horizontal rule): four identical square nodes in a left-to-right chain labeled "decomposer", "evidence_seeker", "verifier", "synthesizer" connected by blue solid arrows labeled "forward". Add a small greyed-out strikethrough "split" icon and "audit?" red dashed arrow above the chain, both labeled "Stage-2 only" to mark what the prototype lacks. A small green leaf at the synthesizer labeled "final answer + terminal F1 update". A red dashed feedback arrow from synthesizer back to decomposer labeled "scalar competence update (TCPB) — R3 fallback". Bottom panel C (~30% height, NEW): two side-by-side mini-diagrams separated by a thin vertical rule. Left mini: a dashed-border box labeled "AutoGen GroupChatManager (Wu et al. 2024)" containing a "select_speaker()" callout, with a purple #7d3aa8 hollow arrow pointing INTO the callout labeled "our R3 vector belief Bᵢᵗ(j)" and a "Swap target" subscript. Right mini: a dashed-border box labeled "ChatEval MetaReviewer (Chan et al. 2024)" containing an "aggregate()" callout, with a purple hollow arrow pointing INTO the callout labeled "our R2 audit decision" and a "Swap target" subscript. Use sans-serif font ≥ 8pt (italic R-tags can be 7 pt). No prose blocks inside the image. Tiny legend in the bottom-right of Panel A: solid blue = outsource/split delegation; red dashed = R2 recursive acceptance audit; green leaf = final accepted answer; italic R1/R2/R3 tags = Stage-2 mechanism. Style should look like a clean ICML/EMNLP Figure 1, monochrome with three accent colors only (blue #2c5fab, red #d8332e, green #5e9b5e, purple #7d3aa8 for swap arrows). Output as SVG or PDF.**

---

## 5. Acceptance criteria (so the user knows when the deliverable is "done")

| Check | Pass if |
|---|---|
| File format | `.pdf` or `.svg` (vector); `.png` 300+ dpi as fallback |
| File location | `artifacts/figures/fig1_3action_policy.{pdf,svg,png}` (the canonical paper-asset directory; `\graphicspath{{../../artifacts/figures/}}` is already set in `article/latex/edo_paper.tex` so this path resolves automatically) |
| Read-time | A reviewer who has *not* read §3 / §4 can identify (a) the three primitive actions, (b) the audit return arrows, AND (c) **which of our mechanisms swaps into which external host** in ≤ 15 seconds |
| All three panels | Panel A (full EDO sparse graph + task tree + R1/R2/R3 annotations) + Panel B (TCPB chain prototype + greyed-out Stage-2 placeholders) + Panel C (SWAP-1 + SWAP-3 mini-diagrams) all present |
| R-tags visible | R1 / R2 / R3 italic labels appear on the corresponding arrows / panels — reviewer should be able to map "R2 audit" in §3 prose to the "R2 audit ladder" annotation in Panel A and to the "our R2 audit decision" arrow in Panel C |
| Color discipline | ≤ 3 accent colors + black + green leaf; no rainbow palettes; purple reserved for Panel C swap arrows only |
| Single-column width | Final rendered file fits 3.3 in width without truncation in `\includegraphics[width=\columnwidth]{fig1_3action_policy}` |
| No identifying info | No "we" / "our project name" / GitHub URL / author hints inside the image (anonymization compliance per `docs/demand.md §2`). The labels "Wu et al. 2024" and "Chan et al. 2024" in Panel C ARE acceptable (they cite published prior work, not our authorship) |

---

## 6. Once the asset lands

* Notify the scientist (drop a line in `docs/coordination/SCIENTIST_TODO.md § D` revision record).
* `S-010` will then unblock: scientist embeds via `\includegraphics{...}` in the LaTeX paper, replacing the current `\fbox{}` placeholder in §3 (added in R5).
* The new Figure 1 will then anchor §3 (Panel A + B for methodology) AND §4.x (Panel C for module-swap experiments) — both sections cite the same Figure 1.
* If only `.png` is delivered (raster only), scientist embeds with `\includegraphics{...}` width-only and adds a 1-line note in §3 saying "vector version pending" (no need for U-XXX-decide; raster acceptable for ARR submission, vector preferred for camera-ready).

---

## 7. Failure modes to avoid (common pitfalls when AI tools generate this kind of figure)

* **Multiple colors per node** — agents must look identical (same circle in Panel A; same square in Panel B) to convey "near-homogeneous"; the only allowed asymmetry is graph position.
* **Curved arrows mixed with straight arrows** — pick one style for delegation (solid straight), one for audit (dashed straight or slight curve consistently in one direction).
* **Inline equations or paragraph captions inside the image** — captions go in LaTeX, not the figure.
* **Drop shadows / 3-D bevel / gradient fill** — academic figures use flat 2-D vector strokes only.
* **Clip-art-style icons** (e.g., cartoon robot for the agents) — use plain geometric shapes (circles for full EDO panel, squares for the prototype panel) to make the homogeneity visually obvious.
* **Mixing R-mechanism colors with action-type colors** — R1/R2/R3 should be in italic *labels* on/near existing arrows, not change the arrow color. Keep blue=delegation / red=audit / purple=swap as the only color encoding.
* **Drawing AutoGen/ChatEval boxes in Panel C with the SAME color as our agent nodes** — third-party hosts must use a dashed border or different fill to make the "they are external" clear.
* **Overcrowding Panel C** — Panel C only needs to show 2 boxes + 2 arrows + 4 labels; resist adding arrows for SWAP-2 / SWAP-4 / SWAP-5 (those were rejected per `U-015-decide` and are explicitly out of scope).

---

## 8. Reference: where each panel maps to paper sections

| Panel | Paper anchor | Why |
|---|---|---|
| A | §3.1 problem formulation, §3.5 recursive audit, §3.6 persona update, §3.9 Stage-2 Roadmap (R1/R2/R3) | Single visual that indexes the entire Methodology |
| B | §3.7 Current restricted instantiation (TCPB), §3.8 separation matters, Prototype Scope Box | Single visual that grounds "what we ran in Stage-1" |
| C | §4.x External Baseline + Module-Swap Comparison (S-121/S-122/S-123 forthcoming after E-012) | Single visual that lets reviewer parse the §4.x table without re-reading §3 |
