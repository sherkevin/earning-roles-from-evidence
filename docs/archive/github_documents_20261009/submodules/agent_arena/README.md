# Agent Arena

**A self-regulating arena where AI agents compete for work through sealed-bid auctions.**

## The Problem

You have multiple AI agents (LLMs), each with different strengths, costs, and track records. How do you decide which one to assign to a task? You could pick manually, or pick the cheapest, or always use the same one. But none of these scales, adapts, or learns.

## The Solution

Agent Arena runs a **sealed-bid auction** for every task. Think of it like hiring freelancers:

1. You post a job
2. Multiple freelancers bid on it — without seeing each other's bids
3. The platform picks the best one based on a composite of skill, track record, and price
4. If the winner fails, the job goes to the runner-up (and the winner's reputation takes a hit)

The result is a market that self-regulates: agents that do good work earn reputation, win more auctions, and get more work. Agents that do bad work lose reputation and get outbid. Nobody can cheat.

**Now with adaptive bidding**: agents learn from their win/loss history and automatically adjust their pricing strategy. Watch it happen live via the WebSocket feed in the dashboard.

## See It In Action

Here's what happens when you submit a task to 4 agents:

```
Task: "Create a Python CLI tool that fetches weather data"
                    ↓
        Decomposed into 6 subtasks
                    ↓
    Each subtask → 4 agents bid → best wins

 Subtask: "Implement Python code"
 ┌──────────────────┬──────┬────────┬──────┬─────────┐
 │ Agent            │ Conf │ Price  │ Spec │ Result  │
 ├──────────────────┼──────┼────────┼──────┼─────────┤
 │ CodeMaster-3000  │  92% │ $24.35 │ x1.5 │ WINNER  │ ← python specialist
 │ DeepResearch-AI  │  85% │ $14.71 │ x0.8 │ lost    │ ← cheaper but wrong spec
 │ DocWriter-Pro    │  85% │ $31.77 │ x0.8 │ lost    │
 │ PixelPerfect-UI  │  70% │ $42.86 │ x0.8 │ lost    │
 └──────────────────┴──────┴────────┴──────┴─────────┘
 Score = (confidence × reputation × spec_multiplier) / price

 CodeMaster wins despite higher price because the x1.5 specialization
 bonus for "python" on a Python task outweighs the cost difference.
```

After the auction, reputations update:

```
 Agent              Before  After   Why
 DeepResearch-AI    0.50 →  0.68    Won 3 subtasks, avg quality 87%
 CodeMaster-3000    0.50 →  0.61    Won 2 subtasks, avg quality 80%
 DocWriter-Pro      0.50 →  0.54    Won 1 subtask, quality 72%
 PixelPerfect-UI    0.50 →  0.50    Won nothing (no design subtasks)
```

In the **next** auction, DeepResearch-AI starts with a competitive edge from higher reputation.

## Why This Matters (Game Theory)

This project demonstrates four concepts from academic research on multi-agent systems:

| Concept | What it means | How it works here |
|---------|--------------|-------------------|
| **Sealed-bid auction** | Agents bid without seeing competitors | Each agent evaluates the task independently via its LLM, produces a price and confidence. No agent knows what others bid. |
| **Strategyproof design** | Cheating is always unprofitable | If an agent inflates confidence to win cheaply, it executes poorly → reputation drops → loses future auctions. If it fails on purpose, it gets `quality=0.0` penalty + the task goes to the runner-up. There is no winning strategy except doing good work. |
| **Emergent specialization** | Specialists beat generalists in their domain | A Python agent gets a x1.5 score multiplier on Python tasks. It doesn't *have* to be a Python task — any agent can bid — but specialists have a structural advantage in their domain. |
| **Reputation as a public signal** | Past performance predicts future selection | Reputation multiplies into the score formula. A proven agent can win even against a cheaper newcomer, just like in real markets where you pay more for a trusted supplier. |

Based on: [Duetting 2023](https://arxiv.org/abs/2310.10826) (mechanism design), [Hernandez-Leal 2019](https://arxiv.org/abs/1911.10635) (multi-agent RL), [ChatDev 2023](https://arxiv.org/abs/2307.07924) (role specialization), [AutoGen 2023](https://arxiv.org/abs/2308.08155) (per-agent LLM backends).

## Quick Start

### Prerequisites

- Docker and Docker Compose
- An LLM API key (Anthropic, OpenAI, or a local Ollama instance)

### 1. Configure

Create a `.env` file:

```bash
LLM_API_KEY=sk-ant-your-key-here
```

### 2. Start everything

```bash
docker compose up -d
```

This starts PostgreSQL + the backend with auto-migration. The dashboard is at **http://localhost:8000**.

### 3. Register agents

Create a team of agents with different specializations:

```bash
# A Python specialist
curl -s -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CodeMaster-3000",
    "specialization": "python",
    "description": "Expert Python developer.",
    "cost_per_token": 0.008,
    "speed_factor": 1.2,
    "llm_provider": "anthropic",
    "llm_model": "claude-haiku-4-5-20251001"
  }'

# A researcher
curl -s -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DeepResearch-AI",
    "specialization": "research",
    "description": "Literature review and analysis specialist.",
    "cost_per_token": 0.005,
    "speed_factor": 0.8,
    "llm_provider": "anthropic",
    "llm_model": "claude-haiku-4-5-20251001"
  }'

# A technical writer
curl -s -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DocWriter-Pro",
    "specialization": "technical",
    "description": "Clear, concise technical documentation.",
    "cost_per_token": 0.006,
    "speed_factor": 1.0,
    "llm_provider": "anthropic",
    "llm_model": "claude-haiku-4-5-20251001"
  }'
```

Or use the dashboard: go to **Agents** → **New Agent**.

### 4. Run an auction

```bash
curl -s -X POST http://localhost:8000/auctions/run \
  -H "Content-Type: application/json" \
  -d '{"description": "Write a brief report on the history of the Byzantine Empire."}'
```

Or use the dashboard: go to **Run Auction** → type a task → click **Run Auction Pipeline**.

### 5. Watch the results

Open **http://localhost:8000** to see:
- **Overview**: market stats, reputation leaderboard, quality charts, **Live Auction Feed** (WebSocket)
- **Tasks**: subtask tree with bids, winners, and expandable **Decision Log** showing every auction decision
- **History**: completed auctions with quality scores

The **Live Auction Feed** streams every event in real-time via WebSocket — no need to refresh.

## How the Pipeline Works

```
POST /auctions/run { "description": "..." }
         │
         ▼
   ┌─────────────┐     "Break this into subtasks"
   │ Decomposer  │────▶ LLM structured output
   └──────┬──────┘     Returns: [{description, required_specialization}, ...]
          │
    For each subtask:
          │
          ▼
   ┌─────────────┐     Each agent's LLM evaluates the task
   │  Agent Pool  │────▶ Returns: confidence + estimated_tokens
   │  + Strategy  │     BiddingStrategy adjusts confidence & cost based on history
   └──────┬──────┘     Price = effective_cost × tokens × (1/adjusted_confidence)
          │
          ▼
   ┌─────────────┐     score = (confidence × reputation × spec_multiplier) / price
   │   Auction    │────▶ Rank all bids, return sorted list
   │   Engine     │     (no winner marked yet — orchestrator decides)
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐     Try #1 agent → success? → done
   │ Orchestrator │     Try #1 agent → fail? → penalize, try #2
   │  (fallback)  │     All fail? → subtask marked "failed"
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐     LLM generates output → LLM scores quality
   │  Executor    │────▶ reputation = 0.8 × old + 0.2 × quality_score
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐     Every decision logged as AuctionEvent (JSONB)
   │ Audit Logger │────▶ Visible in dashboard Decision Log
   │  + WebSocket │     Events broadcast live to connected clients
   └─────────────┘
```

## The Scoring Formula

```
score = (confidence × reputation × specialization_multiplier) / max(price, 0.001)
```

| Factor | Range | What it rewards |
|--------|-------|----------------|
| **confidence** | 0–1 | Agent's self-assessed ability for this specific task |
| **reputation** | 0–1 | Track record from past executions (EMA, starts at 0.5) |
| **specialization** | 0.8–1.5 | Match between agent's skill and task's requirement |
| **price** | > 0 | Lower is better (derived from confidence × cost_per_token) |

### Specialization multipliers

| Match | Multiplier | Example |
|-------|-----------|---------|
| Exact | x1.5 | agent `python`, task needs `python` |
| Parent | x1.2 | agent `python`, task needs `coding` |
| Sibling | x1.0 | agent `python`, task needs `javascript` |
| No match | x0.8 | agent `python`, task needs `literature` |

Taxonomy: **coding** (python, javascript, rust, sql) · **research** (literature, data_analysis, fact_checking) · **writing** (technical, creative, translation) · **design** (ui, architecture, system)

### Why agents can't cheat

**Inflate confidence?** → Price drops (you win), but quality is scored independently. Low quality → reputation drops → you lose future auctions.

**Fail on purpose?** → Reputation penalty (`quality = 0.0` in EMA). Task goes to runner-up. You gained nothing, lost reputation.

**Underbid?** → You win but your low confidence penalizes your score. You need genuinely low cost_per_token to bid low honestly.

## Adaptive Bidding

Agents don't bid with fixed parameters. Each agent has a **bidding strategy** that adjusts its behavior based on past auction results:

| Strategy | Behavior |
|----------|----------|
| **adaptive** (default) | Lowers price after 3 losses, raises after 3 wins. Balanced. |
| **aggressive** | Reacts after just 2 losses/wins. Fast adaptation, volatile. |
| **conservative** | Needs 6+ losses/wins to react. Stable, slow to change. |
| **fixed** | No adaptation. Baseline for comparison. |

The strategy adjusts two knobs before each bid:
- **confidence_delta** — shifts the LLM's self-assessed confidence up or down
- **cost_multiplier** — scales the agent's cost_per_token (effectively changing the price)

Example: an agent with `adaptive` strategy that lost 3 auctions in a row will lower its cost by 10% and reduce confidence by 0.05, making its bids more competitive in the next round.

All adjustments are logged as `strategy_adjustment` events in the audit trail and streamed via WebSocket.

## WebSocket Live Feed

The dashboard connects to `ws://localhost:8000/ws/auctions` and receives every auction event in real-time:

- Auction started / subtask failed
- Winner selected / execution completed
- Strategy adjustments (with delta values)
- Fallback triggered / execution failed

Events appear in the **Live Auction Feed** panel on the Overview page — color-coded by type.

## Dashboard

Available at **http://localhost:8000** (auto-redirect from root).

| Page | What it shows |
|------|--------------|
| **Getting Started** | 3-step onboarding flow + pipeline diagram |
| **Overview** | KPI cards, reputation leaderboard, charts, **Live Auction Feed** (WebSocket) |
| **Agents** | Agent cards with strategy badges + **create agent form** (with strategy picker) |
| **Run Auction** | Submit task form + live results |
| **Tasks** | Task tree with bids, specialization badges, **Decision Log** |
| **History** | Completed auctions table |

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe |
| `POST` | `/agents` | Register a new agent |
| `GET` | `/agents` | List all agents |
| `POST` | `/tasks` | Create a task (no auction) |
| `GET` | `/tasks` | List tasks (optional `?status=` filter) |
| `GET` | `/tasks/{task_id}` | Get a single task |
| `POST` | `/auctions/run` | Full decompose → bid → execute pipeline |
| `GET` | `/analytics/market` | Market-wide statistics |
| `GET` | `/analytics/agents` | All agents' performance |
| `GET` | `/analytics/agents/{agent_id}` | Single agent's performance |
| `GET` | `/analytics/history` | Recent completed auctions |
| `GET` | `/analytics/auctions/{task_id}/events` | Audit trail for a task |
| `WS` | `/ws/auctions` | Live auction event stream (WebSocket) |

## Configuration

All settings via environment variables or `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...localhost:5434/arena` | PostgreSQL connection |
| `LLM_DEFAULT_PROVIDER` | `ollama` | Default LLM for decomposition |
| `LLM_DEFAULT_MODEL` | `llama3` | Default model |
| `LLM_API_KEY` | _(empty)_ | API key for the provider |

Each agent uses its own LLM resolved from `llm_provider`/`llm_model` via [llmwire](https://github.com/alexmar07/llmwire). Different agents can use different providers (e.g., one on Ollama, another on OpenAI).

## Tech Stack

- **Backend**: FastAPI (async), SQLAlchemy 2.0, PostgreSQL 16, Alembic
- **LLM**: [llmwire](https://github.com/alexmar07/llmwire) (Anthropic, OpenAI, Ollama)
- **Real-time**: FastAPI WebSocket with in-memory broadcast
- **Frontend**: Single-page dashboard (Tailwind CSS, Chart.js, Lucide icons, Fira Code/Sans)
- **Testing**: 131 tests (pytest-asyncio)

## Roadmap (v0.2.0)

- ~~**Adaptive bidding** — agents adjust strategy based on win/loss history~~ Done
- ~~**WebSocket streaming** — real-time auction events~~ Done
- **Nash equilibrium learning** — agents learn optimal bidding via reinforcement learning
- **Coalition formation** — agents form temporary teams for complex tasks
- **Multi-model arena** — different LLMs (GPT-4, Claude, Llama) compete head-to-head
- **Concurrent subtask execution** — independent subtasks run in parallel

## References

- Duetting et al., "Mechanism Design for Large Language Models", 2023 — [arxiv.org/abs/2310.10826](https://arxiv.org/abs/2310.10826)
- Hernandez-Leal et al., "A Survey of Multiagent Deep Reinforcement Learning", 2019 — [arxiv.org/abs/1911.10635](https://arxiv.org/abs/1911.10635)
- Qian et al., "Communicative Agents for Software Development" (ChatDev), 2023 — [arxiv.org/abs/2307.07924](https://arxiv.org/abs/2307.07924)
- Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation", 2023 — [arxiv.org/abs/2308.08155](https://arxiv.org/abs/2308.08155)

## Disclaimer

This project was built entirely via **Vibe Coding** with [Claude Code](https://claude.ai/claude-code).

## License

MIT
