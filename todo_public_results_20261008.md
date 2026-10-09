# 公开成绩参照台账

目标：把当前 benchmark/baseline 的一手公开成绩、评价口径和可比性落到用户指定 reasonable_results；不把公开成绩移植为我们的实测或高置信度预测。

- [doing] 2026-10-08 核查 TeamBench 原生公开成绩、任务/模型/预算与结果统计单位；产出 teambench 来源与结果表。
- [doing] 2026-10-08 核查 graph-ipd/PeerSelect 原生公开成绩与 payoff 定义；产出 peerselect 来源与结果表。
- [doing] 2026-10-08 核查 Meta-Team、DecisionBench、CooperBench/MultiAgentBench 的相关公开成绩；只保留直接相关且一手可核验的记录。
- [open] 2026-10-08 汇总可比性矩阵、偏差约束和对 Guide 的使用规则；不修改 Goal 或科研规范。
- [open] 2026-10-08 核对引用、逐条来源/单位/误差定义，写 task report、更新 Guide 使用入口。

- [done] 2026-10-08 TeamBench原生来源与结果归档：160条记录、26份源，binary/partial分开，模型归属与版本冲突保留。
- [done] 2026-10-08 graph-ipd归档：4条实证文字记录、29份源，公开合作率阈值不转为payoff；原PDF/图已保存。
- [done] 2026-10-08 Meta-Team/CooperBench/DecisionBench归档：11条记录、5份源，统计单位与缺失误差明确。
- [done] 2026-10-08 独立可比性审查修复metadata与来源归属，审查前版本保留；不为RARE/L2-public移植数字。
- [done] 2026-10-08 175条CSV值/指针、60源hash/size通过；task report与Guide入口同步，Goal不变。
- [pending] 2026-10-08 真实方法高置信度预测：缺合格独立future streams与同口径联合误差；本任务不启动实验、不用公报补造。
