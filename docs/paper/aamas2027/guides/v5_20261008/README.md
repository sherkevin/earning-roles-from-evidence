# Guide v5：条件化方向矩阵与科学关闭门

日期：2026-10-08。状态：`CURRENT_CONDITIONAL_DIRECTION_GUIDE_PENDING_EVIDENCE`。

v5 不是一组结果，也不把 v4 的关闭规则改成更低的标准。它修正 v4 与正文结果表之间的语义断裂：每个可比较的 regime×contrast 现在必须同时声明四个独立端点的方向、机制前提、反证和允许的 claim。方向只在前置条件由 development stream 或外生 mutation 封存后才可进入 confirmation；观察到结果后不得倒推条件。

## 与 v4 的关系

- v4 保留为历史版本，负责 B1--B7 的 fail-closed benchmark+baseline 关闭契约。
- v5 只新增方向矩阵、baseline/arm 资格边界、端点拆分和结果录入约束；它没有关闭任何科学 gate。
- 主 Guide PDF 可以展示 v5，但主回执仍必须在真实证据齐全后才从 `OPEN` 变为 `CLOSED_FULL`。

## 方向符号

所有符号均表示 RARE 相对指定 baseline 的预注册方向，而不是已观测数字。

| 符号 | 含义 |
|---|---|
| `>` | RARE 在该端点应优于 baseline；只有前提、共同评估集和信息/成本平价均已封存时才可检验 |
| `=` | 机制预测近似无差异；必须用预注册等效/非劣边界判定，不是“没有显著性” |
| `<` | RARE 在该端点应劣于 baseline；这是有意保留的负向 regime |
| `?` | 没有诚实的先验方向；只做双侧估计，不得包装成优越性 |
| `N/A` | 该 arm 尚未资格化或该端点不属于它；保留 NO-GO 原因，不可把空白当作胜负 |

端点必须分开：H1 是共同 held-out cohort 上的 Brier/log loss（越低越好）；H2 是独立 future assignment→independent $Y$ 的完整成本效用 $U=Y-\lambda C$（越高越好）；H3 是固定到达率/资源预算下的 publish/read/update p95、backlog 与 drop/timeout（越低越好）；H4a 是按 owner truth 计的 false producer attribution（越低越好），H4b 是 coverage、abstention 和 UNKNOWN 的伴随报告。H4b 不是可被 abstention 人为抬高的 precision 单列指标。

## 资格边界

主 ArtifactRole hero comparison 必须包含：uniform/no-update、raw acceptance、terminal-only、contextual-trust-linear（完整公共表示）、task-conditioned ridge 或明确 NO-GO、pooled controller、冻结配置的 RARE，以及 closest published adapter 或明确 NO-GO。J-masked、count-only、trace-only 是信息反事实，不是可省略的附加消融；证据×delayed-credit 必须是同一 stream 的四臂 factorial。Meta-Team L2-public 在未完成同协议适配前只能显示 `NO-GO`。

所有 adaptive arms 使用各自独立的 realized-history namespace；不能让 pooled controller 读取其他 policy 的 live state。所有 baseline 共享 candidate menu/version、合法 read cut、公开字段、encoder/checkpoint/schema、机会集、延迟、探索、服务/API/token/tool/state/queue budget 和完整成本合同。

## 当前不可宣称的内容

当前没有合格 confirmation roots、完整 live baseline parity、独立 streams、future-Y、统计/成本回执、clean replay 或独立科学关闭复核。因此 v5 仍是 `OPEN`。v1 的 5pp、`.20` assignment-change、`0.297ms` 等数值已经撤回，不能回填到本版本。

## 关闭条件

沿用 v4 的 B1--B7，不因方向矩阵完成而自动关闭。只有真实收据中 B1--B7 全部 `PASS`、每个 root×stream×arm×factor target cell 有分母、主轨 future-Y 已独立评分、统计/成本/UNKNOWN/失败完整、clean replay 和独立复核通过时，才可写 `CLOSED_FULL`。正向、中性或负向的完整结果都可以关闭证据门，但各自只能支持相应范围的科学结论。

## v5 审查结论

三位 Codex 独立审查员分别检查了 benchmark/baseline、效果一致性、方法边界。共同意见是：v4 的关闭契约合理，但原正文矩阵遗漏强同信息 control、保留错误的 `ΔA↑`、混合 H4 与 continual-learning 指标，并把未资格化 adapter 放进可比较行。v5 已把这些问题变成明确的 NO-GO、方向、反证和录入规则；下一步仍是获得真实证据，而不是填写预测数字。
