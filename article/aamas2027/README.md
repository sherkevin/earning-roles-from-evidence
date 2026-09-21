# AAMAS 2027 internal revision

Active specification: [REQUIREMENTS.md](../../docs/paper/aamas2027/REQUIREMENTS.md), v1.3. Current gaps/work: [AAMAS_TASKS.md](../../docs/coordination/AAMAS_TASKS.md). The user selected acquired capabilities and composable workflows (C); the [Q1 discussion](../../docs/scientist/analysis/AAMAS_Q1_worker_differences.md) now includes a published-work audit and a candidate fusion with EDO's local evidence principle. The existing LaTeX/PDF is an older internal allocation-only scaffold, not the new C method or its evidence. Scientific sections must be rewritten after the B/M contracts; its official template remains reusable.

Build from the project root:

```powershell
python scripts/build_aamas2027.py
```

- `main.tex`: rewritten research question, minimal proposed protocol, corrected analysis, verified historical results, and decisive prospective tests.
- `supplement.tex`: complete component directions, logging limitations, actual failure trace, evaluation contract, and assistance disclosure.
- `build/main.pdf`, `build/supplement.pdf`: compiled internal drafts.
- `aamas.cls`, `ACM-Reference-Format.bst`, `by.pdf`: byte-identical copies from the official AAMAS 2027 template.
- `aamas_metadata.tex`: official conference/copyright settings and an explicit internal submission-ID marker.

The original EMNLP/ACL sources remain in `article/latex/` and have not been overwritten.

This draft separates a revised, not-yet-evaluated protocol from historical measured variants. It is not submission-ready. The external submission guard is:

```powershell
python scripts/build_aamas2027.py --submission
```

It refuses release until `docs/paper/aamas2027/submission_gate.json` and manuscript metadata are finalized. Do not remove internal status text merely to make the guard pass. Replace prospective sections with executed, independently verified evidence or narrow the paper's contribution explicitly.

After reviewed requirements/task-ledger changes, run `python scripts/check_aamas_documents.py --sync-gate --check-gate`. The gate is derived from the fifteen requirement rows and bound to both document hashes; submission builds reject a stale gate. Document checks do not certify scientific validity.

S-518 records the historical first pass. Its separate venue/positioning/reviewer/handoff notes have been consolidated into the two active documents above.
