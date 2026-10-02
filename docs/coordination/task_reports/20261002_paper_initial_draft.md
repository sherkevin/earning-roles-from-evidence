# 2026-10-02 AAMAS 论文初稿任务汇报

## 任务

根据当前生效的故事线、方法合同、benchmark/baseline 计划及三份评价标准，建立一份正式的 AAMAS LaTeX 初稿。本文是内部 pre-results draft：不填任何方法效果数值，不把工程资格回执写成 scientific efficacy，不改变 Goal 或六份 active research documents。

## 已完成

- 将旧的历史 allocation/router 主稿保留为 `article/aamas2027/main_historical_allocation_20261002.tex`。
- 重写 `article/aamas2027/main.tex`，当前主标题为 **Know Who You Are: Earning Roles from Situated Peer Judgments**。
- 采用单一中心问题：situated recipient judgment 是否能经过责任归因，形成 producer role evidence，改变执行前的 future assignment，并在未见任务上改善质量与完整成本。
- 将方法写成两阶段合同：`publish` 只发布不可变 public evidence；`choose` 使用 read cut 并封存 propensity；`validate/update` 只对后续 assignment 做 delayed selected-only credit。
- 明确区分 producer contract、recipient action、downstream adoption、terminal outcome 和 `UNKNOWN`，并写入重复、乱序、版本替换、correction、replay 与资源失败的 no-op/UNKNOWN 语义。
- 记录候选 RARE 机制和其可替换组件边界；没有把 Laya、AnyJev、RLS、online SGD、periodic refit 或 frozen representation 直接称作创新。
- 写入 ArtifactRole 主轨和 PeerSelect 副轨，保留二者的 label、scorer、分母和 scientific claim 隔离。
- 写入完整 baseline table：uniform、no update、raw acceptance、terminal-only、contextual trust/bandit、pooled controller、closest published adapter、RARE。
- 写入四个 RQ，及包含 root/split、policy/intervention、责任变异、drift、延迟反馈、消融和成本指标的完整实验矩阵。结果列全部为空占位。
- 写入指标、stream-level uncertainty、95% interval、完整成本、UNKNOWN 分母、Ablation、falsification、失败处理和结果解释 truth table。
- 写入当前真实证据的窄边界：现有链路只支持工程资格和问题发现，不能支持 role specialization、future quality improvement 或实时训练收益。

## 验证

构建命令：

```bash
python3 scripts/build_aamas2027.py
```

结果：

- `main`: 5 pages，content pages 5，citations resolved，no overfull boxes。
- `supplement`: 2 pages，citations resolved，no overfull boxes。
- 官方 AAMAS class/bst/by.pdf 校验通过。
- submission gate 仍保持关闭，符合 pre-results 约束。
- 期间曾出现一次 `amssymb` 与模板的 `\\Bbbk` 重定义，以及一次长公式 overfull；已移除多余包并将故事链/时间链拆成 aligned equations，最终构建通过。

## 引用边界

本次没有新增外部引用，也没有使用未经核验的 citation key。主稿只使用项目已有 `references.bib` 中的条目：partner selection、reputation、LLM multi-agent organization、dynamic role assignment、bandit comparator 等。没有把 TeamBench-derived 候选写成已经冻结的公认 benchmark；主稿将其明确标为 candidate，待上游 provenance、root independence、scorer、clean replay 和 independent live history 资格通过后再提升 claim 等级。

## 仍被 submission guard 阻塞的主张

- benchmark 尚未冻结，第二 structural root 和独立 confirmation split 尚未关闭；
- seven-arm live parity、closest published adapter、完整 later-assignment 与 complete cost 仍未完成；
- 没有独立 live histories 证明 judgment 的 out-of-sample 信息价值或 future assignment 后果；
- 最终 backbone、representation、updater 和实时训练结果尚未确定；
- update p50/p95、drift response、forgetting、UNKNOWN precision 和 quality--cost utility 尚无科学结果；
- 因此当前稿件是可审阅的 pre-results 方法/实验合同，不是 submission-ready efficacy paper。

## 下一步

先由研究主线确认这份初稿的结构和术语，再在 benchmark/baseline gate 通过后按矩阵生成冻结 experiment card。只有真实 raw evidence 与 claim-evidence reconciliation 完成，才能将空表格替换为结果并准备 submission build。
