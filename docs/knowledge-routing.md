# 知识路由表

> 所有可复用知识必须先判断类型，再路由到对应通道沉淀。不混用通道。

## 三通道路由

| 内容类型 | 沉淀通道 | 工具 | 适用场景 | 示例 |
|---|---|---|---|---|
| 可复用流程/SOP/工作流 | **Skills** | skill_manage | 多次重复的任务模式 | "项目初始化流程"、"飞书绑定流程" |
| 事实性信息/偏好/环境设定 | **Memory** | memory | 跨会话需要记住的事实 | "用户偏好深色系设计"、"macOS 无 Docker" |
| 正式文档/报告/规格/计划 | **仓库 docs/** | write_file | 项目交付物 | "部署指南"、"模块职责" |
| 归档数据 | **public/data.json** | write_file | 进化记录（不可变） | Skill/记忆点/进化点/探索节点 |

## data.json 数据追加规则

1. 新归档只追加，不修改历史条目
2. 同一天的多次对话合并为一条归档（同日合并增量原则）
3. 无实质进化不归档（实质进化门槛）
4. 追加前必须有明确的 skill/memory/evolution/node 提炼

## 沉淀决策树

```
内容产出
  ├─ 是"多次重复的操作流程"？ → Skills (skill_manage)
  ├─ 是"需要跨会话记住的事实"？ → Memory (memory)
  ├─ 是"项目交付物"？ → 仓库 docs/ 或 reports/ (write_file)
  ├─ 是"进化归档数据"？ → public/data.json (write_file)
  ├─ 是"一次性任务流水账"？ → 不沉淀，session 记录即可
  └─ 不确定？ → 提交主控判断
```

## 知识维护

- Skills 发现过时或不完整时，立即用 skill_manage(action='patch') 更新
- Memory 发现有误时，用 memory(action='replace') 更正
- 仓库 docs/ 随项目演进定期更新
- 不把会在 7 天内过期的信息写入 memory
