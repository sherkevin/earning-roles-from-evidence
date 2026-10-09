# Task report — Guide v5 conditional direction matrix

日期：2026-10-09

## 目的

审查 v4 Guide 是否只写了关闭规则而没有把方法何时赢、何时平、何时输写成可执行矩阵。三位独立 Codex 审查员分别检查 benchmark/baseline、效果一致性和方法边界；本次修订不使用任何新 API、GPU 或 benchmark 结果。

## 发现

三份审查一致指出：当前真实证据仍只有诊断性快照，没有合格 confirmation roots、live baseline parity、独立 future-Y 或方法效能；因此科学 gate 仍必须 `OPEN`。v4 与论文表之间还存在四个阻断问题：强同信息 task-conditioned ridge/匹配对照缺失；`assignment change` 被错误标成向上成功指标；H4 attribution 与 forgetting/recovery 混在一起；未资格化的 published adapter 被放进可比较行。

## 完成的修订

- 新建 `docs/paper/aamas2027/guides/v5_20261008/directional_matrix.json`，为 regime×contrast 封存 `>`、`=`、`<`、`?`、`N/A` 语义、机制前提、falsifier、允许 claim 和 H1/H2/H3/H4 端点门。
- 新建 v5 PDF 源，加入 baseline/NO-GO 资格表、evidence×delayed-credit 四臂 factorial、local/global 对照、updater factor、方向矩阵、稳定性/安全矩阵、结果账本和 v4 B1--B7 关闭规则。
- 明确 RARE 只在“typed evidence 对强同信息 control 有增量信息、异质性和合法支持充分”的条件下预期胜出；在 trace 已解释、constant J、stale/mismatch、稀疏历史、高成本/高到达率条件下允许平局或失败。
- 保留 v4 历史版本，把主 Guide PDF 和 master receipt 同步到 v5；回执仍为 `CURRENT_CONDITIONAL_DIRECTION_GUIDE_PENDING_EVIDENCE` 与 `closure_status=OPEN`。

## 验证

- `directional_matrix.json`、`gate_spec.json`、`review_rounds.json` 通过 JSON 解析。
- v5 LaTeX 编译成功，5 页；0 overfull、0 fatal、0 undefined；每页有 `GUIDE / NOT RESULTS` 水印。仅有字体替代和 1 个 underfull 警告，不影响内容或页边界。
- 生成和同步过程日志：`experiments/logs/experiment_target_guide_20261008_v5/`。
- 没有产生科学结果：`new_api_calls=0`、`gpu_jobs=0`、`benchmark_runs=0`。

## 未完成与下一步

v5 解决的是方向和矩阵语义，不是实验资格。下一步必须建立 activation manifest，明确结构独立 roots、每 arm 的 independent streams、共同 held-out cohort/随机 transport、future assignment→independent Y、总 API/token/wall budget、MDE/precision 和 stopping；然后逐 arm 做 live parity，最后才允许填数并运行 v4 closure validator。不能用 v5 的方向符号或软件测试替代这些证据。
