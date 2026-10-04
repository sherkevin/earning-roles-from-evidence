# 长任务阶段检查：从 history 接缝回到三份验收标准

日期：2026-10-04  
状态：`PARTIAL`  
对应 Goal：ER-G1、ER-G2、ER-G3、ER-G4；Goal 未修改。

## 本次动作的目的

本次不是追求一个“通过”的数字，而是确认上一小任务是否真的推进了论文主线：

```text
source situated judgment
→ 可归因 role evidence
→ 执行前 later assignment
→ target delayed outcome
→ 可持久、可重放的 peer history
```

只有这条接缝成立，history/no-history/shuffled/reset 四格才有可解释的实验对象；若接缝不成立，继续调用真实 API 或 A800 只会增加不可归因数据。

## 冻结对象与衡量指标

正式回执为 [`n03_peer_history_integration_20261003_v2`](../../../experiments/logs/n03_peer_history_integration_qualification_20261003_v2/)，配置先写入，绑定提交 `df8f3f8`、组件 SHA-256、seed `(0,1)`、candidate registry、fixture scorer 和零 API/GPU预算。

本任务只使用以下工程指标：

| 指标 | 通过条件 | 观察结果 |
|---|---|---|
| delayed-credit 身份 | history receipt 的 credit digest 与已提交 credit 完全相同 | 通过 |
| source/target lineage | source evidence → assignment → selection → target outcome 顺序和 read-cut 全部通过 | 通过 |
| append 原子性 | seal 后注入 append failure，不能留下 orphan seal，重试可成功 | 通过 |
| mode isolation | `off` 与 `append` 的 ledger/selection trace 相等 | 三个 control 均通过 |
| responsibility safety | recipient-owned/mixed 不生成 producer history | 两个 control 均 `NOT_RUN_UNKNOWN` |
| 工程回归 | composition 11 + adapter 5 + binding/history 10 个 focused tests | 26 passed |

正式回执的 producer-owned ledger digest 为 `2cba5e6013b46da927993ac022612c8261ac0271af05389186615ba29f0005f9`；append 模式增加一条 `PASS` history，未改变 selection trace 或 policy update count。回执明确 `scientific_claim_allowed=false`，没有 LLM/API/GPU 调用。

## 与三份标准的对照

### 故事线与创新点

推进了“situated judgment 之后的责任证据必须能进入未来状态”这一必要工程前提；没有证明 judgment 对 peer suitability 有信息价值，也没有证明自进化或质量/成本增益。故事线验收仍为 `PARTIAL`，不能把本回执写进论文效果段。

### 方法论

source→target binding、delayed-credit digest 和 history append 已有可执行边界；但 selector 只得到 projection，尚未在下一次执行前消费它，因此“更新导致未来选择变化”仍未实现。跨进程 credit/policy/history 的共同恢复事务和实测 cost 也未关闭。方法验收仍为 `PARTIAL`。

### Benchmark + baseline

本任务没有增加 structural root、独立 live history 或 baseline arm。PIPE3 仍是单 root 工程候选，PIPE2 authority 和 closest adapter 仍开放，seven-arm same-information parity、完整成本、precision/UNKNOWN 分母尚未冻结。benchmark/baseline 验收仍为 `NOT_READY`。

## 当前距离与下一步放行条件

现在可以进入下一项**零调用 matched replay**，但不能进入真实 API/A800。下一项必须先在文档中冻结四格的操作和指标：

1. `history`：E0 credit 后持久化 history，E2 read-cut 消费 projection；
2. `no-history`：同一 E0/E1 轨迹但清空 projection；
3. `shuffled-history`：同样记录但违反 arrival/read-cut 的顺序，必须 `UNKNOWN/no-update`；
4. `reset-history`：重启后只恢复合法 snapshot，缺失/不匹配必须 fail-closed。

四格的最小可观测量为：E2 chosen peer、propensity、history input digest、selection event digest、later outcome、UNKNOWN reason、append/update latency 和完整成本字段。没有这些字段，四格不能算实验矩阵，也不能作为 AAMAS 结果。

这次检查没有降级任何目标；`goal_change_requested=false`。下一次完成四格协议与零调用回执后，重新对照三份标准，再决定是否有资格开一条有界真实 API 链。
