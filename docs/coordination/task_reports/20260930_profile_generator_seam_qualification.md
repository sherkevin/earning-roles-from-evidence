# Public profile generator seam qualification — 2026-09-30

## Result

The assignment path now has an explicit, replaceable generator boundary:
eligible public PIPE3 feedback is converted into a typed profile together with
a cost/claim receipt. The qualification implementation is deliberately
deterministic and zero-call; it is scaffolding for a future metered public-only
summarizer, not a profile-quality result.

## Evidence

- Implementation: [`scripts/peerrolebench_profile_generator.py`](../../scripts/peerrolebench_profile_generator.py)
- Qualification: [`scripts/peerrolebench_profile_generator_qualification.py`](../../scripts/peerrolebench_profile_generator_qualification.py)
- Tests: [`tests/test_peerrolebench_profile_generator.py`](../../tests/test_peerrolebench_profile_generator.py)
- Log: `experiments/logs/n03_profile_generator_seam_qualification_20260930_v2/` (v1 retained as the pre-gate-interface attempt)
- Qualification checks: **5 passed**; targeted tests: **3 passed**.
- The run made **0 API calls** and submitted **0 GPU jobs**.

## What is enforced

The generator accepts only the typed public projection and selected-candidate
lineage. It rejects UNKNOWN projections, private/terminal fields, and a
profile for an unselected candidate. The returned profile binds its
`source_input_digest` and `profile_digest`; the receipt records mode, elapsed
time, token counts, cost, API/GPU counts, and `scientific_claim_allowed=false`.

## Boundary

This closes a generator interface and its accounting contract. It does not
implement a live summarizer, prove profile quality, establish later-use
predictiveness, or qualify a baseline. Responsibility eligibility still has to
be supplied by the PIPE3 attribution gate; recipient-owned repairs remain
UNKNOWN and must not reach this profile path.

## Goal reconciliation

The task advances the auditable delivery-to-profile seam in ER-G1 and the cost
recording requirement in ER-G4. It does not satisfy ER-G1's live role-evidence
chain, ER-G2's online-learning requirement, ER-G3's benchmark/baseline freeze,
or ER-G4's real-API scientific evidence gate. The active Goal is unchanged.

## Next gate

Compose actual CPU PIPE3 source/scorer/action/outcome cases with the
responsibility gate, then route only an eligible producer case through this
generator, source-bound offer, isolated public read, versioned selection and
native task start. Keep the recipient-owned control as UNKNOWN. Only after
that zero-call composition is replayable should one bounded real episode be
considered.
