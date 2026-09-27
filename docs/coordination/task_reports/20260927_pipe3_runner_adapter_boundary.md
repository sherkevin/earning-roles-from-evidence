# Task report：PIPE3 root-specific runner adapter boundary / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## 对应 Goal

本任务推进 ER-G3 的 root-specific 任务契约和 ER-G4 的可复现实验边界。它解决了
“把 PIPE3 强行塞进 DIST1 runner”这一工程风险，但没有启动真实 API、GPU 或控制器更新。

## 发现

现有 [`scripts/peerrolebench_real_closed_loop.py`](../../scripts/peerrolebench_real_closed_loop.py)
仍把 `mqueue/queue.py`、`mqueue/priority.py`、`consumer.py`、队列接口名和 DIST1
producer scorer 版本写死。直接复用它会把 PIPE3 的 `producer.py → processor.py → sink.py`
责任边界改写成 DIST1 语义，导致 scorer、action、cost 和 ledger 不能回答同一个科学问题。

## 实现的最小 seam

新增 [`scripts/peerrolebench_pipe3_runner_adapter.py`](../../scripts/peerrolebench_pipe3_runner_adapter.py)，
只处理不执行候选代码的纯契约操作：

- 严格附加 `producer.py` delivery，并保留 `processor.py`、`models.py`、`sink.py` 的角色；
- 将 `use`、`repair`、`independent_redo` 的写权限显式化；
- 对完整 recipient snapshot 做路径、大小、语法和 read-only 校验；
- 暴露三个互不混淆的 scorer view：`Q_p=(producer.py,models.py)`、
  `Q_r=(processor.py,models.py)`、adoption=(producer,processor,models,sink)；
- 不把 tests、expected、ledger 或 private scorer 送入 actor view。

新增的 2 个 adapter tests 与既有 PIPE3 scorer tests 合计 `14 passed`。这些测试是零 LLM、
零 GPU 的 contract evidence，不是 agent 效果或 benchmark qualification。

## 与 Goal 的对照

已满足：PIPE3 现在有独立于 DIST1 的 material/action/scorer-view seam，后续真实 runner
可以复用 API/ledger/replay 基础设施而不复用错误的任务语义。

部分满足：adapter 尚未接入 `call_api`、selection policy、真实 ledger episode 或
independent hidden scorer process；`repair` 的 producer 修改仍需要在真实 prompt/成本
协议中进一步规定，不能凭 adapter 单元测试宣称责任因果已成立。

未满足：第二结构 root、same-information baselines、benchmark freeze、真实 situated
judgment 和 online update 仍未完成；没有修改 Goal 或创新主线。

## 下一步

先对 adapter 的 action/repair 语义做独立审查，再实现一个只支持 PIPE3、无 DIST1 fallback
的准备阶段 runner（不发 API），验证 selection→delivery→Qp→judgment 的前半链能落盘；
只有这条准备链和 process-separation gate 通过，才值得消耗真实 API 开发预算。
