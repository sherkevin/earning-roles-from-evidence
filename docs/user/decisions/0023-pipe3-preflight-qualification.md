# 0023：PIPE3 通过前置契约与隔离检查，但不冻结 benchmark

日期：2026-09-27。
状态：Accepted for the next development gate; scientific qualification remains open.

## 背景

PIPE3 的 seed-0 父进程四格 smoke 已能区分 producer quality、recipient work 和
pipeline adoption，但独立复核指出它没有覆盖真实 actor/recipient payload、隐藏评分、
写权限和事件顺序。没有这些边界，recipient 的判断不能成为可靠的责任信号。

## 决定

接受 `n03_pipe3_task_qualification_20260927` 为 PIPE3 的**前置资格通过**：

* seed 0/1/2 只暴露 `producer.py`、`processor.py` 及 `models.py`/`sink.py` 支持文件；
* producer 只能写 `producer.py`，recipient 只能写 `processor.py`；
* tests/expected 和独立 score 留在父进程；
* 账本固定为 selection → delivery → judgment → consumer action → independent score
  → role update；
* 已有 macOS isolation canary 接入同一份结构化日志。

这项决定不把 PIPE3 称为最终 benchmark，不允许开始 N03 方法效果采样，也不允许
由 canary 推导生产级安全或同进程 gold 保护。真实 agent 小流只有在下一张版本化
实验卡冻结后才能运行。

## 理由

这一步消除了“把 hidden score 给 agent”“把 recipient 自己的 integration 算成
producer defect”“在选择后补写 assignment”三类测量错误，同时没有消耗 LLM 或 GPU
预算。前置资格和科学资格分开，符合当前论文的 claim/evidence boundary。

## 后果

下一步是完成真实 PIPE3 小流的 scorer/责任证据覆盖和 independent root split，
再决定是否进入 RQ1/RQ2 的 matched baseline 实验。若真实执行无法形成合法的
recipient judgment 或 upstream responsibility，PIPE3 只能作为协议诊断并转向 MULTI3。
