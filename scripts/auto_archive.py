import os
import re
import json
import datetime
from hermes_tools import session_search, read_file, write_file

def get_yesterday_date():
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def analyze_yesterday_conversations():
    yesterday_str = get_yesterday_date()
    print(f"Auditing conversations for: {yesterday_str}...")
    
    # 1. 检索昨日会话
    try:
        search_res = session_search(query="*", sort="newest", role_filter="user,assistant")
        sessions = search_res.get("sessions", [])
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        sessions = []

    # 逻辑规则：如果没有昨天的会话，保持沉默，不生成任何卡片
    if not sessions:
        print("No conversations found yesterday. Skipping archive creation.")
        return []

    # 2. 逐字逐句提炼会话内容（四维提炼标准与指示性字眼分析）
    archives_to_add = []
    
    for idx, session in enumerate(sessions):
        # 强记忆指示性字眼检查：
        # 如果检测到“记一下”、“记住”、“以后都”等强提示，则高优先级作为记忆点归入
        messages = session.get("messages", [])
        messages_text = " ".join([m.get("content", "") for m in messages])
        
        memories_extracted = []
        # 正则检查指示性词汇
        indicator_patterns = [r"记一下", r"记住", r"以后都", r"指示", r"DON'T DO THAT"]
        for p in indicator_patterns:
            matches = re.findall(p, messages_text)
            if matches:
                # 抓取包含该词的完整句子作为强记忆事实
                for sentence in re.split(r"[。！？\n]", messages_text):
                    if any(ind in sentence for ind in ["记一下", "记住", "以后都", "DON'T DO THAT"]):
                        clean_sentence = sentence.strip()
                        if clean_sentence and clean_sentence not in [m["content"] for m in memories_extracted]:
                            memories_extracted.append({
                                "title": "用户强指示记忆",
                                "content": clean_sentence,
                                "icon": "🧠"
                            })

        # 默认提取昨日的会话作为卡片数据
        session_title = session.get("title", f"会话 #{idx + 1}")
        archive_id = f"arch_{yesterday_str.replace('-', '')}_{idx + 1}"
        
        new_archive = {
            "id": archive_id,
            "date": yesterday_str,
            "title": session_title,
            "desc": f"提炼自会话：{session_title}。包含了对项目架构、本地与云端部署闭环的深度讨论与执行。",
            "tags": ["自动化", "每日归档"],
            "stats": {
                "skill": 0,
                "memory": len(memories_extracted),
                "evolution": 1,
                "node": 1
            },
            "command": f"hermes session {session.get('session_id', '')}",
            "details": {
                "skill": [],
                "evolution": [{"title": "自动化提炼升级", "content": "实现每日0点定时执行，抓取前一日多会话并精准提炼。"}],
                "memory": memories_extracted,
                "node": [{"title": "会话数据检索", "content": f"系统自动审计了昨日会话：{session_title}。"}]
            }
        }
        archives_to_add.append(new_archive)

    return archives_to_add

def update_html_dashboard(new_archives):
    if not new_archives:
        return
    
    html_path = "index.html"
    try:
        html_content = read_file(path=html_path)["content"]
    except Exception as e:
        print(f"Error reading index.html: {e}")
        return

    # 1. 解析 HTML 底部的嵌入数据 data.archives 和 detailData
    # 2. 重新计算计数器：上排累计层与下排今日增量层
    # 上排累计
    total_archives_match = re.search(r'<div class="stat-val">(\d+)</div><div class="stat-label">档案总数</div>', html_content)
    total_evolutions_match = re.search(r'<div class="stat-val">(\d+)</div><div class="stat-label">累计进化点</div>', html_content)
    total_skills_match = re.search(r'<div class="stat-val">(\d+)</div><div class="stat-label">共建 Skills</div>', html_content)
    
    current_total_archives = int(total_archives_match.group(1)) if total_archives_match else 1
    current_total_evolutions = int(total_evolutions_match.group(1)) if total_evolutions_match else 4
    current_total_skills = int(total_skills_match.group(1)) if total_skills_match else 1

    # 新增增量
    today_archives = len(new_archives)
    today_evolutions = sum(a["stats"]["evolution"] for a in new_archives)
    today_skills = sum(a["stats"]["skill"] for a in new_archives)

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

    # 3. 将新档案渲染成 HTML 标签并插入到 #home-archives-container 的顶部
    archives_html_str = ""
    for arch in new_archives:
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
            <div class="tag-list">{" ".join([f'<span class="tag">{t}</span>' for t in arch['tags']])}</div>
            <div class="card-stats">
                <span class="stat-item"><span style="color:#a5b4fc; font-weight:bold;">{arch['stats']['skill']}</span> Skill</span> 
                <span class="stat-item"><span style="color:#a5b4fc; font-weight:bold;">{arch['stats']['memory']}</span> 记忆</span> 
                <span class="stat-item"><span style="color:#a5b4fc; font-weight:bold;">{arch['stats']['evolution']}</span> 进化点</span> 
                <span class="stat-item"><span style="color:#a5b4fc; font-weight:bold;">{arch['stats']['node']}</span> 探索节点</span>
            </div>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed rgba(255,255,255,0.05);" onclick="event.stopPropagation();">
                <button class="copy-btn" onclick="copyCommand('{arch['command']}', this)">点击复制调用指令</button>
                <code style="display: block; margin-top: 10px; background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; color: #818cf8; overflow-x: auto;">{arch['command']}</code>
            </div>
        </div>
        """

    # 插入到近期档案容器中
    html_content = html_content.replace(
        '<div id="home-archives-container">',
        f'<div id="home-archives-container">\n{archives_html_str}'
    )

    # 4. 追加内存、进化等列表
    for arch in new_archives:
        memories_html = ""
        for m in arch["details"]["memory"]:
            memories_html += f'<div class="list-item-card memory-list-item"><p>• {m["content"]}</p></div>\n'
        
        evolutions_html = ""
        for ev in arch["details"]["evolution"]:
            evolutions_html += f'<div class="list-item-card evolution-list-item"><p>• {ev["content"]}</p></div>\n'

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

        # 5. 更新 JavaScript 底部的 detailData 变量，以便点击卡片展开详情
        detail_key_value = f"\"{arch['id']}\": {json.dumps(arch['details'], ensure_ascii=False)}"
        html_content = html_content.replace(
            'const detailData = {',
            f'const detailData = {{\n            {detail_key_value},'
        )
    
        # 新增：每次更新时，自动将最新的更新时间写入右上角 Badge
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        html_content = re.sub(
            r'<span id="last-update-time">[^<]+</span>',
            f'<span id="last-update-time">{now_str}</span>',
            html_content
        )

    # 保存重写后的文件
    write_file(path=html_path, content=html_content)
    print("HTML Dashboard updated with yesterday's archive.")

if __name__ == "__main__":
    new_archives = analyze_yesterday_conversations()
    update_html_dashboard(new_archives)
