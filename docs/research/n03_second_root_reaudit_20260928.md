# N03 second-root independent re-audit: PIPE3 versus MULTI3

日期：2026-09-28
审查类型：只读、零 LLM、零 GPU、零真实 API
TeamBench 源码：`d185aef1916fd86a9ba554d581fd256319a973af`

补充的零 API 直接组合审计日志见
[`n03_multi3_direct_composition_audit_20260928`](../../experiments/logs/n03_multi3_direct_composition_audit_20260928/)。

本记录独立复核第二个结构 root 是否真的具备：

1. producer 产生可交付 artifact；
2. recipient 有自己的、与 producer 责任可分的工作；
3. recipient 实际接收并使用 artifact；
4. adoption 可以和 producer 质量、recipient 自有质量分别评分。

本记录不冻结 benchmark，不修改 Goal，不启动真实 API 或 A800。

## 结论

当前建议为：

- **PIPE3：conditional GO**，进入下一道最小零 API runner qualification；
- **MULTI3：confirmation root NO-GO**，保留为 fallback design candidate；
- **真实 LLM/API、benchmark freeze、A800：均 NO-GO**，直到 PIPE3 的 runtime gates 完成。

## PIPE3 的可验证事实

`scripts/peerrolebench_pipe3_material_adapter.py` 将角色边界固定为：producer 只写
`producer.py`，recipient 只写 `processor.py`，`models.py` 与 `sink.py` 为只读支持文件，
测试文件隐藏。neutral task text 去掉了 TeamBench 原始 spec 中直接列出的 bug/fix/Planner
信息，保留可检查的 public interface 与 data-flow 要求。

`scripts/peerrolebench_pipe3_runner_adapter.py` 只把 `producer.py` 作为 delivery 附给
recipient。`use` 只能修改 `processor.py`；最终 adoption view 包含
`producer.py`、`processor.py`、`models.py` 和 `sink.py`。这构成了 producer delivery、
recipient 独立工作和 downstream sink adoption 的实际因果候选。

PIPE3 已有独立的 Qp/Qr/adoption scorer：

- Qp 只读取 producer artifact 与 `models.py`；
- Qr 只读取 recipient processor 与 `models.py`；
- adoption 读取完整 public runtime，并由 sink 消费组合结果。

`experiments/logs/n03_pipe3_lineage_preflight_20260927_v5/summary.json` 的四格控制
（all-correct、producer-bad、recipient-envelope-bad、recipient-encoding-bad）观察到
Qp、Qr 和 adoption 分离。该结果只证明责任边界和控制矩阵，不是 agent 学习效果。
`experiments/logs/n03_pipe3_policy_sidecar_fixture_20260928_v2/` 也已通过 seed-0
sidecar/ledger 离线 fixture，但仍不是 live runner 证据。

## PIPE3 尚未通过的 gate

1. sidecar fixture 由脚本手工构造，尚未由 root-specific live runner 产生；
2. candidate、private scorer、operator ledger 的端到端进程/IPC 隔离尚未在真实 runner
   中证明；
3. 真实 ledger/manifest hash-chain、exact-once lineage、延迟/乱序 replay 仍需 runner
   生成并回放；
4. 多事件、异常、超时、成本和 UNKNOWN 路径尚未覆盖完整；
5. `prepare_pipe3_action` 当前给 `independent_redo` 标注
   `prior_delivery_may_have_been_seen=true` 和 `independent_redo_is_blinded_control=false`。
   因而不能把它当作 blinded no-handoff control；下一步应修正语义，或把该动作排除在
   主比较之外；
6. producer downstream defect 不应被回写成 producer label，必须继续使用 Qp/Qr/adoption
   分离和责任 gate。

另外，当前 `FeedbackSidecar` 的绑定仍不能称为完整 responsibility lineage：
`bind_to_ledger_record` 检查 sidecar 对 judgment/outcome 的 hash、event type/id 和可用的
task identity，`PolicySidecarBridge` 检查 selection 与 chosen producer，但还没有把
`delivery_id`、`recipient_id`、`producer_id` 与 canonical `producer_delivery` 对照，也
没有把 `action` 与 canonical `consumer_action` 对照（sidecar 目前没有 `action_id` 或
action record hash）。同样，judgment 的 observed artifact digest 与 outcome 的
delivery_id 还需通过 delivery index 严格关联。该缺口必须作为 live runner gate，不能用
当前 fixture 的 PASS 代替。

所以 PIPE3 只获得“进入下一道零 API 资格门”的 conditional GO。

## MULTI3 的关键反证

TeamBench generator 生成 `backend/processor.py`、`frontend/handler.py`、
`shared/schema.json` 和隐藏测试 `tests/test_contract.py`。但是 native test 的设计明确
将 frontend 检查与 backend 输出隔离：

- 测试预先构造 `self.correct_wire` 和 `self.correct_envelope`；
- frontend 的 id、null、date、envelope 和 round-trip 测试都消费这些 canonical 对象；
- `test_round_trip` 是 `correct_wire -> handler.deserialize_record`，不是
  `processor.serialize_batch -> handler.process_envelope`。

因此 native grader 通过时，不能证明 backend artifact 被 frontend 实际采用。

为避免只依赖静态阅读，审计在临时工作区把每个 seed 的原始
`processor.serialize_batch` 输出直接交给 `handler.process_envelope`。seed 0/1/2 的
初始组合均失败（分别为错误 ID、错误日期解析、错误 ID）；native tests 也均未通过。
这不是效果实验，但确认当前 MULTI3 不能以“原生测试通过”替代真实 adoption 证据。

此外，`schema.json` 在每个生成任务中都注入 `schema_wrong_field_name`，但当前没有定义：

- schema bug 归 producer 还是 recipient；
- schema 是否可写以及 delivery 是否包含它；
- backend artifact 的 digest、recipient 接收记录和 adoption lineage；
- independent scorer、operator ledger、UNKNOWN 和责任映射。

当前仓库也没有 MULTI3 adapter、scorer 或零 API qualification。若直接把 MULTI3 作为
第二 root，会把局部 canonical-input 测试误写成 adoption 证据，并引入 schema ownership
混淆。

MULTI3 全部实现仍是 Python，核心是 backend/frontend schema conversion；相对于 PIPE3
三阶段 producer→processor→sink，它既缺少真实 adoption 证据，也没有更清晰的结构差异。

## 下一步最小资格动作

在不改 Goal、不调用 LLM/GPU 的前提下，优先完成 PIPE3：

1. seed 0/1 由 root-specific runner 真实生成 selection、delivery、pre-action judgment、
   use/repair/independent-redo action、Qp/Qr/adoption 结果和 sidecar/manifest；
2. 对四格控制复核责任归因；加入 action-only repair 不更新 producer label、UNKNOWN
   no-update、delivery digest mismatch、out-of-order replay；
3. 所有 baseline 使用同一个 sealed snapshot、公开信息、探索随机数和成本口径；
4. 只有零 API gate 全部通过后，才允许一条真实 API 开发链；
5. 如果 PIPE3 失败，再按同一 manifest/baseline contract 重写 MULTI3 adapter，而不是
   直接把 native MULTI3 测试当作确认结果。

该复审不修改 `docs/coordination/GOAL.md`，也不降低任何既定科学标准。
