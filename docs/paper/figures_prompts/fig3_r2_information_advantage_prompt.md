# Figure 3 Prompt — R2 recursive audit information advantage

> Owner: scientist prompt; user / AI image tool renders.
> Purpose: Best-Paper method-theory figure.
> Target asset: `artifacts/figures/fig3_r2_information_advantage.{svg,pdf,png}`.
> Paper anchor: Method / theory section around R2 recursive audit, Appendix F.5, and the future T-Best-3 comparison against MAD / terminal-only aggregation.
> Status: prompt ready; data-free conceptual theorem figure. Do not insert empirical numbers.

---

## 1. Scientific message

This figure must make one idea visually obvious:

> Terminal-only aggregation observes one final label and gives at most `O(1)` credit-assignment signal, while recursive per-hop audit observes an audit trail over `H` hops and yields `Ω(H)` credit-assignment signal.

The figure should feel like a theorem diagram, not a product architecture diagram.

---

## 2. Layout

Use a clean two-column comparison with a thin vertical divider.

### Left panel: Terminal-only aggregation

- Title: `Terminal-only feedback`
- Draw an `H`-hop chain as five small nodes: `hop 1`, `hop 2`, `hop 3`, `...`, `hop H`.
- Use grey arrows between hops.
- At the end, draw one large terminal box labeled `final answer y`.
- Draw one red feedback arrow from `y` back to the whole chain, labeled `one global signal`.
- Add a small equation callout: `I(F ; y) ≤ O(1)`.
- Add a small label: `failure attribution is ambiguous`.
- Optional faded silhouettes under the chain: `which hop failed?` repeated with question marks.

### Right panel: R2 recursive audit

- Title: `R2 recursive audit`
- Draw the same `H`-hop chain.
- Above or below each hop boundary, draw a small audit token: `a₁`, `a₂`, `a₃`, `...`, `a_H`.
- Draw red dashed local feedback arrows for each hop, pointing from downstream back to upstream.
- At the end, also show `final answer y`, but make it visually secondary.
- Add a blue bracket spanning all audit tokens labeled `per-hop audit sequence`.
- Add a theorem callout: `I(F ; a₁...a_H, y) ≥ Ω(H ε²)`.
- Add a small label: `failure attribution becomes local`.

### Bottom bridge

Across the bottom, place a short centered conclusion:

`recursive audit turns terminal supervision into per-hop credit assignment`

Do not include a long paragraph inside the figure.

---

## 3. Visual style

- Academic vector style, white background.
- Single-column or 1.5-column friendly; target width 6.8 in if two-column, 3.3 in if single-column.
- Use only black/grey plus two accents:
  - blue `#2c5fab` for information brackets / theorem emphasis;
  - red `#d8332e` for feedback / audit arrows.
- No 3D, no gradients, no cartoon robots.
- Use flat line art, high contrast, sans-serif labels.
- Equations must be typeset cleanly and legibly.

---

## 4. Drop-in AI image prompt

```text
Create a clean academic vector schematic for an NLP / ML paper. White background, flat line art, sans-serif font, no gradients, no 3D. The figure is a two-column comparison with a thin vertical divider.

Left panel title: "Terminal-only feedback". Draw a horizontal H-hop reasoning chain with five small grey nodes labeled "hop 1", "hop 2", "hop 3", "...", "hop H". Grey arrows connect the hops. At the end, draw a larger box labeled "final answer y". Draw one red feedback arrow from the final answer back to the entire chain, labeled "one global signal". Add a theorem callout near this panel: "I(F ; y) <= O(1)". Add a small caption inside the panel: "failure attribution is ambiguous". Add faint question marks under the hop nodes to indicate uncertainty about which hop failed.

Right panel title: "R2 recursive audit". Draw the same H-hop chain. At each hop boundary, draw a small red audit token labeled "a1", "a2", "a3", "...", "aH". Draw red dashed local feedback arrows from each downstream hop back to its upstream hop, indicating recursive audit. At the end, show a smaller final answer box labeled "final answer y". Add a blue bracket spanning all audit tokens labeled "per-hop audit sequence". Add a theorem callout: "I(F ; a1...aH, y) >= Omega(H epsilon^2)". Add a small caption inside the panel: "failure attribution becomes local".

At the bottom across both panels, place one centered conclusion line: "recursive audit turns terminal supervision into per-hop credit assignment". Use black and grey for structure, blue #2c5fab for information brackets and theorem emphasis, red #d8332e for feedback and audit arrows. Ensure all labels are readable at paper scale. Output as SVG or PDF.
```

---

## 5. Acceptance criteria

| Check | Pass condition |
|---|---|
| Theorem contrast | The viewer can identify `O(1)` vs `Ω(H ε²)` in under 5 seconds. |
| Mechanism clarity | Right panel visibly has per-hop audit tokens; left panel visibly has only final feedback. |
| No overclaim | Figure does not show empirical curves or fabricated values. |
| Paper compatibility | Works as vector `.svg` or `.pdf`, legible at column scale. |
| Anonymity | No author names, project URLs, or implementation paths inside the artwork. |

