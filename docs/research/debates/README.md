# 研究辩论记录

这里保存 earning-roles 的结构化研究辩论 charter、来源、证据、claims 和逐轮结论。
它不是故事线、方法论或 benchmark 的第七份 active 规范；这些规范仍以
`docs/research/canonical/active_versions.json` 为准。

每次辩论必须：

1. 先写 charter，明确阶段、问题、候选主张、约束和人类决策门；
2. 独立完成 Round 0，再公布其他 agent 的报告；
3. 用 `POSITION/TARGET/EVIDENCE/REASONING/DECISION TEST/CONFIDENCE` 格式进行挑战；
4. 最多三轮；没有新增证据或决定性测试时停止；
5. 综合时保留少数意见、kill criterion 和 unresolved 项，不用多数票证明创新或真理；
6. 只由 coordinator 写 synthesis/task report，review agent 不改 active 研究文档；
7. 需要改变 primary track、Goal、active benchmark 或方法时，停在用户决策门。

当前辩论目录：

- `benchmark_baseline_lock_20260929/`：ArtifactRole 与 PeerSelect/IPD 的 primary/secondary、benchmark authority、baseline parity 和最小 kill test。

当前推荐的工具组合：

- `/Users/jingwu/.codex/skills/paper-research-pipeline/SKILL.md`：B/M/E/D/R 研究阶段和结构化辩论；
- `/Users/jingwu/.codex/skills/paper-research-pipeline/references/debate_protocol.md`：轮次、角色和消息格式；
- `/Users/jingwu/.agents/skills/orchestration/SKILL.md`：Orca Run/Task/Dispatch、FIFO 消息、worker lifecycle 和 decision gate；
- `/Users/jingwu/.codex/skills/paper-reviewer/SKILL.md`：进入投稿前 R 阶段时的五视角独立审稿。
