# PIPE1 原生隔离与材料接线修复卡 v0.1

日期：2026-10-08。状态：`CANDIDATE / BLOCKED_PRE_EXECUTION`。

这不是 benchmark 选择决议，也没有打开 API 预算。它记录了对 pinned TeamBench
PIPE1 原生 harness 的零调用审查，以及进入真实路由前必须满足的最小执行合同。

## 已复现的事实

### 1. Executor 可以读到 operator 目录

`references/aamas/task_signal_materials_20261007/native_harness/harness/agent_interface.py`
中的 `make_executor_config` 将 `workspace_dir`、`reports_dir`、`messages_dir` 和
`os.path.dirname(brief_path)` 全部加入 `ReadFileTool.allowed_roots`。因此同一个工具
可以读取 `../reports/expected.json`，也可以读取 task 目录里的 brief/spec。路径映射
只改变前缀，不构成目录隔离。

在临时目录中用同一份 pinned 函数实测：

| 读取请求 | native 结果 |
|---|---|
| `etl.py` | 成功，8 字节 |
| `../reports/expected.json` | 成功，14 字节 |
| reports 的绝对路径 | 成功，14 字节 |
| `../task/brief.md` | 成功，5 字节 |

这是工具可见性事实，不是模型实际读过 gold 的证据。审计没有调用模型，也没有
执行候选代码。

### 2. Executor 的 shell 工具没有白名单

同一配置的 `RunCommandTool` 是 `shell=True`、`allowed=True`，
`allowed_commands=None`。所以即便从 prompt 中声称“只能改 workspace”，工具配置也
没有把命令执行限制在这个边界内。把 `allowed=True` 解释为安全沙箱是不成立的。

### 3. `run_all` 没有把生成的 spec/brief 写进 task 目录

TeamBench generator 的 `write_to_disk` 只有在收到 `task_dir` 时才写 `spec.md` 和
`brief.md`。pinned `harness/run_all.py` 调用的是：

```python
gen.write_to_disk(result, workspace_dir=workspace, reports_dir=reports)
```

没有传 `task_dir`。而 `TaskOrchestrator` 从 task 目录读取这些文件；缺失时其
`_read_file` 返回空字符串。因此直接复用该 runner 不能声称 Planner 得到了完整
spec、Executor 得到了 brief，甚至不能声称它运行了目标任务协议。

## 对论文问题的影响

这三个事实足以阻止直接启动 PIPE1 的 `no_message / full_spec_relay /
generated_planner` 对照。否则可能出现三种混淆：

1. Executor 读取 expected 或完整 spec 后得到的分数，被误认为 Planner 消息价值；
2. 空的 role prompt 被误认为没有消息条件；
3. unrestricted Verifier 或 remediation 修改最终 workspace 后，终局 grade 掩盖
   Planner 消息在 Verifier 介入前的差异。

先前的 PIPE1 预审已经列出 exact scorer、lineage、时区、provider、预算和 live
ledger 缺口；本卡新增的是**隔离与材料接线属于科学前置条件**，不是一般工程优化。

## 最小修复边界

修复必须另立版本化 runner，不修改或重写历史 native 结果：

1. 在同一个冻结 run directory 写入 generated `spec.md`/`brief.md` 的只读副本，
   对 actor 暴露的路径在 manifest 中逐项列出；缺失或 digest 不同直接 `UNKNOWN`。
2. Executor 的 read/write/run 必须进入独立进程或已有受限 sandbox。仅修改
   `allowed_roots` 不足以阻止 Python/shell 通过 `..`、符号链接或命令访问 parent；
   只允许读取公开 brief、workspace、合法消息，严禁 reports/expected、private
   scorer、operator ledger 和其他候选的历史。
3. Verifier 必须在独立快照上运行，先封存 Executor 介入前的 workspace 和 exact
   public checks，再记录 Verifier 前后结果；最终 grade 不能覆盖 pre-Verifier 读数。
4. `full_spec_relay` 与 generated message 使用相同 message channel、最大字节数、
   Executor 工具、Verifier、retry 和完整成本。`no_message` 只是依赖诊断，不是
   strongest baseline。
5. 在真实调用前用 mutation matrix 验证：读取 expected、跨候选历史、改写 reports、
   symlink escape、空 spec/brief、Verifier 写 workspace、消息截断都必须拒绝或标为
   `UNKNOWN`，并且失败分母和成本保持完整。

这些要求满足后，仍只能先做同一 target 的三路路由筛查；它不会自动证明自然
Planner 异质性、J 的未来选人增量或跨 root 泛化。

## 可复用资产与不能复用的部分

可直接复用：pinned generator 的 source/target material、`pipe1_route_receipt` 的
hash-chain schema、adapter rebind 的 fail-closed 校验、已有 actor history 接口，
以及 full-spec relay 的原生消息语义。不能直接复用：原生 `make_*_config` 的权限
边界、`run_all` 的材料接线、最终 grade 作为唯一 outcome、已有静态 source/target
投影和未封存的 timezone/provider。

零调用审计原始记录：[n03_pipe1_isolation_audit_20261008_v1](../../../experiments/logs/n03_pipe1_isolation_audit_20261008_v1/)。
PIPE1 的旧预审与候选筛查卡仍保留，均未被本卡改写。
