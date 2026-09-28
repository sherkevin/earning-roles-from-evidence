# 方法论评价标准 v1.1

- **状态**：`ACTIVE`
- **类别**：evaluation/method
- **评价对象**：[`method_v1.0_20260928.md`](../../method/method_v1.0_20260928.md)
- **生效日期**：2026-09-28
- **前一版本**：`method_v1.0_20260928_eval.md`
- **用途**：投稿前审查方法是否真正新、可运行、可验证、实时且稳定；不保证录用。

## A. 形式完整性硬门

方法必须让独立读者可以从一条事件重放出一次选择和更新，至少给出：

- 原始输入、公开/私有状态、候选集合、动作、反馈和 `UNKNOWN` 的精确定义；
- 选择发生在何时，哪些结果在当轮不可见；
- 更新伪代码、初始化、探索、版本替换、snapshot/restore、异常和停止规则；
- episode index 与 feedback-arrival index 的区分，watermark/replay 和 late correction 的幂等语义；
- 状态容量、context 编码/哈希、淘汰、跨 context 泛化和时间复杂度；
- 每个不变量的测试或证明：一次事件一次更新、UNKNOWN no-op、lineage 完整、重放一致。

只有公式没有这些语义，不能称为可运行方法。

## B. 创新识别硬门

必须完成 closest-method audit：对最近邻逐项比较信息、参数更新、计算预算、记忆范围和输出行为。若把冻结表示加小 head、RLS、online SGD、周期 refit、普通 bandit 或现成 JEV wrapper 作为新方法，必须证明其新增机制在同信息、同预算、同接口下不可被 baseline 复现；否则只能作为 baseline 或工程组件。

必须有：

1. 最小核心消融；
2. 同表示/同初始化/同探索的 updater 对照；
3. 去掉责任门、延迟处理或遗忘保护后的反事实对照；
4. 一项预注册的失败条件，结果不佳时不能事后加模块救场。

## C. 在线性质硬门

每条合法 selected-only feedback 都要报告：update p50/p95、service lag、端到端选择延迟、状态字节、CPU/GPU/token/tool/人工成本。必须分别测：

- **实时性**：更新是否在服务预算内完成，而非批量 refit 冒充逐条更新；
- **时效性**：预设 drift 后在窗口内恢复，包含延迟/乱序反馈；
- **稳定性**：旧 root/task holdout 的峰值和平均遗忘、恢复窗口、UNKNOWN 率；
- **安全性**：责任不明和 recipient 自有错误不会错误惩罚 producer。

报告完整分布和不确定性，不能只给平均 latency 或“没有观察到遗忘”。

## D. 训练与系统证据

若论文声称实时训练，必须说明哪些参数冻结、哪些参数更新、每次更新读写多少数据、是否触发 full-model forward/backward、如何并发、如何恢复和如何限流。真实 API、模型版本、代码 commit、硬件、配置、原始事件和失败必须可复现。A800 结果只能回答已冻结实验卡上的一个瓶颈，不能替代算法/benchmark 资格。

## E. 目标函数、调参与统计

方法必须明确优化/评估对象至少属于以下之一：role-evidence prediction risk、future assignment regret、或预先定义的 team quality–complete-cost utility。调参只能使用 development roots；confirmation root 的 updater、阈值、context vocabulary、遗忘系数和停止规则必须在看到结果前封存。主比较必须给 effect size、95% interval、独立 stream 分母和精度/功效理由，不能把一次概率变化当学习效果。

## F. 系统负载与漂移定义

实时性不只看 p50/p95。必须在预注册的并发、突发 arrival rate 和状态大小下报告吞吐、队列/backlog、event-arrival→next-decision service lag、峰值 CPU/GPU/RAM、持久存储、token/API/tool 成本。时效性必须指定 drift 类型、发生点和响应窗口；稳定性必须报告 old-root 峰值/平均 forgetting、恢复时间、UNKNOWN 率及不确定性。迟到 judgment 的 later-outcome correction、撤销和 checkpoint-resume 要有逐事件 state digest。

## G. 选择偏差与判断可靠性

如果 feedback 只来自 selected peer，必须记录 propensity，并给出 selection bias、missing label 和 judge reliability/calibration 的估计或敏感性分析。judge 与 producer 使用同一模型时，要控制或承认共享错误、prompt 污染和信息泄漏；没有独立 gold 时，明确可识别范围，不把 judge agreement 当 ground truth。

## H. 两档交付门

`Findings-ready` 可以是一个可复现、范围有限的在线机制或强负结果；`Proceedings-ready` 还必须有完整机制闭环、独立 confirmation、closest-method 对照、负迁移/遗忘分析和负结果解释。两档都要求 clean-environment replay 能重建主表；没有 replay 只能是 exploratory。

## I. 反驳与停止

以下任一情况时，方法主张不通过：

- contextual trust/bandit 在相同信息和成本下解释全部收益；
- 更新收益来自额外 gold、private scorer、复制 proposed policy memory 或事后 assignment；
- late correction、重复/乱序、版本替换没有确定语义；
- 只有零调用 fixture 或单次 API 链而没有独立 live streams；
- 实时性成立但旧任务遗忘、完整成本或错误归因恶化且未报告。

## 来源边界

AAMAS 官方来源支持 soundness、reproducibility、evidence 和 claims justification；形式不变量、closest-method audit、延迟/遗忘/成本门和训练透明度是本项目为检验“实时更新”主张而制定的严格标准。来源见 [`docs/research/20260928_evaluation_criteria_provenance.md`](../../../20260928_evaluation_criteria_provenance.md)。
