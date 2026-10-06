# Task report — independent review of C1 v4 and next-card design

Date: 2026-10-06
Status: `BLOCKED_BY_EVIDENCE`
Goal change requested: `false`

An independent read-only Codex `gpt-6-sol` reviewer inspected the v4 summary, active method, and
benchmark contract. It confirmed that the structural-owner gate obeyed ADR 0047: recipient-owned
`processor.py` modification could not become producer evidence, while noisy judged-role text alone
did not censor a registered producer-owned event.

The reviewer identified the decisive remaining issue: the contextual arm stopped before target
assignment/outcome, so complete-case comparison would introduce arm-specific selection bias. The
source gate status `PENDING_ATTRIBUTION` is a determinate structural stop and must be separated from
transport or missing-evidence `UNKNOWN` in future accounting. ITT, gate-stop, and eligible-conditional
denominators must be reported independently.

The next candidate is documented in
[`c1_shared_source_card_v0.1_20261006.md`](../../research/candidates/c1_shared_source_card_v0.1_20261006.md).
It reuses one real, immutable source receipt across independent policy states, then runs independent
target assignments/outcomes. It remains a development-only identification card, not the final
independent-history scientific comparison. Before execution it still requires sidecar/native-selection
binding, full costs, explicit denominators, and a frozen bounded card. No extra API/GPU run occurred
in this review, and no result cell was filled.
