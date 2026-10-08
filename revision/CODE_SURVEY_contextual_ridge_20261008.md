# 任务条件线性对照：复用核查

日期：2026-10-08；范围为候选 baseline 的表示与计算，不锁定论文方法。

## 原始需要

对同一组 Agent，任务改变时最合适的人可能改变。现有身份 one-hot 不足以表达这个关系；单个共享线性头简单拼接任务向量也不能表达交叉偏好。需要候选与任务的交互，不是更多身份字段。

## 已核查的一手来源与可复用部分

- Li et al., WWW 2010，[原文 §3.1、§3.2、§5.2.2](https://arxiv.org/html/1003.0146v2)：分别给出候选独立线性参数、共享加独立参数及交互特征。本文借用经典 disjoint ridge 作为对照，不把它当新算法；尚未实现其 UCB 探索项。
- [NumPy kron 文档](https://numpy.org/doc/stable/reference/generated/numpy.kron.html)：用于独立批量参考表示；运行核心复用既有 `SignedRidgeState`，不真的分配全部候选的大矩阵。
- [MiniLM 官方模型卡](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)：384 维短文本 encoder，Apache-2.0；默认长于 256 wordpieces 的输入截断。现有本地权重可用于零外部调用的表示审计，不据此选定最终 backbone。
- [SentenceTransformer API](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html)：复用已安装库与本地文件模式；CPU、冻结权重、禁下载。实际版本与文件摘要由执行卡记录。

## 本地复用结论

复用 `scripts/peerrolebench_signed_ridge.py` 数值核心，在同文件添加按精确 candidate@version 隔离的统计量组。复用现有 `DecisionSidecar.captured_features` 接口规划封存，暂不修改 native runner。现有 C1 只记录 selection binding 摘要，不能宣称它已经保存了可恢复的完整特征。

现有 `_public_features` 用菜单位置作 one-hot 坐标；在历史固定菜单下未证明发生错配，但菜单重排时坐标含义会变。新对照按身份/版本字典取状态，避免该问题。`MetaTeamProfile` 目前是信息边界合同，不是已经生成的语义画像或 encoder；不冒充可直接复用的学习模型。

本地完整 MiniLM snapshot 为 `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`。只有 CPU 表示审计获准在本轮执行；不触发新任务生成、judge API、GPU、正式比较或 ACTIVE 方法切换。

实际审计发现467token合同超过MiniLM的256限制，因此仅补一次已缓存 [BGE-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) 的覆盖检查（MIT；revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`，384维、原生512）。四份输入不截断，但这不是语义质量评比或最终模型选择。一手页面和模型卡已保存到 `references/aamas/contextual_ridge_sources_20261008/`，含URL和摘要；模型权重留在原缓存，不复制入仓库。
