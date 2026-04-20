# E-010 ChatEval adapter inspection (R41 engineer MCP-3)

**When**: 2026-04-20 R41 engineer session (MCP-3).
**Who**: engineer.
**Intent**: Per `implementation_log.md [external_baseline_decisions_landed_20260420]` E-010 ticket, inspect the ChatEval repo at `external_baselines/chateval/` on server and produce an adapter spec that makes it runnable on our HotpotQA seed data, with the SWAP-3 (R2 audit → MetaReviewer) integration point identified.

## 1. Upstream repo layout (observed on server)

Location: `/media/data3/dengkw/idea04/external_baselines/chateval/`.

```
chateval/
├── llm_eval.py                # 主入口 (80 samples from FairEval by default)
├── agentverse/                # 多 agent 调度框架（内嵌复制自 AgentVerse repo）
│   ├── agentverse.py          # AgentVerse.from_task(config) 入口类
│   ├── agents/                # Agent 基类 + LLM-eval-multi variant
│   ├── environments/
│   │   ├── base.py
│   │   ├── basic.py
│   │   ├── llm_eval.py        # ⭐ 多 agent "referee" 辩论 environment（核心）
│   │   └── rules/
│   ├── llms/
│   │   ├── base.py
│   │   ├── openai.py          # ⭐ OpenAI wiring (需改 → newapi)
│   │   └── __init__.py
│   ├── tasks/
│   │   ├── config.yaml        # FairEval pair-compare config (4-turn sequential debate)
│   │   └── llm_eval/
│   │       ├── config.yaml
│   │       └── data/faireval/preprocessed_data/test.json
│   └── memory/                # 消息/memory manipulator
├── FastChat/                  # 子模块（vLLM-serve 开源模型时用；newapi 可跳过）
├── eval_helper/get_evaluation.py  # referee 们 chat 完后抽 Assistant 1/2 分数的 parser
├── calc_adversarial_results_calc_score_calibration.py  # 评估收尾脚本
├── venv_chateval/             # 已 install 好的 virtualenv（R38 R2 setup）
└── requirements.txt + setup.py + README.md
```

**Key observation**: ChatEval's canonical task is **pair-comparison** (FairEval / AdvBench): given a question + two candidate responses, N referee agents (General Public / Critic / Psychologist / News Editor / ...) 轮流辩论并打分 → final 聚合打分。**它不是一个直接解答 HotpotQA 的 QA 系统**。

## 2. LLM call pattern

`agentverse/llms/openai.py` uses the legacy OpenAI 1.x SDK. The entry `llm_eval.py` hardcodes `os.environ["OPENAI_API_KEY"]` + `os.environ["OPENAI_BASE_URL"]` at the top (currently `***` placeholder).

**Newapi wiring** (engineer next step):
```python
os.environ["OPENAI_API_KEY"] = "<newapi key from configs/llm.json>"
os.environ["OPENAI_BASE_URL"] = "https://xh.v1api.cc/v1"
# + edit model name in config.yaml from "gpt-3.5-turbo" → "gpt-4.1-mini"
```
No code-level refactor of `openai.py` expected — modern `openai-python` respects `OPENAI_BASE_URL` env var out of the box.

## 3. SWAP-3 integration point (per `docs/paper/external_baseline_plan.md §2-§4`)

The SWAP-3 design is "R2 audit → ChatEval MetaReviewer". Issue discovered during inspection:

- **There is no class literally named `MetaReviewer` in the repo.** `grep -rn 'MetaReviewer\|meta_reviewer\|MetaAgent' --include='*.py'` returns 0 hits.
- The closest semantic match is the "referee aggregation" step in `eval_helper/get_evaluation.py` — given N referees' chat logs, extract Assistant 1 / Assistant 2 numerical scores and average them.
- The final-judgement logic actually lives inside `agentverse/environments/llm_eval.py` + `agents/llm_eval_multi.py` (not read yet; next session should dump these two files).

**Reinterpretation of SWAP-3**: Instead of substituting a class literally called `MetaReviewer`, SWAP-3 should replace the **final-round referee aggregator** (the per-agent-score mean + parity check) with TCPB's **R2 `audit_runtime`** decision (pass / reject_reroute / resplit / accept). Concretely:

| ChatEval native flow | SWAP-3 replacement |
|---|---|
| N referees debate 4 turns | keep (unchanged) |
| `get_evaluation(setting='every_agent', messages=..., agent_nums=N)` extracts per-referee scores | **replace** with TCPB's `audit_runtime.audit_answer(...)` evaluating the referee debate transcript as "hop evidence" |
| Mean over agents + parity check | **replace** with TCPB's `audit_decision` (pass / reject_reroute / resplit / accept) + ChainSolver feedback loop |

Net effect: ChatEval becomes the "multi-persona evidence-gathering stage" and TCPB's `audit_runtime` becomes the "hop-level verifier gate". This matches the scientist's SWAP-3 narrative in `external_baseline_plan.md` more faithfully than a literal class swap would.

## 4. HotpotQA adapter strategy

Since ChatEval is natively pair-compare, running it on HotpotQA (single-answer QA) requires either:

