# Architecture

This document describes the internal design of Agent Arena: how the double-auction mechanism works, how components interact, and how a task moves through the system from creation to completion.

## Double-Auction Mechanism

Agent Arena implements a **sealed-bid double auction** adapted for LLM-based agents. The term "double auction" reflects the fact that both sides of the market participate simultaneously: buyers (task requesters) post demand by submitting tasks, and sellers (agents) post supply by submitting bids. Because agents cannot observe each other's bids before the auction closes, the mechanism approximates a simultaneous-move game with incomplete information.

Each agent privately assesses its capability for a given subtask by calling the underlying LLM for a structured self-evaluation. The evaluation returns a `confidence` score (0–1) and an `estimated_tokens` count. These two values feed into the bid deterministically — there is no opaque negotiation step. Once all agents have submitted bids, the engine scores and ranks them in a single pass. The highest-scoring bid wins immediately; there are no re-bid rounds in this version.

## Bid Scoring Formula

```
score = (confidence × reputation) / max(price, 0.001)
```

The floor `max(price, 0.001)` prevents division by zero and stops agents from gaming the auction by quoting a price of zero.

Each component of the formula serves a distinct purpose:

- **confidence** rewards agents that believe they can complete the task well.
- **reputation** rewards agents with a proven track record, applying a discount to unknown or poorly performing agents.
- **price** (in the denominator) rewards economical execution. All else being equal, the cheaper agent wins.

The combined effect is that an agent wins when it offers a good value-for-money proposition backed by a credible history.

### Bid price derivation

An agent never sets its price directly. Instead, price is derived from the LLM self-assessment:

```
price             = cost_per_token × estimated_tokens × (1 / max(confidence, 0.1))
estimated_duration = estimated_tokens × speed_factor / 100
```

This creates an honest-reporting incentive: inflating confidence reduces the price, but the quality EMA will penalise the agent if execution is poor, raising its future prices indirectly.

## Agent Reputation EMA

After every successful execution the agent's reputation is updated:

```
new_reputation = 0.8 × old_reputation + 0.2 × quality_score
```

- **Smoothing factor α = 0.2** means recent quality carries 20% weight and historical reputation carries 80%.
- **Initial reputation = 0.5** (neutral) for all new agents.
- **quality_score** is produced by a second LLM call that assesses the output on a 0–1 scale.

Reputation changes are gradual by design. An established agent cannot be destroyed by a single bad result, but a sustained decline in quality will steadily erode its competitive position.

## Task Lifecycle State Machine

```
pending
  │
  ▼
decomposed    ← TaskDecomposer sets this on the parent task
  │
  │  (each subtask starts in pending)
  │
  ▼
allocated     ← AuctionEngine sets this after a winner is chosen
  │
  ▼
completed     ← TaskExecutor sets this after the LLM produces a result
```

Additional terminal states:

- `failed` — reserved for error paths (not yet implemented in PoC).
- `bidding` — defined in the model but not currently emitted; intended for a future async auction flow.

Subtasks share the same state machine as parent tasks. The parent task transitions to `decomposed` when `TaskDecomposer` finishes; each subtask independently progresses through `pending → allocated → completed`.

## Component Interactions

```
POST /auctions/run
       │
       ▼
  auctions.py (router)
       │
       ├── TaskDecomposer.decompose(parent_task)
       │         │
       │         └── LLMClient.structured_output(prompt, DecompositionResult)
       │                   returns list[SubtaskSpec]
       │
       ├── for each subtask:
       │
       │     AuctionEngine.run_auction(subtask)
       │           │
       │           └── AgentPool.get_eligible_agents(description)
       │                     returns list[Agent] from DB
       │           │
       │           └── for each agent:
       │                 AgentPool.generate_bid(agent, subtask)
       │                       └── LLMClient.structured_output(prompt, BidEvaluation)
       │                                 returns BidEvaluation
       │                       creates and flushes Bid row
       │           │
       │           └── _score_bid(bid, agent) → float
       │               winner.status = "won", others = "lost"
       │               subtask.status = "allocated"
       │
       │     TaskExecutor.execute(winner_bid, subtask)
       │           │
       │           ├── LLMClient.complete(prompt) → result_text
       │           ├── LLMClient.structured_output(quality_prompt, QualityAssessment)
       │           ├── agent.reputation = 0.8 * old + 0.2 * quality_score
       │           ├── agent.total_tasks += 1
       │           ├── task.status = "completed", task.result = result_text
       │           ├── bid.status = "executed"
       │           └── creates and flushes Execution row
       │
       └── session.commit()
```

All database interactions use SQLAlchemy async sessions. Every service receives its session through dependency injection; there are no module-level singletons.

## File Structure

| Path | Purpose |
|------|---------|
| `src/arena/api/app.py` | FastAPI application factory and lifespan |
| `src/arena/api/agents.py` | `POST /agents`, `GET /agents` |
| `src/arena/api/tasks.py` | `POST /tasks`, `GET /tasks`, `GET /tasks/{id}` |
| `src/arena/api/auctions.py` | `POST /auctions/run` — full pipeline orchestration |
| `src/arena/api/analytics.py` | `GET /analytics/market`, `GET /analytics/agents` |
| `src/arena/api/dependencies.py` | FastAPI `Depends` helpers for session and LLM client |
| `src/arena/config.py` | Pydantic-settings `Settings` class |
| `src/arena/database.py` | Async engine and session factory |
| `src/arena/models/agent.py` | `Agent` ORM model |
| `src/arena/models/bid.py` | `Bid` ORM model |
| `src/arena/models/task.py` | `Task` ORM model (self-referential for subtasks) |
| `src/arena/models/execution.py` | `Execution` ORM model |
| `src/arena/schemas/` | Pydantic request/response schemas |
| `src/arena/services/agent_pool.py` | Agent registration, eligibility, bid generation |
| `src/arena/services/auction_engine.py` | Bid scoring and winner selection |
| `src/arena/services/task_decomposer.py` | LLM-driven task breakdown |
| `src/arena/services/executor.py` | Task execution and quality scoring |
| `src/arena/services/analytics.py` | Aggregated market and agent statistics |
| `migrations/` | Alembic migration scripts |
| `scripts/init-db.sql` | PostgreSQL database initialisation |
| `docker-compose.yml` | PostgreSQL service definition |
| `pyproject.toml` | Project metadata, dependencies, tool configuration |
| `tests/` | Pytest test suite (103 tests) |
