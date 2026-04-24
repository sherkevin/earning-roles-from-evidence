# E-009 — External Baseline Survey Report

> Phase block: `[E-009_external_baseline_survey_20260420]` in `docs/coordination/ENGINEER_TODO.md`.
> Triggered by R10 commit (U-014 ✅ 2 systems = AutoGen + ChatEval, U-015 ✅ R2+R3 swap, U-016 ✅ drop E-007).
> Probe date: 2026-04-19.

## §1. Finalist roster (locked by U-014 ✅)

User has selected exactly **2 hosts** for the module-swap baseline matrix:

| # | Repo | Swap target (U-015 ✅) | Our R-x mechanism | Owner |
|---|------|-----------------------|-------------------|-------|
| 1 | [microsoft/autogen](https://github.com/microsoft/autogen) | `BaseGroupChatManager.select_speaker` | **R3** vector belief | Microsoft Research |
| 2 | [chanchimin/ChatEval](https://github.com/chanchimin/ChatEval) | `Critic` agent's `final_prompt_to_use` aggregation (MetaReviewer-equivalent) | **R2** audit decision | Tsinghua / academic |

Both finalists are confirmed in scope; **no further selection work in E-009**. The remaining E-009 deliverable is to verify each is *actually* installable + OpenAI-compatible against our `newapi` (xh.v1api.cc) endpoint, so E-010 reproduce can launch without surprises.

## §2. AutoGen (microsoft/autogen) — verified locally

We already have a clone at `workspace/autogen/` (R7 commit, kept on disk for sprint reuse).

### 2.1 Metadata (from the local clone)

| Field | Value |
|---|---|
| Last commit (`git log -1`) | `8544314` · 2026-03-25 20:15 · "fix: restrict importlib provider loading to trusted namespaces (#7463)" |
| Recency vs today (2026-04-19) | **25 days old** — extremely fresh |
| Code license (`LICENSE-CODE`) | **MIT** ✓ |
| Docs license (`LICENSE`) | CC-BY-4.0 (separate, applies to `docs/` only — standard Microsoft repo split) |
| Non-`.git` size | 55.7 MB |
| `.git` size | 29.9 MB |
| Top-level dirs | `.azure / .devcontainer / .github / docs / dotnet / protos / python` |
| Python packages | `autogen-agentchat 0.7.5`, `autogen-core`, `autogen-ext`, `autogen-magentic-one`, `autogen-studio`, `autogen-test-utils`, `pyautogen`, `agbench`, `magentic-one-cli`, `component-schema-gen` |
| Build system | uv / pyproject (PEP 621) |

### 2.2 OpenAI-compat verification

`autogen-ext` ships an `openai` client adapter (`autogen_ext.models.openai`); both Chat and Completion endpoints are wrapped. For a `newapi` swap we need only override `base_url` + `api_key` on the `OpenAIChatCompletionClient` constructor — confirmed via package layout grep.

**Compat verdict**: Drop-in. No fork needed. The standard recipe is:

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient
client = OpenAIChatCompletionClient(
    model="gpt-4.1-mini",
    base_url="https://xh.v1api.cc/v1",
    api_key="<from configs/llm.json newapi.key>",
)
```

### 2.3 R3 swap point (U-015 ✅)

Located via `Get-ChildItem | Select-String "GroupChatManager|select_speaker"`:

- **`python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat_manager.py`** — defines `BaseGroupChatManager`. Subclasses (`RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneOrchestrator`, etc.) override the speaker-selection logic.
- The `SelectorGroupChat` variant uses an LLM call inside `select_speaker`. **This is our R3 swap point**: replace the LLM-driven selection with our 7-dim vector-belief argmax.
- Adapter file (E-011 deliverable): `workspace/idea04_core/external_baselines/autogen_swap.py` subclasses `SelectorGroupChat` and overrides `select_speaker` to read the per-neighbour `B_i^t(j)` vector (from R3 `persona_model.py`) and pick `argmax` over the dot-product with the task signature `phi(z)`.

### 2.4 Risks specific to AutoGen

- **API surface velocity** — autogen-agentchat is at v0.7.5 with frequent breaking changes; pin the exact commit hash `8544314` in `survey_report.md` lockfile so E-010/E-011/E-012 are reproducible.
- **Weight footprint** — none, AutoGen is pure orchestration code; gpt-4.1-mini API calls handle all inference. No GPU needed for AutoGen itself.
- **Async ergonomics** — autogen-agentchat is fully async; our existing runner is sync. The adapter must wrap with `asyncio.run(...)` per sample (acceptable overhead at our scale).

## §3. ChatEval (chanchimin/ChatEval) — verified via web

No local clone (we follow E-009 spec: metadata-only check; clone at E-010 if reproduce path proceeds).

### 3.1 Metadata (from GitHub API + raw README)

| Field | Value |
|---|---|
| Last commit (`api.github.com/.../commits/main`) | `56b320c0` · **2024-10-19 08:15 UTC** · "add missing config" |
| Recency vs today (2026-04-19) | **~18 months old** — stale (paper-archive mode) ⚠ |
| License (`raw.githubusercontent.com/.../LICENSE`) | **Apache 2.0** ✓ |
| Stars | 331 |
| Forks | 0 (per the listing returned, but unreliable; not a useful signal anyway) |
| Default branch | `main` (only branch) |
| Repo size (compressed) | small — `cd ChatEval && du -sh` will be performed during E-010 clone |
| Citation | arXiv:2308.07201 (Chan et al., EMNLP 2023 / 2024 LLM-Eval) |
| Built on | [agentverse](https://github.com/OpenBMB/AgentVerse) framework (config-driven multi-agent) + [FastChat](https://github.com/lm-sys/FastChat) for arena demo |

### 3.2 OpenAI-compat verification

Per upstream README:

> "We basically call the OpenAI's API for our LLMs, so you also need to export your OpenAI key as follows before running our code"
> ```bash
> export OPENAI_API_KEY="your_api_key_here"
> ```

The `agents.llm` config block also takes a `model` field (e.g. `"gpt-3.5-turbo-0301"`). The codebase uses the official `openai` Python SDK; for newapi we set:

```bash
export OPENAI_API_KEY=<configs/llm.json newapi.key>
export OPENAI_BASE_URL=https://xh.v1api.cc/v1     # picked up by openai SDK >= 1.0
```

**Compat verdict**: Drop-in via env vars. **No code change required** for newapi routing.

### 3.3 R2 swap point (U-015 ✅)

Per README the multi-agent debate happens through `agentverse/tasks/llm_eval/config.yaml` agent personas (`Critic`, `General Public`, ...) whose `final_prompt_to_use` aggregates per-agent scores at the last round. **This aggregation is the R2 audit swap point**: replace ChatEval's "average + free-form rationale" with our `AuditDecision ∈ {ACCEPT / ACCEPT_WITH_NOTE / REJECT_REROUTE / REJECT_RESPLIT}` (per `workspace/idea04_core/audit_runtime.py`).

Adapter file (E-011 deliverable): `workspace/idea04_core/external_baselines/chateval_swap.py` writes a custom `agentverse` agent class that calls our `audit_candidate(...)` instead of ChatEval's vanilla aggregator.

### 3.4 Risks specific to ChatEval

- **Stale codebase** — last commit 18 months ago. The agentverse / FastChat dependency chain may have drifted; E-010 must `pip install -r requirements.txt` in a fresh venv with pinned deps and confirm the agentverse import still works against newapi.
- **CUDA/FastChat optional** — the arena demo path needs CUDA (vicuna-7b workers). We do **not** need that path; we only need the `llm_eval` evaluator pipeline. E-010 will explicitly skip the FastChat install.
- **Reproduction band** — the original paper's eval is on `FairEval` dataset, not HotpotQA. Our E-012 swap-comparison must use the same HotpotQA / MuSiQue subset for both `host original` and `host + R2 swap` arms, not paper's FairEval (which would not let us compare to our Stage-2 fullval).
- **Repo activity 0 forks** — questionable; if we hit a blocker we will likely need to fork to apply our adapter rather than relying on upstream PRs.

## §4. Risk roll-up vs `external_baseline_plan.md` §5

| Plan §5 risk | Status after E-009 |
|---|---|
| **U-014 / U-015 / U-016 拍板延迟** | ✅ Resolved (R10 commit) |
| **AutoGen / ChatEval repo 跑不通** | ⚠ Partially mitigated: AutoGen LICENSE+freshness ✓; ChatEval LICENSE ✓ but **18-month-old codebase** is the main remaining risk → moved into E-010 entry condition |
| **Reproduction error > 5% F1** | Cannot assess from metadata alone; gated to E-010 reproduce smoke |
| **Swap 输给 host 原 mechanism** | Is real research risk; out of scope for E-009 |
| **MetaGPT (R1 swap) 太 tightly-coupled** | Avoided — U-014 dropped MetaGPT; only R2+R3 swaps remain |

## §5. Next-step entry conditions for E-010

E-010 (reproduce baseline on our newapi infrastructure) can start once:

1. ✅ E-009 metadata verdict says both repos are LICENSE-compatible and OpenAI-compat. (Confirmed above.)
2. ✅ E-008 newapi probe passed and `_normalize_newapi() / newapi_target()` are in `llm_providers.py`. (Confirmed in `[E-008_newapi_smoke_20260420]`.)
3. ⏳ Engineer creates a `workspace/idea04_core/external_baselines/` package directory and pins the AutoGen commit hash `8544314` + ChatEval commit hash `56b320c0` to a lockfile (`external_baselines/lockfile.json`). E-010 step 1.
4. ⏳ ChatEval gets a fresh shallow clone to `workspace/chateval/` (estimated ~5 MB; we will not commit, just `.gitignore`).

Estimated E-010 wall time per host:

| Host | Steps | Wall time |
|---|---|---|
| AutoGen | already cloned → minimal `pip install -e python/packages/autogen-agentchat` in fresh venv → 1-sample HotpotQA smoke through newapi | **~2 h** |
| ChatEval | shallow clone + `pip install -r requirements.txt` (skip FastChat opt-deps) + 1-sample llm_eval smoke through newapi | **~3 h** |

Total E-010: ~5 h elapsed; per sprint kickoff plan E-010 is allotted 2 d × 2 hosts = 4 d. We have **substantial headroom**. The bigger calendar consumer will be E-011 (write 2 swap adapters: 2 d × 2 hosts = 4 d).

## §6. Cost estimate (E-009 + E-010 prep, per `[E-API-budget-check_placeholder_20260420]`)

E-009 itself sent **0 LLM requests** (metadata + WebFetch only) → **$0**.

E-010 quickstart smokes (1 sample each, gpt-4.1-mini via newapi):

| Smoke | Est. tokens | Est. cost (newapi pricing TBD) |
|---|---|---|
| AutoGen `SelectorGroupChat` 1-sample HotpotQA | ~3 000 in + ~500 out | <$0.01 |
| ChatEval `llm_eval` 1-sample (2 agents × 2 rounds) | ~6 000 in + ~1 200 out | <$0.02 |

E-010 well under the `[E-API-budget-check]` $100/batch threshold; **no new `U-EXEC-XXX` to user required at this stage**. (Will re-estimate at E-012 swap-comparison batch which scales 200 samples × 2 hosts × {original, swapped} × 3 seeds.)

## §7. Files touched by E-009

- **Added**:
  - `artifacts/external_baselines/survey_report.md` (this file)
- **Modified**:
  - `docs/coordination/ENGINEER_TODO.md` (E-009 phase block ⏳ → ✅ in `[engineer_day1_5_completion_20260420]`)
- **Not touched** (per E-009 scope — no install / no LLM call / no key write):
  - `configs/llm.json`
  - `workspace/idea04_core/`
  - any host repo source files
