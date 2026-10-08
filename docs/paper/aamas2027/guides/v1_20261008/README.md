# 实验矩阵 Guide v1：研发目标与预期情景

日期：2026-10-08。类型：`GUIDE / PROSPECTIVE / NOT_OBSERVED / NOT_PREREGISTERED`。

**后续置信度审查：ARCHIVED_EXPECTATIONS_WITHDRAWN。** 方法均值、误差及人群之间
缺少已拟合的联合生成过程，不能作为高置信度预期。本文数字和历史 PDF 保留不改；
当前参照为 [v2 条件分布 Guide](../v2_20261008/README.md)。本页“当前独立 Guide”链接
指向新版主 Guide，v1 固定版本链接仍指向历史文件。

这是用户要求的新建目标文档，不是实验结果，不是已冻结的确认实验卡，也不替代
Goal 和三份验收标准。后续可用它比较真实实验距离目标的差距；不能将其中的值复制
到论文结果、摘要、图表或结果日志中冒充实测。每页 PDF 有斜向水印、红色状态页眉
和页脚，表格附近再次标明其目标性质。

## 查看与复现

- 当前独立 Guide：[PDF](../../../../../artifacts/aamas2027/guide_experiment_matrix.pdf)。
- 不可变版本：[v1 PDF](../../../../../artifacts/aamas2027/guide_experiment_matrix_v1_20261008/guide_experiment_matrix.pdf)。
- 编辑源：[LaTeX](../../../../../article/aamas2027/guides/v1_20261008/guide_experiment_matrix.tex)。
- 输入假设：[target_spec.json](target_spec.json)。
- 计算与来源摘要：[calculations.json](../../../../../artifacts/aamas2027/guide_experiment_matrix_v1_20261008/calculations.json)。
- 构建入口：`python3 scripts/build_experiment_target_guide.py`，随后编译独立 LaTeX。
  后续实质修改必须新建版本；首轮审查前 PDF/source/spec/calculations 已保留在
  v1 输出目录的 `pre_independent_review/`，不能删除。

## 数字从哪里来

**实测参照**只有原始 PIPE3 开发运行：8 次真实调用；三组产出检查 2/3、接收方
检查 3/3、旧 adoption 检查 1/2；两次更新耗时分别 0.520 和 0.297 ms；没有更新后
实际执行的新任务。原始评分版本、共享产物和范围限制保留，不能将这些检查比例
当作独立任务正确率。

**Table 1 的工作目标情景 S1**假设 no-update 的未来完整成功率为 .50，强线性基线
为 .55，RARE 为 .60。它要求我们比强基线提高 5 个百分点，同时允许完整成本比
no-update 多 5%；这是一项需要实验兑现的目标，现有结果不支持这条性能排序。
统一使用 Guide-only 的 `U = Q - 0.10 C`，因此 RARE 的目标 U=.495，强基线
U=.447，差值 .048。所有效用由输入计算，没有单独手写有利的效用数字。

Brier 使用明确的两组风险情景和同一评价人口计算。Calib 使用固定概率区间的
population ECE：常数 .5 预测的 ECE=0，但 Brier=.25；因此没有把“常数预测校准
好”错误解释成具有信息价值。Meta-Team 尚未合格，数字只代表条件性的强基线
参考水平，不是对其真实性能的估计。

**Table 2 的数字是服务/适应目标**，不是无依据的 p95 预测。5 ms 包括缓存 64 维
输入下的小 head 更新、记录与状态序列化，不包含未知 backbone 的 forward/backward。
完整的实时训练仍须另测；此处不能替代该验收要求。更新参考方法和 RARE 使用相同
延迟预算，强 graph 参考和 RARE 的目标 payoff、恢复速度相同。100 events/s、4 条
一批、40 ms 到达一次，在每条最大服务时间 5 ms 的假设下，20 ms 可排空一批；
仅有 p95≤5 ms 不足以证明 backlog≤4。动态状态预算包含 head、128 条缓冲记录和
metadata，演算为 38 KiB，低于 64 KiB；冻结模型、完整 ledger 和进程内存另计。

**Table 3 的四格消融**使用相同的质量/成本口径，交互项恰为 .020。public evidence
开关只控制 selector 能否读源观察；operator 保留合法 assignment/lineage receipt，
delayed-credit 开关控制是否更新。各臂有独立历史和自己的实际目标反馈，不能复用
别的臂的 realized label。无责任门的压力情景取四类误归因率 .25/.15/.10/.05，
等权平均 .1375，与消融表一致。完整方法的零误归因是 fail-closed 的研发要求，
不是统计测出的零。当前 selected-only 合同无法定义合法的“无 selected-only”
效果预测，所以该行明确 N/A，留待单独定义诊断干预，不能虚构未选候选的反馈。

## 不只保留成功情景

PDF 同时列出无质量增益、微小增益、成本超支，以及强基线胜出。最后一种的
RARE−control utility=-.072。后续真实结果若为负，应保留结果、分析并改进方法；
不能改数字使之接近 Guide。no-locality 情景也允许质量略高、但完整成本更贵，
没有强迫所有消融在每个指标上都输。

## 样本量和代价约束

18 个 paired streams、至少 3 个结构独立 root，只是工作量情景。基于假定的配对
流 SD=.06 和 utility 差值 .048，normal approximation 约需 13 个流；18 个流的
条件精度半宽约 .030。这不代表跨 root 泛化或多重比较有 80% power；需要开发
pilot 方差、root-aware 统计、正式 primary contrast 和预算冻结后重新确定。

8 个臂 ×18 个流 ×30 个未来任务，约 4320 个 target episodes。以每个 fresh target
3 次调用、每流每臂再加 3 次初始 source 调用计，骨架约 13,392 次调用、24.30M
tokens、40.9 summed API hours；仅沿用现有 8 调用的平均长度与耗时，不是完整成本
预测，也不是下一次实验规模。先通过 root/label/baseline 资格，再做有界开发 pilot；
profile、重试、工具、scorer、通信和训练成本必须另列。生成 Guide 没有运行任何
API、GPU 或 benchmark，也没有修改现有执行预算。
