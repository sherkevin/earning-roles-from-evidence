# 2026-10-02 N03 前置设计任务汇报

## 任务目标

把 N02 真实 API 追踪暴露出的识别问题转成下一次实验的硬放行门，避免在
benchmark、baseline、责任标签或 agent 状态尚未成立时继续消耗 API/GPU 预算。

## 已检查的证据

- N02 v3 的 2 条完整链、6 次真实任务请求、15 条事件哈希链和独立复核记录；两次
  consumer 行为分数均为 4/4，但概率没有更新，反馈映射等于先验；
- `n02_posthoc_priority_sandbox_20260926`：两次被声称修复的 priority 接口仍有独立
  import/constructor 问题，原 consumer score 没覆盖 producer correctness；
- `n02_posthoc_responsibility_20260926`：两次只改 `consumer.py`，不能把正常 recipient
  integration 当 producer 返工；
- active benchmark/baseline v1.1：PIPE3 仍是主候选，DIST1 仅诊断，PIPE2 完整 root
  被 malformed CSV 阻塞，MULTI3 仍缺 producer→recipient adoption；七个 arm 尚未完成
  independent live parity；
- active method v1.1：`publish`、`choose`、`validate_later`、`update` 已分成两阶段
  合同，但 backbone、表示和 updater 仍明确开放；
- active Goal ER-G1–ER-G4：要求真实 recipient judgment、可归因 evidence、执行前
  assignment、未见任务质量/完整成本，以及实时性/时效性/稳定性证据。

## 本轮产出

新增 [`docs/research/n03_prerequisite_design_20261002.md`](../../research/n03_prerequisite_design_20261002.md)，将下一次真实实验前置为四个识别条件：

1. 两个结构独立且材料/评分/可见性已冻结的 root；
2. producer correctness、recipient action/judgment、later outcome、ownership 和
   `UNKNOWN` 分开的责任标签；
3. 同初始状态、可审计且真正影响下一次 generation/choice 的 per-agent persistence；
4. uniform、no-update、raw、terminal、同信息 contextual、pooled 和 RARE 的 live
   baseline parity。

文档同时规定了零调用 replay → 单 root 真实材料 → 四格信息价值 → 同信息 parity →
独立 confirmation root → 单个 A800 challenger 的顺序，以及信息价值、闭环后果、实时
性、时效性、稳定性和完整成本的结果字段。

## Goal 对照

| Goal 硬标准 | 本轮状态 | 解释 |
|---|---|---|
| situated judgment → attributable evidence | `OPEN` | 责任标签与 producer 覆盖仍待真实资格化 |
| evidence → pre-execution assignment | `ENGINEERING-QUALIFIED / SCIENCE-OPEN` | 离线接缝存在，独立 live history 未完成 |
| unseen quality/cost improvement | `NOT_RUN` | N02 没有信息增量或闭环效能证据 |
| real-time/stability/forgetting | `NOT_RUN` | 无最终 updater/backbone，不能启动 A800 |
| benchmark/baseline authority/parity | `NOT_READY` | PIPE3 主候选尚未冻结，七 arm parity 未完成 |

## 决策与下一步

本轮没有修改 Goal、active benchmark、active method 或实验成功标准，也没有把失败数据
降级为结果。下一步只能从前置设计的第 1 项开始：对 PIPE3 与一个真正独立的第二 root
做材料/评分/责任覆盖审查；若第二 root 仍不合格，保留 `UNKNOWN` 并记录替代路径，
不通过改 seed 或手工修复制造 confirmation 样本。

验证：`python3 scripts/check_aamas_documents.py --sync-gate --check-gate` 在图稿和本
设计加入后通过；本任务 0 次 LLM API、0 次 GPU、0 个科学结果。
