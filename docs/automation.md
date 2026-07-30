# 自动化登记

> 所有自动化必须登记。自动化只能做已登记范围内的动作，不得绕过风险门禁，不得静默写入外部系统。

## 自动化登记表

| 名称 | 触发方式 | 频率 | 输入 | 输出 | 交付目标 | 外部写入 | 风险等级 | 最近验证 |
|---|---|---|---|---|---|---|---|---|
| GitHub Pages 自动部署 | push 到 main | 每次 push | 仓库源码 | dist/ 构建产物 | GitHub Pages | 是（写入 Pages） | 低 | 2026-07-29 |

## GitHub Pages 自动部署

- **名称**: GitHub Pages 自动部署
- **触发**: push 到 main 分支
- **频率**: 每次 push
- **输入**: 仓库源码
- **执行动作**: npm ci → npm run build → 上传 dist/ → 部署到 GitHub Pages
- **输出**: GitHub Pages URL
- **交付目标**: GitHub Pages（全球可访问）
- **是否外部写入**: 是（写入 GitHub Pages）
- **风险等级**: 低（只写公开页面，不涉及敏感数据）
- **失败处理**: GitHub Actions 自动通知（仓库 Actions 页面可见）
- **替代方案**: 曾用 launchd + publish_evolution.sh（已废弃，绑死单机）

## 已废弃的自动化（保留记录）

| 名称 | 方式 | 状态 | 废弃原因 |
|---|---|---|---|
| evolution-publish launchd | macOS launchd 每天 8AM | 已废弃 | 绑死单机，换电脑无法运行 |
| publish_evolution.sh | Shell 脚本 + git push | 已废弃 | 依赖本机 Python + Git 配置 |
| update_evolution.py | Python 重新生成 215KB HTML | 已废弃 | 数据烘焙在 HTML 中，无法分离 |

## 自动化原则

- 自动化只能做已登记范围内的动作
- 自动化不得绕过风险门禁
- 自动化不得静默写入外部系统
- 自动化输出必须可追溯
- 自动化失败必须回传主控
