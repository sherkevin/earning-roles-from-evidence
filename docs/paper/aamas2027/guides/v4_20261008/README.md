# Guide v4：实验结果与 Benchmark+Baseline 关闭门

日期：2026-10-08。状态：`CURRENT_CONDITIONAL_GUIDE_PENDING_SCIENTIFIC_EVIDENCE`。

用户指出 v3 的关键缺陷：它能判断结果方向是否合理，却不能在实验完成后签收
benchmark+baseline 验收。v4 保留 v3 的机制条件、赢/平/输边界和反证，新增第 5 页
“closure receipt”，把验收写成七个必须同时通过的门。

## 关闭语义

Guide 方向一致是 B5 的必要条件，不是充分条件。只有 B1–B7 各出现一次且全部 `PASS`，主轨所需 future-assignment→independent-Y 单元已执行，必需结果单元有完整分母，clean replay 与独立复核通过，且没有未解决的泄漏、不公平信息、矛盾或缺失分母，才可以将
`benchmark+baseline acceptance = CLOSED_FULL` 写入关闭回执。`CLOSED_BOUNDED` 不属于本验收门状态；只有 findings-ready 的范围受限证据时，状态仍为 `OPEN`。

这与方法是否取得正收益分开：

- B1–B7 全部通过且 H1/H2/H3 均支持：可以关闭 benchmark+baseline，并支持限定范围的正向方法结论；
- B1–B7 全部通过但只有 H1：关闭 benchmark+baseline，只支持判断的信息价值；
- B1–B7 全部通过但 H2/H3 为中性或负向：关闭 benchmark+baseline，报告范围限定的 null/negative/trade-off；
- 任一 B 门未通过：不能关闭，即使数字落在 Guide 的条件范围内。

## B1–B7

| 门 | 必须具备的证据 |
|---|---|
| B1 Benchmark 权威性与主张适配 | 主轨 manifest、结构独立 roots、可追溯 scorer、标签/责任映射、污染与可见性审计、clean replay |
| B2 Baseline 可执行资格 | 每个报告 arm 有版本化入口、独立历史、原始回执、失败分母；最近邻适配器必须资格化；预先登记的 NO-GO 只能保留该行并限制 claim，不能让 CLOSED_FULL 绕过资格 |
| B3 信息与成本公平 | 合法 read cut、菜单/version、机会集、延迟、探索、服务/API/token/state/完整成本一致；gate 后 coverage/UNKNOWN 分臂报告 |
| B4 矩阵完整性与独立性 | root/split/arm/责任/漂移/延迟/stream 全部封存；独立 live history；不静默删除 UNKNOWN 或改 split |
| B5 结果语义与 Guide 一致 | 每个 cell 按预注册条件标为 favorable/neutral/adverse；H1 信息、H2 future utility、H3 在线性质分开；矛盾必须诊断 |
| B6 统计与成本证据 | root/stream 不确定性、效应量、全尝试分母、失败/UNKNOWN/未启动、完整成本、overlap/positivity |
| B7 复现关闭回执 | 源码/数据/scorer/prompt/model/config/hardware/hash/命令/raw/result 链、clean replay、独立复核 |

规范化机器字段在 `gate_spec.json` 和 [`closure_receipt_schema.json`](closure_receipt_schema.json) 中，并由同目录的 fail-closed validator 执行结构与交叉字段检查；每个门的回执字段应包括
`gate_id, claim_scope, required_evidence, pre_run_hash, artifact_path,
replay_command, denominator, verifier, status, decision_reason`。

## 当前状态

本版本尚未关闭任何科学门，未新增 API/GPU/benchmark 实验。v4 只是把未来的关闭
条件写成可执行格式；当前 B1–B7 仍有 OPEN 项。v3 的 PDF、源、审查和计算全部保留。

## 机器关闭检查

`closure_receipt_schema.json` 描述格式，`/Users/jingwu/work/earning-roles/scripts/validate_benchmark_baseline_closure.py` 是实际的 fail-closed 检查入口。它拒绝重复或缺失的 B1--B7、空分母、不可复核的 artifact/hash、相同作者冒充独立复核、缺少真实 API/raw receipt、未完成 future-Y、sentinel 未通过、停止后仍有调用和分母不守恒。验证通过只表示收据满足形式与证据合同，仍须由独立科学审查确认主张范围。

Benchmark+baseline 的关闭与方法结果符号分离：完整、可复现的正向、中性或负向结果都可以关闭证据门；中性/负向结果只能支持相应的 null、negative 或 trade-off 结论。`insufficient`、`UNSTUDIED` 或 findings-ready 的精度不足不能关闭。
