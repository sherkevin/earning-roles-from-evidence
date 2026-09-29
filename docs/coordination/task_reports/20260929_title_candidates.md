# 2026-09-29 论文标题候选

- **状态**：`PARTIAL`
- **对应 Goal**：ER-G1（故事线和论文主张）；不改变 ER-G2–ER-G4
- **Goal 变更请求**：`false`
- **实验/API/GPU**：0

## 做了什么

阅读了当前 active storyline、pre-results manuscript、AAMAS 论文写作规范和已有多 agent/self-evolving 论文材料。当前标题
`Learning Roles from Situated Peer Judgments in Multi-Agent Collaboration` 准确，但没有把“角色由证据获得、随着反馈动态变化、可以迁移到更广泛协作系统”放到标题层面。

形成了标题候选文档 [`title_candidates_v0.1_20260929.md`](../../research/candidates/title_candidates_v0.1_20260929.md)，并把标题评价标准固定为：动态/自进化、situated peer judgment 主线、future responsibility、跨任务想象空间和不过度承诺未验证结果。

## 推荐顺序

1. `Earning Roles: Self-Evolving Responsibility from Situated Peer Judgments`
2. `Who Should Do What Next? Self-Evolving Roles from Situated Peer Judgments`
3. `Know Who You Are: Self-Evolving Roles from Situated Peer Judgments`

第一版最平衡；第二版最像标准科学问题；第三版记忆点最强，但需要在摘要开头解释“know who you are”不是自我认知，而是由协作者对实际交付的使用证据形成动态责任画像。

## 边界

标题候选没有把 `self-evolving` 写成已被当前证据证明的结果，也没有把 active paper source 直接改成新标题。v6 仍只有责任安全/协议链证据，没有 role-learning efficacy；正式标题要在方法和结果确认动态更新主张后激活。

## 下一步

等待作者在候选中选择或提出修改；确认后再同步 `research_proposal.tex`、`mainline_pre_results.tex`、LaTeX metadata 和摘要。Goal、故事线、方法和 benchmark 文档不因标题选择而改变。
