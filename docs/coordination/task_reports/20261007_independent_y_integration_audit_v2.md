# 终端评分与真实 API 产物复核 — 2026-10-07

状态：`PARTIAL`；`goal_change_requested=false`。对应 ER-G1/G3/G4。

**后续解释更正（2026-10-07）：** [公开合同审查](20261007_public_contract_and_budget_repair.md)
发现适配器删掉了原生 T 时间戳要求。下文“局部合同违规”只适用于原生/私有检查
合同，不能读作违反 actor 当时可见的说明，也不能据此判 recipient 错误。
原始分数与日志不变；新公开材料不得与历史提示条件直接合并。

本轮目的不是再增加一种日志格式，而是回答：现有 C1 的 `J=accept` 与
`Qp=FAIL`、旧终局 `FAIL` 的冲突，究竟是 recipient 判断错误，还是测量对象不同？
成功标准是在不重跑 LLM、不改历史结果的前提下，用同一冻结终端检查评分四份真实
API 产物，并从实际 ledger、请求和响应验证归属；任一信息缺失保留 UNKNOWN。

## 结果与解释

对 [真实 C1 记录](../../../experiments/logs/n03_c1_parent_source_live_20261006_v1/summary.json)
的 parent source 与三条 target 分别执行新终端检查：

| 路径 | J | Qp | recipient check | 旧 D composite | 新 terminal holdout | 原生 later assignment |
|---|---|---|---|---|---|---|
| parent source | accept | FAIL | PASS | FAIL | PASS | 无 |
| no update | accept | FAIL | PASS | FAIL | PASS | 无 |
| contextual trust | accept | FAIL | PASS | FAIL | PASS | 有 |
| RARE | accept | FAIL | PASS | FAIL | PASS | 有 |

**这四条记录仅有一份独立代码快照**，不是四个独立样本、任务或重复实验。
新检查为两条冻结输入，检查最终字段投影、数量/顺序与解码后的 Unicode 值；四次
调用都是 3/3。新增 scorer wall time 合计 1.8253 秒；没有新 API/GPU 调用或策略更新。
原始文件的逐文件哈希执行前后一致。记录见
[配置与原始评分](../../../experiments/logs/n03_c1_posthoc_terminal_v2_20261007_v1/config.json)、
[逐样本结果](../../../experiments/logs/n03_c1_posthoc_terminal_v2_20261007_v1/summary.json)。

代码解释很直接：producer 使用 `str(datetime)` 产生空格分隔的时间戳；当前
processor 的 `datetime.fromisoformat` 接受该输入，并用 `isoformat()` 规范化输出。
旧 adoption 的 `A1_producer_boundary` 要求 producer 原始时间戳含 `T`，所以失败；
`A2_sink_adoption` 和新的终端行为检查则成功。

因此，`Qp=FAIL` 仍是一个真实的**局部合同违规**；recipient 的接受与下游可用性
相符，但不等于它对所有合同条款的判断都正确。原生 TeamBench spec 明确要求修复
producer 的序列化，故 **新 terminal PASS 不等于原生 benchmark 全部通过**。
本次没有运行 native grader，也没有替换旧 outcome、回填正式结果表或更改主指标。
它推翻的是“旧复合 FAIL 就足以证明下游不能使用、J 判断错误”的解释。

## 独立审查如何改变实现

第一轮 Codex 审查建议保留旧 native outcome 用于回放，新 Y 另存 sidecar；同时
指出 task-start 无原生 ID、worker-input digest 缺失、D 含 Qp 分量。这些被采纳。

第二轮独立审查与真实产物又纠正了第一轮中的两点：

1. **Y 与 L 不同。** no-update 没有 LaterAssignment，但必须具有同等的终端测量。
   所有已执行 episode 都可测量；只有已绑定 assignment 的目标才具备后续 L 的
   结构前提。本轮所有回执仍 `policy_update_allowed=false`，没有创建 credit。
