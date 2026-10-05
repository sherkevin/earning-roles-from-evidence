# 六份研究主文档质量审计 — 2026-10-05

状态：`PARTIAL`。本审计回答“六份文档在哪里、写得是否标准/好/完备”，不把文档质量
误写成 benchmark、方法或论文已经达标。`goal_change_requested=false`。

## 1. 六份文档的唯一生效位置

六个类别只有一个 `ACTIVE` 版本，登记在
[`docs/research/canonical/active_versions.json`](../../research/canonical/active_versions.json)，
人类导航入口是 [`docs/research/canonical/README.md`](../../research/canonical/README.md)。

| 主文档 | 当前文件 | 对应要求文档 |
|---|---|---|
| 故事线与创新点 | [`storyline_v1.1_20260928.md`](../../research/versions/storyline/storyline_v1.1_20260928.md) | [`storyline_v1.3_20260928_eval.md`](../../research/versions/evaluation/storyline/storyline_v1.3_20260928_eval.md) |
| 方法论与训练合同 | [`method_v1.1_20260930.md`](../../research/versions/method/method_v1.1_20260930.md) | [`method_v1.2_20260930_eval.md`](../../research/versions/evaluation/method/method_v1.2_20260930_eval.md) |
| Benchmark、baseline 与实验计划 | [`benchmark_baseline_v1.1_20260930.md`](../../research/versions/benchmark-baseline/benchmark_baseline_v1.1_20260930.md) | [`benchmark_baseline_v1.2_20260929_eval.md`](../../research/versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md) |

`GOAL.md` 是不可静默降级的目标章程；task reports、实验日志和论文稿是证据/进展面，
不构成第七套标准。历史版本仍在相同目录中，但不能与上表并列解释为 active 定义。

## 2. 评分口径

分数只评价文档作为研究合同的质量：结构清楚、问题是否 sharp、能否独立实现、能否
把主张映射到证据、版本/状态是否诚实。它不是 AAMAS 官方分数，也不是录用概率。
“完备性”另看硬标准是否已经有可执行定义和证据；科学结果尚未完成不应被伪装成文档
问题，也不能因为文档写得漂亮就算通过。

| 文档 | 文档质量 | 作为当前科学合同的完备性 | 结论 |
|---|---:|---:|---|
| 故事线与创新点 v1.1 | 8.0/10 | 6.5/10 | 主线很清楚，创新已收敛为一个闭环；缺少正文要求的五个最近邻 novelty table、可复现实验最小反例和逐条 claim→evidence 索引 |
| 故事线评价 v1.3 | 8.7/10 | 8.0/10 | 六份中最完整的审查规范之一；把 official floor、项目识别门、强录用目标分开，但仍是内部标准，不是外部审稿表，缺少机器可执行 checklist/评分记录 |
| 方法论与训练合同 v1.1 | 7.8/10 | 6.5/10 | 事件时序、三层 gate、publish/update 分离和 preview→assignment→commit 很扎实；backbone、最终 updater、漂移/遗忘参数仍开放，且历史 amendment 混入正文 |
| 方法论评价 v1.2 | 8.5/10 | 7.5/10 | 对可运行性、实时性、稳定性、统计和反驳条件写得严格；还缺每个 hard gate 的唯一执行命令、最小 artifact schema 和通过/失败自动判定 |
| Benchmark+baseline v1.1 | 7.7/10 | 5.5/10 | 轨道分层、责任边界、baseline 角色、RQ、指标和停止规则完整；benchmark 未冻结、closest published 未实现、独立 root/live history/cell manifest 尚未齐备 |
| Benchmark+baseline 评价 v1.2 | 8.8/10 | 8.0/10 | 选型评分卡、baseline parity、实验矩阵、统计精度门、truth table 和停止规则都具备；仍不能替 benchmark 实际 authority、运行结果与独立 confirmation |

总体判断：**作为内部研究治理文档，六份已经达到可用且偏严格的标准；作为“完备的
论文研究合同”，还没有完备；作为已达到三份验收标准的研究成果，明确没有达到。**

## 3. 做得好的地方

1. 六份文档有唯一 active registry，历史版本没有冒充当前定义，状态字段也明确区分
   “active 文档”和“科学已验证”。
2. 故事线没有把“角色名/接受率/终局成功”冒充角色学习，而是坚持
   `delivery → situated judgment → attribution → future assignment → unseen utility`。
