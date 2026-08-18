# 部署 Agent 文档

## 绑定信息

- **所属项目**：进化档案馆 (evolution-dashboard)
- **Git 分支**：main
- **Agent 文档**：docs/agents/deploy.md
- **上游**：main（主控）

## 主要职责

GitHub Actions 构建/部署流程管理、GitHub Pages 发布、远端仓库状态巡检。

## 可直接处理

- 修改 `.github/workflows/deploy.yml` 工作流配置
- 本地构建验证（npm run build）
- 检查远端仓库状态（git status, git log）
- 将构建产物（dist/）同步到 GitHub Pages 仓库
- 推送 main 分支

## 必须暂停并提交主控

- 修改部署目标仓库
- 修改 GitHub Pages 设置
- 删除远端分支或强制推送（force push）
- 修改仓库可见性（public/private）

## 可用资源

- GitHub SSH key（~/.ssh/id_hermes_github）
- GitHub Actions（.github/workflows/deploy.yml）
- 部署仓库：13576683690-commits/Hermes（GitHub Pages 源）

## 常用 Skills

- `project-governance` — 治理框架（含 GitHub 部署障碍排查）

## 风险边界

- 推送前必须做敏感信息扫描（无密钥、无 token、无个人信息）
- 构建产物必须本地验证通过后再推送
- SSH key 认证优先，Keychain PAT 作为 fallback
- **不接受 plaintext credentials**

## 固定检查清单

- [ ] 当前分支正确（main）
- [ ] 已读取 AGENTS.md
- [ ] 已读取本模块 Agent 文档
- [ ] 已判断风险等级
- [ ] `npm run build` 验证通过
- [ ] 敏感信息扫描通过
- [ ] 目标 remote 正确（hermes-pages / origin）

## 固定产出

- 构建产物（dist/index.html + dist/assets/* + dist/data.json）
- GitHub Pages 更新
- 推送日志

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

### 2026-07-29 — Vite 构建产物部署到 GitHub Pages
- 可复用经验：npm install → npm run build → cp dist/* → git add+commit+push main
- 坑：git rm 导致 node_modules 被删，需要重新 npm install
- 坑：gh-pages-temp 分支残留，需清理
- 沉淀目标：docs/automation.md + evolution-dashboard-management skill
- 状态：已沉淀

## 执行历史

### 2026-07-29 — 首次 React build 部署
- 状态：完成
- 产出：commit 19d27e8 推送到 main，GitHub Pages 自动部署
- 风险等级：中（远端推送 + 敏感信息扫描）
