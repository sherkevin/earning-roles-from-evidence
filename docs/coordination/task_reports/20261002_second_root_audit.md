# 第二 structural root 审查：PIPE2、MULTI3、CROSS5、DIST1

日期：2026-10-02
范围：只读审查 TeamBench pinned source、当前 adapter/worker、已有 qualification
reports 与原始 receipts。没有调用 LLM、真实外部 API、Nebula 或 GPU，也没有把离线
fixture 当作 scientific evidence。
状态：`PARTIAL / SECOND_ROOT_NOT_FROZEN`
`goal_change_requested=false`

## 审查合同

ArtifactRole 的第二 root 必须在同一条可回放链中满足：

```text
producer delivery
  → recipient 实际 use + situated judgment
  → ownership 可分离
  → later assignment 在执行前消费公开 evidence
  → 独立 outcome / complete cost
```

这里的“满足”要求有可绑定的 `delivery_id`、版本和 artifact digest，且 scorer 能把
producer contract、recipient 自有工作、adoption、UNKNOWN 和 later outcome 分开。只
出现同名 ledger event、native 总分或手写 fixture 不算通过。

## 逐候选复核

| 候选 | producer delivery | recipient use / judgment | ownership | later assignment | outcome | 当前判定 |
|---|---|---|---|---|---|---|
| `PIPE2_data_pipeline` | **有工程证据**。v2 material adapter 将 `extract.py` 的 rows 封存为 `pipe2-extracted-rows-v1`，v8 在 seed 0/2 的 sandbox 中执行了 producer→artifact→recipient 的 2×2 矩阵。 | **有 use/adoption，没 situated judgment**。recipient 的 transform/load 真实读取 sealed rows，父进程分别算 `recipient_self` 与 key sequence/row-count adoption；没有真实 recipient judgment 事件或独立 live history。 | **清楚**：producer=`pipeline/extract.py`；recipient=`transform.py`,`load.py`；source/spec 与 runner 为只读；expected output/tests 留在 parent。 | **没有**。PIPE2 还没有接入 RoleEvidence、selection preview→commit 或 next task start。 | **只有本 episode 的工程分数**；没有后续 task quality、rework/complete cost 或 confirmation outcome。 | **CONDITIONAL-HIGH；最值得下一步投入，但尚不是第二 root** |
| `MULTI3_polyglot` | **概念上有** backend serializer，但 native path 没有把本次 wire 封存后交给 frontend。2026-09-28 direct composition 的 seed 0/1/2 全部失败。 | **不满足**。native tests 预构造 `correct_wire`/`correct_envelope`，frontend 没有使用 producer 的输出；无 situated judgment。 | **不干净**：backend、frontend 与 `shared/schema.json` 三方责任未裁决，schema bug 会混入双方 label。 | **没有**。 | **只有 native unit/round-trip 诊断**，不是真实 adoption 或 later outcome。 | **CONDITIONAL-LOW fallback** |
| `CROSS5_event_schema` | **概念上有** Python producer→JSON event；但无 sealed delivery adapter。 | **不满足**。Java consumer 未被执行；native `grade.sh` 的 C1–C10 主要做 Python/Java 源码和字符串/括号静态检查，没有行为 use/judgment。 | **候选上较清楚**：producer、Java consumer、read-only schema；但 schema digest/consumer input binding 尚未实现。 | **没有**。 | **没有可接受的 consumer outcome**；没有 later-use/cost ledger。 | **FALLBACK-UNQUALIFIED；暂不投入** |
| `DIST1_queue_race` | **协议事件存在，但科学 delivery 不合格**。N02 v3 ledger 有 delivery digest；v2 material 也明确 queue/priority 属 producer、consumer.py 属 recipient。 | **有一次真实 recipient use/judgment/action**，但 scorer 只覆盖 consumer 四项；producer priority/queue correctness 未被测量。两次结果均为 consumer 4/4，不代表 producer delivery 正确。 | **表面清楚，实际覆盖不足**：两次真实 action 都只改 `consumer.py`；`producer_objective_quality=null`。post-hoc 检查还发现 producer priority 缺陷未进入原分数。 | **ledger 中确有 later assignment/task start**，但概率没有因 feedback 改变；同一 structural root，且原任务/历史泄露，不能作为独立 confirmation root。 | **有 consumer terminal outcome**，没有 producer contract outcome，也没有完整 responsibility-aware quality/cost。 | **DIAGNOSTIC-ONLY；不作为第二 root** |

### PIPE2 的实证细节

`experiments/logs/n03_pipe2_runtime_adoption_qualification_20261001_v8/summary.json`
记录了 seed 0/2 的 8 个 producer×recipient cells；每个 cell 都在 pinned sandbox
中运行，且把 producer contract、recipient self、artifact adoption 分开。该 receipt
明确是 `scientific_claim_allowed=false`。随后 shape audit
`n03_pipe2_fixture_shape_audit_20261001_v3` 发现 seed 1/4/6/9 的 generator 用未转义
逗号写 CSV，`DictReader` 产生未声明的 `None` 字段；v9 只因此得到
`FAILED_OFFLINE`。它不能被删掉、静默修写或把 valid subset 直接升格为 benchmark。

