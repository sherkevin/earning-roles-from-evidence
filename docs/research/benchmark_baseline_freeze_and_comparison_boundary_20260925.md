# Benchmark、Baseline 与当前效果结论

> 日期：2026-09-25  
> 状态：建议冻结，等待项目负责人确认后作为主实验协议  
> 目标：先确定可比较的数据与方法，再评价动态 JEV/实时更新器。

## 先回答当前争议

此前“当前方法效果不好”有两层含义，不能混在一起：

1. **已经完成的 earning-roles 小实验**只比较了合成 selected-only 流中的 `static`、关联式 S/Z 更新、对角最小二乘、OnlineRLS，以及最近的 residual fast-weight。它回答的是“这个更新器在受控机制实验中是否比简单在线回归更好”，不是公开 benchmark 的最终结论。
2. **benchmark 仓库**已经在 LLMRouterBench、ASlib SAT12-ALL 和 BBB 上跑过 incumbent、UCB1、Beta-TS、LinUCB、LinTS、ACTS 以及部分 RFF/PAK、P-LinUCB/P-TS、Pareto 风格适配器。但这些结果目前是 canonical baseline 之间的比较；我们的 residual fast-weight/dynamic JEV 尚未在完全相同的正式协议中跑完。因此，不能据此声称“我们的方法比这些 baseline 都差”。

严格表述应为：**在现有合成控制流中，当前更新器尚未超过 OnlineRLS；在短流中几乎没有收益；在切换流中 residual fast-weight 有优势，但还没有公开 benchmark 证据。**

## 冻结的数据集与角色

### 主 benchmark：LLMRouterBench 固定可审计子集

作用是检验现代模型/工具路由中的 selected-only 在线选择和新候选接入。

- 本地已核对的 panel：11,481 个 query-context、20 个候选模型、15 个数据集。
- 每个实例有候选模型的离线质量分数，可以构造同一批数据上的回放；决策时只把已选模型的反馈交给 learner。
- 固定训练/验证/测试划分、模型池、上下文变换和延迟反馈队列。
- 主要指标：累计 reward、regret、challenger regret、beneficial-adoption precision/recall、harmful adoption rate、更新与决策延迟。
- 事后全臂最优只作 oracle 上界；未选模型的分数不能泄露给在线方法。

