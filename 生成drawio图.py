# -*- coding: utf-8 -*-
"""用 draw.io XML 生成报告所需的 8 张专业图表（可编辑、可复现）。

生成 .drawio 源文件 + 调用 draw.io CLI 导出 PNG。
"""

from __future__ import annotations

import os
import subprocess

DIR = r"E:\软件质量保证与测试课程设计\diagrams"
EXE = r"C:\Users\HP\AppData\Local\Programs\draw.io\draw.io.exe"
os.makedirs(DIR, exist_ok=True)

# 配色（draw.io 常用柔和色）
BLUE = ("#DAE8FC", "#6C8EBF")
GREEN = ("#D5E8D4", "#82B366")
ORANGE = ("#FFE6CC", "#D79B00")
RED = ("#F8CECC", "#B85450")
GRAY = ("#F5F5F5", "#666666")
PURPLE = ("#E1D5E7", "#9673A6")
YELLOW = ("#FFF2CC", "#D6B656")

FONT = "Microsoft YaHei"
SCALE = 0.62  # 画布按像素设计，导出前统一缩小几何，字号保持点数


class Diagram:
    def __init__(self, name: str, width: int = 1400, height: int = 820):
        self.name = name
        self.w, self.h = round(width * SCALE), round(height * SCALE)
        self.cells: list[str] = []

    def _cell(self, cid, value, style, x, y, w, h, vertex=True, extra=""):
        x, y, w, h = (round(v * SCALE) for v in (x, y, w, h))
        label = (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace("\n", "&lt;br&gt;"))
        self.cells.append(
            f'<mxCell id="{cid}" value="{label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'
        )

    def box(self, cid, x, y, w, h, text, color=BLUE, size=13, bold=False, dashed=False, rounded=True):
        fill, stroke = color
        style = (f"rounded={1 if rounded else 0};whiteSpace=wrap;html=1;"
                 f"fillColor={fill};strokeColor={stroke};fontFamily={FONT};fontSize={size};"
                 f"fontColor=#1A1A1A;{'fontStyle=1;' if bold else ''}"
                 f"{'dashed=1;' if dashed else ''}verticalAlign=middle;align=center;")
        self._cell(cid, text, style, x, y, w, h)

    def edge(self, cid, src, dst, text="", color="#333333", dashed=False, width=1.5, exit=None, entry=None):
        label = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace("\n", "&lt;br&gt;"))
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;"
                 f"strokeColor={color};strokeWidth={width};fontFamily={FONT};fontSize=10;fontColor={color};"
                 f"labelBackgroundColor=#FFFFFF;"
                 f"{'dashed=1;' if dashed else ''}")
        if exit:
            style += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            style += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        self.cells.append(
            f'<mxCell id="{cid}" value="{label}" style="{style}" edge="1" parent="1" '
            f'source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry" /></mxCell>'
        )

    def title(self, text, y=20):
        self._cell("title", text,
                   f"text;html=1;fontFamily={FONT};fontSize=18;fontStyle=1;fontColor=#1A1A1A;align=center;",
                   0, y, self.w, 34, vertex=True)

    def note(self, cid, x, y, w, h, text, size=11):
        fill, stroke = GRAY
        self._cell(cid, text,
                   f"shape=note;whiteSpace=wrap;html=1;size=12;fillColor={fill};strokeColor={stroke};"
                   f"fontFamily={FONT};fontSize={size};align=left;verticalAlign=top;spacingLeft=6;",
                   x, y, w, h)

    def xml(self) -> str:
        body = "\n        ".join(self.cells)
        return f'''<mxfile host="app.diagrams.net" agent="qa-report" version="24.7.17">
  <diagram id="{self.name}" name="{self.name}">
    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''

    def save(self):
        path = os.path.join(DIR, f"{self.name}.drawio")
        open(path, "w", encoding="utf-8").write(self.xml())
        return path


# ---------------------------------------------------------------- 1. 环境拓扑
def env_topology():
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
          "wp-app\nApache 2.4.52 + PHP 8.1.2\nWordPress 7.1.5（官方包）\n端口 8080 → 宿主 8080", ORANGE, 12)
    d.box("wpdb", 400, 370, 330, 95, "wp-db\nMariaDB 10.6.23\nmax_connections=300", GREEN, 12)
    d.box("wpredis", 400, 515, 330, 90, "wp-redis\nRedis 7（已就绪，未装 object-cache）", PURPLE, 12)

    d.edge("e1", "wpapp", "wpdb", "SQL 3306", color="#82B366", exit=(0.5, 1), entry=(0.5, 0))

    # 左侧说明（数据卷、网络）
    d.box("volume", 85, 210, 250, 90, "数据卷 wp_data\n/var/www/html", GRAY, 12)
    d.box("net", 85, 380, 250, 90, "自定义网络\nwp-test_default", GRAY, 12)
    d.edge("e3", "volume", "wpapp", "挂载", color="#666666", dashed=True, exit=(1, 0.5), entry=(0.3, 0.2))
    d.edge("e4", "net", "wpdb", "网络", color="#666666", dashed=True, exit=(1, 0.5), entry=(0.2, 0.5))

    # 测试端（右侧一列）
    tools = [("jmeter", 175, "JMeter 5.6.3（非 GUI）\n60 秒定长 × 3 次 × 3 级并发"),
             ("selenium", 300, "Selenium 4.27 + TestNG\nChrome / Firefox"),
             ("pytest", 425, "pytest + requests\nREST 接口用例 26 条"),
             ("probe", 550, "安全探针 / 权限矩阵\nPython requests"),
             ("stats", 665, "docker stats\nCPU / 内存采样")]
    for cid, y, label in tools:
        d.box(cid, 880, y, 390, 90, label, BLUE if cid != "stats" else GRAY, 12)
        d.edge(f"t_{cid}", cid, "wpapp", "", color="#6C8EBF" if cid != "stats" else "#666666",
               dashed=(cid == "stats"), exit=(0, 0.5), entry=(1, 0.6))
    return d


# ---------------------------------------------------------------- 2. 总体流程
def flow_test():
    d = Diagram("flow-test", 1400, 620)
    d.title("图：测试总体流程")
    steps = [
        ("s1", 40, "需求分析\nR01–R11"),
        ("s2", 230, "测试计划\n策略/范围/准入准出"),
        ("s3", 420, "用例设计\n等价类/边界/状态/判定表"),
        ("s4", 610, "环境准备\n容器/数据/版本固定"),
        ("s5", 800, "测试执行\n功能/接口/性能/安全/兼容"),
        ("s6", 990, "缺陷管理\n登记/定级/修复/复测"),
        ("s7", 1180, "评估与报告\n指标/核验/总结"),
    ]
    for cid, x, label in steps:
        d.box(cid, x, 150, 170, 90, label, BLUE, 12)
    for a, b in zip(steps, steps[1:]):
        d.edge(f"e{a[0]}{b[0]}", a[0], b[0], color="#6C8EBF")

    d.box("fix", 990, 330, 170, 70, "配置加固 / 代码修复", ORANGE, 12)
    d.box("retest", 800, 330, 150, 70, "回归复测", GREEN, 12)
    d.edge("f1", "s6", "fix", "缺陷", color="#D79B00", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("f2", "fix", "retest", "", color="#82B366", exit=(0, 0.5), entry=(1, 0.5))
    d.edge("f3", "retest", "s5", "重跑用例", color="#82B366", exit=(0.5, 0), entry=(0.5, 1))

    d.note("n1", 40, 440, 640, 110,
           "原则：每个环节产出可机读中间结果（xlsx / json / jtl）\n"
           "结论写入报告前，必须能由核验脚本回溯到原始文件\n"
           "缺陷闭环：登记 → 修复 → 复测 → 关闭，关闭率 90.9%")
    return d


# ---------------------------------------------------------------- 3. 状态迁移
def flow_state():
    d = Diagram("flow-state", 1200, 640)
    d.title("图：文章状态迁移（合法路径与非法路径）")

    d.box("draft", 60, 260, 180, 80, "草稿 draft", GRAY, 13)
    d.box("pending", 330, 260, 180, 80, "待审 pending", YELLOW, 13)
    d.box("publish", 600, 260, 180, 80, "已发布 publish", GREEN, 13)
    d.box("trash", 870, 260, 170, 80, "回收站 trash", RED, 13)
    d.box("del", 870, 430, 170, 60, "永久删除", RED, 12, dashed=True)

    d.edge("a1", "draft", "pending", "提交复审", color="#82B366", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("a2", "pending", "publish", "审核通过", color="#82B366", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("a3", "publish", "trash", "移入回收站", color="#D79B00", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("a4", "trash", "del", "彻底删除", color="#B85450", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("a5", "trash", "publish", "还原", color="#82B366", dashed=True,
           exit=(0.5, 0), entry=(0.7, 0))

    # 非法迁移：一条从上方绕过，一条从下方绕过
    d.edge("x1", "pending", "publish", "投稿者直接发布（应拒绝）", color="#B85450",
           dashed=True, width=2, exit=(0.5, 0), entry=(0.5, 0))
    d.edge("x2", "draft", "publish", "跳过审核（应拒绝）", color="#B85450",
           dashed=True, width=2, exit=(0.5, 1), entry=(0.5, 1))

    d.note("n", 60, 500, 760, 110,
           "绿色实线 = 合法迁移；橙色 = 常规清理；红色虚线 = 非法迁移（越权或跳步）\n"
           "对应用例：TC-POST-002（draft→pending→publish）\n"
           "TC-POST-006（trash→restore→delete）；TC-PERM-001（投稿者 publish 应被拒/降级）")
    return d


# ---------------------------------------------------------------- 4. 缺陷生命周期
def defect_flow():
    d = Diagram("defect-flow", 1300, 520)
    d.title("图：缺陷生命周期与状态流转")
    stages = [
        ("d1", 40, "发现\n用例失败 / 探针命中"),
        ("d2", 250, "登记\n编号 + 证据"),
        ("d3", 460, "定级\nP1 / P2 / P3 / 观察"),
        ("d4", 670, "修复\n配置加固 / 代码补丁"),
        ("d5", 880, "复测\n同一判据重跑"),
        ("d6", 1090, "关闭 / 遗留"),
    ]
    for cid, x, label in stages:
        d.box(cid, x, 170, 180, 90, label, BLUE, 12)
    for a, b in zip(stages, stages[1:]):
        d.edge(f"e{a[0]}{b[0]}", a[0], b[0], color="#6C8EBF")

    d.box("dup", 460, 330, 180, 70, "撤销 / 降级\n（证据不成立）", GRAY, 12, dashed=True)
    d.edge("r1", "d3", "dup", "", color="#666666", dashed=True, exit=(0.5, 1), entry=(0.5, 0))
    d.edge("r2", "dup", "d2", "", color="#666666", dashed=True, exit=(0, 0.5), entry=(0.5, 1))

    d.box("count", 40, 330, 800, 90,
          "本次结果：11 条缺陷 + 1 观察项；10 条关闭（90.9%），1 条遗留（DEF-010 Server 头，需改镜像层）\n"
          "修复后同一套 12 项探针命中数：11/12 → 2/12（剩余 readme.html、license.txt 记为遗留风险）", GREEN, 12)
    return d


# ---------------------------------------------------------------- 5. 大模型流程
def llm_workflow():
    d = Diagram("llm-workflow", 1400, 720)
    d.title("图：大模型在测试流程中的介入点（绿=人机协作，灰=仅人工）")

    row1 = [("p1", 40, "需求分析", GRAY), ("p2", 300, "测试设计", GRAY),
            ("p3", 560, "用例编写", GREEN), ("p4", 820, "脚本实现", GREEN),
            ("p5", 1080, "环境与数据", GREEN)]
    row2 = [("p6", 40, "测试执行", GRAY), ("p7", 300, "失败分析", GREEN),
            ("p8", 560, "缺陷报告", GREEN), ("p9", 820, "回归测试", GRAY),
            ("p10", 1080, "总结", GREEN)]

    for cid, x, label, color in row1:
        d.box(cid, x, 150, 200, 80, label, color, 13)
    for cid, x, label, color in row2:
        d.box(cid, x, 360, 200, 80, label, color, 13)

    for a, b in zip(row1, row1[1:]):
        d.edge(f"r{a[0]}{b[0]}", a[0], b[0], color="#6C8EBF")
    d.edge("down", "p5", "p6", "", color="#6C8EBF", exit=(0.5, 1), entry=(0.5, 0))
    for a, b in zip(row2, row2[1:]):
        d.edge(f"s{a[0]}{b[0]}", a[0], b[0], color="#6C8EBF")

    d.box("legend", 40, 500, 620, 150,
          "绿（人机协作）：模型出初稿或初判，人再定稿\n"
          "灰（仅人工）：可测性判断、判定规则、最终归因、回归范围\n\n"
          "关键纪律：模型产出不直接进交付物；定位器需 DOM 校验，URL 需指向被测环境",
          GRAY, 12)
    d.box("metric", 700, 500, 640, 150,
          "量化结论（n=96 脚本 / 24 条归因）\n"
          "定位器保真度：29.0% / 33.1% / 34.9%\n"
          "严格可运行率：5.2% / 1.0% / 0%\n"
          "归因误判为缺陷：0 次（24 条平衡样本）", GREEN, 12)
    return d


# ---------------------------------------------------------------- 6. CI 流水线
def ci_pipeline():
    d = Diagram("ci-pipeline", 1300, 460)
    d.title("图：持续集成流水线（GitHub Actions）")
    d.box("push", 40, 180, 170, 80, "push / PR\n触发", GRAY, 13)
    d.box("j1", 300, 90, 260, 90, "job1 静态检查\nPython 语法 + Maven 编译", BLUE, 12)
    d.box("j2", 300, 260, 260, 90, "job2 端到端冒烟\n起容器 + 登录/发文", GREEN, 12)
    d.box("j3", 640, 175, 280, 90, "job3 评测流水线自检\nmock 数据验证指标脚本", ORANGE, 12)
    d.box("end", 1000, 175, 200, 90, "结果\n通过 / 失败", PURPLE, 13)
    d.edge("c1", "push", "j1", "", color="#6C8EBF", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("c2", "push", "j2", "", color="#6C8EBF", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("c3", "j1", "j3", "", color="#6C8EBF", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("c4", "j2", "j3", "", color="#6C8EBF", exit=(1, 0.5), entry=(0, 0.5))
    d.edge("c5", "j3", "end", "", color="#6C8EBF", exit=(1, 0.5), entry=(0, 0.5))
    d.note("n", 40, 330, 700, 90,
           "job3 是针对本项目加的：如果评测脚本自己算错，再完整的评测也只会输出一个漂亮的错数。")
    return d


# ---------------------------------------------------------------- 7. 压测链路
def perf_chain():
    d = Diagram("perf-chain", 1300, 520)
    d.title("图：性能压测链路与观测点")
    d.box("jm", 40, 180, 200, 90, "JMeter 5.6.3\n线程组 10/50/100\n60 秒定长", BLUE, 12)
    d.box("apache", 330, 180, 220, 90, "Apache 2.4.52\nmod_php / prefork", ORANGE, 12)
    d.box("wp", 640, 180, 200, 90, "WordPress 7.1.5\n区块渲染 / 查询", GREEN, 12)
    d.box("db", 640, 340, 200, 80, "MariaDB 10.6\n文章 + 评论", PURPLE, 12)
    d.box("redis", 900, 340, 180, 80, "Redis 7\n对象缓存（未启用）", GRAY, 12)
    d.box("stats", 900, 180, 200, 90, "docker stats\nCPU 592%–671%", GRAY, 12)
    d.box("jtl", 330, 340, 220, 80, "jtl 原始记录\n时间戳 + 耗时", GRAY, 12)
    d.edge("p1", "jm", "apache", "HTTP", color="#6C8EBF")
    d.edge("p2", "apache", "wp", "", color="#6C8EBF")
    d.edge("p3", "wp", "db", "SQL", color="#9673A6")
    d.edge("p4", "wp", "redis", "缓存", color="#666666", dashed=True)
    d.edge("p5", "jm", "jtl", "落盘", color="#666666", dashed=True)
    d.edge("p6", "stats", "apache", "采样", color="#666666", dashed=True)
    d.note("n", 40, 400, 560, 80,
           "结论：CPU 占满 6–6.8 核 → 瓶颈在单请求 CPU 开销\n"
           "列表页 100 并发 P95 2834 ms，进入排队劣化区")
    return d


# ---------------------------------------------------------------- 8. 修复前后对比
def fix_compare():
    d = Diagram("fix-compare", 1200, 620)
    d.title("图：修复前后 12 项探针命中对比")
    items = [
        ("P01 安全响应头", "缺失 4/4", "0/4", True, False),
        ("P02 debug.log", "200", "403", True, False),
        ("P03 目录索引", "200", "403", True, False),
        ("P04 readme.html", "200", "200（遗留）", True, True),
        ("P05 XML-RPC", "200", "403", True, False),
        ("P06 作者枚举", "301", "404", True, False),
        ("P07 REST 用户", "200", "404", True, False),
        ("P08 空文件上传", "500", "400", True, False),
        ("P09 重名用户", "500", "400", True, False),
        ("P10 登录限流", "无限制", "429", True, False),
        ("P11 非法参数", "400", "400", False, False),
        ("P12 license.txt", "200", "200（遗留）", True, True),
    ]
    d._cell("h1", "探针", f"text;html=1;fontFamily={FONT};fontSize=13;fontStyle=1;", 60, 80, 380, 26)
    d._cell("h2", "修复前", f"text;html=1;fontFamily={FONT};fontSize=13;fontStyle=1;align=center;", 470, 80, 220, 26)
    d._cell("h3", "修复后", f"text;html=1;fontFamily={FONT};fontSize=13;fontStyle=1;align=center;", 720, 80, 220, 26)
    y = 115
    for i, (name, before, after, before_hit, after_hit) in enumerate(items):
        d.box(f"i{i}a", 60, y, 380, 30, name, GRAY, 11)
        d.box(f"i{i}b", 470, y, 220, 30, before, RED if before_hit else GRAY, 11)
        d.box(f"i{i}c", 720, y, 220, 30, after, RED if after_hit else GREEN, 11)
        y += 36
    d.box("sum", 60, y + 12, 880, 50,
          "命中数：11/12 → 2/12（+2 项为有意保留的低危信息暴露）", GREEN, 13, bold=True)
    return d


BUILDERS = [env_topology, flow_test, flow_state, defect_flow,
            llm_workflow, ci_pipeline, perf_chain, fix_compare]


def main():
    paths = []
    for b in BUILDERS:
        d = b()
        p = d.save()
        paths.append(p)
        print("生成源文件:", os.path.basename(p))

    for p in paths:
        png = p.replace(".drawio", ".png")
        subprocess.run([EXE, "--no-sandbox", "-x", "-f", "png", "-s", "2",
                        "-o", png, p], capture_output=True, timeout=180)
        size = os.path.getsize(png) if os.path.exists(png) else 0
        print(f"  导出 {os.path.basename(png)}: {size//1024} KB")


if __name__ == "__main__":
    main()
