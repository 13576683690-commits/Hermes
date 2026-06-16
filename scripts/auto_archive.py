import json
import datetime
import os
import re

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def analyze_today_conversations():
    today_str = get_today_date()
    print(f"Auditing conversations for manual update: {today_str}...")
    
    # 彻底摆脱 hermes_tools 依赖，采用标准 Python 文件读写。
    # 我们直接生成今天这场极其硬核、从 React 重构一路杀回静态部署并解决缓存、SSH 密钥的“自进化档案馆”之战！
    new_archives = []
    
    memories_extracted = [
        {
            "icon": "🧠",
            "title": "老对话重启规则",
            "content": "系统固化认知：老对话重启后，沟通内容需重新提炼归档，并在当天生成新卡片。"
        },
        {
            "icon": "🧠",
            "title": "强记忆指示词强拦截",
            "content": "只要对话中说出‘记一下’、‘记住’、‘指示’等，强制 100% 捕获并原汁原味归档。"
        },
        {
            "icon": "🧠",
            "title": "一历多卡独立归档",
            "content": "同一天的不同对话拒绝合并，全部作为独立卡片和独立调用指令归档展示。"
        }
    ]

    new_archive = {
        "id": f"arch_{today_str.replace('-', '')}_today",
        "date": today_str,
        "title": "自进化档案馆：全自动 Web App 闭环上线",
        "desc": "成功打通了从本地到 GitHub Pages 自动构建与部署的闭环流。重构 index.html 采用极轻量单文件原生渲染，彻底杜绝白屏并注入了‘复制指令’按钮的绿色交互反馈。写入了 auto_archive 归档逻辑，完成了 SSH 部署密钥配置并注入了科技感脉冲呼吸指示灯与 HTTP 强缓存消除头。",
        "tags": ["SPA架构", "自动化", "SSH密钥", "缓存消除", "双脑协作"],
        "stats": {
            "Skill": 2,
            "记忆": 3,
            "进化点": 3,
            "探索节点": 4
        },
        "is_new": True,
        "command": "hermes session current",
        "details": {
            "skill": [
                {"icon": "🛠️", "title": "auto_archive.py", "content": "编写了自动提炼和数据重写的 Python 自动化大脑脚本。"},
                {"icon": "🛠️", "title": "Deploy Keys", "content": "配置了 SSH 写入权限密钥，打通了免密推送通道。"}
            ],
            "evolution": [
                {"icon": "📈", "title": "消除白屏强缓存", "content": "在 index.html 头部注入禁用缓存 Meta 标签，实现了即开即用、自动最新。"},
                {"icon": "📈", "title": "数据面板精准联动", "content": "完成了上排‘累计层’与下排‘今日增量层’在 HTML 级别的自动化计算与正则重写。"}
            ],
            "memory": memories_extracted,
            "node": [
                {"icon": "📍", "title": "SSH Key 生成", "content": "终端生成了专属 id_hermes_github 部署密钥。"},
                {"icon": "📍", "title": "强制推送覆盖", "content": "强制推送覆盖了远程 Git 冲突版本，彻底点亮网页。"}
            ]
        }
    }
    new_archives.append(new_archive)
    return new_archives

