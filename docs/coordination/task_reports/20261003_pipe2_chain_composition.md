# PIPE2 typed responsibility chain composition

日期：2026-10-03  
状态：`PARTIAL`；零调用链路组合通过，真实 recipient judgment、独立终局和同信息 baseline 仍未接入。

## 做了什么

新增 `scripts/peerrolebench_pipe2_chain_composition.py`，把派生 PIPE2
材料、严格 `PeerRoleLedger` 与责任安全 feedback gate 接成一个最小可审计链：

```text
selection → task_start → delivery → producer score → recipient judgment
→ action → terminal outcome → responsibility gate → role evidence
→ later assignment → next selection → next task_start
```

`eligible` 控制表示同一 artifact 被直接采用，producer score、recipient judgment
和 terminal outcome 都完整且绑定同一 digest，因此允许写入 role evidence 并提供
下一任务 assignment。`repair` 只修改 recipient-owned 文件，`mixed` 同时涉及两侧；
两者都停止在 gate，不写 producer evidence，不改变后续 policy。

新增 `scripts/peerrolebench_pipe2_chain_qualification.py`，在 5 个材料等价类、3
种责任控制上写出 config、append-only raw JSONL、summary、源码 SHA256、实际 argv、
事件类型序列和逐事件 record hash。首次 v1 的 event-count 合约错误（将未追加
evidence 的控制写成 8 而非 7）原样保留；v2 在源码尚未提交时通过但不作为最终
provenance receipt；v3 暴露事件类型合约漏项并保留；提交 provenance 修复后用 v4
重新执行。

## 证据

命令：

```bash
python3 scripts/peerrolebench_pipe2_chain_qualification.py \
  --output experiments/logs/n03_pipe2_chain_qualification_20261003_v4 \
  --seeds 0 1 2 3 4
```

结果：`QUALIFIED_OFFLINE`，15/15 authored controls 通过；v4 config 的 `git_commit`
与源码 SHA256 对应已提交版本，并保留完整事件序列与逐事件 hash；0 candidate code、0
LLM/API、0 GPU、0 native grader。测试覆盖链组合 3 项；与派生材料、责任 gate、
manifest、shape/runtime qualification 的定向集合合计 37 项通过（具体命令和原始
日志保留在仓库）。

## 解释边界

这一步只证明事件顺序、digest 绑定、责任 gate 的保守停止和 later-assignment
plumbing 能够在同一 typed ledger 中闭合。`eligible` 是 authored control，不是
模型判断、真实质量标签或学习收益；`scientific_claim_allowed=false`，
`benchmark_qualified=false`。它没有解决：

1. 真实 LLM recipient judgment 与结构化评分；
2. producer correctness 的独立可观测 outcome；
3. 跨 episode 的持久 peer state 与后续 assignment read-cut；
4. 同信息 baseline parity、独立 history、成本和任何 online update 效果。

## Goal 对照与下一步

| Goal 要求 | 本任务状态 |
|---|---|
| situated judgment 可归因到交付 | `OPEN`：当前 judgment 为 authored control |
| evidence → future assignment → next decision | `OFFLINE COMPOSITION QUALIFIED`，真实 episode `OPEN` |
| 至少两个 structural roots | `PARTIAL`：PIPE2 仍为 candidate derived root，未升格 |
| benchmark/baseline 与科学结果 | `OPEN` |
| 实时更新与 A800 | `BLOCKED BY EVIDENCE GATES`，没有提交实验 |

下一小步应是把这个 composition 作为 live runner 的父侧 contract，先接入真实
recipient judgment 和独立 outcome 的小链；在责任、信息 read-cut 和 baseline parity
没有同时可审计之前，不启动 A800，也不把离线资格写成方法效果。

`goal_change_requested=false`；Goal 未修改、未降级。
