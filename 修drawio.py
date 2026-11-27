# -*- coding: utf-8 -*-
"""修正 draw.io 生成：换行转 <br>、重排拓扑图、简化回流线。"""

import io
import re

P = r"E:\软件质量保证与测试课程设计\生成drawio图.py"
t = io.open(P, encoding="utf-8").read()

# ---------- 1) 换行转 <br> ----------
t = t.replace(
    '''        label = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")''',
    '''        label = (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace("\\n", "<br>"))''')
t = t.replace(
    '''        label = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")''',
    '''        label = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace("\\n", "<br>"))''')

# ---------- 2) 重写环境拓扑 ----------
start = t.index("def env_topology():")
end = t.index("# ---------------------------------------------------------------- 2. 总体流程")
new_env = '''def env_topology():
    d = Diagram("env-topology", 1320, 780)
    d.title("图：测试环境拓扑")

    # 宿主机外框
    d.box("host", 30, 70, 810, 660, "", GRAY, rounded=False)
    d._cell("hostlabel", "Windows 11 宿主机（8 核 / 16 GB）",
            f"text;html=1;fontFamily={FONT};fontSize=15;fontStyle=1;align=left;verticalAlign=top;spacingLeft=14;",
            44, 80, 520, 26)

    # WSL2 / Docker 内框
    d.box("wsl", 55, 120, 760, 585, "", BLUE, dashed=True, rounded=False)
    d._cell("wsllabel", "WSL2 Ubuntu 22.04 · Docker 29.1.3 · Compose 2.40.3",
            f"text;html=1;fontFamily={FONT};fontSize=13;align=left;verticalAlign=top;spacingLeft=12;",
            68, 128, 640, 24)

    # 三个容器（纵向堆叠在右侧）
    d.box("wpapp", 470, 175, 320, 120,
          "wp-app\\nApache 2.4.52 + PHP 8.1.2\\nWordPress 7.1.5（官方包）\\n端口 8080 → 宿主 8080", ORANGE, 12)
    d.box("wpdb", 470, 350, 320, 95, "wp-db\\nMariaDB 10.6.23\\nmax_connections=300", GREEN, 12)
    d.box("wpredis", 470, 500, 320, 90, "wp-redis\\nRedis 7（对象缓存）", PURPLE, 12)

    # 卷与网络（左侧）
    d.box("volume", 90, 175, 300, 95, "数据卷 wp_data\\n/var/www/html", GRAY, 12)
    d.box("net", 90, 350, 300, 95, "自定义网络\\nwp-test_default", GRAY, 12)

    d.edge("e1", "wpapp", "wpdb", "SQL 3306", color="#82B366", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("e2", "wpdb", "wpredis", "缓存 6379", color="#9673A6", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("e3", "volume", "wpapp", "挂载", color="#666666", dashed=True, exit=(1, 0.5), entry=(0.5, 0.25))
    d.edge("e4", "net", "wpdb", "网络", color="#666666", dashed=True, exit=(1, 0.5), entry=(0.5, 0.5))

    # 测试端（右侧一列）
    tools = [("jmeter", 170, "JMeter 5.6.3（非 GUI）\\n60 秒定长 × 3 次 × 3 级并发"),
             ("selenium", 300, "Selenium 4.27 + TestNG\\nChrome / Firefox"),
             ("pytest", 430, "pytest + requests\\nREST 接口用例 26 条"),
             ("probe", 560, "安全探针 / 权限矩阵\\nPython requests"),
             ("stats", 688, "docker stats\\nCPU / 内存采样")]
    for cid, y, label in tools:
        d.box(cid, 900, y, 380, 92, label, BLUE if cid != "stats" else GRAY, 12)
        d.edge(f"t_{cid}", cid, "wpapp", "", color="#6C8EBF" if cid != "stats" else "#666666",
               dashed=(cid == "stats"), exit=(0, 0.5), entry=(1, 0.6))
    return d


'''
t = t[:start] + new_env + t[end:]

# ---------- 3) 去掉绕顶的回流线，改由说明框承担 ----------
t = t.replace('''    d.edge("f4", "s7", "s2", "过程改进", color="#9673A6", dashed=True,
           exit=(0.5, 0), entry=(0.5, 0))
''', "")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("已修正换行与拓扑图；含 <br> 处理:", "<br>" in t)
