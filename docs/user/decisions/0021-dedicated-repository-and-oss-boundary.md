# ADR-0021：earning-roles 使用独立仓库与 OSS 前缀

日期：2026-09-27
状态：Accepted

## 背景

earning-roles 最初与 benchmark 在同一工作区中推进。两者后来形成了不同的
任务、数据、实验预算和论文叙事：benchmark 研究医药 provider/tool selection，
earning-roles 研究从 situated peer judgments 学习协作角色。共享目录和 OSS
前缀会让实验归属、复现实验和删除操作产生歧义。

## 决策

1. earning-roles 的 canonical Git 远端是：
   `git@gitlab.alibaba-inc.com:jingwu.jw/earning-roles.git`。
2. earning-roles 的 OSS canonical 前缀是：
   `jingwu/earning-roles/`，同时使用 `ai4sci-develop-storage` 和
   `ai4sci-develop-fast`，endpoint 为 `oss-cn-zhangjiakou.aliyuncs.com`。
3. 旧的 earning-roles OSS 前缀 `earning-roles/` 已逐对象复制到
   `jingwu/earning-roles/`，完成对象数、大小和 ETag 比对后删除旧前缀。
4. benchmark 的 Git、任务、源代码、实验日志和 `jingwu/benchmark/...`
   OSS 前缀不属于本次迁移，不能因仓库分离而删除或改名。
5. 凭证只通过本机受保护配置或运行时注入使用，不进入 Git、OSS、实验日志
   或本文档。

## 迁移证据

迁移日志保存在：
`experiments/logs/oss_prefix_migration_20260927/`。

归档桶旧前缀 80 个对象、813,346 bytes，快速桶旧前缀 10 个对象、36,439
bytes。复制后两桶分别得到相同的对象数、相对路径、大小和 ETag；删除后旧
前缀查询结果均为 0，新前缀仍为 80/10 个对象。

## 后果

今后的代码、报告、训练数据和实验产物只写入 earning-roles 仓库和
`jingwu/earning-roles/`。需要复用 benchmark 的开源资料或方法时，复制并
记录来源，不移动 benchmark 的原始资产；跨项目数学边界只在各自仓库中维护。
