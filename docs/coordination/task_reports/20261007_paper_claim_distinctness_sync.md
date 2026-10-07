# 论文 claim 与任务 distinctness 同步

日期：2026-10-07。状态：`PARTIAL / INTERNAL_BUILD_VERIFIED`。

## 目的

把刚完成的任务 distinctness 审计反映到正文措辞，避免读者把候选 benchmark 的
计划字段误读成已经通过 live qualification 的结果。此任务不改变故事线、方法合同、
benchmark/baseline 版本，也不填任何实验结果。

## 修改

在 [`article/aamas2027/main.tex`](../../../article/aamas2027/main.tex) 做了三处窄化：

- `unseen quality and cost` 改为 `held-out future quality and cost`，明确这是待测目标；
- `root-level splits` 改为 `pre-registered root-level split requirements`，不暗示独立 root 已存在；
- ArtifactRole 的字段描述改为 `is specified to expose`，与当前 candidate/not-frozen 状态一致。

独立只读审查确认摘要、结论、结果占位和 cross-root matrix 没有把历史 C1 写成
RARE 效果或泛化结果，因此没有扩大修改范围。

## 构建证据

隔离目录构建命令为：

```text
python3 scripts/build_aamas2027.py --main-only \\
  --build-dir build_distinctness_20261007 --require-content-pages 8
```

构建日志和摘要保存在
[`experiments/logs/paper_distinctness_claim_sync_20261007/`](../../../experiments/logs/paper_distinctness_claim_sync_20261007/)。
PDF 为 9 页，其中正文 8 页、References 从第 9 页开始；hash 为
`3174a7799a195a1de8353da5d363c167ef39e5924f91dba72446a0987e344a23`。

这只是版式与 claim 边界验证，API/GPU 均为 0，scientific submission gate 仍关闭。
当前图稿有其他协作者的未提交修改；本次只保存窄化文本及隔离 PDF，不覆盖其工作。

## 三份标准对照

| 标准 | 本轮变化 | 仍未满足 |
|---|---|---|
| 故事线与创新 | 目标性措辞更准确，避免把计划当成结果 | 独立 live 证据、创新增量和完整 falsification |
| 方法论 | 不改变 observation/credit 分离 | 合法后续 reward、实时性、稳定性和遗忘结果 |
| Benchmark + baseline | 正文与 candidate/not-frozen registry 一致 | root freeze、强同信息 live parity、真实矩阵和完整成本 |

下一步仍是预算发行、provider/TZ/source-target ledger preflight；不以这次 8 页构建
替代科学结果，也不启动 A800。
