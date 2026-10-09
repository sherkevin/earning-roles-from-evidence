# Guide v4 独立审查与修复记录

日期：2026-10-08。本文档审查的是“未来如何关闭 benchmark+baseline 验收”的 Guide
合同，不是实验结果，也不是方法优越性证明。当前真实科学收据仍不存在，关闭状态保持
`OPEN`。

## 用户指出的缺陷

v3 能描述机制驱动的 favorable/neutral/adverse 条件，却不能回答实验结束后“哪些证据
齐备、如何签收、何时正式关闭 benchmark+baseline”这一问题。因此 v3 作为结果方向
参考可以使用，作为验收标准不合格。v4 增加 B1--B7 关闭门、目标 cell ledger、停止
收据和机器校验入口。

## 首轮只读审查

- `/root/guide_gate_closure_design`：确认 B1--B7 覆盖 benchmark 权威性、强同信息
  baseline、信息/成本 parity、独立 streams、未来 assignment→independent Y、
  ITT/UNKNOWN、clean replay 和独立复核；建议明确 `CLOSED_FULL`/bounded 的状态语义、
  真实 API 证据、B3 的 history opportunity 与各臂独立 realized history。
- `/root/guide_gate_adversarial_audit`：实际构造出七条重复 B1、缺 B2--B7、空分母、
  不存在 artifact、同作者 verifier，却被旧 schema 接受为 `CLOSED_FULL`；还构造出全 FAIL
  gate 被接受为 `CLOSED_BOUNDED`。这些反例被保留为修复依据。

## v4 修复

1. 关闭状态只允许 `OPEN`、`CLOSED_FULL`、`FAIL`；`CLOSED_BOUNDED` 不是 benchmark
   验收状态。findings-ready 或 bounded claim 保持 `OPEN`。
2. `CLOSED_FULL` 要求 B1--B7 恰好各出现一次且全部 PASS、至少两个结构不同 root，
   proceedings-ready 的三 root 或事前注册的双 root precision justification、每个 arm
   至少两个独立 stream、结构/时间 holdout、完整 target-cell ledger、H1/H2/H3/safety
   四类 cell、ArtifactRole future Y 的 assignment 和证据 digest、真实 API/raw receipt、
   API 与 stop 计数一致、零 post-stop call、完整分母/成本 ledger、所有 sentinel 有
   evidence、clean replay 和独立复核。
3. 完整的 positive、neutral 或 adverse 方法结果都可以关闭 benchmark+baseline 的
   **证据门**；这不产生方法优越性结论。`insufficient`、`UNSTUDIED`、缺 future Y、
   精度不足或未启动 cell 都不能关闭。
4. B3 要求相同的合法 read-cut、信息机会、表示、预算和公共输入 digest；自适应 arm
   保留独立 realized-history namespace，不复制另一 arm 的状态。
5. `scripts/validate_benchmark_baseline_closure.py` 通过标准库执行结构、路径/hash、
   分母、笛卡尔 cell 覆盖、finite interval、API/stop、sentinel 和独立复核交叉检查。
   companion schema 负责格式，validator fail-closed 检查负责语义交叉字段。

## 修复后的软件审计

`tests/test_benchmark_baseline_closure.py` 的 8 个软件-only 测试通过，日志在
`experiments/logs/experiment_target_guide_20261008_v4/closure_validator_v4/`。测试覆盖
重复 B1、禁止 bounded、完整 neutral synthetic receipt、future-Y 缺失、零分母/API-stop
不一致、H2 无 Y artifact、恶意数组 ID、恶意数组 status/hypothesis。所有 fixture 明确
标记为 synthetic contract，不包含 benchmark observation、LLM/API 调用或 GPU。

v4 PDF 已由本地 latexmk 和 Codex 内置编译器成功编译：5 页，每页可见 NOT OBSERVED
水印，0 overfull、0 fatal、0 undefined。PDF 与 layout receipt 保存在
`artifacts/aamas2027/guide_experiment_matrix_v4_20261008/`。

## 审查边界与状态

这轮修复证明旧的 schema 漏洞已被软件负例堵住；它没有证明真实 benchmark、baseline、
方法结果或 Goal 已完成。两次额外的 Codex 独立复核因模型容量未能启动，另一次在用户中断时未完成，因而本版本的
状态记录为 `CURRENT_CONDITIONAL_GUIDE_PENDING_SCIENTIFIC_EVIDENCE`，并保留独立复核
pending 标记。任何真正的 `CLOSED_FULL` 必须来自未来真实实验的收据和独立科学审查，
不能由这份 Guide 或软件测试自动生成。