3. 方法文档把 public publication 与 persistent update 拆开，写出了 UNKNOWN、late/
   duplicate、assignment-before-selection 和 selected-only 语义；这已经能约束实现。
4. Benchmark 标准没有只列论文名字，而是要求 authority、信息/成本 parity、root split、
   cell manifest、统计精度和 UNKNOWN 分母；这符合审稿人真正会追问的可识别性问题。
5. 三份评价文档都明确写出不是什么：不是官方录用保证，zero-call fixture 不能升级成
   方法效果，baseline 未冻结不能启动正式 efficacy/A800。这种边界是可信度的优点。

## 4. 当前文档本身的缺口

### 4.1 故事线文档缺少可直接执行的 novelty 证据表

评价标准在故事线评价 v1.3 §B 要求至少五个最近邻，主文档目前只有机制叙述和反驳
条件，没有实际表格、来源、信息边界和“为什么同信息替代不能解释收益”。因此主线是
好的研究假设，但还不是审稿人可直接检查的 novelty package。不能凭空填论文名称；下一步
需要建立带来源的 novelty table，并把每一行绑定到实验对照或明确的 `NO-GO`。

### 4.2 方法文档此前缺少符号实例；现已补齐最小实例表，但最终方法仍未锁定

方法 v1.1 新增 §1.1，将 `x_t,C_t,a_t,o_t,m_t,Q_p,J,A,Y,E,w_t,R_t,g_t,B_k,L_j,θ`
逐一绑定到 PIPE3 episode 的真实字段/事件，说明 `UNKNOWN` 如何出现。这个修复解决了
“公式有符号但没有 case”的文档缺陷；它没有决定最终 backbone、representation 或
updater。方法评价仍不能判通过，因为实时性/时效性/稳定性必须由独立 live experiment
测量，而不是由符号表替代。

### 4.3 Benchmark 主文档存在过时的 baseline 名称歧义；已做文字收敛

原矩阵只写 `contextual_trust` 为 strongest same-information control，而同一文档后续
amendment 已认定它只消费 context×candidate Beta，不能满足 RARE 的同 `φ`/base-score
要求。现已把矩阵拆成：候选 strongest comparator `contextual_trust_linear`，以及保留为
diagnostic 的 `contextual_trust`。这只是把已确认的 parity 结论同步到矩阵，不代表
`contextual_trust_linear` 已冻结；baseline 仍是 `NOT_FROZEN`。

### 4.4 六份正式文档混入了较多 dated progress amendments

这提高了审计可追溯性，但降低了“读者拿到当前合同即可实现”的干净程度：规范、状态、
失败历史和下一步建议交替出现。后续应把不可变规则留在六份主文档，把实验进展移到 task
report，再在主文档只保留一个短的“当前状态与证据索引”段。不能删除历史记录，也不能
覆盖旧版本；应在下一次版本升级时整理。

### 4.5 要求文档很严格，但还不是自动验收器

六份文档能告诉我们“必须检查什么”，但还不能单独运行出 PASS/FAIL：例如 novelty table
完整性、每个 cell 的 power/precision 字段、完整成本守恒、每个 hard gate 的 artifact
路径仍需人工对照。已有 `check_aamas_documents.py` 只能检查文档链接、映射和科学 readiness
状态，不能代替 benchmark/scorer/live evidence。下一步应把三份评价标准各自收敛成一张
machine-checkable gate matrix，而不是继续扩写散文。

## 5. 距离目标的客观结论

- **文档治理**：六份唯一 active 文档、版本入口和对应关系已经清楚；可用性约 8/10。
- **故事线**：问题切口和主机制基本清楚，但 novelty evidence package 未完成；约 65% 的
  验收内容具备定义，未具备结果。
- **方法论**：协议/数学对象/时序已能指导当前工程实现，但最终训练方法和实时/遗忘结果
  未锁定；约 60–65%。
- **Benchmark+baseline**：候选与评价规则很完整，科学选型和执行矩阵尚未冻结；约 45–55%。
- **论文可投稿性**：当前仍是 pre-results research package，不能把六份文档的完整性写成
  AAMAS 论文已经达标。

这不是 Goal 降级，也不是因为实验失败而降低标准；它只是把“文档质量不错”和“研究证据
已经完备”分开。下一步优先级是：补 novelty table → 生成 machine-checkable cell/gate
matrix → 完成 chosen-candidate 独立 outcome 的 live parity → 再决定是否冻结 baseline 和
启动真实 API/A800。
