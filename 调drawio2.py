# -*- coding: utf-8 -*-
"""调整 draw.io 图：缩放 0.62、连线标签白底、重排状态迁移图。"""

import io

P = r"E:\软件质量保证与测试课程设计\生成drawio图.py"
t = io.open(P, encoding="utf-8").read()

t = t.replace("SCALE = 0.5  #", "SCALE = 0.62  #")

# 连线标签加白底，避免压线
t = t.replace(
    '''f"strokeColor={color};strokeWidth={width};fontFamily={FONT};fontSize=11;fontColor={color};"''',
    '''f"strokeColor={color};strokeWidth={width};fontFamily={FONT};fontSize=10;fontColor={color};"
                 f"labelBackgroundColor=#FFFFFF;"''')

# 重写状态迁移图：状态一行、非法迁移走上下两侧
start = t.index("def flow_state():")
end = t.index("# ---------------------------------------------------------------- 4. 缺陷生命周期")
new_state = '''def flow_state():
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
           "绿色实线 = 合法迁移；橙色 = 常规清理；红色虚线 = 非法迁移（越权或跳步）\\n"
           "对应用例：TC-POST-002（draft→pending→publish）\\n"
           "TC-POST-006（trash→restore→delete）；TC-PERM-001（投稿者 publish 应被拒/降级）")
    return d


'''
t = t[:start] + new_state + t[end:]
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("已调整：SCALE 0.62、标签白底、状态图重排")
