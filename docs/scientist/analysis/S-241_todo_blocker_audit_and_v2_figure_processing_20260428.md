# S-241 TODO Blocker Audit And V2 Figure Processing

Date: 2026-04-28
Author role: scientist

## 1. Purpose

This task was opened after the user asked the scientist to carefully inspect current TODOs, verify whether blockers had cleared, continue every unblocked item, persist intermediate results, update TODO/dependency documents, and commit paper-polish changes.

## 2. Blocker Sweep

Current scientist blockers:

- `S-211-final-sync`: still parked by paid API route. `USER_TODO.md` now contains `C-027`, but the user has not explicitly reopened the paid `E-030` / `E-041` Wave-1 execution gate. This remains genuinely blocked.
- `tracking-C-026`: partially unblocked. New assets `article/figures/figure2_v2.png` and `article/figures/figure3_v2.png` exist; no `figure1_v2` asset exists.

Engineer sync items already landed before this pass:

- `E-050` 2Wiki local transfer is negative.
- `E-051` canonical matrix blocker audit confirms paid Wave-1 remains the true canonical matrix blocker.
- `E-052` guarded launcher/status hardening removes launch-script friction but does not create evidence until the paid gate opens.

No new scientist-side claim promotion follows from these items.

## 3. Figure Asset Judgment

### Figure 2 v2

`article/figures/figure2_v2.png` is acceptable as the current main method figure direction:

- it has a white/paper-like outer area and warm internal cards;
- the previous design-scaffold label is gone;
- the duplicate `(b) Governed action cycle` label is gone;
- evidence wording is safer (`Logged evidence trail`, `evidence bundle`);
- it is visually appropriate only as a two-column figure.

Action: wired `figure2_v2.png` into the main paper as a `figure*` at `0.96\textwidth`.

### Figure 3 v2

`article/figures/figure3_v2.png` is not acceptable:

- visible title text contains `(optionally Tiempos Text / Anthropic Serif)`, directly violating the Styrene-only requirement;
- `Peer j` appears twice;
- it remains too dense for the main body while Figure 2 is now the primary method figure.

Action: kept Figure 3 out of the main paper and tightened the Figure 3 prompt to forbid visible font/style notes and duplicate Peer j.

### Figure 1

No `figure1_v2` exists. `figure1_v1.png` remains temporarily wired, but it is not final under the user's v6 A4-card / Styrene-only style request. To preserve the page budget, Figure 1 was changed from a full-width `figure*` to a single-column `figure`.

## 4. Build Verification

Final main-paper build command:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/build_paper.ps1" -Clean
```

Result:

```text
[OK] build succeeded
PDF pages including Limitations and References: 10
Main body ends on page 8: COMPLIANT
Overfull hboxes: 0
Underfull hboxes: 32
```

## 5. Status

`S-241` is complete. Remaining scientist work is blocked on:

1. user decision `C-027` / paid route reopening for canonical matrix execution;
2. user rendering of final Figure 1 and Figure 3 assets under the v6 style.
