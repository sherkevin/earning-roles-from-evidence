# Contributing

## Prerequisites

- Python 3.12 or later
- Docker and Docker Compose (for the test and development database)
- `git`

## Development Setup

Clone the repository and set up a virtual environment:

```bash
git clone <repo-url>
cd agent-arena
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Start the development database:

```bash
docker compose up -d
```

Run migrations:

```bash
alembic upgrade head
```

Start the development server:

```bash
uvicorn arena.api.app:create_app --factory --reload
```

## Running Tests

The test suite requires a running PostgreSQL instance. The test fixtures in `tests/conftest.py` connect to `arena_test` on port `5434` and create the schema automatically.

Create the test database (only needed once):

```bash
docker exec arena-postgres psql -U arena -c "CREATE DATABASE arena_test;"
```

Run all tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src/arena --cov-report=term-missing
```

Run linting:

```bash
ruff check src/ tests/
```

## Adding a New Agent Specialization

Agent specializations are free-form strings stored in `agents.specialization`. There is no registry of valid values — any string is accepted. To formally document a new specialization:

1. Pick a short lowercase label, for example `"summarisation"`.
2. Register agents with that label via `POST /agents` or through `AgentPool.register_agent`.
3. The `TaskDecomposer` prompt already instructs the LLM to assign one of `research / analysis / writing / validation / coding` to each subtask. If you want the LLM to emit your new specialization, update the prompt in `src/arena/services/task_decomposer.py`:

```python
# Before
"required specialization (research/analysis/writing/validation/coding).\n\n"

# After
"required specialization (research/analysis/writing/validation/coding/summarisation).\n\n"
```

4. When specialization-based filtering is implemented in `AgentPool.get_eligible_agents`, add a `WHERE agents.specialization = subtask.required_specialization` clause and write tests in `tests/test_agent_pool.py` covering the filter logic.

## Adding a New Bid Scoring Strategy

The current scoring formula lives in `AuctionEngine._score_bid` in `src/arena/services/auction_engine.py`:

```python
def _score_bid(self, bid: Bid, agent: Agent) -> float:
    return (bid.confidence * agent.reputation) / max(bid.price, 0.001)
```

To experiment with an alternative strategy:

1. Add a new private method to `AuctionEngine`, for example `_score_bid_v2`.
2. Accept a `strategy: str = "default"` parameter in `__init__` and dispatch to the appropriate method inside `run_auction`.
3. Write at least one unit test in `tests/test_auction_engine.py` that:
   - Creates two agents with known attributes.
   - Generates two bids with known price and confidence values.
   - Asserts that your new strategy selects the expected winner.
4. Document the formula in `ARCHITECTURE.md` under the "Bid Scoring Formula" section.

## Pull Request Process

1. Create a branch from `main`:

```bash
git checkout -b feat/my-feature
```

2. Make your changes. Write or update tests so that overall coverage stays above 80% (`pytest --cov`).

3. Ensure all checks pass before opening a PR:

```bash
ruff check src/ tests/
pytest tests/ -v
```

4. Open a pull request against `main`. The PR description should explain:
   - What problem the change solves.
   - How it was tested.
   - Any trade-offs or follow-up work.

5. Address review comments. A maintainer will merge once all checks pass and the review is approved.
