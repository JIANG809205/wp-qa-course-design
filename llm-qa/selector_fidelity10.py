#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 10 条脚本样本上重算定位器保真度（与旧 3 条样本口径一致，仅扩大样本）。"""

from __future__ import annotations

import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(BASE, "outputs", "scripts10")

REAL = {
    "user_login", "user_pass", "wp-submit", "login_error",
    "title", "save-post", "publish", "message", "wpadminbar",
    "comment", "author", "email", "submit", "wpbody",
    "the-comment-list", "createuser", "blogname", "plupload-browse-button",
}

ID_PAT = re.compile(r'By\.id\(\s*"([^"]+)"\s*\)')
CSS_PAT = re.compile(r'By\.cssSelector\(\s*"([^"]+)"\s*\)')
# 顺带统计 By.name / xpath 里出现的 id
NAME_PAT = re.compile(r'By\.name\(\s*"([^"]+)"\s*\)')

MODELS = {"deepseek-v4.1-flash": "DeepSeek-V4.1-Flash",
          "deepseek-v4-pro": "DeepSeek-V4-Pro",
          "qwen-plus": "Qwen-Plus"}

rows = []
for key, label in MODELS.items():
    d = os.path.join(SCRIPTS, key)
    files = glob.glob(os.path.join(d, "*.java"))
    total = real = 0
    per = []
    for f in files:
        code = open(f, encoding="utf-8", errors="replace").read()
        ids = ID_PAT.findall(code) + NAME_PAT.findall(code)
        for css in CSS_PAT.findall(code):
            ids.extend(re.findall(r"#([A-Za-z0-9_-]+)", css))
        total += len(ids)
        r = sum(1 for i in ids if i in REAL)
        real += r
        per.append({"file": os.path.basename(f), "selectors": len(ids), "real": r})
    rate = round(real / total * 100, 1) if total else 0
    rows.append({"model": label, "scripts": len(files), "selectors": total,
                 "real": real, "fidelity": rate, "detail": per})
    print(f"{label:<22} 脚本 {len(files):>2} 个，定位器 {total:>3} 个，命中真实 {real:>3} → {rate:>5.1f}%")

out = os.path.join(BASE, "outputs", "selector-fidelity10.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已写入", out)
