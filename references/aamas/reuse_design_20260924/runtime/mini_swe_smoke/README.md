# mini-SWE-agent zero-LLM smoke

- Repository: `SWE-agent/mini-swe-agent`
- Commit: `04d809ceab9df28f9adaed044884180159172930`
- Version: `2.4.6`, MIT license.
- Runtime: CPython 3.12.13, uv isolated environment at `/tmp/reuse_runtime_20260924b/venv_mini`.
- Paid API/model calls: none; `DeterministicToolcallModel` scripted outputs only.
- Script: `run_smoke.py`
- Result: two deterministic agent calls executed in `LocalEnvironment`; first emitted a producer proposal, second emitted completion marker; trajectory serialized to JSON with 6 messages, 2 calls, one tool observation, and submission `accepted`.
- Setup failures are retained in `raw.jsonl` (missing `python-dotenv`, `platformdirs`, `rich`) and were repaired by installing the declared dependencies in the isolated environment.
