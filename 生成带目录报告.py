# -*- coding: utf-8 -*-
"""两遍生成带静态目录的报告：
1) 第一遍生成 docx（目录页码占位），转 PDF，定位各标题所在页；
2) 写 toc.json，第二遍生成，页码填入目录。
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = r"E:\软件质量保证与测试课程设计"
GEN = os.path.join(ROOT, "生成报告docx-模板.py")
MD = os.path.join(ROOT, "报告-按示例模板.md")
DOCX = os.path.join(ROOT, "课程设计报告-241303109-蒋晓涵.docx")
TOC = os.path.join(ROOT, "toc.json")

NODE = r"D:\deepseek\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
CLI = r"D:\deepseek\resources\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js"


def build_docx():
    env = dict(os.environ, OUT_DOCX=DOCX, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, GEN], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])


def to_pdf(pdf_path):
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    r = subprocess.run([NODE, CLI, "convert", "--input", DOCX, "--output", pdf_path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(pdf_path):
        raise SystemExit("PDF 转换失败: " + (r.stderr or r.stdout)[-300:])


def headings():
    out = []
    in_code = False
    for ln in open(MD, encoding="utf-8").read().splitlines():
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,2})\s+(.*)$", s)
        if m:
            out.append((len(m.group(1)), m.group(2).strip()))
    return out


def locate(pdf_path, heads):
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    pages = []
    for pg in reader.pages:
        try:
            pages.append((pg.extract_text() or "").splitlines())
        except Exception:  # noqa: BLE001
            pages.append([])

    def norm(s):
        return re.sub(r"\s+", "", s)

    # 用正文首句定位正文起始页，避免命中目录页里的标题行
    sentinel = "本报告记录了一次完整的"
    body_start = 0
    for idx, lines in enumerate(pages):
        if sentinel in "".join(lines):
            body_start = idx
            break

    entries = []
    search_from = body_start
    for level, text in heads:
        key = norm(text)
        page_no = None
        # 标题行必须与标题文本一致（允许前后空白），且按顺序向后查找
        for idx in range(search_from, len(pages)):
            for line in pages[idx]:
                if norm(line) == key:
                    page_no = idx + 1
                    break
            if page_no:
                break
        if page_no is None:
            # 退化：整页包含且长度接近
            for idx in range(search_from, len(pages)):
                joined = norm("".join(pages[idx]))
                if key and key in joined:
                    page_no = idx + 1
                    break
        if page_no:
            search_from = page_no - 1
        entries.append({"level": level, "text": text, "page": page_no if page_no else "—"})
    return entries


if __name__ == "__main__":
    heads = headings()
    print("标题数:", len(heads))

    # 第一遍：无 toc.json → 目录用占位
    if os.path.exists(TOC):
        os.remove(TOC)
    build_docx()
    pdf1 = os.path.join(ROOT, "_toc_pass1.pdf")
    to_pdf(pdf1)
    entries = locate(pdf1, heads)
    json.dump({"entries": entries}, open(TOC, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("已写 toc.json，命中页码:", sum(1 for e in entries if e["page"] != "—"), "/", len(entries))

    # 第二遍：带页码
    build_docx()
    pdf2 = os.path.join(ROOT, "_toc_pass2.pdf")
    to_pdf(pdf2)

    from pypdf import PdfReader
    n1 = len(PdfReader(pdf1).pages)
    n2 = len(PdfReader(pdf2).pages)
    print(f"页数：第一遍 {n1}，第二遍 {n2}")
    if n1 != n2:
        print("⚠ 两遍页数不同，目录页码可能偏移，需重跑一次以收敛")

    for f in (pdf1, pdf2):
        try:
            os.remove(f)
        except OSError:
            pass
