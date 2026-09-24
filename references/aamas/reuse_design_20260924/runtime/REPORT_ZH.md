# 运行时复用审计与选型（2026-09-24）

## 结论

本轮只选择 **OpenHands Software Agent SDK** 作为实验运行时，不把两个框架拼成新的运行时。选择的精确版本是：

- 仓库：`OpenHands/software-agent-sdk`
- commit：`e21d77673b738f056676044600c4ad81c5a575c8`
- SDK：`openhands-sdk==1.49.5`
- 许可证：MIT（原始许可证快照见 `openhands_snapshot/LICENSE`）
- manifest：`openhands_snapshot/openhands_sdk/pyproject.toml`

mini-SWE-agent 只保留为一个外部对照/备选执行器，不与 OpenHands 共享 agent loop。它的精确版本是 `SWE-agent/mini-swe-agent@04d809ceab9df28f9adaed044884180159172930`，MIT；它更小、更容易跑 CooperBench 这类 shell/code benchmark，但没有 OpenHands SDK 原生的事件持久化与 PreToolUse/PostToolUse 钩子，因此不适合直接承载本文的 judgment→role 证据链。

AutoGen Core 与 AgentScope 也做了源码核查，许可证和 commit 见 `manifest_commits.json` 与对应快照目录；两者适合消息编排或中间件扩展，但需要我们额外搭建交付封存、事件持久化和跨任务证据存储，不能减少本文核心适配工作。

## 为什么 OpenHands SDK 更贴合我们的故事

我们的最小闭环需要“生产者产生交付 → 接收者实际使用或返工 → 记录判断 → 后续职责选择”，运行时必须能保存证据并在工具使用前后插入控制点。OpenHands SDK 已提供：

1. `Conversation(..., workspace=..., persistence_dir=..., callbacks=..., tags=...)`：每个 agent 可以有独立 workspace 和持久化目录；任务、agent、角色条件可以写入 tags。
2. `ActionEvent`、`ObservationEvent`、`MessageEvent`、`LLMCompletionLogEvent` 等事件：动作、工具结果、对话和 LLM 调用均进入事件流；事件存储落成 JSON 文件，方便逐条审计。
3. `HookConfig` / `HookManager`：`PreToolUse` 可以在动作真正执行前阻断或封存，`PostToolUse` 可以把工具输入和结构化结果写入 judgment ledger；这比在一个大循环里自己插入 if/else 更适合做协议边界。
4. `callbacks`：可以在事件落盘链上追加不可变的 producer、consumer、delivery、judgment、repair、role-update 记录。
5. `LLM(model=..., base_url=..., api_key=...)`：模型和网关地址是独立配置字段，后续可以把 cc-switch “内部”配置转换成 OpenAI-compatible/LiteLLM 参数；本轮只做字段与代码路径审计，未发付费请求。

## 已执行的零付费 smoke

### OpenHands SDK

配置先写入 `openhands_smoke/config.json`，执行轨迹流式写入 `openhands_smoke/raw.jsonl`。使用 Python 3.12.13 的 uv 隔离环境，`TestLLM` 脚本返回固定 tool call，不访问任何付费模型。

`run_smoke.py` 注册了一个真实 `EchoTool`，执行一次 proposal action，再返回终止文本。结果：

- `ActionEvent=1`、`ObservationEvent=1`；总 callback 事件 5 个（含 system/message）
- 状态为 `FINISHED`
- 本地 event store 写出 5 个 `event-*.json` 和 `base_state.json`
- 另外用 [hook_smoke.py](openhands_smoke/hook_smoke.py) 直接调用 SDK 的 `HookManager`，真实执行 stdin JSON 命令，`PreToolUse` 和 `PostToolUse` 都得到 `decision=allow` 的结构化结果；证据见 [hook_result](openhands_smoke/hook_result.json)。
- 第一次漏掉 `register_tool` 的失败也保留在 `raw.jsonl`，第二次修复后通过。这说明 custom tool 必须在发送消息前显式注册，是后续适配的真实约束。

证据：

- [smoke README](openhands_smoke/README.md)
- [script](openhands_smoke/run_smoke.py)
- [result](openhands_smoke/result.json)
- [raw JSONL](openhands_smoke/raw.jsonl)
- [成功 event store](openhands_smoke/persistence/5bd84dff8d9d4dea86dd0eb34e4652e5/events)

### mini-SWE-agent

