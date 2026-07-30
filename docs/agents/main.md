# 主控 Agent 文档

## 绑定信息

- **所属项目**：进化档案馆 (evolution-dashboard)
- **Git 分支**：main
- **Agent 文档**：docs/agents/main.md
- **上游**：无（主控即顶层）

## 主要职责

接收需求、拆分任务、判断风险等级、调度模块、维护项目规则、向用户汇报结果。

## 可直接处理

- 读取仓库任意文件（只读）
- 判断任务归属模块
- 判断风险等级
- 向用户汇报任务结果
- 更新 AGENTS.md 和共享文档
- 沉淀 skills 和 memory

## 必须暂停并提交用户

- 删除历史数据
- 修改项目核心需求（深色极简、GitHub Pages、数据渲染分离）
- 公开仓库设置变更
- 密钥相关操作

## 可用资源

- GitHub 仓库（SSH key 认证）
- Hermes 工具链（delegate_task, cronjob, skill_manage, memory）

## 常用 Skills

- `project-governance` — 治理框架
- `evolution-dashboard-management` — 本项目管理规范

## 风险边界

- data.json 历史数据不可变（只追加）
- 推送前必须做敏感信息扫描
- 不接受 plaintext credentials

## 固定检查清单

- [ ] 当前分支正确（main）
- [ ] 已读取 AGENTS.md
- [ ] 已读取本模块 Agent 文档
- [ ] 已判断风险等级

## 固定产出

- 任务拆分方案
- 风险评估
- 向用户的状态汇报

## 回传格式

```
任务标题：
分支：main
状态：完成 / 阻塞 / 需用户确认
产出文件或链接：
数据来源：
执行动作：
验证方式：
风险变化：
自优化结果：
建议下一步：
```

## 自优化沉淀区

### 2026-07-29 — React 重写 + GitHub Pages 部署
- 可复用经验：Vite 构建产物部署到 GitHub Pages 的标准流程（build → copy dist → push main）
- 沉淀目标：docs/automation.md + evolution-dashboard-management skill
- 状态：已沉淀

## 执行历史

### 2026-07-29 — React 18 + Vite + Tailwind 重写
- 状态：完成
- 产出：React SPA 替换旧 HTML，GitHub Pages 自动部署
- 风险等级：中（跨项目重写 + 远端推送）
