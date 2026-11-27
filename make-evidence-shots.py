# -*- coding: utf-8 -*-
"""把控制台日志渲染成终端风格截图，用于报告的"关键过程截图"。

输入：evidence/*.log；输出：evidence/*.png
"""
import os
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(ROOT, "evidence")

MONO = None
for cand in ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/CourierNew.ttf"):
    if os.path.exists(cand):
        MONO = cand
        break
CJK = "C:/Windows/Fonts/msyh.ttc"


def font(size, cjk=False):
    path = CJK if cjk else MONO
    return ImageFont.truetype(path, size)


def has_cjk(s):
    return bool(re.search(r"[\u4e00-\u9fff]", s))


def pick(lines, head=9, tail=6, title=""):
    if len(lines) <= head + tail + 2:
        return list(dict.fromkeys(lines))
    return list(dict.fromkeys(lines[:head])) + ["  ⋯（中间省略）"] + list(dict.fromkeys(lines[-tail:]))


def render(src, dst, title, head=9, tail=6, width=980, fsize=19):
    raw = open(os.path.join(EV, src), encoding="utf-8", errors="replace").read().splitlines()
    noise = re.compile(r"^(Nov \d|WARNING|SLF4J|Session ID|Build info|System info|Driver info|Capabilities|\s*\{|\(Session info)")
    lines = []
    for l in raw:
        s = re.sub(r"\x1b\[[0-9;]*m", "", l).rstrip()
        s = s.replace("\u2713", "\u221a").replace("\u2717", "\u00d7")
        if not s.strip() or noise.match(s):
            continue
        if s.strip("\u25a1\u2500-\u257f " ) == "" or s.strip() in ("\u25a1", "?"):   # 只剩方块/横线的行
            continue
        lines.append(s)
    # 优先展示含关键结论的行
    keys = ("Tests run", "passed", "不一致", "命中数", "BUILD", "已写入", "Total tests")
    hot = [l for l in lines if any(k in l for k in keys)]
    shown = pick(lines, head, tail, title)
    if hot:
        shown = shown[:max(6, head - 4)] + hot[:6] + ["  ⋯"] + shown[-tail:]

    f = font(fsize)
    fc = font(fsize, cjk=True)
    line_h = int(fsize * 1.55)
    pad = 18
    bar = 34
    w = width
    h = bar + pad * 2 + line_h * len(shown)
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, bar], fill="#2B2B2B")
    d.text((14, 9), title, font=font(13), fill="#E8E8E8")
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        d.ellipse([w - 62 + i * 18, 12, w - 50 + i * 18, 24], fill=c)

    y = bar + pad
    for ln in shown:
        txt = ln[:118]
        if ln.strip().startswith("[ERROR]") or "FAILED" in ln or "失败" in ln:
            color = "#B00020"
        elif "passed" in ln or "+ 通过" in ln or "不一致：0" in ln:
            color = "#1B5E20"
        elif ln.strip().startswith("⋯"):
            color = "#8A8A8A"
        else:
            color = "#1F1F1F"
        d.text((pad, y), txt, font=fc, fill=color)
        y += line_h
    d.rectangle([0, 0, w - 1, h - 1], outline="#D0D0D0")
    img.save(os.path.join(EV, dst))
    print("已生成", dst, f"{len(shown)} 行")


for src, dst, title in (
    ("mvn-test.log", "mvn-test.png", "bash · mvn test  (TestNG 9 条)"),
    ("pytest.log", "pytest.png", "bash · pytest -q  (REST 接口 26 条)"),
    ("matrix.log", "matrix.png", "bash · permission_matrix.py  (36 格)"),
    ("probe-compare.log", "probe-compare.png", "bash · 12 项探针 修复前后对照"),
):
    path = os.path.join(EV, src)
    if os.path.exists(path):
        render(src, dst, title)
    else:
        print("缺日志:", src)
