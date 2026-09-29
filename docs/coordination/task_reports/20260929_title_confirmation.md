# 2026-09-29 标题确认与 LaTeX 同步

- **状态**：`COMPLETE`
- **对应 Goal**：ER-G1（论文主张与故事线表达）
- **Goal 变更请求**：`false`
- **用户确认**：已确认使用 `Earning Roles: Self-Evolving Responsibility from Situated Peer Judgments`。

## 已完成

- 更新 [`research_proposal.tex`](../../../../article/aamas2027/research_proposal.tex)；
- 更新 [`mainline_pre_results.tex`](../../../../article/aamas2027/mainline_pre_results.tex)；
- 关键词统一为 `self-evolving roles`、`peer judgment`、`online adaptation`；
- 历史 `main.tex`/`supplement.tex` 保持不变；
- 新增 [ADR 0041](../../user/decisions/0041-select-earning-roles-title.md)，并更新决议索引；
- 候选标题文档状态改为 `SELECTED_WORKING_TITLE`。

## 验证

- `python3 scripts/build_aamas2027.py --proposal`：1 页，引用已解析，无 overfull box；PDF metadata title 为新标题；
- `latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build mainline_pre_results.tex`：3 页，PDF metadata title 为新标题；
- 内置 LaTeX compiler 已尝试，但其独立编译上下文缺少项目 `aamas.cls`，因此返回 `File aamas.cls not found`；项目自带模板构建已成功，源码保留未改动。

标题的 `self-evolving` 是研究目标定位，不是当前已验证的效果声明。实时更新、遗忘、漂移恢复和 role-learning efficacy 仍须由 benchmark/baseline 验收和真实实验支持。
