# 自动化登记

## Deploy to GitHub Pages

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
