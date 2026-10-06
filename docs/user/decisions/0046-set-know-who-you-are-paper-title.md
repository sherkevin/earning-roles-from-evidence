# ADR 0046 — 将主稿标题统一为 Know Who You Are

日期：2026-10-06
状态：Accepted
范围：earning-roles 当前 AAMAS 主稿、proposal 和 pre-results 阅读稿

## Context

ADR 0041 先确认了 `Earning Roles: Self-Evolving Responsibility from Situated Peer
Judgments`。随后围绕投稿标题的记忆点、动态性和跨任务想象空间，用户确认采用
`Know Who You Are` 作为标题前缀。当前主稿已经使用该前缀，但 proposal、pre-results
稿和 ADR 仍保留旧标题，形成了可见的标题漂移。

## Decision

当前生效标题统一为：

> **Know Who You Are: Earning Roles from Situated Peer Judgments**

`Know Who You Are` 负责留下跨任务的想象空间；`Earning Roles` 指角色机会通过交付、
使用和责任安全的反馈逐步获得；`Situated Peer Judgments` 明确证据来自真实协作者对
具体交付物的使用判断。

## Interpretation boundary

标题表达研究对象和目标机制，不等于已经证明了自进化、实时训练、稳定性或角色学习
收益。摘要、正文和结果表仍必须遵守 Goal 的证据边界；在真实确认实验完成前，不能
把标题解释成已经取得的效果。

## Consequences

- `main.tex`、`mainline_pre_results.tex`、`research_proposal.tex` 和 AAMAS 阅读 README
  统一使用该标题。
- ADR 0041 被本决议 supersede；其历史理由与旧标题仍保留，避免丢失决策过程。
- 本决议只解决标题治理，不改变故事线、方法、benchmark、baseline、Goal 或科学门。
