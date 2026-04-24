# E-018 ReAgent adapter inspection (R41 engineer MCP-3)

**When**: 2026-04-20 R41 engineer session (MCP-3).
**Who**: engineer.
**Intent**: Per `ENGINEER_TODO.md [sota_full_system_workstream_20260420]` E-018 ticket (Axis A Tier-1: MA-RAG + ReAgent), inspect the ReAgent repo at `external_baselines/reagent/` on server and produce an adapter spec so the next engineer session can write `run_reagent_hotpotqa.py` without repeating the discovery work.

**Status of the sibling Axis A finalist**: MA-RAG adapter (`external_baselines/marag/run_marag_hotpotqa.py`, Path A gold-context) is already written (R2) + smoke-probed in R41 (see `[e_015_e_018_smoke_parallel_launch_20260420]`). ReAgent is the only Axis A system that still lacks a smoke adapter; this doc closes that gap as pure analysis (no LLM / no code execution in this session).

## 1. Upstream repo layout (observed on server)

Location: `/media/data3/dengkw/idea04/external_baselines/reagent/`.

```
reagent/
├── main.py                      # top-level wiring: dataset → agents → Moderator → run
├── Agent/
│   ├── agent.py                 # BaseAgent / Agent classes
│   ├── moderator.py             # simple moderator (baseline reasoning loop)
│   ├── moderator2.py            # advanced moderator ⭐ (with voting + human/blacksheep)
│   ├── thinker.py               # optional reflection agent
│   ├── blacksheep.py            # optional adversarial agent
│   └── human.py                 # optional interactive intervention agent
├── Environment/
│   ├── environment.py           # base env
│   └── groupchat.py             # GroupChatEnvironment (multi-agent concurrency)
├── Interaction/messagepool.py   # shared message bus
├── DataProcess/
│   ├── Dataset.py               # HotpotqaDataset (loads JSON → list of HotpotQA objs)
│   ├── Hotpotqa.py              # HotpotQA class (per-sample wrapper)
│   └── Document.py              # Document class (title + context paragraphs)
├── backend/
│   └── api.py                   # ⭐ OpenAI/Azure wiring, services dict (api_key + base_url)
├── venv_reagent/                # pre-built venv (openai + pandas + pyyaml + tqdm)
├── main.py / README.md          # usage docs
└── .git/                        # upstream commit @ 2026-04-19 23:04 clone
```

## 2. Native data schema (what ReAgent expects)

Each HotpotQA sample in ReAgent's expected JSON must include:

| field | type | our seed field | notes |
|---|---|---|---|
| `_id` | str | derivable from `task_id` | ReAgent uses it as primary key |
| `type` | str | missing | HotpotQA has `bridge` / `comparison`; our seeds stripped it; we can default `"bridge"` |
| `level` | str | missing | `easy` / `medium` / `hard`; can default `"medium"` |
| `question` | str | `question` | ✓ 1:1 |
| `answer` | str | `answer` | ✓ 1:1 |
| `context` | list[list] | `context_passages: list[str]` | ⚠ shape mismatch (see §3) |
| `supporting_facts` | list[list] | `supporting_facts` (sometimes) | optional, can default `[]` |

Our seed schema (from `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl`):
```json
{
  "task_id": "hotpotqa-0000",
  "question": "Were Scott Derrickson and Ed Wood of the same nationality?",
  "answer": "yes",
  "context_passages": [
    "[Ed Wood (film)] Ed Wood is a 1994 American biographical period ...",
    "[Scott Derrickson] ... "
  ]
}
```

ReAgent's native schema expects the nested-list form:
```json
{
  "_id": "hotpotqa-0000",
  "type": "comparison",
  "level": "medium",
  "question": "Were Scott Derrickson and Ed Wood of the same nationality?",
  "answer": "yes",
  "context": [
    ["Ed Wood (film)", ["Ed Wood is a 1994 American biographical ...", "..."]],
    ["Scott Derrickson", ["Scott Derrickson is an American ...", "..."]]
  ],
  "supporting_facts": [["Ed Wood (film)", 0], ["Scott Derrickson", 1]]
}
```

