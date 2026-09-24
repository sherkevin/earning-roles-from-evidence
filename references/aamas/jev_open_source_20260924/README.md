# 开源 Jev / System-One 决策模型审计

审计日期：2026-09-24

目标：为 `learning roles from others' judge` 的 peer-select 问题找一个可复用的开源决策模型，并判断它是否真的支持“新标签到来后实时更新”。

## 结论先行

当前没有审计到一个开源 Jev 实现提供“每个事件到来后，在线更新完整模型权重”的现成能力。公开实现基本都把更新做成离线批量训练、checkpoint warm-start 或外层 harness 反思。

**实现底座暂定选 `jaredpalmer/kev`，首轮使用 Kev-0.8B 做每个 agent 的本地选择器，Kev-4B 做质量对照。** 原因是它同时具备 1–255 个候选、候选顺序隔离、choice/score/noul、可训练的 LoRA + pointer head、校准、replay 和本地/HTTP 服务；这些是把方案接到 CooperBench/DecisionBench 上的工程最小条件。Kev 的 Apache-2.0 许可证也适合二次改造。

`TianyuCodings/NanoJev` 保留为强方法参考和第二实现候选。它的训练脚本明确提供 `observed_outcome` 目标、动态 2–255 候选和 set-attention head，这比 Kev 更贴合我们的标签语义；但当前仓库更像研究原型，仍没有流式更新服务，成熟度和校准证据不足。因此首版不把它当唯一生产底座，而是借鉴它的训练契约。

## 候选审计

