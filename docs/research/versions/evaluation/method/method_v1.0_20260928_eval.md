# 方法论评价标准 v1.0

- **状态**：`ACTIVE`
- **评价对象**：[`method_v1.0_20260928.md`](../../method/method_v1.0_20260928.md)
- **用途**：审查更新机制是否可运行、可识别、实时且稳定。

## 必须通过

1. 给出完整事件 schema、合法信息边界、eligible/UNKNOWN/INVALID 规则、更新伪代码和 snapshot/restore。
2. 一次 feedback 只能按固定 lineage 更新一次；重复、乱序、延迟、版本替换和资源失败都有确定处置。
3. producer contract、recipient action、final outcome 和 cost 不混成一个 label；正常 recipient integration 不惩罚 producer。
4. 任何候选 updater 都有同信息 contextual trust、terminal-only、RLS/SGD/refit 对照。
5. 分别测 update latency、service lag、状态大小、drift 响应、旧任务峰值/平均遗忘和完整成本。
6. 现成 Laya/AnyJev/RLS/SGD 只能作为 backbone、运行时或 baseline；新颖性必须来自可反驳的更新机制或诚实的负结果。

## 反驳测试

若候选机制不能超过同信息 trust/bandit，或其收益来自额外 gold、私有 scorer、更多调用、复制的 realized memory 或事后 assignment，方法主张不成立。公式能运行不等于效果已证明；推导必须连接到可测的状态、复杂度和错误边界。

## 交付门

在真实 API 前先通过零调用 schema/replay 矩阵；在 A800 前必须有真实信号和明确瓶颈。没有实时性、时效性、稳定性三组独立证据，不得写“实时训练已实现”。
