# Task report：recipient payload / delivery IPC probe / 2026-09-27

状态：`PARTIAL`。`goal_change_requested=false`。对照 Goal v1.0 的 ER-G3、ER-G4；不修改目标。

## 冻结与执行

- 源码、TeamBench pin、seed：`TeamBench@d185aef1916fd86a9ba554d581fd256319a973af`
  / seed 0。
- 运行前 config、原始事件流、sandbox settings、summary：
  [`n03_pipe3_recipient_runtime_preflight_20260927`](../../experiments/logs/n03_pipe3_recipient_runtime_preflight_20260927/)。
- 执行类型：真实本地 sandbox stdin/RPC worker；`llm_calls=0`、`gpu_jobs=0`、
  `candidate_code_executed=false`、`scientific_claim_allowed=false`。
- RPC 输入上限：16 KiB；默认 4 KiB 上限未改变，只对 recipient payload 这一有界探针
  显式提高并记录。

## 结果与 Goal 对照

| Goal 条目 | 状态 | 本轮证据 | 仍不能支持的主张 |
|---|---|---|---|
| ER-G3 recipient/delivery 可见性 | `PARTIAL` | recipient role、source files、required delivery paths 和 selected delivery 通过独立 worker；delivery digest 与 allowlist 一致 | 不是实际 LLM 生成的 producer delivery，也不是完整 runner 的 payload export |
| ER-G3 operator/hidden 边界 | `PARTIAL` | worker 读取 operator-only ledger 得到拒绝；sandbox settings 和 launch metadata 已保存 | 未验证 hidden scorer、完整 operator ledger 和所有异常路径 |
| ER-G3 lineage/exact-once | `PARTIAL` | 父进程生成 selection→delivery→recipient-dispatch 三事件 hash-chain，event ID 唯一、digest 和 source refs 绑定 | 这是 ledger fixture，不是真实多事件 replay；没有 retry、missing、exception、乱序覆盖 |
| ER-G4 可审计实验 | `PARTIAL` | config/raw/summary 和源码 hash 记录完整，运行无 LLM/GPU | 没有真实 judgment/action/producer contract/final score，因此没有科学效果数据 |
| ER-G2 在线训练 | `OPEN` | 未触碰更新器、backbone 或 labels | 仍无合法纵向学习信号和实时/遗忘结果 |

## 根因与修复

之前只证明 producer payload，recipient payload 加 delivery 会超过原 4 KiB RPC 上限，
因此这不是“实验失败”，而是 runtime contract 未覆盖该 payload 大小。现在把输入上限
做成显式参数，默认安全上限不变；本轮只对 16 KiB 探针记录并验证实际 payload。

## 下一步

1. 将该边界接入真实 producer→recipient runner，使用 LLM 输出而不是 fixture source。
2. 加入 delivery retry、missing-field、exception、out-of-order 和 exact-once replay。
3. 把 hidden scorer/operator ledger 放到实际 runner 的独立 IPC 服务，再做可见性探针。
4. 只有这些门通过，才冻结 N03 真实 API 小流；本报告不请求 Goal 变更。
