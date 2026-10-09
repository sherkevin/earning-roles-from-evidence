# Task report — 公开 benchmark/baseline 成绩参照

日期：2026-10-08。状态：`PUBLIC_REFERENCE_ARCHIVED / METHOD_FORECAST_OPEN`。
Goal变更：false。0 新模型推理、0 benchmark运行、0 GPU作业。

## 目的与标准

用户要求将公开的benchmark/baseline已跑成绩保存到`~/work/reasonable_results`，
约束实验预期的量级、分布和误差。本任务只接受作者论文/官方仓库一手来源；每条
数字必须绑定模型、任务、指标、N、误差定义与版本。不把改造任务继承为原生成绩。

## 完成了什么

新增独立目录：
[`reasonable_results/earning-roles/20261008_v1`](../../../../reasonable_results/earning-roles/20261008_v1/README.md)。
同级原有资料保持原样。保存TeamBench、graph-ipd、Meta-Team、CooperBench、DecisionBench
原生参照；MultiAgentBench只登记官方来源。三组结构化档案共175条记录，另有可筛选CSV，
包含精确数、上下界和定性信息。60个源文件约9.36MB，固定URL/版本、时间和SHA-256可回查。

TeamBench归档论文主榜、Mini、我们相关PIPE/DIST任务的单次原始分数。原生binary pass
与partial score分开；graph-ipd合作率与环境payoff/解析回报分开。Meta-Team全系统与L2
消融收益分开。每格缺少误差时保留not_reported，没有用原始样本量补造SE/CI。

## 对预期有帮助的发现

- TeamBench-Mini .7544是partial，不能解释成75.44%成功率或据此支持Guide .60。
  论文90题榜单的二元成绩另列，并标明90是归一化分母而非每格完成数。
- Meta-Team Ansible原生成绩40.8→53.9%，但无L2为50.7%；整体13.1pp和L2边际3.2pp
  不能混为一个模块的预期提升。原生L2成绩仍不能迁移为public adapter。
- DecisionBench GAIA .407→.393，以及CooperBench通信对照提示额外信息/协作可以
  没有收益；Guide不可强迫所有新增机制正向改善。
- graph-ipd公开的是20run、末100轮的合作率文字范围与图上95%CI，缺少精确端点、
  经验payoff及我们的实时/遗忘/恢复结果。本地14.15 smoke仍不能与之换算比较。

## 问题、审查与修复

三个Codex gpt-6-sol worker分开收集来源，一个只读方法审查员独立核对可比性。
审查发现并修复DecisionBench fidelity子集被误写为跨三套件、Meta avg@3统计单位、
Cooper共享任务对的非独立性和印刷差值冲突。还修复四个非90题行的metadata分母，
以及Meta Table3消融沿用Table1推断说明的问题。所有审查前档案保留。

进一步核查发现TeamBench的155题摘要无模型/API/输入来源；默认合并脚本不校验模型。
该分布标为mixed/unattributed，不作为已验证真实模型方差先验。论文、事实表、仓库
部分值冲突并列保存，未选有利版。来源核对不等于独立重跑证实论文实验。

CSV逐条位置/值、60个源文件的哈希/大小和主要链接已核查。首次本地metadata核查因
字面匹配过严失败，修正核查条件后通过；失败记录保留，无数据值改动。

## 与Goal和三份标准的对照

本任务改善benchmark/baseline参照依据、实验结果解释和预期约束。它不能关闭原生任务
到ArtifactRole的资格、强baseline同信息比较、独立未来history、真实联合方差、实时/漂移
或科学投稿gate。Guide .7/.3、κ、成本、root方差/ICC仍未拟合；有公开数字不等于这些
参数已估计，也不自动证明benchmark公认权威或符合我们的故事。

可复用资产已落地：原生相关任务记录、评分与预算定义、误差单位、历史长度/identity
条件、收益矩阵、源PDF/图、CSV来源索引，以及原生→本项目映射与对标规则。
下一步应按相同指标/任务/模型/预算做资格化的真实pilot，拟合可观察联合分布并检查
独立留出覆盖。本任务未启动该实验，没有修改Goal、方法或标准。

构建/核查记录：`experiments/logs/public_results_reference_20261008_v1/`。
当前Guide说明已链接公开档案；主PDF和条件模型参数未改。
