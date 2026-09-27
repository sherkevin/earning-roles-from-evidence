# Task report：双 root material payload runtime preflight / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## Goal 对照

- **ER-G3**：DIST1/PIPE3 的中性材料、producer→recipient delivery binding、operator ledger deny 和 lineage fixture 已通过受限 runtime probe；hidden scorer、完整 ledger replay 和真实 runner 仍未通过。
- **ER-G4**：配置、逐事件 raw JSONL、sandbox launch/response、digest 和最终 hash 已落盘；全程 0 LLM、0 GPU，不能支持效果结论。
- **ER-G1/ER-G2**：不改变 situated judgment→role evidence 主线；RARE/backbone/update 仍未选择。

## 实际运行

脚本 [`peerrolebench_material_payload_runtime_preflight.py`](../../scripts/peerrolebench_material_payload_runtime_preflight.py)
读取候选 manifest 和两个 versioned material adapter，用同一 pinned `SandboxedWorker`
分别发送每个 root seed-0 的 producer payload 与 recipient payload。recipient 只收到 producer
拥有的文件作为 delivery；worker 尝试读取 private operator ledger，记录为 `PermissionError`。
原始证据在 [`n03_material_payload_runtime_preflight_20260927`](../../experiments/logs/n03_material_payload_runtime_preflight_20260927/)。

结果：两 root 各自的 producer dispatch、recipient dispatch、delivery digest 和三事件
selection→delivery→dispatch lineage 均通过；最终 hash 为
`0a1b1953aa233eefac92609613fc16e87c07b2eecffb7584253bb4a52974e872`。worker 只检查
payload/路径，不导入或执行候选任务代码。

## 结论与下一步

这关闭了“材料能否进入 sandbox、delivery 是否绑定、operator 文件是否可见”的工程门，
没有关闭 benchmark 资格。下一小任务是把 adapter 和 delivery binding 接到一个新的、
预注册的 live runner card；该 card 必须先通过 hidden scorer/ledger IPC、异常/UNKNOWN
和成本边界，才允许新的真实 API 调用。旧 N02 episode budget 不重开，A800 仍不启动。
