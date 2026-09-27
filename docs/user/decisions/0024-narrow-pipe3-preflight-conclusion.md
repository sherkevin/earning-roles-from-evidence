# 0024：收窄 PIPE3 前置检查结论

日期：2026-09-27。
状态：Accepted。
Supersedes: [ADR 0023](0023-pipe3-preflight-qualification.md)。

## 背景

独立审查了 `n03_pipe3_task_qualification_20260927` 后发现，原结论把三种不同层级
的检查混成了“前置资格通过”。脚本只检查了静态 workspace 文件集合、一个新建的
账本夹具和列出的访问 canary，没有把真实 actor payload 发到候选进程，也没有回放
真实事件账本或证明隐藏 scorer 与 operator 文件不可读。更严重的是，TeamBench 原始
PIPE3 的 `spec.md`、`brief.md` 和生成源码逐条写出了三个 bug 及修复方向，不能用于
发现或归因能力的科学测量。

## 决定

1. 将历史结果的含义限定为：`contract_fixture_preflight_passed=true`、
   `ledger_fixture_passed=true`、`listed_isolation_canary_passed=true`。这三项是
   无 LLM 的静态工程检查，不是实际 agent 运行资格。
2. 新版脚本额外记录 actor payload schema/digest、expected 元数据 deny-list、任务
   文本 oracle 泄漏和真实 dispatch/ledger replay 状态。当前 `task_text_scientific_qualified`
   必须为 false，且 `real_agent_preflight_verified` 必须为 false。
3. 在修订任务文本、实现真实 payload/export adapter、隔离 hidden scorer 和 operator
   ledger、完成 exact-once lineage/propensity replay 之前，不启动 PIPE3 LLM 小流，
   不把 PIPE3 冻结为 benchmark，也不启动 A800 方法实验。

## 后果

历史 v1 运行目录不修改，v2 只作为收窄后的工程诊断保存。论文、任务账本和 claim
matrix 只能引用“static contract fixture + listed canary”；任何 discovery、
responsibility attribution、benchmark qualification 或方法效果主张都仍然开放。
下一张实验卡必须使用不泄露答案的 task root，并将 operator 证据置于候选不可读的
独立进程/IPC 边界中。
