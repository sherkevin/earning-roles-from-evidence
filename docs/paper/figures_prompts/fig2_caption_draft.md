# Figure 2 — Caption draft (scientist-owned, asset already rendered)

> Owner: **scientist** (rendered by `scripts/plot_fig2_backbone_sensitivity.py`).
> Asset: `artifacts/figures/fig2_backbone_sensitivity.{png,pdf}`.
> Data provenance: `artifacts/figures/fig2_backbone_sensitivity_data.md`.
> Insertion target: §4.3 of `docs/paper/EMNLP_paper_draft.md`, immediately after Finding 2 (the backbone-sensitivity finding).

---

## Final caption (LaTeX-ready, single-column figure)

```
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/fig2_backbone_sensitivity}
  \caption{
    Backbone-sensitive method ordering on the chain-200 HotpotQA slice.
    All three Stage-1 fixed methods improve by $\approx +15$--$20$ F1 points
    when the backbone is upgraded from \texttt{glm-4-flash} to
    \texttt{gpt-4.1-mini}, but the relative ordering between methods inverts.
    On \texttt{glm-4-flash} the ordering is
    \texttt{peer\_calibrated} ($0.596$) $>$
    \texttt{static\_roles} ($0.580$) $>$
    \texttt{self\_claim} ($0.562$);
    on \texttt{gpt-4.1-mini} it becomes
    \texttt{self\_claim} ($0.764$) $>$
    \texttt{static\_roles} ($0.745$) $>$
    \texttt{peer\_calibrated} ($0.738$).
    The red star marks the only validated full-validation point
    (\texttt{peer\_calibrated} on \texttt{gpt-4.1-mini}, $F_1 = 0.770$, $n=7405$);
    \texttt{static\_roles} and \texttt{self\_claim} fullval runs are pending
    rerun under the runtime integrity guard
    (cf.~\S\ref{sec:limitations}).
    All values are mean answer F1 over $n=200$ shared HotpotQA validation
    questions; identical inputs and routing code are used across backbones.
  }
  \label{fig:backbone-sensitivity}
\end{figure}
```

---

## Plain-text version (for Markdown drafts before LaTeX migration)

> **Figure 2.** Backbone-sensitive method ordering on the chain-200 HotpotQA slice. All three Stage-1 fixed methods improve by ~15–20 F1 points when the backbone is upgraded from `glm-4-flash` to `gpt-4.1-mini`, but the relative ordering between methods *inverts*. On `glm-4-flash` the ordering is `peer_calibrated (0.596) > static_roles (0.580) > self_claim (0.562)`; on `gpt-4.1-mini` it becomes `self_claim (0.764) > static_roles (0.745) > peer_calibrated (0.738)`. The red star marks the only validated full-validation point (`peer_calibrated` on `gpt-4.1-mini`, F1 = 0.770, n=7405); `static_roles` and `self_claim` fullval runs are pending rerun under the runtime integrity guard (cf. §5). All values are mean answer F1 over n=200 shared HotpotQA validation questions; identical inputs and routing code are used across backbones.

---

## In-text mention (one sentence to add at the end of §4.3 Finding 2)

> Figure~\ref{fig:backbone-sensitivity} visualises the inversion: the same routing code, the same 200 questions, and the only changed variable (backbone identity) reverses the relative method order — a result that motivates the broader EDO theory rather than further tuning of any single Stage-1 method.

---

## Why this caption is structured this way

1. **Numbers in the caption** — ARR review heuristic: a reader who looks only at figures + captions should be able to extract the headline finding without reading the body.
2. **Inversion verbalised twice** — once as ordering A (GLM) and once as ordering B (gpt-4.1-mini), so a reviewer with poor color vision can still read the finding.
3. **Star marker explained inline** — to avoid a separate "legend" key in the image; the legend is part of the caption itself.
4. **Forward reference to §5 Limitations** — the corruption / pending-rerun caveat is honest and sits in the caption so reviewers cannot accuse "selective reporting".
5. **`identical inputs and routing code`** — preempts the Reviewer-S2 concern "is this just noise from a different question split or different code path?".

---

## Status

* PNG + PDF generated: ✅
* Caption text drafted: ✅
* Inserted into `EMNLP_paper_draft.md`: ⏳ blocked by `U-003-decide` (single-draft merge would be the natural moment to wire in `\includegraphics{...}` once the file is in LaTeX form via `S-013`).
