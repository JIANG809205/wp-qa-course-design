#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 20 条脚本样本上重算定位器保真度（与 n=10 同口径，仅扩大样本）。"""

from __future__ import annotations

import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DIRS = {"DeepSeek-V4.1-Flash": "/opt/qa/scripts20-deepseek-v4.1-flash/deepseek-v4.1-flash",
        "DeepSeek-V4-Pro": "/opt/qa/scripts20-deepseek-v4-pro/deepseek-v4-pro",
        "Qwen-Plus": "/opt/qa/scripts20-qwen-plus/qwen-plus"}

REAL = {
    "user_login", "user_pass", "wp-submit", "login_error",
    "title", "save-post", "publish", "message", "wpadminbar",
    "comment", "author", "email", "submit", "wpbody",
    "the-comment-list", "createuser", "blogname", "plupload-browse-button",
    "post-search-input", "search-submit", "posts-filter", "publish",
}

ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')

rows = []
for label, d in DIRS.items():
    files = sorted(glob.glob(os.path.join(d, "*.java")))
    total = real = 0
    for f in files:
        code = open(f, encoding="utf-8", errors="replace").read()
        ids = ID_PAT.findall(code) + NAME_PAT.findall(code)
        for css in CSS_PAT.findall(code):
            ids.extend(re.findall(r"#([A-Za-z0-9_-]+)", css))
        total += len(ids)
        real += sum(1 for i in ids if i in REAL)
    rate = round(real / total * 100, 1) if total else 0
    rows.append({"model": label, "scripts": len(files), "selectors": total,
                 "real": real, "fidelity": rate})
    print(f"{label:<22} 脚本 {len(files):>2}，定位器 {total:>3}，命中 {real:>3} → {rate:>5.1f}%")

out = os.path.join(BASE, "outputs", "selector-fidelity20.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已写入", out)
