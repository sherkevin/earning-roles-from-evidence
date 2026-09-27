# Task report：DIST1 neutral-v2 contract qualification / 2026-09-27

状态：`PARTIAL`（工程契约门通过；benchmark、学习和方法主张仍开放）；
`goal_change_requested=false`。

## 这一步对应的 Goal 标准

本任务对应 Goal v1.0 的 G2（可审计的真实协作闭环）、G3（公平且可验证的
benchmark/baseline）和 G4（证据驱动的候选方法选择）。它只处理“任务公开接口、
材料版本、评分器和 runner 是否对同一语义”的前置条件，不证明 situated judgment
有信息价值，也不启动训练或 A800。

## 运行前冻结的条件

- TeamBench pin：`d185aef1916fd86a9ba554d581fd256319a973af`。
- DIST1 结构 root 未改变；材料契约从 `dist1-neutral-v1` 升为
  `dist1-neutral-v2`，版本标识为 `peerrolebench-dist1-materials-v2`，公开接口为
  `dist1-queue-interface-v1`。
- 新卡为
  [`n03_peerrole_dev_neutral_v2.json`](../../configs/aamas2027/n03_peerrole_dev_neutral_v2.json)。
  它仍然关闭 controller update、科学主张和 GPU；最多只允许在全部零调用门通过后
  消耗一条新的真实 episode。
- 旧 v1 真实 episode 的 UNKNOWN 结果不重跑、不改写，也不与 v2 合并。

## 零调用证据

以下结果都没有 LLM 请求、GPU 作业或 native grader：

1. v2 adapter 回归：15 个针对 adapter/manifest/runner 的 pytest 通过；未知
   `material_adapter` 现在会立即报错，不再静默退回另一种材料。
2. v2 static provenance：
   [`n03_manifest_provenance_20260927_v4`](../../experiments/logs/n03_manifest_provenance_20260927_v4/)
   中两个 root 的 static visibility 均通过，`benchmark_frozen=false`。
3. v2 runtime payload preflight：
   [`n03_material_payload_runtime_preflight_20260927_v2`](../../experiments/logs/n03_material_payload_runtime_preflight_20260927_v2/)
   通过 producer/recipient dispatch、selected delivery digest、operator ledger deny
   和 lineage hash-chain；candidate code 未执行。
4. producer scorer qualification v2：
   [`n03_producer_scorer_qualification_20260927_v4_2012`](../../experiments/logs/n03_producer_scorer_qualification_20260927_v4_2012/)
   的 corrected control 为 `PASS, label=1, quality=1.0`；原始 buggy 和两个
   near-miss 为 `FAIL`；malformed source 和四类 response mutation 为 `UNKNOWN`。
   因而 response/label 语义和资源异常保护通过了零调用矩阵，但 scorer 仍标记为
   `scorer_is_qualified=false`，因为它仍是 TeamBench-shaped、非对抗 Python worker，
   尚未完成独立 root 与 live attribution 资格。
5. v2 prepare：
   [`n03_peerrole_dev_neutral_v2_prepare_20260927`](../../experiments/logs/n03_peerrole_dev_neutral_v2_prepare_20260927/)
   成功生成 seed 0/1 材料；公开文本逐字固定了 `get() -> None | (message, receipt)`、
   非阻塞空队列、`ack`/`nack` 及容量语义。

## 发现与解释

v1 的真实 episode 已证明旧任务文本存在科学上不可接受的语义歧义：producer 和
recipient 按实际交付形成了自洽的 `(receipt, message)` / `acknowledge` 协议，hidden
scorer 却要求另一套 `(message, receipt)` / `ack`/`nack` 非阻塞接口。v2 修正的是
benchmark contract，不是模型能力。任何 v2 结果都必须单独编号，不能把 v1 的 UNKNOWN
当成 v2 的负标签或正标签。

公开契约变得更明确也会降低开放式协作难度；这不是隐藏测试隔离已经完成的证明。冻结
前仍需说明这些语义来自公开 API 设计，而不是从 hidden test 名称反推，并在第二个结构
root 上复现同样的责任、交付和评分边界。

## Goal 对照

| 标准 | 状态 | 证据/原因 |
|---|---|---|
| 真实 API 可调用并可审计 | `PARTIAL` | v1 三次真实请求完整记录；v2 尚未发 API |
| 公开材料与 scorer 语义一致 | `PARTIAL` | v2 文本、adapter、零调用 scorer 矩阵一致；仍非正式 benchmark |
| producer 质量可作为标签 | `OPEN` | corrected controls 只证明实现路径，不能证明任务标签的外部效度 |
| recipient judgment 进入未来职责 | `OPEN` | v1 无 outcome/update；v2 尚未运行 |
| benchmark/root split 与 baseline 冻结 | `OPEN` | manifest 仍 `CANDIDATE_NOT_FROZEN`，PIPE3 尚未 live qualification |
| RARE/实时更新/A800 | `OPEN` | 依赖前述数据资格；没有新训练或 GPU 证据 |

## 下一步

在不修改 Goal 的前提下，若当前报告及 v2 产物进入版本库，才可按 N03 预算至多跑
一条 seed-0 v2 真实闭环。该调用只回答“修正后的公开契约能否让 scorer/recipient
形成完整可判定链”，不回答方法优越性；任何 UNKNOWN 都关闭这条 integration route，
不增加重试、不启动 PIPE3 或 A800。若链完整，再单独分析 producer label、recipient
outcome、assignment 和 controller update 是否真的产生可学习信号。
