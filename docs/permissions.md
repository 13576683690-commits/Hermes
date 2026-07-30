# 权限规则

> 权限按资源和动作分级。默认保守。

## 权限分级

| 类型 | 含义 | 默认处理 |
|---|---|---|
| 只读 | 读取文件、检查 git 状态 | 低风险，直接处理 |
| 本地草稿 | 修改 src/ 组件、调整样式 | 低风险，构建验证后回传 |
| 本地数据 | 追加 data.json 新条目 | 中风险，需备份 + MD5 校验 |
| 远端写入 | git push 到 GitHub main | 中风险，敏感信息扫描后推送 |
| 不可逆动作 | 删除历史数据、修改 data.json schema、force push | 高风险，必须用户确认 |

## 项目专属权限边界

### data.json

```
资源名称：public/data.json
允许模块：数据
允许动作：追加新归档条目、追加 memory/evolution、更新 stats
禁止动作：修改已存在条目、删除条目、改变 schema
是否需要主控确认：是（追加前主控审核四维提炼）
是否需要用户确认：否
回滚方式：从 .bak 恢复
验证方式：JSON 校验 + MD5 对比
```

### GitHub 推送

```
资源名称：GitHub main 分支
允许模块：部署
允许动作：git push origin main（正常 commit）
禁止动作：git push --force, 删除远端分支
是否需要主控确认：否（日常部署）
是否需要用户确认：否
回滚方式：git revert
验证方式：git log + GitHub Pages 线上确认
```

### 构建产物

```
资源名称：dist/
允许模块：部署
允许动作：npm run build 生成、同步到 Pages 仓库
禁止动作：提交 dist/ 到源码仓库（.gitignore 排除）
是否需要主控确认：否
是否需要用户确认：否
回滚方式：重新 build
验证方式：本地 build 成功 + 产物完整性检查
```

## 密钥边界

- 本项目无 API 密钥
- GitHub 认证：SSH key（~/.ssh/id_hermes_github）或 Keychain PAT
- 不接受、不请求 plaintext credentials
- 发现疑似泄露的密钥：立即提醒用户撤销，不复制、不传播
