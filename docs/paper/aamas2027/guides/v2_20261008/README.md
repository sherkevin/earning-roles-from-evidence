# Guide v2：联合分布、误差与置信度

日期：2026-10-08。类型：`ASSUMPTION_CONDITIONAL / NOT_OBSERVED / NOT_FITTED`。

版本状态：`ARCHIVED_CONDITIONAL_DISTRIBUTION_REFERENCE`。
当前研究 Guide 为 [v3](../v3_20261008/README.md)；本版联合模型、计算和固定 PDF 保留，
不再独立宣称为当前 Guide。此状态更新不改变任何历史数值或原始 PDF。

**数学一致性已独立审查；真实方法效果的预测置信度仍未建立。** 这份 Guide 给科学家
提供可复算的分布参照和失配诊断规则。它不把未经测量的 RARE、baseline 排名写成预期事实，
也不取代 Goal、三份标准或确认实验卡。v1 留存，但不再作为效果与误差的预期依据。

## 查看与复现

- 唯一当前 Guide：[guide_experiment_matrix.pdf](../../../../../artifacts/aamas2027/guide_experiment_matrix.pdf)。
- 固定版本：[v2 PDF](../../../../../artifacts/aamas2027/guide_experiment_matrix_v2_20261008/guide_experiment_matrix.pdf)。
- [LaTeX 源](../../../../../article/aamas2027/guides/v2_20261008/guide_experiment_matrix.tex)。
- [参数与范围](joint_model_spec.json)；[精确计算](../../../../../artifacts/aamas2027/guide_experiment_matrix_v2_20261008/joint_distribution_calculations.json)。
- [空白对标模板](pilot_distribution_comparison_template.csv)；[独立审查](independent_review.md)。
- 生成：`python3 scripts/build_experiment_target_guide_v2.py`。PDF 编译命令和来源摘要保存在
  `experiments/logs/experiment_target_guide_20261008_v2/`。

PDF 每页均有 `GUIDE — NOT OBSERVED` 水印、状态页眉和页脚。正文结果表与 main.pdf
不由本任务写入。版本修改前的源码、计算和 PDF 另存，不能删除来隐藏错误。

## 为什么撤回 v1 的预期矩阵

v1 分别赋予方法质量、成本与误差目标，没有拟合它们共同的生成过程。其平衡风险人群
与选择后人群之间缺少明确的选择关系；假定的 SD=.06 也没有真实流支持。数字可以
局部演算正确，却不足以支持真实方法的联合分布、排序和预测置信度。

现有最完整参照仍是单个 PIPE3 root 的八次真实 API 调用：没有更新后执行的新任务，
没有独立的方法未来历史，也没有合格的概率—终局标签评价人群。单次 0.520/0.297 ms
更新与 3408/4688 bytes 状态可作精确事件参照，不能预测 p95、遗忘或后续效果。

## 新版怎样保持联合自洽

同一任务中，假设两个候选类型的成功概率为 .7/.3；选择更好类型的概率由 κ 决定。
同一已选结果 Y 同时决定质量、预测损失、返工费用和效用。成本另有明确的独立
±.1 等概率扰动。所有 κ、质量差、预测偏差、费用和扰动都是未拟合的情景输入，
没有哪一个真实方法被指定为某种情景。

- 选择人群改变时，质量与 Brier/ECE 均在同一个选择后人群上计算。
- 从候选计数、两组成功计数和费用扰动计数的二项分布精确积分，得到均值、SD、
  离散预测区间和协方差，避免为每列单独指定有利误差。
- S2/S3 的 Brier 都是 .2125，统一显示四位小数，避免浮点舍入制造不存在的差异。
- S3 的 population ECE=.05，而 30 次独立观察的 sample ECE 期望约 .09995。
  两者不同来自绝对值与有限样本，不能以总体值强行要求样本值。
