# A800 首轮运行命令（待队列确认）

这不是科学结果任务，而是测量缓存表示 scorer 和逐事件 fast update 的真实
GPU 延迟。它不读取 Task36/38 数据，也不会把 CPU 结果冒充 A800 结果。

当前推荐队列快照显示 `pailitao_algo_high_a800` 有可用 A800 配额；正式提交前
仍需确认队列和工作区策略。命令由 Nebula CLI 生成，按 `nebula-support` 规则不
在本地自动执行写操作：

```bash
nebula-cli run mdl \
  --nebula_project nebula_trial \
  --queue pailitao_algo_high_a800 \
  --worker_count 1 \
  --worker_gpu 1 \
  --algo_name pytorch280 \
  --job_name streamjev-a800-runtime-20260924 \
  --git_path https://github.com/sherkevin/earning-roles-from-evidence.git \
  --git_branch codex/aamas-real-validation-20260922 \
  --commit_id ba63c59ce80224dc1d3fe64c48317e582656761d \
  --entry references/aamas/streamjev_20260924/nebula_entry.py \
  --user_params "--steps 20000 --state-dim 32 --hidden-dim 64"
```

提交前的硬检查：确认队列、A800 配额、远程 commit 可见；运行结束后取回
`config.json`、`raw.jsonl`、`results.json`，再讨论 p50/p95 和吞吐。这个 job 的
结果只能回答 runtime 假设，不能回答真实数据效果。
