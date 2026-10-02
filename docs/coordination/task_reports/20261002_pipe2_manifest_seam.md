# PIPE2 fixture authority manifest seam

日期：2026-10-02（环境日期）
状态：`PARTIAL`；零调用工程 seam 完成，PIPE2 仍不是 benchmark。

## 目的

为 PIPE2 的下一次严格 qualification 提供一个显式、可回放、fail-closed 的 fixture
authority seam。该工作只处理 fixture bytes、来源和摘要，不选择 authority，不修改
TeamBench pinned checkout，也不启动候选代码、LLM、GPU 或 native grader。

## 实现

新增 `scripts/peerrolebench_pipe2_fixture_manifest.py`，版本为
`pipe2-fixture-authority-v1`，包含：

- `authority_kind` 仅允许 `pinned`、`derived`、`valid_subset`；
- TeamBench commit、generator/overlay SHA-256、schema/key columns、public/hidden seed
  split、每个 seed 的 source/expected path 与 bytes digest；
- `malformed_policy` 强制使用 `reject_without_label` 和 `unknown_without_label`，并拒绝
  fallback/default label；
- root digest 覆盖 manifest 内容，`benchmark_qualified` 必须为 `false`；
- 重复 seed、未知 split、缺字段、越界路径、schema 不一致、root digest 或文件 digest
  不匹配都会抛出 `ManifestError`；
- `load_public_fixture` 只返回 public source bytes 和 schema。expected bytes 只在完整性
  校验中读取，不进入 public payload，也不返回 expected path/digest；
- `create_manifest` 只读取已有 fixture 文件计算摘要，不运行任何候选代码。

## 验证

新增 `tests/test_peerrolebench_pipe2_fixture_manifest.py`，覆盖真实临时 fixture bytes：

- authority、commit、generator/overlay digest、split、policy 和 root digest 读取；
- public loader 隔离 expected 内容，hidden seed 拒绝；
- 重复 seed、未知 split、跨 split 重复、缺字段、允许静默 label、
  `benchmark_qualified=true` 的 fail-closed 行为；
- source bytes 和 hidden expected bytes 被篡改时分别拒绝。

定向结果：`8 passed`。

## 边界

此 seam 没有把任何 derived fixture、valid subset 或 manifest 升格为 benchmark，也没有
修改 active benchmark/baseline 文档。下一步仍需由作者确认 authority path，并在该 manifest
之上完成全 seed replay、responsibility/judgment、later assignment、independent history
和 same-information baseline parity，之后才有资格申请新的真实 episode。
