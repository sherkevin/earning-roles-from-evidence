# Task report：将 replay gate 接入真实 runner / 2026-09-27

状态：`PARTIAL`。`goal_change_requested=false`。本任务对应 ER-G3、ER-G4，不修改 Goal。

## 已完成

在 [`peerrolebench_real_closed_loop.py`](../../scripts/peerrolebench_real_closed_loop.py) 中：

- 读取已有 ledger 时先经过 parent-side replay；合法的 live 中间态显式为 `UNKNOWN`，
  非法 schema、hash、顺序或引用直接停止；
- 在 `role_evidence_update` 后、controller update 前调用严格 `replay_gate`；
- 在 episode summary 前再次调用严格 `replay_gate`；
- gate 失败先写入 raw `ledger_replay_gate` 事件，保留 context、错误码、索引和 snapshot。

没有重跑 N02、没有新的 LLM/API/GPU 请求，也没有修改历史 raw ledger 或 summary。

## 验证与 Goal 对照

- `python3 -m py_compile scripts/peerrolebench_real_closed_loop.py` 通过。
- runner smoke 读取保存的 v3 ledger 15 个事件成功；临时篡改 `previous_hash` 被报告为
  `hash_chain_break` 并拒绝。
- 独立 validator 的真实 v3 replay 与 8-case mutation matrix 仍为 `PASS`/预期拒绝或
  `UNKNOWN`，85 项定向回归测试通过；这次集成只增加调用边界，没有重新生成科学数据。

| Goal | 状态 | 结论 |
|---|---|---|
| ER-G3 ledger/causal boundary | `PARTIAL` | runner 不能绕过 replay gate；hidden scorer/operator IPC、retry/exception 定义仍开放 |
| ER-G4 reproducible experiment | `PARTIAL` | gate context 进入 raw log；尚未有新真实 episode，因此没有新增效果证据 |
| ER-G2 online training | `OPEN` | gate 是前置安全条件，不是实时更新器 |
| ER-G1 scientific chain | `OPEN` | 没有新增 judgment 信息价值、角色转移或未见任务质量/成本证据 |

## 下一步

把严格 gate 与实际 producer→recipient/scorer IPC 接通，先在单个新的、冻结的开发卡上
验证 retry、异常和 hidden scorer 的事件语义；只有这些结果可审计且存在合法纵向信号，
才进入 baseline 对照和训练方法/A800 选择。Goal 没有变更请求。
