# Best-Paper Figure Prompt Index

> Created: 2026-04-24
> Owner: scientist
> Purpose: collect AI-renderable prompts for the Best-Paper methodology / evidence route.

---

## Recommended rendering order

1. `fig3_r2_information_advantage_prompt.md`
   - Highest scientific value.
   - Supports R2 recursive audit and T-Best-1 / T-Best-3.
   - Can be used before new experiments land.

2. `fig5_small_model_capability_boundary_prompt.md`
   - Highest narrative value if Phi-4 / SmolLM3 results arrive.
   - Must remain placeholder until real metrics land.

3. `fig4_r3_specialization_entropy_prompt.md`
   - Strong for emergence / specialization, but should ideally wait for E-023 or at least be labeled as theoretical template.

4. `fig6_best_paper_evidence_map_prompt.md`
   - Useful for internal planning and possibly appendix.
   - Main-body insertion only if page budget allows.

Existing prompt:

- `fig1_3action_policy_prompt.md` remains the core system schematic.
- The new Figure 3 prompt should not replace Figure 1; it explains the theorem-level advantage of R2.

---

## Suggested user rendering batch

Ask the AI image tool to render:

```text
1. fig3_r2_information_advantage as SVG/PDF
2. fig5_small_model_capability_boundary as SVG/PDF
3. fig4_r3_specialization_entropy as SVG/PDF
4. fig6_best_paper_evidence_map as SVG/PDF only if time remains
```

Place final assets under:

```text
artifacts/figures/
```

Keep any raster previews alongside the vector file, but the paper should prefer `.pdf` or `.svg`.
