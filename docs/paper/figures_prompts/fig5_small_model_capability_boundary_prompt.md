# Figure 5 Prompt — Small-model capability boundary emergence

> Owner: scientist prompt; user / AI image tool renders.
> Purpose: Best-Paper empirical-story template for weak-agent organization.
> Target asset: `artifacts/figures/fig5_small_model_capability_boundary.{svg,pdf,png}`.
> Paper anchor: small-model emergence axis, `docs/paper/small_model_emergence_response_20260423.md`, future experiment section.
> Status: prompt ready; template only. Replace placeholder marks with real Phi-4 / SmolLM3 / gpt-4.1-mini values after engineering artifacts land.

---

## 1. Scientific message

This figure should visually prepare the strongest possible best-paper story:

> Organization should matter most near the model capability boundary. The key empirical test is whether `Δ = F1_multi − F1_single` is larger for weaker local backbones than for the strong API backbone.

The figure must not fabricate results. It should be rendered as a clean template with placeholder markers.

---

## 2. Layout

Use a two-panel figure.

### Panel A: Matched backbone comparison

- X-axis: `Backbone scale / capability`
- Three x positions:
  - `SmolLM3-3B`
  - `Phi-4-mini`
  - `gpt-4.1-mini`
- For each x position, show two bars:
  - grey bar = `single_agent`
  - blue bar = `EDO / Stage-2`
- Since real values are pending, show bars as semi-transparent placeholders with a light diagonal hatch.
- Above each pair, reserve a blank delta label:
  - `Δ_Smol = ?`
  - `Δ_Phi = ?`
  - `Δ_strong = ?`
- Add a note: `values filled after matched runs`.

### Panel B: Emergence hypothesis curve

- X-axis: `individual model capability`
- Y-axis: `organization gain ΔF1`
- Draw a conceptual inverted-U or boundary-region curve:
  - low capability: near zero / unstable;
  - boundary region: high positive gain;
  - strong model: smaller gain.
- Shade the middle region and label it `capability boundary`.
- Add three markers corresponding to the three backbones, with hollow circles and question marks until data lands.
- Add caption text inside panel: `test: Δ_small > Δ_strong?`

---

## 3. Visual style

- Clean EMNLP / NeurIPS-style vector figure.
- Use no fake numbers.
- Use placeholder / hatched bars to signal "template awaiting data".
- Accent colors:
  - blue `#2c5fab` for EDO / Stage-2;
  - grey `#8a8a8a` for single-agent;
  - amber `#d49b27` for the capability-boundary shaded region.
- Avoid "emergence" as magical imagery. Keep it statistical and sober.

---

## 4. Drop-in AI image prompt

```text
Create a sober two-panel academic vector figure for an NLP paper. White background, flat design, sans-serif font, no gradients, no 3D, no cartoon robots.

Panel A title: "A. Matched backbone comparison". Draw a grouped bar chart with x-axis "Backbone scale / capability" and three groups: "SmolLM3-3B", "Phi-4-mini", "gpt-4.1-mini". Each group has two semi-transparent hatched placeholder bars: grey bar labeled "single_agent" and blue bar labeled "EDO / Stage-2". Do not show numeric y-values. Above each group place placeholder delta labels: "Delta_Smol = ?", "Delta_Phi = ?", "Delta_strong = ?". Add a small note: "values filled after matched runs".

Panel B title: "B. Capability-boundary hypothesis". Draw a conceptual curve with x-axis "individual model capability" and y-axis "organization gain Delta F1". The curve is low at very weak capability, rises in a middle shaded region, and becomes smaller again for strong models. Shade the middle region in amber #d49b27 with label "capability boundary". Add three hollow circular markers with question marks corresponding to SmolLM3-3B, Phi-4-mini, and gpt-4.1-mini. Add a compact test label: "test: Delta_small > Delta_strong?".

Use grey #8a8a8a for single_agent, blue #2c5fab for EDO / Stage-2, amber #d49b27 for the capability boundary. Make clear that this is a data-to-be-filled template and not completed results. Output as SVG or PDF.
```

---

## 5. Acceptance criteria

| Check | Pass condition |
|---|---|
| No fabricated data | No numeric F1 values or fake confidence intervals appear. |
| Hypothesis clarity | Viewer understands the test is `Δ_small > Δ_strong?`. |
| Matched comparison | Each backbone visibly compares `single_agent` vs `EDO / Stage-2`. |
| Best-paper fit | Figure frames a capability-boundary claim, not generic "more agents better". |
| Future-proof | Real values can replace placeholders later. |

