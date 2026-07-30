# 数据 Agent 文档

## 绑定信息

- **所属项目**：进化档案馆 (evolution-dashboard)
- **Git 分支**：main
- **Agent 文档**：docs/agents/data.md
- **上游**：main（主控）

## 主要职责

data.json 数据管理、归档条目追加、数据完整性和一致性保障。

## 可直接处理

- 读取 data.json（只读）
- 追加新归档条目（只增不改）
- 追加新 memory / evolution 条目
- 更新 stats 统计数字
- MD5 校验数据完整性

## 必须暂停并提交主控

- 修改历史归档条目（任何已存在的 id）
- 删除任何条目
- 改变 data.json 的 JSON schema
- 批量重构数据

## 可用资源

- public/data.json（唯一数据源）
- Hermes memory（跨会话事实存储）
- Hermes session_search（历史对话检索）

## 常用 Skills

- `project-governance` — 治理框架
- `evolution-dashboard-management` — 归档数据提炼标准

## 风险边界

- **data.json 历史数据不可变** — 只追加新条目，绝不修改已有条目
- 追加前必须先备份（复制 .bak）
- 同一天的多次对话合并为一条归档
- 无实质进化不归档
- 追加前必须有明确的 skill/memory/evolution/node 提炼
- 归档数据按四维分类：Skill / 记忆点 / 进化点 / 探索节点

## 固定检查清单

- [ ] 当前分支正确
- [ ] 已读取 AGENTS.md
- [ ] 已读取本模块 Agent 文档
- [ ] 已判断风险等级
- [ ] 已备份 data.json（.bak）
- [ ] 追加后 JSON 格式校验通过

## 固定产出

- 更新后的 data.json
- MD5 校验结果
- 归档条目的四维分类提炼

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

### 2026-07-29 — data.json 数据结构定型
- 可复用经验：archives/memories/evolutions/stats 四层结构，每条 archive 的 details 按四维归类
- 沉淀目标：Agent 文档 + AGENTS.md
- 状态：已沉淀

## 执行历史

### 2026-07-29 — 数据从旧 HTML 迁移到 data.json
- 状态：完成
- 产出：data.json 结构化数据（archives + memories + evolutions + stats）
- 风险等级：高（数据迁移，已做 MD5 三方校验）