因此 PIPE2 目前最接近合同，但缺的不是再写一个 handoff probe，而是把 material
authority、公开 judgment、later assignment 和独立 outcome 接到同一条 source-bound
ledger。它仍与 PIPE3 的 streaming producer→processor→sink 结构不同，不能把 seed
变体当成多个 root。

### DIST1 的反例意义

`experiments/logs/n02_peerrole_dev_v3_20260926/summary.json` 与其 ledger 确实记录了
delivery→judgment→action→terminal outcome→later assignment→task start 的事件顺序，
ledger hash chain 也有效。这证明协议 plumbing 可以连通；它没有证明 ArtifactRole
合同，因为 producer score 缺失，recipient 的修复成本和 consumer score 被当作主要
结果，而 producer-owned priority 缺陷在四项 consumer scorer 外。复审记录的两个
完整 episode 都是 `producer_objective_quality=null`、controller 概率保持
`0.5→0.5`，且两个最终 artifact 只改 `consumer.py`。因此不能把 DIST1 的完整事件
链误读为角色学习证据或独立第二 root。

## 最值得投入的候选

下一步只建议投入 **PIPE2 的零调用 root qualification**，保留 PIPE3 为主候选。理由
是 PIPE2 已经同时拥有真实中间 rows、recipient 自有 transform/load 工作和可执行的
adoption 检查；其主要阻塞点是可明确修复并可版本化的 fixture authority。MULTI3 还缺
最基本的 producer-wire→frontend-handler 绑定；CROSS5 需要重做 Java 行为执行基础设施；
DIST1 虽有历史 ledger，但责任覆盖和 root 独立性不合格。

这不是把 PIPE2 现有 receipt 当成科学结果，也不是自动选择新的 active benchmark。
只有以下门全部通过后，才能申请新的 benchmark-baseline 版本和 live experiment card：

1. **Fixture authority**：共同决定上游修复、版本化 derived root 或放弃 PIPE2；不得
   静默删 seed。source/expected shape、generator、seed split 和 digest 必须重新封存。
2. **完整责任评分**：producer contract、recipient self、adoption、recipient judgment
   和 UNKNOWN 使用独立字段；expected output、tests、private scorer 不进入任何 agent
   payload。
3. **真实公开判断**：recipient 在 terminal outcome 前对已绑定 delivery 做结构化
   accept/repair/reject/redo，并记录 observed artifact digest；其判断不能由 parent
   control 代替。
4. **later assignment/outcome**：RoleEvidence 必须在 assignment read-cut 前可见，
   `candidate_id@version`、menu、propensity、assignment 和 task start 完整绑定；下一个
   task 的独立 terminal quality、adoption、rework 和完整成本必须可回放。
5. **同信息 baseline parity**：uniform、no-update、raw、terminal、contextual 与 RARE
   在相同 menu、预算、arrival、UNKNOWN 分母和独立 history 下运行。

## 可复用材料

- PIPE2：`scripts/peerrolebench_pipe2_material_adapter_v2.py`、
  `peerrolebench_pipe2_runtime_qualification.py`、`peerrolebench_pipe2_runtime_worker.py`
  和 `peerrolebench_pipe2_fixture_shape_audit.py`；已有 sandbox、digest、2×2 control
  和 UNKNOWN 分类可直接复用。
- 通用协议：`RoleEvidenceOffer`、source-bound feedback adapter、selection
  preview→assignment→commit、native ledger/replay、cost receipt 和 PIPE3 的 responsibility
  gate 可以作为 PIPE2 的外层，不复制一套 selector。
- MULTI3：generator 的 backend/frontend/schema 结构、字段级 contract 和 direct
  composition audit 仅保留为 fallback；必须先加真实 sealed wire adapter。
- CROSS5：Python producer、canonical JSON schema、Java consumer 的源文件可作为
  cross-language stress candidate；需要固定离线 Java/org.json worker 后才有价值。
- DIST1：neutral-v2 ownership contract、producer scorer 设计、consumer scorer 和
  已验证 hash-linked ledger 可复用作诊断，但历史 v3 不得重算或升格。

## 停止条件

- PIPE2 generator/fixture 无法在不静默改写历史、不删除病例的前提下版本化；或完整 root
  仍不能通过 shape/replay gate：停止该 root，保留 receipts，不发 label。
- recipient 未真实读取 sealed artifact，或 scorer 无法区分 producer defect、recipient
  self、ignore/drop artifact 与 infrastructure UNKNOWN：停止，不扩大到 LLM/A800。
- judgment、assignment、task start、later outcome 任一无法在执行前后按 digest/版本
 绑定：停止，不把本 episode 写成 ArtifactRole 闭环。
- 同信息 baseline、独立 history 或完整 cost 无法冻结：停止正式效果流；不通过调 label、
  timeout 或分母放宽门槛。
- MULTI3 若继续失败于真实 wire adoption/schema ownership，维持 fallback；CROSS5 若
  Java consumer 不能在固定依赖下真实执行，维持 fallback；DIST1 继续保持 diagnostic-only。

## 结论

当前没有候选完整满足 ArtifactRole 的五段合同。PIPE2 是唯一值得继续做一轮严格、零
调用资格工作的第二 root；它通过后仍需独立 live history、baseline parity 和 later-use
结果，才能进入 benchmark freeze 或任何真实 LLM/A800 实验。本报告不修改 active
benchmark-baseline 文档，也不降低 Goal。
