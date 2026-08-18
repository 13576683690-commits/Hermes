# 前端 Agent 文档

## 绑定信息

- **所属项目**：进化档案馆 (evolution-dashboard)
- **Git 分支**：main（本项目不使用多分支，直接在 main 上开发）
- **Agent 文档**：docs/agents/frontend.md
- **上游**：main（主控）

## 主要职责

React 组件开发、UI/UX 调整、样式修改、构建验证。

## 可直接处理

- 修改 `src/` 下的组件代码（App.jsx, ArchiveCard.jsx, StatsGrid.jsx, ViewRouter.jsx）
- 修改样式（src/styles.css, tailwind.config.js）
- 修改 HTML 模板（index.html）
- 本地 `npm run build` 验证
- 调整布局、动画、交互

## 必须暂停并提交主控

- 改变 data.json 数据结构（影响数据层）
- 新增 npm 依赖
- 修改构建配置（vite.config.js, postcss.config.js）
- 改变设计语言（深色极简 → 其他风格）

## 可用资源

- React 18 + Vite 5 + Tailwind CSS 3
- src/components/ 组件目录

## 常用 Skills

- `project-governance` — 治理框架
- `evolution-dashboard-management` — 本项目管理规范

## 风险边界

- 构建产物（dist/）不提交到源码仓库（.gitignore 排除）
- 改动后必须 `npm run build` 验证通过
- 设计规范：深色系 `#0f111a` 背景，`#a5b4fc` 主文字色
- Web 资源严禁中文命名（CI/CD 中引发 404）

## 固定检查清单

- [ ] 当前分支正确
- [ ] 已读取 AGENTS.md
- [ ] 已读取本模块 Agent 文档
- [ ] 已判断风险等级
- [ ] `npm run build` 验证通过

## 固定产出

- 修改后的组件代码
- 构建验证结果（build 成功/失败）

## 回传格式

```
任务标题：
分支：main
状态：完成 / 阻塞 / 需主控判断 / 需用户确认
产出文件或链接：
数据来源：
执行动作：
验证方式：
风险变化：
自优化结果：
建议下一步：
```

## 自优化沉淀区

### 2026-07-29 — React 组件拆分
- 可复用经验：ArchiveCard 展开/折叠 + 点击复制指令的标准交互模式
- 沉淀目标：Agent 文档
- 状态：已沉淀

## 执行历史

### 2026-07-29 — React 18 SPA 重写
- 状态：完成
- 产出：App.jsx + 3 子组件（ArchiveCard, StatsGrid, ViewRouter）
- 风险等级：低（本地开发 + 构建验证）
