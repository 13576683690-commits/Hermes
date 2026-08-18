# 档案卡定版模板（2026-08-18 用户拍板）

> 每次归档必按此模板。四维缺一不可填全，icon 必带，知识库标注必带。

## 卡片字段规范

| 字段 | 规范 | 反例（禁止） |
|---|---|---|
| `title` | 动词开头的事件句，15-30 字 | 「今日工作」 |
| `desc` | **长叙事**：做了什么+具体数字+commit 链+验收结果，150-300 字 | 两句话概述 |
| `tags` | 5-8 个，含项目名+技术点+裁决点 | 2-3 个泛标签 |
| `command` | 可执行的验证/入口命令 | 空或纯描述 |
| `stats` | 四维计数，与 details 条数一致 | 有 details 无 stats |

## 四维 details 规范

每一维至少 1 条（无实质内容宁可不归档）。**每条必带 icon**：

| 维度 | icon | 内容要求 |
|---|---|---|
| skill | 🔌 | 新增/patch 的程序化能力+触发场景 |
| memory | 🧠 | 固化的稳定事实/裁决/红线，含"已写入持久 memory"标注 |
| evolution | 📈 | 能力前后对比（旧→新格式），量化数字 |
| node | 📍 | 分支决策、修复链、根因定位过程 |

## 知识库标注（必带，2026-08-18 新增立法）

凡涉及知识库的卡，desc 或 details 至少一处嵌入：
- 页路径（如 `concepts/AI进化档案馆.md`）
- 或 commit 链（如 `f074048→3ce04f1`）
- 或具体数字（24 页/675 文件）
让卡片可溯源回 Knowledge vault。

## 写卡流程

1. 会话内四问复盘（used/gap/patch/归档候选）产出原料
2. 按本模板填写 → JSON 校验 → **门控：用户批准后才写入 data.json**
3. 写入前 `cp data.json data.json.bak` 备份
4. 部署：`cd ~/Desktop/Codex-Hermes && mkdir -p dist-root && cp index.html avatar.png data.json dist-root/ && cp -r assets dist-root/ && npx wrangler pages deploy dist-root --project-name=evolution-dashboard --commit-dirty=true && rm -rf dist-root`
5. 验证：sleep 18 后 curl 线上 data.json（加 ?t= 防缓存）确认新卡 ID + icon 齐备
6. git commit + push main

## 模板示例（arch_20260818_01 即按此写）

见 data.json 中 id=arch_20260818_01 的卡片，为当前定版格式的基准样本。