同样先写 `mini_swe_smoke/config.json`，使用 `DeterministicToolcallModel` 和真实 `LocalEnvironment`，没有 API 请求。两次 tool call 分别写入 proposal 和 completion marker，结果：`Submitted`、`api_calls=2`、trajectory 6 条消息、1 条工具观察，完整 trajectory 已保存为 JSON。

证据：[mini-SWE smoke README](mini_swe_smoke/README.md)。

## 需要我们自己写的薄适配

选用 OpenHands SDK 并不等于创新已经实现。我们只复用 agent loop、工具执行、事件存储和 hook，下面五部分仍是本文自己的实验协议：

1. **DeliveryEnvelope**：把 producer 的输出、输入任务、依赖、版本、workspace、event-id 和 hash 封装成不可变交付物。consumer 只能看到明确允许的字段。
2. **ConsumerGate**：在 consumer 读取或执行交付前调用 `PreToolUse`/自定义 callback，记录 `accept`、`reject`、`repair`、`use_without_change` 和理由；使用之后记录实际采用、修改、回退和下游结果。
3. **Judgment ledger**：追加式 JSONL 记录 `{producer, consumer, task_id, delivery_id, observed_action, evidence_scope, judgment, downstream_outcome, cost}`；ledger 不能回写历史事件，也不能把某个 owner 的私有 trust 伪装成公共角色证据。
4. **Role updater + third-party scheduler**：依据已冻结的判断到角色证据规则，在未来任务中由没有直接评价该候选人的第三方 owner 选择职责；该 scheduler 必须能切换 raw-acceptance、terminal-only、local-trust/bandit 和我们的更新器。
5. **Evaluation adapter**：为 AppWorld 或 CooperBench 提供独立 task root、producer/consumer workspace、真实 evaluator、成本统计和同信息控制。运行时只报告轨迹，不能自行把 evaluator 分数注入下一次 prompt。

## 不应做的拼接

- 不要把 OpenHands SDK 和 mini-SWE-agent 混在同一 agent loop。
- 不要把 OpenHands 的 `HookManager` 直接称为本文方法；它只是协议实现位置。
- 不要把 SDK 自带的 critic/goal judge 当成 peer judgment；本文需要的是**真实接收者的采用/返工动作和后续下游效果**。
- 不要把事件持久化当成 role learning；事件只是证据，role updater 和第三方 future assignment 才是需要验证的科学对象。

## 版本与依赖风险

OpenHands SDK 要求 Python `>=3.12`，依赖 LiteLLM、FastMCP、MCP、tree-sitter 等，明显重于 mini-SWE-agent；如果 CooperBench 的官方容器固定另一 Python/工具版本，应在 benchmark adapter 层隔离，不要修改 SDK 核心。OpenHands 的 `Conversation` 本地 workspace 和 CooperBench/AppWorld evaluator 之间也需要单独的只读/写入边界测试。

所有四个候选仓库的 commit、工作树状态和 license/manifest 快照见 [manifest_commits.json](manifest_commits.json)；48 个本地快照/实验文件的大小和 SHA-256 见 [source_hashes.json](source_hashes.json)。源码关键片段见：

- [OpenHands agent base](openhands_snapshot/openhands_sdk/agent_base.py)
- [OpenHands conversation factory](openhands_snapshot/openhands_sdk/conversation_factory.py)
- [OpenHands hooks config](openhands_snapshot/openhands_sdk/hooks_config.py)
- [OpenHands hooks manager](openhands_snapshot/openhands_sdk/hooks_manager.py)
- [OpenHands LLM](openhands_snapshot/openhands_sdk/llm.py)
- [mini-SWE default agent](mini_swe_snapshot/src/default.py)
- [mini-SWE LiteLLM model](mini_swe_snapshot/src/litellm_model.py)
- [AutoGen intervention protocol](autogen_snapshot/base_agent.py)
- [AgentScope agent/middleware](agentscope_snapshot/agent.py)

## 下一步实施顺序

1. 先在 OpenHands SDK 上写一个**不含学习算法**的 `DeliveryEnvelope + ConsumerGate + append-only ledger`，用 TestLLM 和本地工具验证协议边界。
2. 再接入一个 CooperBench/AppWorld 小任务，先只测 producer→consumer 的完整证据链，禁止宣称角色学习。
3. 冻结 role updater 和 third-party scheduler，再接同信息 baseline。
4. 最后才用“内部”真实 LLM API 做小批量开发实验；每次调用沿用本项目的 config/raw/processed/summary 日志要求。
