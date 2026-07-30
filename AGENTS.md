# 进化档案馆 (Evolution Dashboard) — 项目总章程

## 项目身份

- **项目名称**: AI 进化档案馆
- **项目简称**: evolution-dashboard
- **项目目标**: 记录 Hermes & 锅仔的共同进化史，可视化展示 Skill / 记忆点 / 进化点 / 探索节点
- **主要用户**: 锅仔（个人）
- **主要产出**: 深色极简看板 Web App
- **核心工作对象**: data.json（归档数据）+ React 前端
- **长期维护周期**: 长期项目
- **GitHub 仓库**: 13576683690-commits/Hermes
- **部署 URL**: GitHub Pages

## 核心需求（不可妥协）

1. **跨设备查看** — GitHub Pages 部署，任何设备打开 URL 可见
2. **跨设备数据同步** — data.json 与渲染层分离，任何设备 push 数据即更新
3. **云端自动化** — GitHub Actions 构建部署，不依赖单台 Mac launchd
4. **零本地依赖** — 不需要某台电脑在线才能运转

## 技术栈

- **前端**: React 18 + Vite 5 + Tailwind CSS 3
- **部署**: GitHub Pages（通过 GitHub Actions 自动构建）
- **数据**: public/data.json（结构化归档数据，唯一数据源）

## 数据结构

```json
{
  "archives": [{ "id, date, title, desc, tags, details, stats, command" }],
  "memories": [{ "content" }],
  "evolutions": [{ "content" }],
  "stats": { "archives, points, skills" }
}
```

每条 archive 的 details 按 Skill / 记忆点 / 进化点 / 探索节点 四维归类。

## 模块结构

| 模块 | 职责 | Agent 文档 | 文件 |
|---|---|---|---|
| 主控 | 任务管理、资源统一、风险裁判 | docs/agents/main.md | AGENTS.md |
| 前端 | React 组件开发、UI/UX、构建验证 | docs/agents/frontend.md | src/App.jsx, src/components/* |
| 数据 | data.json 管理、归档追加 | docs/agents/data.md | public/data.json |
| 部署 | GitHub Actions、Pages 发布 | docs/agents/deploy.md | .github/workflows/deploy.yml |
| 自优化 | 复盘规则、经验沉淀 | docs/agents/self-optimization.md | — |

## 设计规范

- 深色系渐变: `#0f111a` 背景，`#a5b4fc` 主文字色
- Tailwind 类名驱动
- 卡片展开动画 + 自定义滚动条
- 点击复制指令交互

## 工作原则

- 先读取仓库已有资料，再提出结论或执行修改
- data.json 只增不改（历史数据不可变，只追加新归档）
- 改动保持最小，只触碰完成任务必须触碰的文件
- Web 资源严禁中文命名（必须英文/拼音），否则 CI/CD 中引发 404
- 不提交 API key、token、cookie、账号密码
- 遇到风险等级不清楚时先暂停

## 风险门禁

| 等级 | 定义 | 处理 |
|---|---|---|
| 低 | 只读、本地草稿（src/ 修改）、可回滚 | 直接处理 |
| 中 | 追加 data.json、远端推送、构建部署 | 主控判断后执行 |
| 高 | 修改/删除历史数据、force push、仓库设置变更 | 用户确认后执行 |
| 不确定 | 无法判断影响范围 | 按高风险处理 |

详见 docs/risk-gates.md。

## 密钥边界

- 本项目无外部 API 依赖
- GitHub 推送通过 SSH key（~/.ssh/id_hermes_github）或 Keychain PAT helper
- 不接受 plaintext credentials

## 知识沉淀

- 可复用流程 → Hermes skills
- 事实性信息 → Hermes memory
- 正式文档 → 本仓库 docs/
- 归档数据 → public/data.json（只追加）

## 自优化要求

每个任务结束必须做全量回读复盘。详见 docs/agents/self-optimization.md。