### Option A — convert HotpotQA into pair-compare task (fastest, closest to ChatEval's DNA)
1. For each HotpotQA sample, first generate **two** candidate answers via two different TCPB agents (or one TCPB + one single-agent baseline).
2. Run ChatEval's multi-referee debate to pick the "better" answer.
3. Score: EM / F1 of the winning answer vs gold.
- **Pro**: zero upstream changes; just drive `llm_eval.py` with a synthetic FairEval-shaped JSON.
- **Con**: twice the LLM cost (two candidates); comparison frame is unnatural for QA.

### Option B — repurpose as multi-agent QA (closer to MAD pattern, overlap risk)
1. Rewrite `agentverse/tasks/config.yaml` so agents are "Decomposer / EvidenceSeeker / Verifier / Synthesizer" (match TCPB chain roles).
2. Change prompt templates: instead of "compare two assistants", ask each agent to contribute to answering the HotpotQA question.
3. After N debate turns, `get_evaluation` extracts the consensus answer.
- **Pro**: produces a fair comparison "ChatEval-as-multi-agent-QA" vs TCPB.
- **Con**: moderate upstream edit (config.yaml + prompt templates); starts overlapping with MAD (already covered by SWAP-4 under U-018).

**Engineer recommendation (for scientist approval)**: **Option A** is the right fit because:
- It preserves ChatEval's native task type (pair-compare), avoiding the concern that we're shoehorning it into QA.
- The two-candidate generation can reuse TCPB runs we already have (stage1 vs stage2 answers from E-017) — zero extra LLM cost for the candidates.
- SWAP-3 then becomes a clean "swap the `get_evaluation` aggregator for `audit_runtime.audit_answer`" ablation; the debate mechanism itself stays upstream-authentic.
- Writes up naturally as "When using ChatEval as the pair-compare judge over {stage1, stage2} candidates, auditing the debate with our R2 verifier (SWAP-3) recovers X% of debates where naive aggregator chose the wrong answer".

## 5. Smoke-probe recipe (for E-010 step 1-3, post-E-017 window)

Before committing to Option A vs B, a ≤ 20-sample smoke probe is strongly recommended (per §6.1.3 of `four-role-todo-workflow.mdc`, also satisfies `< 100 call` = pre-flight probe optional). Minimum script outline:

```bash
# server-side
cd /media/data3/dengkw/idea04/external_baselines/chateval
source venv_chateval/bin/activate
# 1) Patch llm_eval.py:
#    - set OPENAI_API_KEY = newapi key
#    - set OPENAI_BASE_URL = https://xh.v1api.cc/v1
#    - edit loop bound: `data[:80]` → `data[:5]`
# 2) Patch agentverse/tasks/llm_eval/config.yaml:
#    - model: gpt-3.5-turbo → gpt-4.1-mini
# 3) Run:
bash workspace/tmp/newapi_quota_probe.sh   # STATUS: ACTIVE
python llm_eval.py --config agentverse/tasks/llm_eval/config.yaml
# 4) Inspect outputs/.../pair_comparison_results.json
```

Expected total cost ≈ $0.20 (5 samples × 4 turns × 3 agents × ~500 tokens input / 200 output / sample × 4.0e-7 input + 1.6e-6 output = ~$0.20 upper bound).

## 6. Holding pattern + blockers

- **Not launched yet**: E-010 step 2-4 (smoke + patched run + SWAP-3 integration) wait for E-017 seed=42 to complete (~2h more at current rate). Running alongside would push the server past the observed "≤ 2 newapi batches × 8 workers" rate-limit envelope (see `[u_rollback_001_path_a_landed_20260420]` operational corollary).
- **Adapter code not written yet**: engineer writes `external_baselines/chateval/run_chateval_hotpotqa.py` (Option A thin wrapper) in the next session window that opens after seed=42 done.
- **Blocker on SWAP-3 design sign-off**: scientist should confirm Option A vs B (see §4). Per `four-role-todo-workflow.mdc §4`, this is a *structural* choice — file it as `U-XXX-decide` if scientist does not have standing authority from `external_baseline_plan.md`. Current `external_baseline_plan.md §3.3` names "MetaReviewer" without specifying adapter; Option A is a minor design-refinement within scientist authority.

## 7. Cross-references

- `implementation_log.md` [external_baseline_decisions_landed_20260420] — E-010 original dispatch
- `implementation_log.md` [E-017_migration_landed_ack_20260420] — round-2 setup that cloned ChatEval + built venv
- `docs/paper/external_baseline_plan.md` §ChatEval / SWAP-3 — scientist's SWAP-3 narrative
- `external_baselines/chateval/llm_eval.py` — entry point (80-sample loop)
- `external_baselines/chateval/agentverse/tasks/config.yaml` + `tasks/llm_eval/config.yaml` — debate config (referees, turns, prompts)
- `external_baselines/chateval/eval_helper/get_evaluation.py` — referee aggregator (SWAP-3 replacement target)
- `external_baselines/chateval/venv_chateval/` — pre-built server venv (langchain 1.2.15 + openai 2.32.0)

## 8. Hand-off checklist

- [ ] Scientist signs off Option A vs B (default: Option A per engineer rec).
- [ ] When E-017 seed=42 both batches done (~23:10-00:54 server time) + scheduler enters seed=43 launch, engineer launches the 5-sample smoke from §5.
- [ ] Write `external_baselines/chateval/run_chateval_hotpotqa.py` Option A thin wrapper (~2h engineering, no LLM cost).
- [ ] Dispatch E-011 (ChatEval + SWAP-3 audit-runtime replacement) after smoke passes.
