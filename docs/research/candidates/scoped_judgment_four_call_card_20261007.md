# 四次判断调用：评价对象能否分开

状态：`PREPARED / AWAITING_ADDITIONAL_BUDGET`。不修改 Goal 或 ACTIVE 方法。

## 只回答一个问题

给接收方明确公开职责后，它能否分别判断“producer 交付是否合规”和“自己的
processor 是否还需修改”，而不把自己的集成工作记到 producer 头上？
这是一张单根固定材料诊断卡，不是论文 benchmark、准确率估计或方法效果对比。

## 已封存的输入与核验

- [机器卡](../../../configs/aamas2027/n03_scoped_judgment_diagnostic_v1.json)
- [四份实际请求与私有映射](../../../experiments/logs/n03_scoped_judgment_prepare_20261007_v2/)
- parent manifest SHA-256：`3d46c2398cb814906500b958b3b6247c71dc22c4b4cdc4742958e5a23c4da11b`
- [本地独立标签检查](../../../experiments/logs/n03_scoped_judgment_gold_20261007_v1/summary.json)

P、R 各用历史真实 API 修复产物和原生未改产物，交叉为四格。两类来源均以同一
规则删注释/docstring，support 源码和任务说明相同；来源与期望标签不发给模型。
单独执行两份 producer 与两份 recipient，不重复执行四种完整管道：

| 组件 | 本地结果 | 解释 |
|---|---|---|
| 历史 producer | 三项 PASS | 有限 producer 检查通过 |
| 原生 producer | 仅 P2 FAIL | 原始时间戳未满足新版公开 T 要求 |
| 历史 processor | 三项 PASS | 合规上游输入下的有限 recipient 检查通过 |
| 原生 processor | 执行发生 UnicodeEncodeError | recipient 自身无法处理合法输入；后续两项因此失败 |

这些是四次本地沙箱执行，零 API、零 GPU；仅用来支持预期标签。没有改标签迁就
结果，没有执行新的 recipient action。通过有限测试不保证完整合同正确。

冻结发送顺序：P合规/R需改 → P不合规/R需改 → P不合规/R无需改 → P合规/R无需改。
模型只看到 opaque case ID，各请求相互独立，没有前一格结果或历史对话。
`needs_change` 指 processor 面对合规上游时的自身职责，不要求它弥补 producer 违约。

## 请求与停止条件

使用已用过的“内部”服务 `qwen3.8-max`，temperature=0、thinking disabled、SSE，
每请求最多 1024 输出 token、300 秒，最多 **4 次请求/4 次 episode**，零重试。
只返回两个判断字段及理由，不生成代码、action、policy update 或训练。

成功须四格 producer verdict 与 recipient needs_change/target_paths 全部匹配，
artifact digest 正确，结构有效；producer 负例须引用 C2，并在理由指出时间分隔
不匹配。格式、传输、绑定错误，或任何不正确/uncertain 判断即终止，不补样本、
不改 prompt、不换模型。若提前终止，剩余格记为未执行，不算失败或已完成。

即使 4/4，也只能说明这四份固定代码在此条件下可分；历史产物还有校验/编码等
其他变化，不能说识别仅由 T 要求引起，不能排除风格捷径。不自动追加动作实验。

## 为什么需要另行确认预算

[累计清点](../../../experiments/logs/n03_attempt_budget_census_20261007_v1/summary.json)
已记录 31 次任务尝试，原计划上限为 24；此前越界保留在账，不能重置。当前请求
是最多追加 4 次，若全跑完累计为 35。机器卡和准备脚本均不能调用 API；确认后
才建立版本化执行卡，复核输入摘要、独立标签回执和累计数，复用真实 transport。

本卡不改变论文科学标准。成功后也仅获得进一步研究判断信号的理由；正式论文
仍缺自然独立交付、未来任务收益、强对照、跨根泛化及成本/稳定性证据。
