# Benchmark 与 baseline 评价标准 v1.1

- **状态**：`ACTIVE`
- **类别**：evaluation/benchmark-baseline
- **评价对象**：[`benchmark_baseline_v1.0_20260928.md`](../../benchmark-baseline/benchmark_baseline_v1.0_20260928.md)
- **生效日期**：2026-09-28
- **前一版本**：`benchmark_baseline_v1.0_20260928_eval.md`
- **用途**：审查实验是否真的能识别故事和方法主张；不保证录用。

## A. Benchmark 有效性硬门

- 至少两个结构不同 root，且 root 级 development/confirmation split 在看结果前冻结；强录用目标是三个及以上 root 或预注册的精度证明。
- 每个 root 有真实 producer→recipient 依赖；producer contract、recipient use/modify/rework、sink adoption 和 final outcome 分开测量。
- task/source/tests/expected/scorer/operator ledger/candidate workspace 的可见性、写权限、网络、时间和资源边界运行前冻结。
- 任务文本不泄露修复方向、hidden test 名称、答案或后验标签；候选 agent 不能读 private gold、其他 policy state 或 operator ledger。
- scorer、ledger、lineage、UNKNOWN 和资源失败有零调用 mutation matrix；完整覆盖不足只能 UNKNOWN。

## B. Baseline 公平性硬门

每个主 baseline 必须提供真实可执行入口、版本、配置和相同事件 schema，而不是只写名字。至少包括：uniform、no-update、raw acceptance、terminal-only、同信息 contextual trust/bandit、pooled controller、closest published method、RARE 以及必要的核心消融。

必须有一张 parity table，逐项核对：

- 候选集合和初始状态；
- 可见字段、feedback eligibility、UNKNOWN/selected-only、arrival order；
- exploration/propensity、LLM/tool/API/token/scorer/retry/communication 预算；
- state capacity、模型/backbone、并发和 wall-clock 预算；
- 训练、判断、评估和返工成本。

任何 baseline 读到更多信息、拥有更多预算或继承 proposed policy 的 live memory，整组比较无效。

## C. 实验设计与统计硬门

执行前冻结 RQ、primary metric、方向、effect size 口径、split、seeds/streams、停止规则、异常 disposition 和主分析脚本。主结论必须来自独立 live histories；matched replay 只能诊断机制，不能替代泛化结果。

每个主比较都要报告 per-root/per-stream 原始结果、均值或中位数、95% uncertainty interval、effect size、失败和 UNKNOWN 分母。样本量必须有精度或功效理由；无法达到预设精度时只能标为 exploratory，不能用更多聚合掩盖样本不足。禁止只报单一成功率、单一 episode、最好 seed 或 post-hoc 选择指标。

## D. 结果完整性与可复现性

至少报告四组结果：

1. 信息价值：judgment 对 independent contract/later-use 的增量预测与校准；
2. 闭环效果：执行前 assignment change、未见 root 质量、返工和完整成本；
3. 在线性质：update/service latency、state size、drift recovery、旧任务遗忘；
4. 边界：版本替换、延迟/乱序、consumer 自有错误、scorer/资源失败和 UNKNOWN 率。

原始配置、逐样本/逐事件 JSONL、模型与数据 hash、代码 commit、硬件、API usage、失败日志、统计脚本和复现命令必须进入补充材料或可访问 artifact。AAMAS 官方也要求 claims 有 evidence 支持并鼓励提供代码、数据和详细实验材料。[Findings](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/findings/)、[Submission Instructions](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/)

## E. 基座、污染和复现硬门

权威基座必须固定 source URL、commit/tag、license、数据版本、scorer 版本和完整生成器 hash；自定义 `PeerRoleBench-TB` 扩展必须公开复现入口，并说明为什么它仍是任务适配而不是未经验证的新 benchmark。运行前做 task/source/test/expected/LLM contamination audit；任何答案、hidden test 名称、后验 label 或其他 policy memory 泄漏都使该 root 失效。

每个 arm 必须保留配置、prompt/template、model/API route/version、temperature、tool、token、并发、timeout、retry、storage、GPU 和调参记录。clean environment 从 manifest 能重建数据、runner、scorer、主分析脚本和结果摘要；不能只提供截图或手工 notebook。

## F. 基线、统计和异质性

除通用矩阵外，必须有与主张最接近的已发表方法 faithful adapter；oracle 只能作为上界，不能作为唯一强 baseline。所有条件的调参只在 development roots 完成，confirmation 只执行封存配置。主分析要报告 per-root/per-stream effect size、95% interval、总体和异质性、失败/UNKNOWN/未启动分母；多重比较要预先说明校正策略。无法达到预设精度时只能标 exploratory。

质量和成本要同时报告 Pareto 或预先定义的 scalar utility，不能只挑质量上升的图。需要记录 assignment 实际采用率、judge calibration/reliability、selection propensity、负迁移、OOD/cross-root transfer 和模型版本漂移。

## G. 两档结果标准

- **Findings-ready**：一个可复现、范围有限的 benchmark/方法/负结果，至少有一个独立确认或严格的受控诊断，明确不推广到未测范围。
- **Proceedings-ready**：至少三个结构独立 root，或在只有两个 root 时提供预注册的精度/广度理由；每个主条件有多条独立 live streams，完成同信息强 baseline、未见 root、完整成本和 clean replay。

两档都不能把 fixture/协议资格写成科学效果，也不能把 UNKNOWN 删除出分母。

## E. 一票否决与停止

任务泄漏、root 非独立、scorer/ledger 隔离失败、baseline 信息不公平、UNKNOWN 被当负例、主指标看结果后改变、没有独立 confirmation、没有失败分母或没有完整成本时，不得写主结果。RARE 未超过 contextual trust 或质量—成本目标不成立时，停止扩展模型/A800，报告未支持机制。

## 来源边界

AAMAS 官方要求提供 relevance、validation、evidence、state-of-the-art comparison 和 reproducibility；root 数量、责任分离、parity table、统计精度、成本口径和 UNKNOWN 分母是本项目的严格实验识别标准，不是 AAMAS 官方指定 benchmark 清单。来源见 [`docs/research/20260928_evaluation_criteria_provenance.md`](../../../20260928_evaluation_criteria_provenance.md)。