- Q 与费用的负相关来自“失败增加返工费用”假设；效用由两者导出。真实系统若成功
  需要更多 token，相关性可能不同，应修订费用模型，不能改实测。
- 配对方差取决于候选潜在结果的耦合。跨 root 效果差异和流内相关又会扩大误差；
  同一个平均提升可以对应越过零的规划区间。

前两页是指定 iid 冻结策略和 Rademacher 扰动下的精确分布。root/ICC 页是已知假定
方差下的 normal 规划近似，不属于前述精确分布，也不是实测置信区间或 power 保证。
离散区间的概率质量针对未舍入端点计算；这不是留出数据上的预测覆盖率。

## 科学家怎样对标

先资格化 root、scorer、责任真值、强 baseline 和合法反馈；每臂保留自己的实际历史。
开发数据用于拟合，未来独立流/root 用于检验。空白 CSV 一行对应一个
`root × stream × arm × metric`，不含虚构观察或默认方法效果。

1. 记录拟合版本、信息截止点和评价窗口，再写分布中心、SD 和 80%/95% 预测区间。
   一组指标必须来自同一套联合拟合及费用定义；不能逐列调成满意的数。
2. 填实测值、合法分母、UNKNOWN 数和来源 receipt。propensity 与预测正确率分别保存。
   任一资格失败都不能补成零或成功。
3. 比较残差、区间成员资格、指标协方差、跨 root 偏差及流内相关。标准化残差只是诊断，
   不应自动套用正态显著性检验；离散值可另用已定义的概率变换。
4. 在未参与拟合的独立流上报告 80%/95% 覆盖、区间宽度和它们的抽样不确定性；按 root、
   J/owner 类别分层。相依流要用相应的统计单位。宽到没有决策价值的区间也不合格。
5. 失配先区分选择、人群/标签、费用、反馈延迟、序列相关和 UNKNOWN，再修订模型。
   模型失配不能成为改实测、换分母或降低验收标准的理由。

κ 与 u 是分析用的潜在参数，不能从 selected-only 标签均值单独识别。若无法合法测量
候选真值，应直接拟合可观察的流级联合分布和方法差值；不要补造未选候选结果。
同 seed 不保证自适应方法的未来产物或潜在结果相同。

## 与三张正文矩阵的关系

| 正文表 | Guide 可提供的对标关系 | 尚缺的真实数据 |
|---|---|---|
| 方法预测/分派 | 同人群 Brier、ECE、Y、完整费用、效用的联合误差 | 合格概率与标签；各臂独立未来历史；强对照 |
| 服务/漂移 | 单次事件参照；服务上限与排队的条件关系 | 完整更新尾延迟、到达过程、状态轨迹、旧/新 holdout |
| 消融/责任 | 四格交互与联合协方差；责任违规与 coverage 的分别计量 | 独立四格历史、合法多样 J、独立 owner 真值与负例 |

方法效能排序、假设参数的现实拟合及留出覆盖仍是 OPEN。独立审查的 GO 只表示条件
模型计算正确、边界清楚；这次改进没有打开科学投稿 gate。0 新 API，0 GPU 作业。

## 后续补充：公开原生成绩参照

用户要求的公开档案已放在
[reasonable_results/earning-roles](../../../../../../reasonable_results/earning-roles/20261008_v1/README.md)，
含 TeamBench、Meta-Team、CooperBench、DecisionBench 和 graph-ipd 的原生成绩、统计
单位、误差定义与固定来源。TeamBench 的 binary pass 与 partial 不能互换，部分作者
版本存在冲突；其155题混合聚合不能拟合真实模型方差。Meta-Team 的整体增益与L2消融
差值分别记录。具体对标规则见档案中的 `HOW_TO_USE.md`。

这些参照没有把本 Guide 的 .7/.3、κ、费用或方差变成拟合参数，也没有给 RARE/L2-public
赋值。PDF仍为条件模型v2；该补充只提供出处入口，不修改PDF、Goal或正式结果。
