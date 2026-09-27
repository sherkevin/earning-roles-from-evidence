# 0028：把 parent-side ledger replay 作为学习信号的硬门

日期：2026-09-27。
状态：Accepted as an integrity gate; 不改变 Goal v1.0。

## 背景

此前的 ledger loader 会把序列化事件重新喂给 `PeerRoleLedger`，但没有把“完整链条”
和“可继续执行的半条链”分开，也没有独立覆盖 hash 篡改、重复事件、未知 retry、乱序
和中断。若这种记录直接进入更新器，坏的或未完成的事件可能被误当成合法 selected-only
反馈。

## 决定

新增 parent-side `peerrolebench_ledger_replay.py`，在任何训练/评分消费前依次检查：

1. 记录 schema、事件类型、字段和 hash chain；
2. selection → task start → delivery → recipient judgment → consumer action → terminal
   outcome → role evidence → later assignment 的引用关系和顺序；
3. event ID、task episode、delivery、judgment、action、outcome 和 evidence 的唯一性；
4. 完整链返回 `PASS`，合法中断只能在显式 `allow_incomplete` 下返回 `UNKNOWN`；默认对
   不完整链拒绝，未知事件和 retry 事件始终拒绝。

零 LLM 的 mutation matrix 使用此前真实 v3 ledger 做回放，并覆盖重复、record hash 篡改、
previous hash 篡改、未知事件、retry、乱序和中断。它只证明协议/回放完整性，不证明
benchmark、scorer、agent 或在线学习有效性。

## 理由

这让“没有标签”与“标签为负”保持可区分，也让延迟、异常和重试不会静默改变因果顺序。
验证器放在 parent side，不把候选进程自身的日志当作可信账本；它可被 peer-select 和
tool-select 共用，但两项目仍保留各自的任务、label 和 scorer。

## 后果

- 真实 runner 必须在 role update 前调用验证器，并保存验证结果与原始 ledger hash。
- 该门通过后仍需验证 hidden scorer/operator IPC、真实 producer/recipient 输出、异常
  重试语义和第二结构 root；当前 benchmark 资格与 ER-G2 训练效果仍开放。
- 本决定不改变 N02 历史结果，不把 zero-LLM replay 当作科学效果，也不请求 Goal 变更。
