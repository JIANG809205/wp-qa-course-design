# -*- coding: utf-8 -*-
"""修正对比图配色，接入 8 张 draw.io 图到报告。"""

import io

GEN_D = r"E:\软件质量保证与测试课程设计\生成drawio图.py"
GEN_R = r"E:\软件质量保证与测试课程设计\生成报告docx-模板.py"
MD = r"E:\软件质量保证与测试课程设计\报告-按示例模板.md"

# ---------- 1) fix_compare 显式标记是否命中 ----------
t = io.open(GEN_D, encoding="utf-8").read()
old_items = '''    items = [
        ("P01 安全响应头", "缺失 4/4", "0/4"),
        ("P02 debug.log", "200", "403"),
        ("P03 目录索引", "200", "403"),
        ("P04 readme.html", "200", "200（遗留）"),
        ("P05 XML-RPC", "200", "403"),
        ("P06 作者枚举", "301", "404"),
        ("P07 REST 用户", "200", "404"),
        ("P08 空文件上传", "500", "400"),
        ("P09 重名用户", "500", "400"),
        ("P10 登录限流", "无限制", "429"),
        ("P11 非法参数", "400", "400"),
        ("P12 license.txt", "200", "200（遗留）"),
    ]'''
new_items = '''    items = [
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
    ]'''
if old_items in t:
    t = t.replace(old_items, new_items)

old_loop = '''    for i, (name, before, after) in enumerate(items):
        fixed = ("遗留" not in after) and before != after
        d.box(f"i{i}a", 60, y, 380, 30, name, GRAY, 11)
        d.box(f"i{i}b", 470, y, 220, 30, before, RED if before != after else GRAY, 11)
        d.box(f"i{i}c", 720, y, 220, 30, after, GREEN if fixed else GRAY, 11)
        y += 36'''
new_loop = '''    for i, (name, before, after, before_hit, after_hit) in enumerate(items):
        d.box(f"i{i}a", 60, y, 380, 30, name, GRAY, 11)
        d.box(f"i{i}b", 470, y, 220, 30, before, RED if before_hit else GRAY, 11)
        d.box(f"i{i}c", 720, y, 220, 30, after, RED if after_hit else GREEN, 11)
        y += 36'''
if old_loop in t:
    t = t.replace(old_loop, new_loop)
io.open(GEN_D, "w", encoding="utf-8", newline="\n").write(t)
print("fix_compare 已改为显式命中标记")

# ---------- 2) 报告生成器：新增图映射 ----------
g = io.open(GEN_R, encoding="utf-8").read()
add_map = '''    "flow-test": "diagrams/flow-test.png",
    "flow-state": "diagrams/flow-state.png",
    "defect-flow": "diagrams/defect-flow.png",
    "fix-compare": "diagrams/fix-compare.png",
    "env-topology": "diagrams/env-topology.png",
    "llm-workflow": "diagrams/llm-workflow.png",
    "ci-pipeline": "diagrams/ci-pipeline.png",
    "perf-chain": "diagrams/perf-chain.png",'''
for key in ("flow-test", "flow-state", "defect-flow", "fix-compare",
            "env-topology", "llm-workflow", "ci-pipeline", "perf-chain"):
    g = g.replace(f'    "{key}": "wp-perf/charts-final/{key}.png",\n', "")
if '"env-topology"' not in g:
    g = g.replace('FIG = {\n', 'FIG = {\n' + add_map + "\n", 1)
io.open(GEN_R, "w", encoding="utf-8", newline="\n").write(g)
print("图映射已更新")

# ---------- 3) 插入新图标记 ----------
m = io.open(MD, encoding="utf-8").read()


def ins(anchor, marker):
    global m
    if marker in m:
        return
    if anchor not in m:
        print("未找到锚点:", anchor[:30])
        return
    m = m.replace(anchor, anchor + "\n\n" + marker, 1)


ins("持续集成流水线有三个 job：静态检查（编译与脚本语法）、端到端冒烟（起容器跑登录与发文的少量用例）、评测流水线自检（用 mock 数据验证指标脚本本身没算错）。",
    "[[图:ci-pipeline|图3.1 持续集成流水线]]")

ins("这些配置均记录在环境脚本中，可一键重建。测试站点的首页如下图所示。",
    "[[图:env-topology|图4.1 测试环境拓扑]]")

ins("针对瓶颈做了两次优化实验，结果均为负：",
    "[[图:perf-chain|图5.19 性能压测链路与观测点]]")

ins("这张表说明一个事实：大模型在本项目的介入集中在\"写\"（初稿、样板、措辞）与\"查\"（覆盖遗漏、失败初判），",
    "[[图:llm-workflow|图6.1 大模型在测试流程中的介入点]]")

io.open(MD, "w", encoding="utf-8", newline="\n").write(m)
print("图标记数:", m.count("[[图:"))
