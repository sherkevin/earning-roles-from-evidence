# 2026-10-04 六大叙事范式全量核查

## 核查范围

- 正文：`article/aamas2027/main.tex`
- 叙事参考：`research/2026_AI顶会最佳杰出论文叙事范式_六大范式_阅读整理.md`
- 项目验收：`docs/research/versions/evaluation/storyline/storyline_v1.3_20260928_eval.md`
- 核查性质：论文写作与故事线，不启动实验，不改变 benchmark、baseline 或 Goal。

## 主链核查

当前正文可压缩为：

```text
dependency-bearing collaboration
→ producer defect 与 recipient integration 的最小反例
→ responsibility confounding
→ situated judgment 的归因缺口
→ responsibility-safe public evidence
→ sealed future assignment
→ delayed selected-only credit
→ unseen quality/cost 与 falsification boundary
```

主范式仍为 **①根因手术刀**；②反直觉重构作为 hook；④新基准/比较矩阵暴露近邻的识别缺口；③理论照亮经验目前以 event-time、read-cut、assignment freeze 和可检验不变量呈现，尚未声称定理。

## 逐项结果

| 检查项 | 当前判断 | 证据或缺口 |
|---|---|---|
| 现象与后果 | 通过 | 首段先写 dependency-bearing workflow，再进入研究问题 |
| 最小反例 | 通过 | queue producer contract defect / recipient consumer defect 产生相同 rejection 和 terminal failure |
| sharp gap | 通过 | raw acceptance/terminal reward 不能识别 producer responsibility |
| 唯一机制 | 通过 | situated judgment → responsibility gate → public evidence → future assignment → delayed credit |
| 标题 | 通过 | `Know Who You Are: Earning Roles from Situated Peer Judgments`，未把 backbone 或 runtime 冒充贡献 |
| 摘要五句 | 通过 | 问题、限制、机制、可证伪预测、范围/代价完整；未写未验证效果 |
| Introduction | 通过 | 现象→反例→根因→机制→贡献→路线图→范围边界 |
| Related Work | 通过但需持续维护 | novelty table 按具名近邻、observation/update/credit/object/difference 组织；Auer 已限定为 classical selected-reward control |
| 公式可读性 | 改进后通过 | event 和 score 后均有 queue 实例；符号对应 task/menu/artifact/action/ownership/cost |
| 方法预测性 | 改进后通过 | 三项 properties 改写成可检验 predictions，并映射 RQ2–RQ4 |
| 实验叙事 | 设计级通过 | RQ1→RQ2→RQ3→RQ4；补充方向、MCID/precision、区间和停止规则字段要求 |
| 结果/讨论 | 证据门未通过 | 结果单元仍为空，不能写成闭环收益或泛化结论 |
| 六大范式③理论 | 部分通过 | 当前是协议不变量/可回放约束，若要强理论范式仍需形式命题与证明 |

## 不得在本轮偷偷解决的事项

以下不是文字润色可以替代的缺口：独立 root/live history、later-use、完整成本、同信息强 baseline、真实闭环结果、最终 benchmark 冻结和 claim–evidence 逐句绑定。它们保持 OPEN，不通过改写降低标准。

## 本轮写作修改

1. Figure 1 caption 改为 typed ledger field 的协议描述，去除 planned/not-reported 的部分元话语。
2. 在 `e_t` 与 `score` 后加入 queue 的具体实例，避免公式凭空引入符号。
3. 将“three intended properties”改成可检验 predictions，直接连接 RQ2–RQ4。
4. 将 PeerSelect 的定位收窄为 update behavior 的局部轨道，避免把它写成 ArtifactRole 证据。
5. 补充 primary contrast 的方向、最小重要差异或精度目标、95% interval 和 stopping rule 的预冻结要求。
6. Headline table caption 改为正文风格；结果仍由 confirmation manifest 提供，不伪造数值。

## 版式验证

`python3 scripts/build_aamas2027.py`：主文档 7 页，保守正文末页 7，无未解析引用、无 overfull box。当前 PDF SHA-256：`c4dce1f7f2af16f1c64fedd994e2cc411e5c542993fe6532a907fd97e35d21d3`。

## 审查状态

补充修订：将 recipient 改为 `k` 并在实例中明示 `j_t=k`，以避免与 $R_t$ 冲突；将 phase trace 表改为正文段落以保持 7 页；对所有 figure/table 做了正文引用检查，未发现未引用图表；新增 `docs/research/primary_endpoint_cards_v0.1_20261004.md`，记录 H1--H4 的稳定 ID 和 endpoint 语义，但明确标记 `DESIGN_ONLY / NOT_FROZEN`，因为数值 MCID/precision 和 stopping rule 尚未冻结。独立 Codex reviewer 复核已给出 conditional PASS。`goal_change_requested=false`。
