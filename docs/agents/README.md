# Agent 文档索引

> 分支 → Agent 文档映射。每个模块有独立的角色档案，定义职责、权限、边界。

| 模块 | Agent 文档 | 核心职责 |
|---|---|---|
| 主控 | [main.md](main.md) | 任务管理、资源统一、风险裁判 |
| 前端 | [frontend.md](frontend.md) | React 组件开发、UI/UX、构建验证 |
| 数据 | [data.md](data.md) | data.json 管理、归档追加、数据完整性 |
| 部署 | [deploy.md](deploy.md) | GitHub Actions、Pages 发布、远端状态 |
| 自优化 | [self-optimization.md](self-optimization.md) | 自优化规则与复盘流程 |

## 必读规则

所有模块执行任务前必须读取：
1. `AGENTS.md`（项目总章程）
2. 本模块 Agent 文档
3. `docs/risk-gates.md`（风险门禁）
4. `docs/project-skills.md`（Skills 登记）
