# 公开任务与接收方表示：复用与边界

日期：2026-10-08。目的：把新决策时实际可见的任务与接收方条件变成可恢复表示。

- 复用 `build_materials` 的公开 producer/recipient payload，不能读整个 material manifest 或 expected。其中 task_text 可提供可读合同，source_files 仅在属于实际公开视图时可使用。
- 复用已核查且缓存的 BGE-small-en-v1.5、SentenceTransformer encode/tokenizer；固定 revision，不下载或再筛模型。完整输入超过原生限长则拒绝，本轮不添加压缩模型。
- 复用 `Pipe3SelectionBoundary` 的 captured_features、DecisionSidecar 与新 capture save/load；不用第二套选择器或结果账本。
- 现有 profile generator 是固定软件夹具；现有 history schema 没有历史任务/接收方全文。二者不能替代真实语义支持库。本轮不得声称已接入完整同信息经验。

最小候选将任务合同与接收方公开合同分别编码，再等权拼接为一个上下文向量。接收方 ID、声明版本、read cut 和原文作为可追溯元数据保留；不把不透明 ID 的 embedding 当能力。声明版本不是托管模型权重不变的证明。

该输入规则是候选表示，不是方法创新，也不改变已生效方法。独立任务条件 ridge 仍是经典对照；其更新需要另行合格的所选后续收益。两位 Codex 已分别只读核查接口复用与方法限制。
