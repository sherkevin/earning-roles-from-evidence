# Signed ridge 数值核心复用核查

日期：2026-10-08。用途：候选完整矩阵对照；不锁定 ACTIVE 算法。

第一性需求是同一平方损失的在线累计与正确求解。现有 NumPy 1.26.4 提供所需
外积、矩阵计算和线性求解器，复用它即可，不新增训练框架或运行依赖。

- 现有 `FeatureContextualTrustPolicy` 只有对角统计量，不能当完整岭回归求解器；保留原版本。
- 官方 scikit-learn Ridge 给出相同目标函数；它是批量估计器，本轮用完整X/u重建方程作参考。
- 核查 River `river/utils/math.py` 的 Sherman–Morrison 实现，固定 commit
  `a7fdc82073e2765fb5bfb55e6e517fa0cf28eacd`，BSD-3-Clause。其源码和LICENSE已下载，
  没有复制进运行模块或安装新依赖。逆矩阵递推在本轮小正则反例中出现抵消，故采用NumPy solve。
- 原始来源和下载摘要见 `references/aamas/signed_ridge_sources_20261008/provenance.json`。

新增代码只维护A/b/w与输入校验，不实现 reward 认证、任务运行、选人或消息框架。
当前求解为 O(d³)，不声称与高效平方根RLS等价的计算开销；能否满足完整系统延迟要实测。