def update_html_dashboard(new_archives):
    if not new_archives:
        return
    
    html_path = "index.html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading index.html: {e}")
        return

    # 1. 重新计算计数器
    # 上排累计
    total_archives_match = re.search(r'<div class="stat-val">(\d+)</div><div class="stat-label">档案总数</div>', html_content)
    total_evolutions_match = re.search(r'<div class="stat-val">(\d+)</div><div class="stat-label">累计进化点</div>', html_content)
    total_skills_match = re.search(r'<div class="stat-val">(\d+)</div><div class="stat-label">共建 Skills</div>', html_content)
    
    current_total_archives = int(total_archives_match.group(1)) if total_archives_match else 1
    current_total_evolutions = int(total_evolutions_match.group(1)) if total_evolutions_match else 4
    current_total_skills = int(total_skills_match.group(1)) if total_skills_match else 1

    # 新增增量
    today_archives = len(new_archives)
    today_evolutions = sum(a["stats"]["进化点"] for a in new_archives)
    today_skills = sum(a["stats"]["Skill"] for a in new_archives)

    new_total_archives = current_total_archives + today_archives
    new_total_evolutions = current_total_evolutions + today_evolutions
    new_total_skills = current_total_skills + today_skills

    # 重写上排累计
    html_content = re.sub(
        r'<div class="stat-val">\d+</div><div class="stat-label">档案总数</div>',
        f'<div class="stat-val">{new_total_archives}</div><div class="stat-label">档案总数</div>',
        html_content
    )
    html_content = re.sub(
        r'<div class="stat-val">\d+</div><div class="stat-label">累计进化点</div>',
        f'<div class="stat-val">{new_total_evolutions}</div><div class="stat-label">累计进化点</div>',
        html_content
    )
    html_content = re.sub(
        r'<div class="stat-val">\d+</div><div class="stat-label">共建 Skills</div>',
        f'<div class="stat-val">{new_total_skills}</div><div class="stat-label">共建 Skills</div>',
        html_content
    )

    # 重写下排今日增量
    html_content = re.sub(
        r'<div class="daily-val">\+\d+</div><div class="daily-label">今日新增档案</div>',
        f'<div class="daily-val">+{today_archives}</div><div class="daily-label">今日新增档案</div>',
        html_content
    )
    html_content = re.sub(
        r'<div class="daily-val">\+\d+</div><div class="daily-label">今日进化点</div>',
        f'<div class="daily-val">+{today_evolutions}</div><div class="daily-label">今日进化点</div>',
        html_content
    )
    html_content = re.sub(
        r'<div class="daily-val">\+\d+</div><div class="daily-label">今日共建 Skills</div>',
        f'<div class="daily-val">+{today_skills}</div><div class="daily-label">今日共建 Skills</div>',
        html_content
    )

    # 2. 将新档案渲染并插入到 #home-archives-container 的顶部
    archives_html_str = ""
    for arch in new_archives:
        tags_html = "".join([f'<span class="tag">{t}</span>' for t in arch['tags']])
        stats_items = [f'<span style="color:#a5b4fc; font-weight:bold;">{v}</span> {k}' for k, v in arch['stats'].items()]
        stats_html = " ".join([f'<span class="stat-item">{item}</span>' for item in stats_items])
        
        archives_html_str += f"""
        <div class="archive-card archive-list-item" onclick="showDetail('{arch['id']}')">
            <div class="card-header">
                <span style="color:#818cf8;">{arch['date']}</span>
                <span class='new-tag'>NEW</span>
            </div>
            <h3 class="card-title" style="display:flex; align-items:center; gap:8px;">
                <span>🏗️</span>
                <span>{arch['title']}</span>
            </h3>
            <p class="card-desc">{arch['desc']}</p>
            <div class="tag-list">{tags_html}</div>
            <div class="card-stats">{stats_html}</div>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed rgba(255,255,255,0.05);" onclick="event.stopPropagation();">
                <button class="copy-btn" onclick="copyCommand('{arch['command']}', this)">点击复制调用指令</button>
                <code style="display: block; margin-top: 10px; background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #818cf8; overflow-x: auto;">{arch['command']}</code>
            </div>
        </div>\n"""

    # 插入到近期档案容器中
    html_content = html_content.replace(
        '<div id="home-archives-container">',
        f'<div id="home-archives-container">\n{archives_html_str}'
    )

    # 3. 追加内存、进化等列表到首页展示
    for arch in new_archives:
        memories_html = ""
        for m in arch["details"]["memory"]:
            memories_html += f'<div class="list-item-card memory-list-item"><p>• 【强记忆】{m["content"]}</p></div>\n'
        
        evolutions_html = ""
        for ev in arch["details"]["evolution"]:
            evolutions_html += f'<div class="list-item-card evolution-list-item"><p>• 【进化点】{ev["content"]}</p></div>\n'

        if memories_html:
            html_content = html_content.replace(
                '<div id="home-memories-container">',
                f'<div id="home-memories-container">\n{memories_html}'
            )
        if evolutions_html:
            html_content = html_content.replace(
                '<div id="home-evolutions-container">',
                f'<div id="home-evolutions-container">\n{evolutions_html}'
            )

        # 4. 更新 JavaScript 底部的 detailData 变量，以便点击卡片展开详情
        detail_key_value = f"\"{arch['id']}\": {json.dumps(arch['details'], ensure_ascii=False)}"
        html_content = html_content.replace(
            'const detailData = {',
            f'const detailData = {{\n            {detail_key_value},'
        )

    # 5. 更新右上角徽章时间戳
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_content = re.sub(
        r'<span id="last-update-time">[^<]+</span>',
        f'<span id="last-update-time">{now_str}</span>',
        html_content
    )

    # 保存重写
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("HTML Dashboard locally rewritten successfully.")
    except Exception as e:
        print(f"Error writing index.html: {e}")

if __name__ == "__main__":
    new_archives = analyze_today_conversations()
    update_html_dashboard(new_archives)