选择它作为主 benchmark，是因为它是当前最完整的公开 routing 框架，并且已有统一的基线适配器和成本/性能评估接口。官方资料显示，LLMRouterBench 覆盖 21 个数据集、33 个模型、40 万以上实例，并集成 10 类 routing baseline；我们的固定子集只取其中可审计、可重复的一部分。[官方仓库](https://github.com/ynulihao/LLMRouterBench) · [ACL Findings 论文](https://aclanthology.org/2026.findings-acl.1881/)

### 次 benchmark：ASlib SAT12-ALL

作用是检验方法是否只是利用 LLM 文本路由的特殊结构。

- 1,614 个实例、31 个 solver、113 个实例特征。
- 固定官方 CV split；特征填补、标准化、PCA 和 PAR10 处理必须只在训练折拟合。
- 把 solver 看成候选工具，把实例特征看成上下文，把运行性能映射成 reward/cost。
- 报告与 LLMRouterBench 相同的在线指标，同时保留 PAR10 作为领域原生指标。

ASlib 是算法选择领域的标准化数据格式和场景库，SAT12-ALL 的场景元数据和数据发布均可独立获取。[ASlib 场景库](https://www.coseal.net/aslib/) · [SAT12-ALL 场景](http://coseal.github.io/aslib-r/scenario-pages/SAT12-ALL/index.html)

### 领域案例：BBB/Task36 医药工具回放

作用是检验真实工具输出、版本和真值延迟下的工程可用性，不承担唯一主证据的责任。

- 当前 dense panel：722 个有真值的分子、7 个 provider/tool；另有 652 个 scaffold-held-out 完整样本用于冻结回放。
- 保留 provider/version、工具可用性、冲突和局部优势信息。
- 采用 selected-only delayed feedback；未选 provider 不产生伪负反馈。
- 论文中称为真实领域 case study 或 project replay，不称作已经公开完成的社区 benchmark。

### 机制附录：小型合成流

用于单独诊断稳定性、漂移恢复、探索覆盖、反馈延迟和更新开销。它不能替代上述两个公开 benchmark，也不能单独支持方法优越性结论。

### 自建 PTRB/CooperBench 方向

自建 benchmark 仍然可行，但当前只作为 peer-judgment 协议 smoke 和未来 benchmark 贡献候选。要升级为主 benchmark，必须补齐独立 evaluator、公开 episode schema、隐藏测试 split、版本锁定、从 clean clone 可重放，以及 recipient-only/no-handoff/fixed-cooperation 等反作弊对照。现有审计发现 CooperBench 的 feature 预分配、缺少结构化 acceptance/role update、merge conflict fallback 等问题，暂不能把 `both_passed` 当成 peer 使用了 producer artifact 的证据。

## 冻结的 baseline 矩阵

所有方法必须看到相同的候选菜单、上下文、反馈延迟、探索预算、随机种子和 memory/update budget。

| 层级 | 方法 | 用途 |
|---|---|---|
| B0 | Best-Fixed / Incumbent-only | 增量接入的安全下界；必须有 |
| B0 | Random、UCB1、Beta-TS | 无上下文探索 sanity check |
| B1 | LinUCB、Linear Thompson Sampling | 标准 contextual-bandit 基线 |
| B2 | ACTS | 直接建模 challenger 相对 incumbent 的 advantage |
| B3 | PAK-UCB / RFF-UCB | 非线性、按候选分别建模的强近邻 |
| B4 | P-LinUCB、P-TS、ParetoBandit-style onboarding | transfer、到达和多目标扩展；先放附录 |
| 上界 | Oracle | 事后知道所有候选结果的上界，不能部署 |
| Ours | Dynamic JEV / residual fast-weight | 只有在同一协议封存后进入主表 |

PAK-UCB 的公开工作明确把 prompt-level model selection 建模为 contextual bandit，并使用 per-arm kernel/RFF 更新；因此它是我们需要正面比较的近邻，而不是可以绕过的背景方法。[PAK-UCB 论文与代码](https://arxiv.org/html/2410.13287) · [代码仓库](https://github.com/yannxiaoyanhu/dgm-online-select)

## 已有 baseline 证据

以下数字来自 benchmark 仓库的冻结回放文件，均不是把未选候选标签交给在线 learner 的 full-information 结果。

### LLMRouterBench

在 stationary all-arm history 回放中，平均 reward 为：Best-Fixed/UCB1/Beta-TS `0.67366`，LinUCB `0.70125`，LinTS `0.68734`，offline Ridge `0.70351`。

在 frozen incumbent vs zero-history challenger 回放中：

| 方法 | mean reward | mean IOU | harmful adoption |
|---|---:|---:|---:|
| Incumbent-only | 0.70426 | 0.00000 | — |
| Beta-TS | 0.70302 | -0.00124 | 0.31815 |
| UCB1 | 0.69475 | -0.00951 | 0.26960 |
| LinUCB | 0.68742 | -0.01684 | 0.19418 |
| LinTS | 0.67979 | -0.02447 | 0.22604 |
| ACTS | 0.64824 | -0.05602 | 0.23883 |

这里的 incumbent 很强、challenger beneficial-context rate 约为 `0.05580`，所以“探索越多越好”会直接造成负收益；这正是动态接入需要解决的任务条件，不是 baseline 失效的理由。

### ASlib SAT12-ALL

在 stationary 回放中，Best-Fixed/UCB1/Beta-TS/LinUCB/LinTS/offline Ridge 的平均 reward 分别为 `0.74334/0.74334/0.73923/0.84936/0.79940/0.83476`。

在 frozen challenger 回放中，Incumbent-only `0.87395`，Beta-TS `0.86314`，LinTS `0.78409`，LinUCB `0.75630`，UCB1 `0.74488`；所有已跑方法都低于 incumbent。这说明低机会率和冷启动风险在经典算法选择场景中也存在。

### BBB dense panel

固定 incumbent 为 `0.92768`。UCB1/Beta-TS/LinUCB/LinTS/ACTS 分别为 `0.89703/0.92189/0.90020/0.91454/0.91542`，均低于 incumbent；challenger beneficial-context rate 约为 `0.03921`。

## 我们自己的更新器目前能支持什么结论

在 earning-roles 的合成控制流中，5 个 seed 的长 stationary 流结果是：

| 方法 | reward | regret | 解释 |
|---|---:|---:|---|
| Static | 0.3686 | 0.1104 | 不更新 |
| Associative S/Z | 0.4501 | 0.0290 | 能学到稳定关系 |
| OnlineRLS | 0.4578 | 0.0212 | 当前最强简单在线基线 |
| Residual fast-weight | 0.4192 | 0.0598 | stationary 下尚未超过 RLS |

在 regime-switch 流中，Residual fast-weight `0.5466` 高于 Static `0.4980`、Associative `0.5183` 和 OnlineRLS `0.5240`。因此当前可复述为“有漂移时有潜力，稳定环境下仍落后”，而不是“整体效果不好”。短 100-step smoke 中 associative `0.4187` 与 static `0.4183` 几乎相同，也说明短流不能作为实时学习成功的证据。

这些结果仍然不等于公开 benchmark 结果。下一步必须把 Dynamic JEV 接入同一套 LLMRouterBench/ASlib runner，使用 B0+B1+B2+B3 的封存配置跑一次，才能回答它是否真的超过现有方法。

## 下一步只保留一条实验路径

1. 封存 LLMRouterBench 固定子集的 split、model pool、context adapter、delay queue、seed 和 cost accounting。
2. 先运行 B0、LinUCB、LinTS、ACTS、PAK/RFF-UCB；完成 source-level fidelity 检查后才把结果写入主表。
3. 用完全相同的信息权限和预算接入 Dynamic JEV/residual fast-weight；记录 reward、regret、beneficial precision/recall、harmful adoption、drift recovery、p50/p95 update latency、memory。
4. 在 ASlib SAT12-ALL 重复同一 protocol，验证是否跨域成立。
5. 最后把 BBB 作为真实医药 case study；如果公开 benchmark 不成立，不用 BBB 单点结果补救。

在这条主比较完成前，不提交新的 Nebula 大任务；当前 Nebula 只有已验证的 dry-run 计划，没有实际提交记录。

## 证据文件

- benchmark 选择与协议：`/Users/jingwu/work/benchmark/research/AAMAS2027_Benchmark_Selection_Review.md`、`AAMAS2027_Evaluation_Protocol.md`
- baseline 结果：`/Users/jingwu/work/benchmark/data/tool_results/divergence/t2_*`、`t3_*`
- earning-roles 实验：`references/aamas/streamjev_20260924/experiments/logs/bounded_residual_fast_weight_isolation_20260925_results.json`
- 更新器候选说明：[bounded_residual_fast_weight_candidate_20260925.md](bounded_residual_fast_weight_candidate_20260925.md)

