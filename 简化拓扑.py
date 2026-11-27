# -*- coding: utf-8 -*-
"""简化环境拓扑图：去掉卷/网络方框，减少标签拥挤。"""

import io

P = r"E:\软件质量保证与测试课程设计\生成drawio图.py"
t = io.open(P, encoding="utf-8").read()

start = t.index("def env_topology():")
end = t.index("# ---------------------------------------------------------------- 2. 总体流程")
new = '''def env_topology():
    d = Diagram("env-topology", 1300, 760)
    d.title("图：测试环境拓扑")

    # 宿主机外框
    d.box("host", 30, 70, 800, 640, "", GRAY, rounded=False)
    d._cell("hostlabel", "Windows 11 宿主机（8 核 / 16 GB）",
            f"text;html=1;fontFamily={FONT};fontSize=12;fontStyle=1;align=left;verticalAlign=top;spacingLeft=14;",
            44, 82, 460, 22)

    # WSL2 / Docker 内框
    d.box("wsl", 55, 118, 750, 570, "", BLUE, dashed=True, rounded=False)
    d._cell("wsllabel", "WSL2 Ubuntu 22.04 · Docker 29.1.3 · Compose 2.40.3",
            f"text;html=1;fontFamily={FONT};fontSize=11;align=left;verticalAlign=top;spacingLeft=12;",
            68, 128, 600, 20)

    # 三个容器（靠右纵向堆叠）
    d.box("wpapp", 400, 200, 330, 120,
          "wp-app\\nApache 2.4.52 + PHP 8.1.2\\nWordPress 7.1.5（官方包）\\n端口 8080 → 宿主 8080", ORANGE, 12)
    d.box("wpdb", 400, 370, 330, 95, "wp-db\\nMariaDB 10.6.23\\nmax_connections=300", GREEN, 12)
    d.box("wpredis", 400, 515, 330, 90, "wp-redis\\nRedis 7（对象缓存）", PURPLE, 12)

    d.edge("e1", "wpapp", "wpdb", "SQL 3306", color="#82B366", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("e2", "wpdb", "wpredis", "6380→6379", color="#9673A6", exit=(0.5, 1), entry=(0.5, 0))

    # 左侧说明（数据卷、网络）
    d.box("volume", 85, 210, 250, 90, "数据卷 wp_data\\n/var/www/html", GRAY, 12)
    d.box("net", 85, 380, 250, 90, "自定义网络\\nwp-test_default", GRAY, 12)
    d.edge("e3", "volume", "wpapp", "挂载", color="#666666", dashed=True, exit=(1, 0.5), entry=(0.3, 0.2))
    d.edge("e4", "net", "wpdb", "网络", color="#666666", dashed=True, exit=(1, 0.5), entry=(0.2, 0.5))

    # 测试端（右侧一列）
    tools = [("jmeter", 175, "JMeter 5.6.3（非 GUI）\\n60 秒定长 × 3 次 × 3 级并发"),
             ("selenium", 300, "Selenium 4.27 + TestNG\\nChrome / Firefox"),
             ("pytest", 425, "pytest + requests\\nREST 接口用例 26 条"),
             ("probe", 550, "安全探针 / 权限矩阵\\nPython requests"),
             ("stats", 665, "docker stats\\nCPU / 内存采样")]
    for cid, y, label in tools:
        d.box(cid, 880, y, 390, 90, label, BLUE if cid != "stats" else GRAY, 12)
        d.edge(f"t_{cid}", cid, "wpapp", "", color="#6C8EBF" if cid != "stats" else "#666666",
               dashed=(cid == "stats"), exit=(0, 0.5), entry=(1, 0.6))
    return d


'''
t = t[:start] + new + t[end:]
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("拓扑图已简化")