2. **摘要覆盖范围不同。** delivery 哈希仅覆盖 `producer.py`，action-input 哈希
   覆盖四文件。二者不应相等。现在验证实际 producer 子集、完整 action input 和
   action 后 snapshot；事件顺序从原生 ledger 严格回放获得，不再信任手填索引。

先前 v2 的八个字典用例虽通过，却覆盖不到这些错误；原始输出与当时源码已经保留在
[历史资格目录](../../../experiments/logs/n03_independent_y_contract_v2_qualification_20261007_v1/)，
并追加 `INSUFFICIENT_FOR_PROMOTION` 审查记录，不抹掉这次不足。

## 实现、控制与边界

- [绑定器](../../../scripts/peerrolebench_independent_y_contract_v2.py)复用原生 ledger
  replay 和 action validator，重新计算真实文件、worker request 与 response 摘要。
  原生 `TerminalOutcome` 不新增、不覆盖；事后标签不能倒填历史 arrival/read cut。
- [冻结 holdout](../../../configs/aamas2027/pipe3_terminal_holdout_v2.json)在新评分前
  保存输入与预期输出，v2 adapter 校验固定哈希。它在旧 API 运行之后制定，故仅是
  **post-hoc development diagnostic**，不是确认集或新的预注册实验。
- 新 worker 检查 JSON 解码后的字符，避免将合法 `\u` 转义误判为 UTF-8 失败。
  两个同根 seed 的 12 个沙箱控制验证：完整修复、只修 recipient、合法 Unicode
  转义均 PASS；原始和只修 producer 均 FAIL；PermissionError 为 UNKNOWN。
  [13 项测试复跑](../../../experiments/logs/n03_terminal_scorer_v2_20261007_rerun1/summary.json)
  通过，并拒绝四类坏响应/manifest。
- [真实历史绑定回归](../../../experiments/logs/n03_y_binding_real_artifacts_20261007_v2/summary.json)
  6 项通过；[15 个回执突变](../../../experiments/logs/n03_c1_posthoc_terminal_v2_20261007_v1/mutation_results.json)
  拒绝伪 assignment、坏哈希、换产物、D 改名 Y、重复、UNKNOWN、倒填时间与早读标签。
- worker 与被测代码仍在同一 Python 进程，仅适用于非对抗情形；“独立”指新的评分
  执行/来源，不声称统计独立、因果识别或能抵抗恶意代码。CPU time/RSS 未单独测量。

## 对主线的影响与下一步

1. **不再用这组 static producer 快照直接做效果竞赛。** 四条最终产物相同，当前
   producer 缺陷可被 recipient 消化，所测终端行为没有区分度；再多跑同一卡难以
   判断 selector 改进。旧样本保留作“合同违规但可用”的校准控制。
2. 下一个最小验证应比较“局部合规且可用 / 局部不合规但可用 / 局部不合规且不可用”
   的机制控制，再检查两个候选 root 的原生任务是否自然提供这些差异。控制样例只
   检查测量辨别力，不能伪装成 benchmark 数据。优先复用现有原生任务/真实记录，
   不先换模型、训练 backbone 或重复启动相同 API 小流。
3. 新 live 版本必须对所有 arms 测同一终端结果，将责任证据、benchmark 合规和
   terminal utility 分列；后续 L 绑定新 Y 并保留本 arm 合法反馈通道，不能继续从
   旧 composite outcome 偷渡标签。源 gate 的 `y_complete` 目前也是 legacy
   completeness，尚未完成替换；active 方法与主 benchmark 未因此自动变更。
4. 论文的测量说明应明确区分局部合同与最终可用性，但不把这次事后诊断写成学习
   效果。主指标或故事线如需改变，另行讨论，不能借诊断结果降级 Goal。

ER-G1/G3/G4 部分前进：找到了真实的测量混淆，且已有可复用的 manifest-bound scorer
与实际记录绑定器。ER-G2 在线训练、独立 histories、跨 root 泛化、完整 baseline
和 ER-G5 科学投稿 gate 仍未满足；三份科学核验保持 `NOT_READY`。
