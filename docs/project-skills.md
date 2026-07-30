# Skills 登记

> 项目所需 Skills 通过 Hermes 全局 skill 管理或项目内 skills/ 目录维护。

| Skill | 用途 | 负责维护 | 适用场景 | 风险边界 |
|---|---|---|---|---|
| project-governance | 项目治理框架 | 主控 | 所有任务执行 | 无法读取时暂停 |
| evolution-dashboard-management | 本项目管理规范 | 主控 | 修改 dashboard UI、数据、部署 | 不替代构建验证 |

## Skills 规则

- 所有任务第一步读取并使用 project-governance skill
- 涉及代码、Git、自动化时加载 evolution-dashboard-management skill
- 项目专属 Skill 进入仓库 skills/ 目录（当前无项目专属 skill）
- 全局 Skill 通过 skill_manage 统一管理
- 模块不得私自依赖未登记的全局 Skill

## Skills 维护流程

1. 子代理在自优化回传中建议新增 Skill
2. 主控评估是否值得沉淀
3. 如确认，主控用 skill_manage 创建/更新
4. 登记到本表
5. 通知相关模块（下次 delegate 时在 context 中引用）
