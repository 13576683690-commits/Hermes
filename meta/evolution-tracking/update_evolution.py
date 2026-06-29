import json
from datetime import datetime
from pathlib import Path
import base64

OUTPUT_PATH = Path(__file__).resolve().parent / "index.html"

# ... (数据和之前一致)
data = {
    "stats": {"archives": 1, "points": 4, "skills": 1},
    "daily_stats": {"archives": 1, "points": 4, "skills": 1},
    "memories": [
        {"content": "系统已固化认知：同一天内的同一对话更新，必须合并到当天的档案中；跨日才算作新档案并追加 '- UPDATE'。"},
        {"content": "【核心定义】Skill：新增程序化工具；记忆点：事实性固化；进化点：能力量化提升；探索节点：分支子任务。"},
        {"content": "确立了增量提炼防重原则：跨日旧对话也作为新档案，且仅提炼当日新增内容。"},
        {"content": "用户倾向于深色系、极简的展示风格，且要求严格的模块化与排版锁定。"},
        {"content": "Dashboard 在本地通过 Python 脚本和本地 HTML 生成进行渲染。"}
    ],
    "evolutions": [
        {"content": "建立并测试了基于 Cronjob 的每日早 8 点定时更新机制，实现自动归档。"},
        {"content": "完善了基于 Session 的档案归类本体论（四分法）及同一日历合并规范。"},
        {"content": "完成了从单页到三层视图 SPA 架构的演进，实现了模块化的视图路由切换。"},
        {"content": "视觉排版像素级还原：严格对照设计指南，重构了深色背景、圆角卡片、脉冲动画等视觉元素。"}
    ],
    "archives": [
        {
            "id": "arch_001",
            "date": "2026-06-14",
            "title": "自进化档案馆：从零到一的架构构建",
            "icon": "🏗️",
            "desc": "基于设计规范，从零搭建了具备三层视图的自进化看板，确立归档本体论。并在同一对话周期内，完成了自动化更新机制的实测与防重复/合并逻辑的验证。",
            "tags": ["SPA架构", "视觉重构", "本体论", "增量原则", "自动化测试"],
            "stats": {"Skill": 1, "记忆": 4, "进化点": 4, "探索节点": 5},
            "is_new": True,
            "details": {
                "skill": [
                    {"icon": "🛠️", "title": "evolution-dashboard", "content": "将界面排版要求和档案结构逻辑固化到 skill 中，确保后续更新的绝对稳定性。", "tags": ["productivity", "规范"]}
                ],
                "evolution": [
                    {"icon": "📈", "title": "三层视图 SPA 架构", "content": "引入原生 JavaScript 控制视图切换，实现了主页、全部档案页和详情页的无缝路由切换。", "tags": ["architecture", "frontend"]},
                    {"icon": "📈", "title": "视觉排版像素级还原", "content": "严格对照设计指南，重构了深色背景、圆角卡片、脉冲动画及分类标签等视觉元素。", "tags": ["ui", "css"]},
                    {"icon": "⏰", "title": "定时任务生效", "content": "确认了每日早 8:00 自动触发更新的 cronjob 机制已就绪。", "tags": ["cronjob"]},
                    {"icon": "📝", "title": "归档准则验证", "content": "验证了内容提炼的防重复规则以及同日会话合并的规则。", "tags": ["rule-test"]}
                ],
                "memory": [
                    {"icon": "🧠", "title": "增量更新原则", "content": "确立了“锁定已完成版块，仅通过增加数据实现内容扩充”的工作流，避免排版反复横跳。", "tags": ["workflow"]},
                    {"icon": "🧠", "title": "档案信息分层展示", "content": "明确列表页仅展示统计数字摘要，具体描述下沉至详情页的四分区块展示。", "tags": ["ux", "data"]},
                    {"icon": "🧠", "title": "同日合并规则", "content": "系统固化认知：同一天同一对话的更新必须合并，不能新建档案；跨日重启对话才新建档案(- UPDATE)。", "tags": ["rule"]},
                    {"icon": "🧠", "title": "防重复提炼", "content": "跨日更新时，提炼内容严格限定于当日沟通，绝不追溯冗余信息。", "tags": ["rule"]}
                ],
                "node": [
                    {"icon": "📍", "title": "引入本地头像", "content": "成功对接本地文件资源（进化档案头像.png）作为看板的头部标识。", "tags": ["assets"]},
                    {"icon": "📍", "title": "当日统计面板注入", "content": "在总计数据下方补充了带有绿色高亮的当日新增数据看板。", "tags": ["dashboard"]},
                    {"icon": "📍", "title": "详情页四分区块构建", "content": "按照规范，渲染了包括标题、时间、描述和标签的独立条目卡片。", "tags": ["detail-view"]},
                    {"icon": "📍", "title": "全部档案展开机制", "content": "增加了'查看更多档案'的独立视图模式，保持主页清爽。", "tags": ["interaction"]},
                    {"icon": "📍", "title": "自动化合并测试", "content": "主动纠正了将同日延续对话拆分为新档案的错误，执行了档案合并归档。", "tags": ["debug"]}
                ]
            }
        }
    ]
}

