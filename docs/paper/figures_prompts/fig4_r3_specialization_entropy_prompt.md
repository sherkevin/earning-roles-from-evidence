# Figure 4 Prompt — R3 specialization entropy and persona-vector emergence

> Owner: scientist prompt; user / AI image tool renders.
> Purpose: Best-Paper method-theory figure for R3 vector belief / specialization.
> Target asset: `artifacts/figures/fig4_r3_specialization_entropy.{svg,pdf,png}`.
> Paper anchor: R3 vector-belief update, Appendix F.3, future T-Best-2 specialization entropy theorem.
> Status: prompt ready; conceptual plus placeholder curve. Replace placeholder curve with real data later if E-023 lands.

---

## 1. Scientific message

This figure should explain the R3 emergence claim without overclaiming current evidence:

> Repeated local audit signals update each agent's 7-axis persona vector. If signals are value-informative, cross-agent specialization entropy should decrease over time; a no-audit control should remain flat.

This is a mechanism figure plus a future empirical template.

---

## 2. Layout

Use three horizontal panels stacked vertically.

### Panel A: Persona-vector state

- Draw four near-homogeneous agents `A`, `B`, `C`, `D` as identical circles on a sparse graph.
- Next to each agent, draw a tiny 7-bar mini-vector labeled:
  `solve`, `decompose`, `audit`, `integrate`, `explore`, `efficiency`, `reliability`.
- At `t=0`, all mini-vectors should look similar and low-contrast.
- Label: `near-homogeneous initialization`.

### Panel B: Local audit updates

- Show two or three local interactions:
  - `A → B` delegation;
  - `B → A` audit return;
  - `C → D` delegation;
  - `D → C` audit return.
- Use red dashed arrows for audit returns.
- Draw small update tokens entering persona vectors:
  - `+ audit`
  - `+ decompose`
  - `+ reliability`
- Add formula callout:
  `Pᵢ^{t+1} = (1 − μ)Pᵢ^t + μ Vᵢ^t`
- Label: `local value signals update persona axes`.

### Panel C: Entropy trajectory

- Draw a simple line chart with x-axis `time / tasks` and y-axis `specialization entropy S(t)`.
- Two curves:
  - blue descending curve labeled `R3 vector belief + audit`;
  - grey flat curve labeled `no-audit control`.
- Put a small annotation at the right of the blue curve: `agents specialize`.
- Do not include numeric y-values unless real data is available.

---

## 3. Visual style

- Clean vector figure, white background.
- Use identical agent shapes to preserve "near-homogeneous".
- Use small but readable labels; avoid paragraph text.
- Accent colors:
  - blue `#2c5fab` for R3 / entropy curve;
  - red `#d8332e` for audit arrows;
  - grey `#777777` for no-audit control.
- Keep figure calm and theorem-like, not sci-fi.

---

## 4. Drop-in AI image prompt

```text
Create a clean three-panel academic vector schematic for an ML/NLP paper. White background, flat 2D line art, sans-serif labels, no gradients, no 3D effects.

Panel A title: "A. Persona-vector state". Draw four identical circular agents labeled A, B, C, D connected by a sparse grey graph. Next to each agent, draw a tiny 7-bar vector glyph with labels solve, decompose, audit, integrate, explore, efficiency, reliability. At t=0, the bar patterns are similar and low contrast. Add the label "near-homogeneous initialization".

Panel B title: "B. Local audit updates". Show two delegation interactions: A to B and C to D with solid blue arrows. Show audit returns B to A and D to C with red dashed arrows. Small colored update tokens flow into the 7-bar persona vectors: "+audit", "+decompose", "+reliability". Add a compact formula callout: "P_i^(t+1) = (1 - mu) P_i^t + mu V_i^t". Add the label "local value signals update persona axes".

Panel C title: "C. Specialization entropy". Draw a simple line chart with x-axis "time / tasks" and y-axis "specialization entropy S(t)". Add a blue descending curve labeled "R3 vector belief + audit" and a grey nearly-flat curve labeled "no-audit control". Add a small annotation near the blue curve endpoint: "agents specialize". Do not add numeric y-values. Use blue #2c5fab for R3, red #d8332e for audit arrows, grey #777777 for the control. Output as SVG or PDF, readable at paper scale.
```

---

## 5. Acceptance criteria

| Check | Pass condition |
|---|---|
| Claim boundary | The figure says "should / mechanism / template", not that specialization is already proven. |
| R3 clarity | Persona vectors and EMA update are visible. |
| Emergence clarity | Entropy decreases only in the R3+audit curve; control remains flat. |
| Homogeneity | Agents start visually identical; specialization appears through vectors, not fixed role icons. |
| Future-proof | Numeric values can be added later without redrawing the whole figure. |

