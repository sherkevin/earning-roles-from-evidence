# Candidate card — shared source, independent policy and target streams

日期：2026-10-06
状态：`CANDIDATE / DESIGN_ONLY / NOT RUN`
Goal change requested：`false`

## 需要解决的问题

C1 v4 的 structural-owner gate 按合同运行，但三臂各自生成 recipient action，导致
source 是否 eligible 依赖于每个 arm 的随机 action。contextual arm 改写 `processor.py`
后正确停止，而另外两臂获得 producer evidence；因此只比较完成臂会产生选择偏差，无法
识别 selector 的作用。这里的失败是实验可识别性问题，不是一个 baseline 的负标签。

## 候选设计

对同一个 development source episode，只运行一次真实 recipient judgment/action/outcome，
然后把同一份合法 public evidence snapshot 以相同 digest 分别提供给三个独立 policy state。
该 source receipt 只作为公共输入，不能复用一个 policy 的 state、选择或 target outcome。
每个 arm 的 target assignment 仍在执行前独立封存，并运行独立 recipient/target episode。

这一卡只回答“在相同 source information 下，policy 的分派与 delayed update 是否可审计”。
它不是独立 live histories 的最终科学比较，也不能替代跨 root、真实 peer 能力变化和
source acquisition cost 的验证。source 成本按预注册口径计入每个部署条件或单独报告共享
acquisition cost，禁止把共享调用当免费信息优势。

## 开卡前的硬条件

1. 明确 `episode_status`、`gate_status` 与 estimand inclusion：`PENDING_ATTRIBUTION` 是
   结构性不适用，不与 transport UNKNOWN 混写；所有 source attempts 进入 ITT 分母。
2. source gate 只从冻结 contract/registry/scorer 推导；judged-role disagreement 保留校准。
3. policy-selection 与 native-selection sidecar 做 digest binding，并测试 mutation rejection。
4. 完整记录 source acquisition、target execution、scorer、update、state bytes 和失败成本。
5. 先做 zero-call contract check，固定 arm、source/target root、seed、read cut、propensity、
   API cap、停止规则与 card/source hashes，才允许一次 bounded API run。
6. source 不 eligible 时三个 arm 统一停止并记录 denominator；不能补采 source 到成功。

## 判定与后续

- source 无信息或 gate-stop：分析责任/任务合同，保留整个尝试，不补标签。
- shared source 下 policy 行为一致：不能声称角色分派收益，分析是否有可学信号和足够差异。
- policy 行为不同：仍需独立 target quality/cost 与同信息强 baseline，不能由概率变化宣称效果。
- 只有设计/资格问题闭合后，才起新 API；该候选不改变 active benchmark、方法目标或标准。

## 独立复核

Codex `gpt-6-sol` 的只读审查确认：v4 的 structural-owner gate 按 ADR0047 执行，但 contextual
arm 的 stop 是 arm-specific gate censoring；complete-case-only 比较无效。它要求 ITT 分母、
gate-stop rate、eligible conditional analysis、selection lineage、完整成本与独立 roots。
本候选吸收其 common-source/denominator 建议，保留最终科学比较的独立 history 要求。
