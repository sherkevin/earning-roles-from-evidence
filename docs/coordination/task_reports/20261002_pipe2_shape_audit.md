# 2026-10-02 PIPE2 全量材料形状审计

## 目的

验证 PIPE2 是否具备继续进入零调用 root qualification 的材料前提。此步骤只读取
TeamBench pinned generator 产物，检查 source/expected CSV 的字段形状；不执行候选代码，
不调用 LLM/GPU，也不产生 producer 或 peer label。

## 执行记录

- 命令：`python3 scripts/peerrolebench_pipe2_fixture_shape_audit.py --output experiments/logs/n03_pipe2_fixture_shape_audit_20261002_v5 --seeds 0 1 2 3 4 5 6 7 8 9`
- commit：`9148fc63db0958f41da75996abed3bca7c630e87`
- runner：`pipe2-fixture-shape-audit-v2`
- LLM/API：0；GPU：0；candidate code：未执行；scientific claim：关闭
- v4 失败保留：第一次尝试预先创建输出目录，违反 runner 的 `exist_ok=False` 安全契约，
  在任何 seed 读取前退出；该错误写入 `v4/preflight.json`，没有与 v5 结果合并。

## 结果

v5 summary 状态为 `AUDITED`，但资格结果为：

| 范围 | 有效 | 无效 | 具体问题 |
|---|---:|---:|---|
| public seeds 0–2 | 2 | 1（seed 1） | `products` 的 source 与 expected CSV 均出现未声明的 `null` 列 |
| hidden seeds 3–9 | 4 | 3（seed 4、6、9） | `projects` 的 source 与 expected CSV 均出现未声明的 `null` 列 |
| 全量 0–9 | 6 | 4 | root 不是完整可用材料集合 |

seed 6 与 seed 1 产生相同的 `products` workspace digest；seed 9 与 seed 4 产生相同的
`projects` digest。这进一步说明改 seed 并不自动提供独立结构 root。

原始证据保存在：

- `experiments/logs/n03_pipe2_fixture_shape_audit_20261002_v4/preflight.json`
- `experiments/logs/n03_pipe2_fixture_shape_audit_20261002_v5/config.json`
- `experiments/logs/n03_pipe2_fixture_shape_audit_20261002_v5/raw.jsonl`
- `experiments/logs/n03_pipe2_fixture_shape_audit_20261002_v5/summary.json`

## 判定与影响

本轮 **不能** 把 PIPE2 升格为第二 benchmark root，也不能把 valid subset 直接当作
confirmation split。`benchmark_qualified=false` 且 `scientific_claim_allowed=false`。
在共同决定 fixture authority 之前，不运行 PIPE2 的真实 recipient/judgment、later
assignment、baseline parity 或 A800 实验。

这次审计支持的唯一结论是：当前 pinned generator 的四个 seed 材料无效；它没有证明
PIPE2 的 producer/recipient 机制或论文方法有效/无效。若后续处理，必须选择并记录一种
可审计路径：上游修复后形成新的 derived-root digest、放弃 PIPE2，或由用户确认新的
材料版本。不能静默转义 CSV、删除病例或重写历史 receipt。
