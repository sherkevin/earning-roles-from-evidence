# PIPE1 route receipt 零调用资格 — 2026-10-07

状态：`QUALIFIED_OFFLINE`。这轮只验证 route receipt 的结构和 fail-closed 行为，不运行
模型、TeamBench generator、候选代码或 GPU；不打开 PIPE1 benchmark，也不产生科学效果。

## 为什么做这一步

PIPE1 预检发现，静态 Planner/Executor 投影虽然可读，但缺少一条可审计的
source→message→artifact→Executor→Verifier 链。我们复用了现有 ledger 和 assignment
接口，新增一个独立的 route-level receipt validator，先用合成 receipt 验证“缺字段、
重叠材料、错误顺序、UNKNOWN、成本缺失或信息泄漏都会停止”。

实现：[`peerrolebench_pipe1_route_receipt.py`](../../../scripts/peerrolebench_pipe1_route_receipt.py)
测试：[`test_peerrolebench_pipe1_route_receipt.py`](../../../tests/test_peerrolebench_pipe1_route_receipt.py)

## 覆盖的合同

- 固定 PIPE1 source seed 0 → target seed 3；两个实例共享原生 `task_id`，由 seed 与
  material digest 区分，避免错误地把相同 task contract 当成重复实例；
- source/target material digest、message→artifact→Executor pre/post workspace→Verifier
  pre/post attestation 的可计算 hash binding；
- candidate registry/version、分配 RNG seed、排列、概率、propensity、draw 和 chosen；
- 不含凭据的 provider/model/config fingerprint；UTC 时间和 IANA task timezone 的本地转换；
- source/target message、Executor、Verifier、selection 的逐阶段 wall/token/API/GPU cost；
- selected-only 可见性、expected/scorer operator-only hash 和 causal event order；
- `UNKNOWN` 或缺失字段不能进入 `COMPLETE`，不允许进入学习/评分路径。

## 实际回执

首轮 v1 在增强 registry binding 后暴露了合成 fixture 使用占位 digest 的问题，失败原始
输出保留在 [`n03_pipe1_route_receipt_qualification_20261007_v1`](../../../experiments/logs/n03_pipe1_route_receipt_qualification_20261007_v1/summary.json)。
修订 v2 用 canonical registry digest 重跑，19 个测试全部通过：
[`n03_pipe1_route_receipt_qualification_20261007_v2`](../../../experiments/logs/n03_pipe1_route_receipt_qualification_20261007_v2/summary.json)。
两轮均为 0 API、0 generator、0 candidate、0 GPU；`scientific_claim_allowed=false`。

## 对三份验收标准的影响

这轮只关闭了 PIPE1 的一个离线工程放行门：

- 故事线与创新点：仍没有后续选人收益证据；
- 方法论：source/target lineage、selected-only visibility、成本和 UNKNOWN 语义更具体，
  但还没有真实 route 或实时更新；
- Benchmark + baseline：receipt contract 通过不等于 benchmark freeze；no-message、
  generated-planner、full-spec-relay 和公平成本比较仍未运行。

所以 scientific gate 继续关闭，不能据此启动真实 route 或 A800。下一个动作是把这个
validator 接到零调用 runner preflight，生成一条真实 route 所需的 allocation/provider/TZ
receipt 模板；只有十个 PIPE1 执行阻塞项全部解决并取得独立预算发行后，才讨论 API call。
