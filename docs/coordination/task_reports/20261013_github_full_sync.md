# GitHub 全量信息同步 — 2026-10-13

目标：将 earning-roles 当前研究进展同步到已有 GitHub 归档仓库。

- 仓库：https://github.com/sherkevin/earning-roles-from-evidence
- 分支：`codex/aamas-real-validation-20260922`，遵循 ADR 0051。
- 不合并或改写 main，不改变其他项目或上游源码仓库。

## 归档范围

GitHub 原分支为 `f396d8c256cd297e5e12defba99113fec151275c`。本地已有 6 个
尚未同步提交，最新为 `56a85a8d4848582ab01f303ba720168393f13d8d`。差异涉及
3,589 个文件，涵盖论文源码、中文稿、主 PDF、历史图稿与 PDF、研究与评价文档、
实验矩阵、配置、调用和失败记录、测试、研究论文资料以及引用核查证据。

本轮补充 `work/research-snapshots/20261013-github-sync/research.sqlite3`。
采用 SQLite backup API 读取源数据库，完整性检查为 `ok`；manifest 保存表计数、
SHA-256 和恢复信息。活动数据库及 WAL/SHM 不直接上传，一致性备份保留研究信息。

嵌套源码的四份 EntCollabBench 数据文件与 graph-ipd 补丁，逐字节匹配
`references/benchmark_sources/LOCAL_CHANGES_20261009/` 内已经跟踪的副本。
无需改动或推送上游仓库，固定子模块版本及本地改动归档同时可得。

## 检查与执行

未同步提交引入的 1,540 个 Git blob 版本，合计 185,857,842 字节，以及新增的
数据库备份已检查高置信度凭证模式，未发现匹配。最大单个 blob 为 7,090,505 字节。
此扫描不宣称能识别所有形式的秘密。既有忽略规则及 ADR 0051 指定的会话、配对、
传输运行状态继续排除，没有删除本地研究数据。

GitHub 分支没有独有提交，可以快进推送，无需 rebase 或 force push。
`git-pipeline` 执行 dry-run；实际显式暂存并指定 `github-archive`，避免自动脚本
收集活动数据库日志或推送到默认 GitLab upstream。

提交时发现遗留 `.git/index.lock`。检查没有打开该文件的进程，也没有正在运行的
Git 写操作后，将空锁文件移入 `.git/` 内的留存文件，随后重试。

## 论文状态与验证

本轮不重编、不修改论文。目前主 PDF 是带 `EXPECTED -- NOT OBSERVED` 水印的
预期值预览，不作为真实实验结果。正文 8 页，参考文献从第 9 页开始，总计 10 页。
主版 SHA-256 为 `0889cfd5a8fd6f2e4c9fe62e7e202d38767bd478843b8602a1d897dc1dde0206`。
同步不改变研究 Goal、验收标准或科学投稿 gate。

预检查证据：`docs/coordination/sync_records/20261013-github/preflight.json`。
推送完成后核对 GitHub 远程分支 SHA 与本地提交，不能仅以本地 commit 成功代替同步成功。
