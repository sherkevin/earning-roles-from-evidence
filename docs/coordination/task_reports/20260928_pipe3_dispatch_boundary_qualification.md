# 2026-09-28 PIPE3 actor/scorer dispatch boundary qualification

- 状态：`PARTIAL`（真实进程边界的工程子门通过；真实 LLM runner、benchmark 和科学效果仍开放）
- 对应 Goal：ER-G1、ER-G3、ER-G4；阶段门 G1
- `goal_change_requested=false`
- 真实 LLM/API：0；GPU：0；`scientific_claim_allowed=false`

## 做了什么

新增 `scripts/peerrolebench_pipe3_dispatch_boundary_qualification.py`，复用已经固定的
PIPE3 material/action adapter 和 sandbox RPC，检查一个 seed 的：

1. producer payload 与 recipient payload 是否分别只包含公开 source；
2. producer.py 是否按 delivery allowlist 交给 recipient；
3. operator-only ledger 文件在 sandbox 中不可读；
4. Qp、Qr、adoption 三个 scorer view 是否严格分离；
5. 错误 delivery 和 recipient 修改 read-only 文件是否被拒绝。

第一版误把 evidence 目录提前创建，第二版暴露 recipient payload 超过默认 4 KiB RPC
上限；两次失败均保留。第三版把 64 KiB 写入冻结配置后通过。

## 证据

通过回执：
`experiments/logs/n03_pipe3_dispatch_boundary_qualification_20260928_v3/`

关键结果：

- producer dispatch：`true`；recipient dispatch：`true`；
- scorer views：Qp=`models.py, producer.py`，Qr=`models.py, processor.py`，adoption=`models.py, processor.py, producer.py, sink.py`；
- wrong delivery：`REJECTED`；read-only action：`REJECTED`；
- sandbox worker、payload digest、RPC raw output 和完整配置均已保存。

## 与 Goal 的对照

| Goal 标准 | 状态 | 说明 |
|---|---|---|
| 非 oracle actor payload | 部分满足 | 该 adapter payload 不含 hidden tests；只验证材料边界，尚未用真实 LLM 生成。 |
| candidate / scorer / operator 隔离 | 部分满足 | operator denial 与 scorer view 通过；尚未运行真实 scorer IPC 和完整 live runner。 |
| 责任链可回放 | 已有工程子门 | full-chain qualification 已通过，本任务只补 dispatch/view seam。 |
| 真实 judgment/use/成本 | 未满足 | 没有 API 调用、候选执行或真实 consumer 行为。 |
| benchmark、baseline、方法效果 | 未满足 | 不改变 benchmark freeze，也不解锁 A800。 |

## 结论与下一步

本次关闭了“payload/selected delivery/scorer view/写权限”这一层工程缺口，并记录了真实
RPC 上限不能沿用默认 4 KiB 的实现问题。它不能证明模型会遵守 payload，也不能证明
operator/hidden scorer 在真实 LLM episode 中不可见；下一步需把真实 `内部` API 的 actor
输出接入同一边界，仍只运行一条新的 PIPE3 小链，并在任何 scorer UNKNOWN 时停止后续
feedback/update。
