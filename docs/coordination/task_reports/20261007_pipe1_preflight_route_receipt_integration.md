# PIPE1 route receipt integration — 2026-10-07

状态：`QUALIFIED_OFFLINE_INTEGRATION`。本轮把已经独立通过的
`validate_pipe1_route_receipt` 接入 PIPE1 的零调用执行预检，并用三种输入路径验证
预检的 fail-closed 行为。没有调用模型、生成器、候选代码或 GPU，也没有改写历史结果。

## 目的

PIPE1 不能只保存一个独立的 schema 测试；未来 runner 必须在产生任何昂贵调用前消费
同一份 source seed 0 → target seed 3 route receipt。否则 lineage、随机分配、provider
指纹、时区、成本和 selected-only 可见性可能各自通过，却没有被执行入口强制绑定。

## 实现

- `scripts/peerrolebench_pipe1_preflight.py` 新增 `--route-receipt` 和
  `run(..., route_receipt=...)`。
- 缺失或不存在的回执产生 `BLOCKED`；合法回执产生 `PASS`，并把路径、SHA-256 和
  schema 记录到 preflight config；解析失败或结构非法产生 `FAIL`。
- 任意 `FAIL` 与 `BLOCKED` 都使整体状态保持 `BLOCKED_PRE_EXECUTION`；即使回执合法，
  `scientific_claim_allowed` 仍为 `false`。
- `tests/test_peerrolebench_pipe1_preflight_route_receipt.py` 覆盖缺失、合成合法和非法
  回执三条路径。原有 `tests/test_peerrolebench_pipe1_route_receipt.py` 未修改。

## 零调用证据

完整日志保存在
[`n03_pipe1_preflight_20261007_v4`](../../../experiments/logs/n03_pipe1_preflight_20261007_v4/)。

- 配置先于检查写入，记录工作区源码哈希、Python/macOS 环境和命令；
- `22 passed`，`py_compile` 通过；
- 缺失回执：11 `PASS`、11 `BLOCKED`、1 `OPEN`；
- 合成合法回执：12 `PASS`、10 `BLOCKED`、1 `OPEN`；
- 非法回执：11 `PASS`、10 `BLOCKED`、1 `FAIL`、1 `OPEN`，整体仍
  `BLOCKED_PRE_EXECUTION`。

这里的合法回执是由测试构造的结构样例，不是一次 live source/target route。它只证明
预检入口确实消费并拒绝/接受相应结构，不能证明 actor 交付、Verifier、质量、收益或
任务泛化。

## 对 Goal 的影响

这只关闭了一个工程连接点：route receipt 现在成为未来 PIPE1 runner 的显式前置条件。
它没有关闭 source→artifact→Executor→Verifier 的真实 lineage、exact outcome scorer、
provider/timezone pin、独立预算、relay baseline、同初始 peer 的可辨识差异，也没有
打开三份科学验收标准或投稿 gate。下一步仍应先完成零调用 ledger runner 和剩余
执行阻塞项；没有新的 PIPE1 预算，不启动模型或 GPU。
