# OpenHands SDK zero-LLM smoke

- Repository: `OpenHands/software-agent-sdk`
- Commit: `e21d77673b738f056676044600c4ad81c5a575c8`
- Package: `openhands-sdk==1.49.5`
- Runtime: CPython 3.12.13, uv isolated environment at `/tmp/reuse_runtime_20260924b/venv_oh`
- Paid API/model calls: none; `openhands.sdk.testing.TestLLM` scripted responses only.
- Script: `run_smoke.py`
- Result: one registered custom `EchoTool` call produced `ActionEvent` + `ObservationEvent`; callback captured 5 events; local event store persisted `base_state.json` plus 5 event JSON files; conversation reached `FINISHED`.
- Failure retained in `raw.jsonl`: first attempt omitted `register_tool` and raised `KeyError`; second attempt registered the tool and passed. This is a real integration constraint: custom tools must be registered before `Conversation.send_message`.
- `persistence/4726...` is the failed attempt's empty initial state; `persistence/5bd...` is the successful 5-event trace.

- `hook_smoke.py` exercises the SDK's actual `HookManager` with a real stdin JSON command for both `PreToolUse` and `PostToolUse`; [hook_result.json](hook_result.json) records `pre_continue=true`, exit code 0, and parsed `decision=allow` for both points. This is a zero-LLM hook execution smoke, not a role-learning experiment.

- A no-network constructor smoke also accepted `LLM(model="openai/internal-test", base_url="http://127.0.0.1:1/v1", api_key=SecretStr("redacted"))`; no completion request was made. The actual cc-switch “内部” gateway URL/model mapping must be supplied by the experiment config at runtime.
