# Figure 6 Prompt — Best-Paper evidence map

> Owner: scientist prompt; user / AI image tool renders.
> Purpose: paper-planning / possible introduction figure that maps claims to evidence gates.
> Target asset: `artifacts/figures/fig6_best_paper_evidence_map.{svg,pdf,png}`.
> Paper anchor: Introduction contribution overview or appendix roadmap. Use only if page budget allows.
> Status: prompt ready; conceptual roadmap. This figure may be internal if the final paper is too tight.

---

## 1. Scientific message

This figure should align the paper's best-paper route:

> EDO is not one result. It is a chain of claims, and each claim has a matching evidence gate: mechanism theorem, controlled QA matrix, external SOTA comparison, weak-model emergence, and case-study traces.

The figure helps prevent overclaiming by showing which evidence supports which claim.

---

## 2. Layout

Use a left-to-right pipeline with four stacked lanes.

### Lane 1: Method claim

- Box 1: `EDO framework`
- Box 2: `R1 split`
- Box 3: `R2 recursive audit`
- Box 4: `R3 vector belief`
- Use blue boxes.

### Lane 2: Theory gate

- Under R2: `Ω(H) audit signal`
- Under R3: `specialization entropy`
- Under EDO framework: `1-locality + reduction theorem`
- Use purple or navy outline.

### Lane 3: Empirical gate

- `HotpotQA + MuSiQue matrix`
- `MA-RAG / ReAgent / MAD head-to-head`
- `paired CI + multi-seed`
- `weak-backbone emergence`
- Use green boxes.

### Lane 4: Reviewer risk closed

- `D1 soundness`
- `D3 novelty vs MAD`
- `D4 experiments`
- `D5 reproducibility`
- Use grey risk tags that turn into checkmarks.

At the far right, draw a final gate labeled:

`Oral / Best-Paper readiness`

The final gate should be conditional, not a success claim. Use a lock/gate icon with label `requires all gates`.

---

## 3. Visual style

- Use a professional roadmap / Sankey-like figure, not a flowchart mess.
- Keep labels short.
- Avoid checkmarks that imply already completed unless label says `planned` or `requires`.
- Use thin arrows from claims to evidence gates.
- Good for internal planning and maybe appendix; if inserted into main paper, caption must state it is the evaluation map.

---

## 4. Drop-in AI image prompt

```text
Create a clean academic roadmap figure, vector style, white background, flat design, sans-serif labels. The figure is a left-to-right evidence map with four horizontal lanes and a final gate on the right. Use short labels only.

Lane 1 title: "Method claim". Blue boxes from left to right: "EDO framework", "R1 split", "R2 recursive audit", "R3 vector belief".

Lane 2 title: "Theory gate". Navy-outline boxes aligned under the method boxes: under EDO framework write "1-locality + reduction theorem"; under R2 write "Omega(H) audit signal"; under R3 write "specialization entropy"; leave R1 as "complexity bound".

Lane 3 title: "Empirical gate". Green boxes: "HotpotQA + MuSiQue matrix", "MA-RAG / ReAgent / MAD head-to-head", "paired CI + multi-seed", "weak-backbone emergence". Draw thin arrows from the method boxes to the relevant empirical boxes.

Lane 4 title: "Reviewer risk closed". Grey risk tags that become outlined check tags: "D1 soundness", "D3 novelty vs MAD", "D4 experiments", "D5 reproducibility". Draw arrows from theory and empirical gates down to the risks they close.

At the far right, draw a final locked gate labeled "Oral / Best-Paper readiness" with subtitle "requires all gates". Make it conditional, not celebratory. Use blue #2c5fab for method boxes, green #5e9b5e for empirical gates, navy #1f3f5b for theory, grey #777777 for risks, and a small amber #d49b27 lock/gate. Output as SVG or PDF.
```

---

## 5. Acceptance criteria

| Check | Pass condition |
|---|---|
| Claim discipline | The figure shows evidence gates, not "we are best paper already". |
| Reviewer mapping | D1/D3/D4/D5 risks are explicitly visible. |
| Best-paper route | R2 theorem, external baselines, paired CI, and weak-model emergence are all represented. |
| Low clutter | No box has more than six words. |
| Optionality | Figure can serve as internal roadmap if page budget rejects it. |

