# 0012 — 不锁定 Laya，也不把 RLS 当成论文创新

Status: Accepted research boundary. Date: 2026-09-25.

## 背景

此前把 Laya multilingual 322M 写成“默认小模型候选”，把冻结表示加
在线 RLS 写成工程主线。源码核查确认 Laya 是双向 encoder + typed decision
head，公开 fine-tune 是固定数据的离线 DDP/RLCD；它没有 selected-only、延迟
反馈或逐事件参数更新接口。当前 earning-roles 代码也没有实际加载 Laya 权重。

RLS、Beta/LinUCB、IPS、replay、遗忘正则、gated state、短 unroll、LoRA、
异步 learner 和 RLinf Channel 都有现成先例或明确的工程用途。把这些模块并置
不能构成新的训练方式。现有合成结果只验证了 selected-only 事件协议和一个小头
的可行性，不能证明算法创新。

## 决定

1. Laya multilingual 322M 继续保留为**候选 encoder、静态基线和初始化来源**，
   但不称为已确定 backbone。Laya English/typed-decisions 421M、Kev/NanoJev、
   AnyJev+Qwen 只作为待比较候选或基线，直到真实任务上的小闭环完成。
2. 冻结 encoder + 在线 RLS 是可靠基线和部署下界，不是论文最终方法。下一次
   实验必须能区分静态表示能力、在线更新收益和训练方法本身的收益。
3. 核心创新必须落在“每条 selected-only 延迟反馈如何更新可写参数，同时保护
   旧能力”的新机制上。候选假说暂保留三条：
   - meta-learned event update operator；
   - delay/version-correct event-sourced updater；
   - protected-plasticity update。
4. 在没有完成先例边界、真实数据合约和最小判别实验前，不选择三者之一，不开
     大规模训练，不把任一候选写进论文主张。
5. 如果新机制在相同可写参数、更新预算、探索率和 selected-only 信息下不能稳定
   超过 RLS/online SGD/周期 refit，主张收缩为工程/系统贡献。

## 为什么已有项目没有直接解决这个问题

这不是“别人漏做了一步”。Laya 的目标是静态 typed-decision 精度、校准和
高速推理；AnyJev 的目标是冻结表示上的轻量 head 与周期性 refit；通用 online
bandit、test-time adaptation 和 continual learning 通常分别假设固定臂、较完整
标签、任务边界或不同的服务约束。它们覆盖了问题的不同切面，不能据此声称交叉
组合已经是新方法；交叉缺口仍需与最接近方法逐条对照并做消融。

## 后果

- `docs/research/streamjev_method_spec_v2.md` 作为当前工程 baseline 规范保留，
  但其方法地位降为“待创新机制替换的基线版”。
- 下一次先做真实数据资格和 Laya/候选 encoder 的小型 static smoke；不做无目标的
  backbone 横向大筛选。
- 研究问题的创新边界、候选机制和否决条件记录在
  `docs/research/streamjev_novelty_boundary_20260925.md`。
