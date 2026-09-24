# Peer-judged role learning: targeted primary-source check

Retrieved 2026-09-23 for the author's correction to Q1. Exact saved bytes and
SHA256 values are in `sources.json`. This is a proximity check, not an exhaustive
novelty or venue-status claim.

- `cadmas_ctx_v1.html`: [CADMAS-CTX](https://arxiv.org/html/2604.17950v1)
  (2026 preprint) already maintains local, context-conditioned posteriors about
  peers and routes with uncertainty. Its §3.6 updates from a fixed judge/task
  verifier's binary outcome. It is a strong comparator to binary acceptance
  learning; it does not automatically answer whether *the actual downstream
  consumer's use and rework* should update a judged agent's role state.
- `repunet_v3.html`: [RepuNet](https://arxiv.org/html/2505.05029v3)
  (AAMAS 2026 paper) already updates self/peer reputation from encounters and
  changes network ties. Its experiments study cooperation in social dilemmas,
  not the correctness of dependent task artifacts; this is a scope distinction,
  not evidence of a new algorithm here.
- `c3_v2.html`: [C3, Exact Is Easier](https://arxiv.org/html/2603.06859v2)
  explicitly uses sound-upstream/error-downstream as its §2.2 example of why a
  terminal failure cannot penalize both agents equally. It supplies a
  fixed-history, per-decision counterfactual method and in §7 names post-hoc
  responsibility and capability diagnosis as applications. Therefore
  "do not blame the producer for a consumer-only failure" is prior art, not
  a new credit-assignment claim. Its exact-restoration premise is a complete
  observable text state; a stateful external tool world may require world
  snapshots or costly replays, but this does not establish superiority for an
  observational method.
- `sero_v1.html`: [Sero](https://arxiv.org/html/2605.28433v1)
  already combines role credit, periodic leave-one-out evaluation, historical
  EMA, credit-guided retrieval/routing and contract-preserving role edits.
  Generic "credit changes roles" is therefore also insufficient.
- [Learning Task-Specific Trust Decisions](https://www.ifaamas.org/Proceedings/aamas2008/proceedings/mainTrackPapers.htm)
  appears in the official AAMAS 2008 proceedings; a full-paper URL timed out and
  the alternative PDF returned HTTP 404, so no local full text is claimed.

Existing project caches already include Meta-Team and SkillMAS. In particular,
generic teammate feedback and reputation cannot be claimed as new. What remains
to design and test is a concrete, calibrated consumer-judgment-to-role update
with fair same-information trust/bandit comparisons.

The cached [Meta-Team primary text](../acquisition_followup_20260922/metateam_v1.html)
is especially close: its agent-level update asks how an agent's outputs affected
downstream execution; its interaction-level update revises teammate profiles;
its team-level update can change roles and organization. The original EDO idea's
peer judgments, role profiles and co-evolution are therefore insufficient as a
novelty claim by themselves. A new proposal must identify a narrower executable
operator and test it against a faithful Meta-Team-style alternative where feasible.
The [novelty-boundary note](../../../docs/scientist/analysis/AAMAS_PEER_JUDGMENT_NOVELTY_BOUNDARY_20260923.md)
records the narrower, still-unproven candidate and the corresponding comparisons.
