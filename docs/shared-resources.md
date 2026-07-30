# 共享资源登记

> 本项目无外部 API 依赖。主要外部交互为 GitHub 推送。

| 资源 | 类型 | 用途 | 负责模块 | 当前状态 | 密钥存储 | 风险边界 |
|---|---|---|---|---|---|---|
| GitHub (SSH) | Git | 仓库推送与拉取 | 部署 | 已接入 | ~/.ssh/id_hermes_github | 只推 main 分支，推送前敏感信息扫描 |
| GitHub Pages | 部署平台 | 静态站点托管 | 部署 | 已接入 | 无需密钥（仓库设置） | 只部署 main 分支构建产物 |
| GitHub Actions | CI/CD | 自动构建部署 | 部署 | 已接入 | 仓库内置 Actions token | 只读仓库源码 + 写 Pages 产物 |
| data.json | 数据源 | 归档数据（唯一源） | 数据 | 活跃 | 无需密钥（仓库内文件） | 历史数据不可变，只追加 |

## 密钥规则

- 本项目无外部 API 依赖，无 API key/secret/token
- GitHub 推送通过 SSH key 认证（~/.ssh/id_hermes_github）
- Fallback: Keychain PAT helper（credential.helper osxkeychain）
- 不接受、不请求 plaintext credentials
- 发现未登记资源或权限不明时暂停并提交主控

## 权限登记

### GitHub SSH

```
资源名称：GitHub SSH
允许模块：部署
允许动作：git push origin main, git pull, git status
禁止动作：force push, 删除远端分支, 修改仓库设置
是否需要主控确认：否（日常推送）
是否需要用户确认：否（低风险推送）
回滚方式：git revert + git push
验证方式：git log --oneline -1 确认 HEAD
```
