# Task report — Guide v4 closure gate repair

日期：2026-10-08

## 目的

修复用户指出的 v3 缺陷：v3 能描述结果方向，却不能在真实实验结束后判断
benchmark+baseline 何时正式验收关闭。Goal、故事线、方法论、benchmark/baseline
标准和真实科学目标均未改变。

## 关键结论

v4 把“证据门关闭”和“方法是否优越”分开。benchmark+baseline 只有在 B1--B7
全部通过、主轨 future assignment→independent Y 完整、required cells 和分母完整、
强同信息 baseline/closest adapter 有资格、复现和独立复核通过时才能 `CLOSED_FULL`。
完整的 positive、neutral 或 adverse 结果都可以关闭这条证据门；中性/负向只能支持
相应的 null、negative 或 trade-off 结论。`insufficient`、`UNSTUDIED`、findings-ready
精度不足和缺 future-Y 保持 `OPEN`。`CLOSED_BOUNDED` 不再作为该验收门状态。

## 实现

- 新增 v4 第 5 页 closure receipt：B1 benchmark authority，B2 executable baselines，
  B3 information/cost parity，B4 matrix/independence，B5 result semantics，B6
  statistics/cost，B7 reproducible closure。
- 新增 `gate_spec.json` 的状态矩阵、真实 API 要求、history opportunity 语义和交叉检查。
- 收紧 `closure_receipt_schema.json`：B1--B7 各一次、artifact/hash、独立 verifier、
  target cells、sentinel evidence、future-Y、真实 API、停止证据和 receipt 状态。
- 新增标准库 fail-closed 校验器
  `scripts/validate_benchmark_baseline_closure.py`。它检查 root/stream/arm cell 覆盖、
  H1/H2/H3/safety、finite interval、future-Y artifact、minimum streams、分母/成本
  ledger、API/stop 一致、sentinel、reviewer 独立性和禁止 bounded 状态。
- 新增 8 个软件-only 负例/合同测试，日志在
  `experiments/logs/experiment_target_guide_20261008_v4/closure_validator_v4/`。
  测试没有调用 LLM/API、GPU 或 benchmark，不是科学结果。
- v4 PDF 已由 latexmk 与 Codex 内置编译器通过：5 页、每页水印、0 overfull、0 fatal、
  0 undefined。主 Guide PDF 和 receipt 已同步到 `artifacts/aamas2027/`；v3 receipt
  保留在 v3 version directory。

## 审查与限制

语义设计审查认为 v4 的 B1--B7 与 Goal 一致；对抗审查构造的旧 schema 反例已被软件
测试覆盖。两次追加的外部 Codex 复核因模型容量没有启动，另一次因用户中断未完成，已如实记录在 v4
`review_rounds.json`；这不被解释为通过。当前 Guide 是
`CURRENT_CONDITIONAL_GUIDE`，科学 benchmark+baseline closure 仍 `OPEN`。结构校验器
只能拒绝格式/证据合同漏洞，不能替代独立科学复核或制造真实结果。

## Goal 对照

完成的是验收标准的“可执行定义”和主 Guide 的文档治理；没有完成 benchmark authority、
second root、live baseline parity、future outcome、method efficacy、实时性/遗忘或
A800 训练。Goal 未降级，正文和主论文没有写入结果数字。

## 下一步

先按 v4 收据合同完成 benchmark/baseline 资格与真实小批量矩阵；实验结束后运行校验器，
再由独立审查判断是否能把证据门从 `OPEN` 变为 `CLOSED_FULL`。不能用 Guide 预测数字
或软件 fixture 提前关门。