| 项目 | 固定版本 | 对我们有用的能力 | 实时更新现状 | 主要风险 | 结论 |
|---|---|---|---|---|---|
| [Kev](https://github.com/jaredpalmer/kev) | `62c91838b9a6adc5b386cbeae8ed73daa36ce220` | 0.8B/4B/9B；choice 1–255；option isolation；硬/软标签；LoRA + pointer head；温度校准；replay；serve | `kev/train.py` 是 epoch/batch 训练，未提供事件级 streaming/online API | 仍需我们实现 per-agent 状态、bandit 探索和异步轻量更新；训练数据的 choice 语义必须固定 | **首选实现底座** |
| [NanoJev](https://github.com/TianyuCodings/NanoJev) | `76fdfc9ecdca45a9bcef17991a07d3041a87685a` | 0.6B；动态 2–255 候选；set-attention；显式 `observed_outcome`；完整训练脚本 | `--init-checkpoint` 只是 warm start；训练器没有流式服务或逐事件 optimizer 状态 | 仓库较新；当前公开证据主要是作者自报游戏结果；需要自己补服务、校准和遗忘控制 | **强方法参考 / 第二实现** |
| [Laya](https://github.com/NandhaKishorM/laya) | `23a17522aa4942da6cce53a995a275760320b691` | 生产化 runtime；choice/score/noul；batch；hooks；校准和 fine-tune notebook；Apache-2.0 | notebook 是固定数据集的多 epoch DDP；hooks 只观测/改写请求，不更新权重 | 高基数和置信度校准要单独审计；没有公开事件级更新 | **推理基线，不作主底座** |
| [Von](https://github.com/wfzyx/von) | `1d86116dcc7604d7a6022858447c2d92f18a50f7` | ModernBERT 395M；choice/noul/score；校准；顺序不变性；Apache-2.0 | README 明确展示 post-training；未发现在线更新入口 | 训练/服务路径与我们的 per-agent 私有状态尚未打通 | **校准和顺序不变性对照** |
| [JevHarness](https://github.com/TianyuCodings/JevHarness) | `34d5c9602f6f73792e2c625cc31dd9ed7b4f39b5` | 完整 execution trace；reward/eval；GEPA 选择父代并反思；冻结 harness | 更新的是 harness 代码、问题和特征图，按 train/eval 批次反思；不是 Jev 权重在线学习 | 会把“外层策略进化”和“选择器参数更新”混在一起 | **离线特征/问题设计工具，不作选择器** |

## 为什么 Kev 先胜出

我们的首版不是要重新训练一个通用语言模型，而是要证明：在固定的 peer 候选图中，选择器能利用历史交付结果形成可校准的个体化偏好，并在探索后改善任务结果。Kev 已经把影响这项验证的底层麻烦处理掉了：候选分支、候选顺序、typed 输出、训练/服务和概率校准。

Kev 的训练代码允许每道 choice 题携带硬标签，也允许 soft target；`model.py` 还提供 option-isolation，使候选顺序不成为捷径。它的 API 允许最多 255 个候选，覆盖我们首轮每个节点 2–3 个局部 peer 和后续稀疏图扩展。

NanoJev 的优势是标签契约更贴近我们的研究问题：它把一次真实执行写成 `observed_outcome`，并在完整候选集合上做题级 proper loss。这个契约应借到我们的数据 schema 中，但不能误写成 NanoJev 已经支持实时训练。

## 我们要实现的“实时更新”边界

首版不在每个事件后更新 Kev 的 backbone。完整权重的逐事件更新会带来高延迟、并发读写、灾难性遗忘和不可复现实验。首版将实时性定义为：

1. Kev backbone 和 pointer head 在服务进程中保持冻结。
2. 每个 agent 维护私有、可持久化的 peer 状态和一个很小的可更新 bias/adapter；新事件到来后只更新这部分状态。
3. 选择时把 Kev 的候选 logits 与本地状态合成：
   `p(peer | task, history) = softmax(z_kev + b_agent,peer + exploration_bonus)`。
4. 通过 delayed label 更新。标签来自 recipient 是否采用/修复 artifact 以及 terminal tests；只对被选择 peer 直接得到 bandit feedback，未被选 peer 不伪造标签。
5. 定期把 replay buffer 中的真实事件合并成小批量，异步更新 pointer/LoRA；服务继续使用上一个已校验 checkpoint。更新后必须通过 locked holdout、校准和遗忘检查才能替换线上版本。

这使“Jev 动态化”成为一个可检验的两时间尺度系统：事件级是轻量状态更新，批次级是模型适配，版本级才是完整 checkpoint 切换。

## 与现有 benchmark 的接法

- **DecisionBench selector slice**：先用固定候选输出和最终 reward 测选择 regret、探索、校准和 prequential adaptation；不把它声称成完整 peer handoff benchmark。
- **CooperBench role/handoff slice**：加入 producer artifact、recipient accept/use/rework 和 native tests，生成真正的 selected-only label，验证选择是否改善交付。
- 首轮 3 agents smoke；之后使用 5-agent 无向 ring、每个节点 degree=2。主实验保持同一“内部”模型和每 agent 私有 selector state，异构模型只做后续消融。

## 必须先过的实现门槛

1. 复现 Kev 的本地 choice 推理，确认选项顺序置换不会改变 peer ID 映射。
2. 设计 `peer_event_v1` schema：task snapshot、candidate IDs、propensity、artifact/use/rework/test labels、延迟和 provenance；所有事件 JSONL 追加写入。
3. 用真实 benchmark 轨迹验证 label 延迟和缺失机制，区分 observed outcome、terminal reward 和未观测候选。
4. 实现冻结 backbone + 私有 bias 的 online learner，并与同信息 contextual bandit 对照；不能把普通 trust update 直接包装成 JEV 创新。
5. 加入 replay、版本化 checkpoint、locked test、ECE/Brier、regret 和 forgetting 检查，再决定是否启用小批量 LoRA 更新。

## 可直接复用的文件和依据

- Kev 的训练/服务/校准路径：[repository](https://github.com/jaredpalmer/kev)、[training code](https://github.com/jaredpalmer/kev/blob/62c91838b9a6adc5b386cbeae8ed73daa36ce220/kev/train.py)、[model code](https://github.com/jaredpalmer/kev/blob/62c91838b9a6adc5b386cbeae8ed73daa36ce220/kev/model.py)、[fine-tune skill](https://github.com/jaredpalmer/kev/blob/62c91838b9a6adc5b386cbeae8ed73daa36ce220/skills/kev-finetune/SKILL.md)。
- NanoJev 的动态候选/真实结果训练契约：[training contract](https://github.com/TianyuCodings/NanoJev/blob/76fdfc9ecdca45a9bcef17991a07d3041a87685a/research/algorithm_training_contract_zh.md)、[pipeline](https://github.com/TianyuCodings/NanoJev/blob/76fdfc9ecdca45a9bcef17991a07d3041a87685a/scripts/train_pipeline_decisions.py)。
- Laya runtime 与 fine-tune notebook：[runtime](https://github.com/NandhaKishorM/laya/blob/23a17522aa4942da6cce53a995a275760320b691/laya/agent.py)、[fine-tune notebook](https://github.com/NandhaKishorM/laya/blob/23a17522aa4942da6cce53a995a275760320b691/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb)。
- JevHarness 的完整 trace 和 GEPA 反思：[README](https://github.com/TianyuCodings/JevHarness/blob/34d5c9602f6f73792e2c625cc31dd9ed7b4f39b5/README.md)。

仓库的 README 指标均视为作者自报，不能替代我们在 CooperBench/DecisionBench 上的真实 API 实验。许可证字段由 GitHub API 在审计时读取：Kev/Von/Laya 为 Apache-2.0，NanoJev/JevHarness 为 MIT；二次分发前仍需保留各自许可证和依赖许可证。