def run():
    archives_html = ""
    for idx, arch in enumerate(data['archives']):
        tags_html = "".join([f'<span class="tag">{t}</span>' for t in arch['tags']])
        stats_items = [f'<span style="color:#a5b4fc; font-weight:bold;">{v}</span> {k}' for k, v in arch['stats'].items()]
        stats_html = " ".join([f'<span class="stat-item">{item}</span>' for item in stats_items])
        display_style = "" if idx < 5 else "display: none;"
        
        archives_html += f'''
        <div class="archive-card archive-list-item" style="{display_style}" onclick="showDetail('{arch['id']}')">
            <div class="card-header">
                <span style="color:#818cf8;">{arch['date']}</span>
                {"<span class='new-tag'>NEW</span>" if arch.get('is_new') else ""}
            </div>
            <h3 class="card-title" style="display:flex; align-items:center; gap:8px;">
                <span>{arch['icon']}</span>
                <span>{arch['title']}</span>
            </h3>
            <p class="card-desc">{arch['desc']}</p>
            <div class="tag-list">{tags_html}</div>
            <div class="card-stats">{stats_html}</div>
        </div>'''

    memories_html = ""
    for idx, mem in enumerate(data['memories']):
        display_style = "" if idx < 5 else "display: none;"
        memories_html += f'''<div class="list-item-card memory-list-item" style="{display_style}"><p>• {mem['content']}</p></div>'''

    evolutions_html = ""
    for idx, evo in enumerate(data['evolutions']):
        display_style = "" if idx < 5 else "display: none;"
        evolutions_html += f'''<div class="list-item-card evolution-list-item" style="{display_style}"><p>• {evo['content']}</p></div>'''

    full_data_json = json.dumps(data)
    
    # 将本地图片转化为 base64 编码，使其变成一个纯单文件
    import base64
    try:
        with open("/Users/macgy/Desktop/进化档案头像.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        avatar_url = f"data:image/png;base64,{encoded_string}"
    except:
        avatar_url = "" # 如果找不到头像防崩

    more_archives_btn = '<span class="more-btn" id="more-archives-btn" onclick="showAllArchivesView()">查看更多档案 ></span>' if len(data['archives']) > 5 else ''
    more_memories_btn = '<span class="more-btn" id="more-memories-btn" onclick="showAllMemoriesView()">查看更多记忆 ></span>' if len(data['memories']) > 5 else ''
    more_evolutions_btn = '<span class="more-btn" id="more-evolutions-btn" onclick="showAllEvolutionsView()">查看更多进化 ></span>' if len(data['evolutions']) > 5 else ''

    s_archives = data['stats']['archives']
    s_points = data['stats']['points']
    s_skills = data['stats']['skills']
    d_archives = data['daily_stats']['archives']
    d_points = data['daily_stats']['points']
    d_skills = data['daily_stats']['skills']

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>进化档案馆</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0f111a; color: #a5b4fc; font-family: sans-serif; padding: 40px; }}
        .container {{ max-width: 900px; margin: auto; }}
        
        .hero {{ background: #181c2e; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; border: 1px solid #2d3748; }}
        .title-container {{ display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 15px; }}
        .avatar {{ width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #667eea; }}
        h1 {{ color: #e0e7ff; font-size: 2.2rem; margin: 0; }}
        .sub-text {{ color: #818cf8; margin-bottom: 20px; font-size: 1.1rem; }}
        .slogan {{ background: #2d3748; padding: 8px 20px; border-radius: 20px; display: inline-block; font-size: 0.9rem; color: #e0e7ff; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: #181c2e; padding: 25px; border-radius: 16px; text-align: center; border: 1px solid #2d3748; }}
        .stat-val {{ font-size: 2.5rem; color: #e0e7ff; font-weight: bold; }}
        .stat-label {{ color: #818cf8; font-size: 0.85rem; margin-top: 5px; }}
        .daily-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }}
        .daily-card {{ background: #1a1e35; padding: 15px; border-radius: 12px; text-align: center; border: 1px dashed #374151; }}
        .daily-val {{ font-size: 1.2rem; color: #34d399; font-weight: bold; }}
        .daily-label {{ color: #64748b; font-size: 0.75rem; margin-top: 2px; }}

        .section-header {{ display: flex; justify-content: space-between; align-items: baseline; margin: 40px 0 20px 0; border-bottom: 1px solid #2d3748; padding-bottom: 10px; }}
        .section-title {{ color: #e0e7ff; font-size: 1.5rem; font-weight:bold; display: flex; align-items: center; gap: 8px; margin: 0; }}
        .more-btn {{ color: #6366f1; cursor: pointer; font-size: 0.9rem; transition: color 0.2s; font-weight: bold; }}
        .more-btn:hover {{ color: #a5b4fc; text-decoration: underline; }}

        .archive-card {{ background: #181c2e; padding: 25px 30px; border-radius: 16px; margin-bottom: 20px; cursor: pointer; border: 1px solid #2d3748; transition: border-color 0.2s; }}
        .archive-card:hover {{ border-color: #6366f1; }}
        .card-header {{ display: flex; align-items: center; gap: 10px; font-size: 0.9rem; margin-bottom: 15px; }}
        .new-tag {{ background: #6366f1; color: white; padding: 2px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: bold; }}
        .card-title {{ color: #e0e7ff; font-size: 1.3rem; margin-bottom: 15px; }}
        .card-desc {{ color: #94a3b8; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px; }}
        .tag-list {{ margin-bottom: 20px; }}
        .tag {{ background: #1e293b; color: #818cf8; padding: 6px 14px; border-radius: 14px; font-size: 0.8rem; margin-right: 10px; display: inline-block; }}
        .card-stats {{ color: #64748b; font-size: 0.9rem; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); }}
        .stat-item {{ margin-right: 15px; }}
        
        .list-item-card {{ background: #181c2e; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #2d3748; border-left: 4px solid #667eea; color: #cbd5e1; line-height: 1.6; font-size: 0.95rem; }}

        #all-archives-view, #all-memories-view, #all-evolutions-view, #detail-view {{ display: none; }}
        .view-header {{ margin-bottom: 40px; cursor: pointer; }}
        .view-header h1 {{ color: #f093fb; font-size: 2rem; display: flex; align-items: center; gap: 10px; margin: 0; }}
        
        .detail-category-title {{ color: #e0e7ff; font-size: 1.2rem; font-weight: bold; margin: 30px 0 15px 0; border-left: 4px solid #6366f1; padding-left: 10px; }}
        .detail-card {{ background: #181c2e; padding: 25px; border-radius: 16px; margin-bottom: 15px; border: 1px solid #2d3748; }}
        .detail-card-header {{ display: flex; justify-content: flex-start; align-items: center; margin-bottom: 12px; }}
        .detail-card-title {{ color: #e0e7ff; font-size: 1.1rem; font-weight: bold; }}
        .detail-card-desc {{ color: #94a3b8; font-size: 0.95rem; line-height: 1.6; margin-bottom: 15px; }}
        .empty-state {{ color: #64748b; font-size: 1rem; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container" id="home-view">
        <div class="hero">
            <div class="title-container">
                <img src="{avatar_url}" class="avatar" alt="Avatar">
                <h1>进化档案馆</h1>
            </div>
            <p class="sub-text">Hermes 和 锅仔 的共同进化史</p>
            <div class="slogan">每一条记录都是成长的证明</div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-val">{s_archives}</div><div class="stat-label">档案总数</div></div>
            <div class="stat-card"><div class="stat-val">{s_points}</div><div class="stat-label">累计进化点</div></div>
            <div class="stat-card"><div class="stat-val">{s_skills}</div><div class="stat-label">共建 Skills</div></div>
        </div>
        <div class="daily-grid">
            <div class="daily-card"><div class="daily-val">+{d_archives}</div><div class="daily-label">今日新增档案</div></div>
            <div class="daily-card"><div class="daily-val">+{d_points}</div><div class="daily-label">今日进化点</div></div>
            <div class="daily-card"><div class="daily-val">+{d_skills}</div><div class="daily-label">今日共建 Skills</div></div>
        </div>
        
        <div class="section-header">
            <h2 class="section-title" id="archives-title">📚 近期档案</h2>
            {more_archives_btn}
        </div>
        <div id="home-archives-container">
            {archives_html}
        </div>

        <div class="section-header">
            <h2 class="section-title">🧠 记忆库</h2>
            {more_memories_btn}
        </div>
        <div id="home-memories-container">
            {memories_html}
        </div>

        <div class="section-header">
            <h2 class="section-title">📈 进化库</h2>
            {more_evolutions_btn}
        </div>
        <div id="home-evolutions-container">
            {evolutions_html}
        </div>
    </div>

    <div class="container" id="all-archives-view">
        <div class="view-header" onclick="showHome()">
            <h1>← 全部进化档案</h1>
        </div>
        <div id="all-archives-container"></div>
    </div>

    <div class="container" id="all-memories-view">
        <div class="view-header" onclick="showHome()">
            <h1>← 记忆库大全</h1>
        </div>
        <div id="all-memories-container"></div>
    </div>

    <div class="container" id="all-evolutions-view">
        <div class="view-header" onclick="showHome()">
            <h1>← 进化点总览</h1>
        </div>
        <div id="all-evolutions-container"></div>
    </div>
    
    <div class="container" id="detail-view">
        <div class="view-header" onclick="showHome()">
            <h1>✨ 本次档案的内容</h1>
            <p style="color: #64748b; margin-top: 10px; font-size: 0.9rem;">点击标题返回首页</p>
        </div>
        <div id="detail-content"></div>
    </div>

    <script>
        const data = {full_data_json};
        
        function renderCategory(title, items) {{
            if (!items || items.length === 0) return "";
            let html = `<div class="detail-category-title">${{title}}</div>`;
            items.forEach(d => {{
                let tags = d.tags ? d.tags.map(t => `<span class="tag">${{t}}</span>`).join('') : '';
                html += `
                <div class="detail-card">
                    <div class="detail-card-header">
                        <span class="detail-card-title">${{d.icon || ''}} ${{d.title}}</span>
                    </div>
                    <div class="detail-card-desc">${{d.content}}</div>
                    <div class="tag-list">${{tags}}</div>
                </div>`;
            }});
            return html;
        }}

        function showDetail(id) {{
            hideAll();
            document.getElementById('detail-view').style.display = 'block';
            const arch = data.archives.find(a => a.id === id);
            let html = "";
            if (arch.details && Object.keys(arch.details).length > 0) {{
                html += renderCategory("🛠️ Skill区", arch.details.skill);
                html += renderCategory("📈 进化区", arch.details.evolution);
                html += renderCategory("🧠 记忆区", arch.details.memory);
                html += renderCategory("📍 节点区", arch.details.node);
            }} else {{
                html = "<div class='empty-state'>暂无详情记录。</div>";
            }}
            document.getElementById('detail-content').innerHTML = html;
            window.scrollTo(0,0);
        }}
        
        function hideAll() {{
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('all-archives-view').style.display = 'none';
            document.getElementById('all-memories-view').style.display = 'none';
            document.getElementById('all-evolutions-view').style.display = 'none';
            document.getElementById('detail-view').style.display = 'none';
        }}

        function showAllArchivesView() {{
            hideAll();
            document.getElementById('all-archives-view').style.display = 'block';
            const container = document.getElementById('all-archives-container');
            container.innerHTML = document.getElementById('home-archives-container').innerHTML;
            container.querySelectorAll('.archive-list-item').forEach(el => el.style.display = 'block');
            window.scrollTo(0,0);
        }}

        function showAllMemoriesView() {{
            hideAll();
            document.getElementById('all-memories-view').style.display = 'block';
            const container = document.getElementById('all-memories-container');
            container.innerHTML = document.getElementById('home-memories-container').innerHTML;
            container.querySelectorAll('.memory-list-item').forEach(el => el.style.display = 'block');
            window.scrollTo(0,0);
        }}

        function showAllEvolutionsView() {{
            hideAll();
            document.getElementById('all-evolutions-view').style.display = 'block';
            const container = document.getElementById('all-evolutions-container');
            container.innerHTML = document.getElementById('home-evolutions-container').innerHTML;
            container.querySelectorAll('.evolution-list-item').forEach(el => el.style.display = 'block');
            window.scrollTo(0,0);
        }}

        function showHome() {{
            hideAll();
            document.getElementById('home-view').style.display = 'block';
            window.scrollTo(0,0);
        }}
    </script>
</body>
</html>'''
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

if __name__ == "__main__":
    run()