## 3. Schema conversion rules (for `seed → reagent.json` adapter)

Each `context_passages` entry in our seed is a single-string `"[Title] Paragraph1.  Paragraph2.  ..."`. To match ReAgent's list-of-[title, list-of-sentences]:

1. **Title extraction**: regex `^\[([^\]]+)\]\s*(.*)$` on each passage string. The leading `[...]` is the title; the remainder is the paragraph body.
2. **Paragraph splitting**: split paragraph body on regex `\.\s{2,}` (two-or-more spaces after a full stop — matches HotpotQA's canonical raw dump). Fall back to `.split(". ")` if no double-space matches.
3. **Supporting facts**: default to `[]`; ReAgent's `Moderator2` doesn't strictly require them (only `Verifier` cross-checks when present).
4. **`_id`**: use our `task_id` verbatim (string form is fine for ReAgent).
5. **`type`, `level`**: default `"bridge"` / `"medium"` (safe because `main.py`'s code path only uses them in logging, not in reasoning decisions).

## 4. LLM wiring (services.yaml pattern)

ReAgent's `backend/api.py` reads from a `services.yaml` file with this shape (inferred from `api_call()` at line 82-96):

```yaml
services:
  openai:
    api_key: "<newapi key from configs/llm.json>"
    base_url: "https://xh.v1api.cc/v1"
  # qwen / deepseek / claude blocks: unused for E-018 smoke, can be stubs
```

Plus set `args.model = "gpt-4.1-mini"` (not the default `deepseek-chat`). One-line change in `Args` in `main.py`.

**Pinned caution for engineer**: `api_call()` in `backend/api.py` line 96+ builds `OpenAI(base_url=..., api_key=...)` from services dict per-call. **Fresh-install `openai>=1.0` respects base_url out of the box** — no `openai.api_base` legacy shim needed (unlike MAD which uses the 0.27.6 legacy API and needs `openai_compat_shim.py`).

## 5. Recommended thin wrapper — `external_baselines/reagent/run_reagent_hotpotqa.py`

Estimated size: ~220 lines. Estimated engineering time: 2-3 h (mostly schema-conversion + output parsing).

```python
"""ReAgent HotpotQA adapter — thin wrapper around Moderator2, our seed JSONL.

Implements §2-§3 schema conversion so we can reuse our canonical 200-sample
HotpotQA seed without modifying ReAgent's upstream DataProcess code. Writes
results to ``--out-dir`` in a minimal ``predictions.jsonl`` + ``metrics.json``
pair compatible with our ``workspace/idea04_core/evaluation.py``.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "workspace"))
sys.path.insert(0, str(_REPO_ROOT / "external_baselines/reagent"))

from idea04_core.evaluation import exact_match, token_f1   # noqa: E402

# ReAgent imports must come AFTER services.yaml is written.
# (See step 1 in main()).

def _convert_sample_to_reagent_schema(seed_row: dict) -> dict:
    """§3 §2 — our raw_inputs row → ReAgent native schema."""
    title_re = re.compile(r"^\[([^\]]+)\]\s*(.*)$", re.DOTALL)
    ctx: list[list] = []
    for passage in seed_row.get("context_passages", []):
        m = title_re.match(passage)
        if m:
            title, body = m.group(1).strip(), m.group(2)
        else:
            title, body = "UnknownTitle", passage
        sentences = re.split(r"\.\s{2,}", body)
        sentences = [s.strip() + ("." if not s.endswith(".") else "") for s in sentences if s.strip()]
        ctx.append([title, sentences])
    return {
        "_id": seed_row["task_id"],
        "type": "bridge",         # safe default
        "level": "medium",        # safe default
        "question": seed_row["question"],
        "answer": seed_row.get("answer", ""),
        "context": ctx,
        "supporting_facts": seed_row.get("supporting_facts", []),
    }


def _write_services_yaml(path: Path, llm_json_path: Path) -> None:
    """Generate services.yaml from configs/llm.json newapi block."""
    cfg = json.loads(llm_json_path.read_text(encoding="utf-8"))
    nb = cfg.get("newapi") or cfg.get("providers", {}).get("newapi", {})
    services = {
        "services": {
            "openai": {"api_key": nb["key"], "base_url": nb["url"].rstrip("/")},
            "qwen":   {"api_key": "stub", "base_url": "https://stub.invalid"},
            "deepseek": {"api_key": "stub", "base_url": "https://stub.invalid"},
            "claude": {"api_key": "stub", "base_url": "https://stub.invalid"},
        }
    }
    import yaml
    path.write_text(yaml.safe_dump(services, sort_keys=False), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--samples-jsonl", required=True)
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--model", default="gpt-4.1-mini")
    p.add_argument("--llm-json", default=str(_REPO_ROOT / "configs/llm.json"))
    p.add_argument("--skip-preflight", action="store_true")
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pre-flight quota probe (same pattern as run_e017_fullval_seed.py per E-020.3)
    if not args.skip_preflight:
        probe = _REPO_ROOT / "workspace/tmp/newapi_quota_probe.sh"
        if probe.is_file():
            r = subprocess.run(["bash", str(probe)], capture_output=True, text=True, timeout=30)
            if "newapi ACTIVE" not in r.stdout:
                print(f"[reagent_hotpotqa] pre-flight failed: {r.stdout[-200:]}", file=sys.stderr)
                sys.exit(2)

    # Write services.yaml BEFORE importing ReAgent modules (they read at import time)
    services_yaml = _REPO_ROOT / "external_baselines/reagent/services.yaml"
    _write_services_yaml(services_yaml, Path(args.llm_json))

    # Load + convert seed data
    rows = []
    with Path(args.samples_jsonl).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
            if len(rows) >= args.n:
                break
    reagent_data = [_convert_sample_to_reagent_schema(r) for r in rows]
    tmp_json = out_dir / "reagent_input.json"
    tmp_json.write_text(json.dumps(reagent_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Now import ReAgent modules (requires services.yaml to exist)
    from Agent.moderator2 import Moderator2           # noqa: E402
    from Environment.groupchat import GroupChatEnvironment  # noqa: E402
    from DataProcess.Dataset import HotpotqaDataset   # noqa: E402
    from main import build_agents, Args               # noqa: E402

    rag_args = Args()
    rag_args.model = args.model
    rag_args.dataset_path = str(tmp_json)
    dataset = HotpotqaDataset(dataset_path=str(tmp_json))

    env = GroupChatEnvironment(agents=build_agents(rag_args))
    moderator = Moderator2(name="R41Mod", model=args.model, args=rag_args, group=env)

    preds = []
    t0 = time.time()
    for i, task in enumerate(dataset.tasks):
        result = moderator.run(task)  # returns a dict containing final_answer + trace
        final = result.get("final_answer") or result.get("answer") or ""
        em = exact_match(final, task.answer)
        f1 = token_f1(final, task.answer)
        pred = {"task_id": task.id, "question": task.question,
                "gold_answer": task.answer, "final_answer": final,
                "answer_em": em, "answer_f1": f1,
                "partial_F1_running": None}
        preds.append(pred)
        running_f1 = sum(p["answer_f1"] for p in preds) / len(preds)
        preds[-1]["partial_F1_running"] = running_f1
        print(f"[reagent_hotpotqa] {i+1}/{len(dataset.tasks)} partial_F1={running_f1:.4f} partial_EM={sum(p['answer_em'] for p in preds)/len(preds):.4f}")

    # Write outputs
    (out_dir / "predictions.jsonl").write_text(
        "\n".join(json.dumps(p, ensure_ascii=False) for p in preds), encoding="utf-8")
    metrics = {
        "sample_count": len(preds),
        "answer_em": sum(p["answer_em"] for p in preds) / max(1, len(preds)),
        "answer_f1": sum(p["answer_f1"] for p in preds) / max(1, len(preds)),
        "elapsed_s": round(time.time() - t0, 1),
        "model": args.model,
        "system": "reagent_moderator2_r41",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Concerns the engineer must verify when implementing:

1. `Moderator2.run(task)` return shape — the README says it logs final answer; if the attribute is `result.messages[-1]` instead of `result["final_answer"]`, adapt the extraction line.
2. `GroupChatEnvironment` constructor args — may need `message_pool` or other kwargs; check `Environment/groupchat.py`.
3. `Agent/agent.py` `Agent` vs `BaseAgent` choice — `build_agents()` in `main.py` uses `BaseAgent` for the 6 core agents + `Thinker/BlackSheep/Human` for optional; `Moderator2` probably needs the optional ones present to not crash.

## 6. Smoke-probe recipe (for E-018 step 2-3, post-E-017 window)

After the thin wrapper in §5 is written + committed:

```bash
# server-side
cd /media/data3/dengkw/idea04
bash workspace/tmp/newapi_quota_probe.sh    # STATUS: ACTIVE
external_baselines/reagent/venv_reagent/bin/python \
    external_baselines/reagent/run_reagent_hotpotqa.py \
    --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
    --n 5 \
    --out-dir artifacts/external_baselines/reagent/smoke_$(date +%Y%m%d_%H%M%S)/
```

Estimated cost: 5 samples × ~6 agents × ~3 rounds × ~800 tokens/call ≈ 72 K tokens ≈ $0.20 on gpt-4.1-mini.

## 7. Acceptance criteria (when this adapter is "done")

- [ ] `run_reagent_hotpotqa.py` smoke on 5 samples produces `metrics.json` with `"sample_count": 5` + non-empty `"answer_f1"` (≥ 0).
- [ ] Per-sample `partial_F1` trace appears in stdout (monotonic, matches our other adapters' logging style).
- [ ] `validate_logs.py` can ingest the output dir (may require adding a light schema shim since ReAgent's trace format differs from TCPB's).
- [ ] Scientist confirms via `external_baseline_plan.md §Reagent` that this thin-wrapper behavior is the intended comparison (vs a deeper Moderator internals swap).

## 8. Cross-references

- `ENGINEER_TODO.md` [sota_full_system_workstream_20260420] §Axis A — original E-018 dispatch
- `ENGINEER_TODO.md` [E-017_migration_landed_ack_20260420] `##### ReAgent (E-018 candidate)` — R2 setup notes (venv + clone)
- `external_baselines/reagent/main.py` — ReAgent's canonical entry point (don't invoke directly; use the thin wrapper)
- `external_baselines/marag/run_marag_hotpotqa.py` — sibling Axis A adapter (same pattern, already smoke-probed R41)
- `workspace/tmp/newapi_quota_probe.sh` — E-020.3 pre-flight probe (reused)
- `docs/paper/external_baseline_plan.md` §Axis A Tier-1 — Axis-A write-up context

## 9. Blockers

- None on engineering side. Adapter can be written immediately whenever scheduling permits (estimated 2-3h; no LLM cost for the code itself).
- Smoke probe execution is blocked by `safe parallel envelope ≤ 2 newapi batches × 8 workers` rule — can run alongside E-017 seed=43/44 (they are 2 batches) only if smoke uses workers=1 (smoke = 3rd batch, 1 worker = +1 request/3s, within rate limit per R40 observation).

## 10. Engineer-handoff next step (pinned)

When this ticket is opened next, engineer should:
1. Implement the thin wrapper from §5 (expected 2-3h including stub cleanup).
2. Run the smoke from §6 (≤ 10 min + $0.20).
3. Append `[e_018_reagent_smoke_landed_<TS>]` phase block in `ENGINEER_TODO.md` with the metrics + a comparison row vs our stage2 baseline F1 on the same 5 samples.
4. If smoke F1 < 0.4 (flag), investigate before scaling to 50-sample full smoke.


## 11. R41b actual-implementation findings (2026-04-20, engineer MCP-3 this session)

When implementing `run_reagent_hotpotqa.py` per §5 spec, **three upstream bugs** were discovered in the ReAgent clone at `external_baselines/reagent/` that blocked the smoke probe:

### 11.1 `Agent/thinker.py` contains literal Markdown code-fence lines ✅ PATCHED

First and last lines of `Agent/thinker.py` are literal ```` ```python ```` and ```` ``` ```` (upstream mistakenly pasted Markdown code-fence markers into a `.py` file). Python parser raises `SyntaxError` on import.

Fix: `workspace/tmp/r41b_fix_thinker.py` strips leading + trailing fences. Applied to server at `/media/data3/dengkw/idea04/external_baselines/reagent/Agent/thinker.py` (backup at `thinker.py.orig`). Original: 136 lines; after strip: 134 lines. **Re-apply on every fresh clone.**

### 11.2 `Agent/agent.py` missing `Agent` class definition ✅ PATCHED

Five modules (`moderator2.py`, `moderator.py`, `blacksheep.py`, `thinker.py`, `human.py`) do `from Agent.agent import Agent` and inherit `(Agent)` with `super().__init__(name=..., model=...)`, but `Agent/agent.py` only defines `BaseAgent`. Upstream bug; likely a file was lost during their ReAgent commit.

Fix: `workspace/tmp/r41b_fix_agent.py` inserts a compatibility `Agent(BaseAgent)` class with `(name, model)` signature + default `vote()` (returns 0) + default `say()` BEFORE the first `class BlackSheep(Agent):` line. Applied to server. **Re-apply on every fresh clone.**

### 11.3 `backend/api.py` + openai 2.32.0 `json_format=True` path raises `'str' object has no attribute 'choices'` ❌ NOT FIXED (blocks smoke)

When `api_call(...json_format=True...)` hits the `response_format={"type":"json_object"}` branch at line 115-126, something inside `client.chat.completions.create(...)` returns a value that doesn't have `.choices`. Log shows the error repeated ×8 per step before moderator2 gives up. All Moderator2 calls go through json_format=True (mandatory for the "step/reasoning/next_action" JSON reasoning protocol).

Observed during R41b pilot (PID 335434 on server, 22:30 CST):
```
[reagent_hotpotqa] pre-flight OK: newapi ACTIVE
Error while calling API: 'str' object has no attribute 'choices'
Error while calling API: 'str' object has no attribute 'choices'
Error while calling API: 'str' object has no attribute 'choices'
...
```

Hypotheses (to test next session):
- (H1) newapi endpoint returns non-standard response format for `response_format={"type":"json_object"}` (some proxies re-stringify the message field).
- (H2) openai library 2.32.0 made a breaking change to `chat.completions.create` return shape for structured-output mode.
- (H3) ReAgent's `api_call()` at line 115 has a subtle bug where `stream=stream` (default False) interacts badly with `response_format`.

**Workaround candidates**:
- (W1) Patch `api_call` to fall back to non-json-format + `json.loads(response.choices[0].message.content)` ourselves. Minimal invasive; 10 lines edit.
- (W2) Pin `openai==1.50` (pre-2.x break) in venv_reagent; `pip install 'openai<2' -t venv_reagent/lib`. Requires re-testing compatibility with rest of ReAgent.
- (W3) Replace ReAgent's `api_call` entirely with our `workspace/idea04_core/llm_client.call_llm` — preserves E-020 QuotaExhaustedError protection. ~30 lines wrapper.

**Engineer next-session action**: pilot W1 first (least invasive). If W1 doesn't fix, fall back to W3.

**Impact on R41b pipeline**:
- n=5 ReAgent smoke killed (PID 335434 → SIGTERM at 22:33); quota wasted ~0 (retries caught as exceptions, no successful LLM calls).
- n=50 watcher updated to **skip ReAgent** (only runs MAD n=50 + MA-RAG n=50); see `workspace/tmp/r41b_n50_smokes_watcher.sh` diff in `[e_018_reagent_wrapper_landed_20260420]` ack.
- E-018 Axis A Tier-1 completion is now "**2/3 systems smoke-passed** (MA-RAG ✓, MAD-as-SWAP-4-host ✓; ReAgent blocked on §11.3)".
- ReAgent n=5 adapter code is **otherwise ready**: schema conversion works (dry-run test passed locally before scp); imports clean after 11.1 + 11.2 patches; only the LLM call path needs the W1-W3 fix.

### 11.4 Updated acceptance criteria (revised from §7)

- [x] ReAgent imports + schema conversion work (R41b).
- [x] Adapter wrapper landed (`external_baselines/reagent/run_reagent_hotpotqa.py`, 250 lines).
- [x] Upstream fixes 11.1 + 11.2 applied.
- [ ] Upstream fix 11.3 applied OR workaround W1/W3 landed.
- [ ] `run_reagent_hotpotqa.py` n=5 smoke produces valid metrics.json with non-zero F1.
- [ ] Scientist sign-off in `external_baseline_plan.md` that ReAgent thin-wrapper comparison is the intended design.


## 12. R41c — W3 workaround successful (2026-04-20, engineer MCP-3)

Continuing §11 discovery and resolving §11.3.

### 12.1 Root-cause diagnosis

With traceback-enabled retry, the failing `client.chat.completions.create()` call returned an **HTML error page** (len=1612) starting with:
```
<!doctype html>
<html lang="zh">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="/logo.png" />
    <meta name="theme-color" content="#ffffff" />
    ...
```

This is newapi (xh.v1api.cc) returning its **web dashboard landing page** (Chinese HTML, has `/logo.png`). Trigger observed at message payload ≥ ~5000 chars (HotpotQA gold context); below that (my Test 1-2 with ~50 chars) the endpoint returns proper JSON. Hypothesis: newapi proxy has a **WAF / payload-size route rule** that returns the dashboard HTML for certain POST bodies instead of forwarding to the upstream chat-completion route.

`openai==2.32.0` silently converts this HTML to a Python `str` return value from `client.chat.completions.create(...)` rather than raising a JSON-parse error. ReAgent's downstream `response.choices[0].message.content` then crashes with `'str' object has no attribute 'choices'`.

### 12.2 W3 workaround (ADOPTED, working) ✅

W1 (patch api_call to skip `response_format`) failed — the HTML trigger persists even without `response_format=json_object`. Moved to W3: replace ReAgent's OpenAI-SDK path with our `workspace/idea04_core/llm_client.call_llm` (urllib-based, E-020 QuotaExhaustedError protected).

**Key changes in `run_reagent_hotpotqa.py` `_monkey_patch_api_call()`**:

1. `from idea04_core.llm_client import call_llm as _our_call_llm, extract_text, configure_runtime, QuotaExhaustedError` — route every ReAgent LLM call through our canonical client.
2. `configure_runtime("gpt-4.1-mini", enforce_model=False)` — single backbone, relaxed check (ReAgent may pass exploratory model strings).
3. Cap `max_tokens ≤ 1024` defensively (empirically prevents HTML-dashboard-response trigger).
4. If `json_format=True`, append `"Respond with ONLY a single valid JSON object..."` to system prompt + parse with `json.loads` (fallback: largest-balanced-`{...}` extraction).
5. Monkey-patch applied to **7 modules that `from backend.api import api_call` at import time**: `Agent.moderator2`, `Agent.moderator`, `Agent.agent`, `Agent.blacksheep`, `Agent.thinker`, `Agent.human`, `Environment.groupchat`. This is necessary because Python's `from X import Y` creates a local binding that is NOT overwritten by just reassigning `backend.api.api_call`.
6. E-020 `QuotaExhaustedError` propagates cleanly (never swallowed by outer retry loop).

### 12.3 R41c smoke results

**n=1 W3 smoke** (synchronous, 6.34 s wall):
```json
{"host": "ReAgent (Moderator2, o1-style)", "sample_count": 1,
 "answer_em": 0.0, "answer_f1": 0.20, "wall_s": 6.34}
```
- sample hotpotqa-0000, gold "yes", predicted "Yes, Scott Derrickson and Ed Wood were both American." → semantically correct, F1 penalty from verbosity.

**n=5 W3 smoke** (42 s wall):
```json
{"host": "ReAgent (Moderator2, o1-style)", "sample_count": 5,
 "answer_em": 0.0, "answer_f1": 0.161, "wall_s": 42.11}
```
Per-sample: every sample **semantically correct** but verbose. Extreme example: sample 0003 "Are the Laleli Mosque and Esma Sultan Mansion located in the same neighborhood?" gold=`"no"` (2 chars), ReAgent says "The Laleli Mosque is located in the Laleli neighborhood of Fatih district in Istanbul, while the Esma Sultan Mansion is located in the Ortaköy neighborhood of Istanbul by the Bosphorus. Therefore, they are not located in the same neighborhood." → F1=0.0 despite being perfectly correct.

**Comparison table** (all n=5 smokes, gpt-4.1-mini, HotpotQA head-5, gold context, single-worker):

| System | EM | F1 | Wall | Verbosity observation |
|---|---:|---:|---:|---|
| **TCPB Stage-2** (ref, E-005 n=200) | 0.50 | **0.73** | — | short answers (chain-restricted) |
| MAD (Du et al. 2024) | 0.60 | 0.75 | 153 s | short answers (debate converges concise) |
| MA-RAG (Nguyen et al. 2024, Path A) | 0.40 | 0.70 | 41 s | moderate (1-sentence answers) |
| **ReAgent** (Moderator2, o1-style, --no-mas) | 0.0 | **0.16** | 42 s | extremely verbose (multi-sentence COT dumps) |

### 12.4 Strategic take-away

ReAgent is **functionally working** but its answer-length distribution is incompatible with HotpotQA's char-overlap F1 metric without an extractive post-processor. Three options:

- (a) **Accept F1 penalty** and note in Limitations that ReAgent's o1-style COT traces are not format-compatible with HotpotQA's short-span answers. Honest but penalizes ReAgent 4-5× vs its actual correctness rate.
- (b) **Add a post-processor** across all baselines that extracts the "shortest span matching the gold" (or a separate LLM re-read: "given this long answer, output only the essential span"). Boosts all baselines symmetrically.
- (c) **Prompt-engineer ReAgent** to produce concise final answers. Would require patching Moderator2's "Final Answer" system message to include "Output ONLY the short answer span (typically 1-5 tokens). No explanation.". Minimal upstream change; need scientist sign-off.

Engineer recommendation: (c) is minimal + preserves apples-to-apples. Option (b) is more principled but requires scientist policy call on all baselines.

### 12.5 Updated acceptance criteria

- [x] ReAgent imports + schema conversion work (R41b).
- [x] Adapter wrapper landed (`external_baselines/reagent/run_reagent_hotpotqa.py`, now 340 lines with W3).
- [x] Upstream fixes §11.1 + §11.2 applied.
- [x] §11.3 workaround W3 lands and smoke-validates. (n=5 F1=0.16 but correct answers)
- [ ] Scientist decides §12.4 (a/b/c) for format-sensitivity handling.
- [ ] n=50 smoke via `r41b_n50_smokes_watcher.sh` (re-enabled in R41c).
- [ ] Scientist sign-off in `external_baseline_plan.md §ReAgent` that --no-mas + W3 thin-wrapper comparison is the intended design.
