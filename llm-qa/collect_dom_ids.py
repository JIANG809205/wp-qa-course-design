#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从真实页面抓取全部元素 id/name，构建可信的"真实定位器集合"。"""

from __future__ import annotations

import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE = os.getenv("WP_BASE", "http://localhost:8080")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dom-ids.json")

PAGES = [
    ("login", "/wp-login.php"),
    ("post-new", "/wp-admin/post-new.php"),
    ("posts-list", "/wp-admin/edit.php"),
    ("comments", "/wp-admin/edit-comments.php"),
    ("media-new", "/wp-admin/media-new.php"),
    ("user-new", "/wp-admin/user-new.php"),
    ("options-general", "/wp-admin/options-general.php"),
    ("profile", "/wp-admin/profile.php"),
    ("dashboard", "/wp-admin/index.php"),
]

opts = Options()
for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
          "--window-size=1600,1000", "--lang=zh-CN"):
    opts.add_argument(a)
d = webdriver.Chrome(options=opts)

try:
    d.get(f"{BASE}/wp-login.php")
    d.find_element(By.ID, "user_login").send_keys("admin")
    d.find_element(By.ID, "user_pass").send_keys("Admin@2026")
    d.find_element(By.ID, "wp-submit").click()
    time.sleep(2)

    ids: set[str] = set()
    names: set[str] = set()
    classes: set[str] = set()
    per_page = {}
    for name, path in PAGES:
        d.get(BASE + path)
        time.sleep(1.2)
        page_ids = d.execute_script(
            "return [...document.querySelectorAll('[id]')].map(e => e.id).filter(Boolean);")
        page_names = d.execute_script(
            "return [...document.querySelectorAll('[name]')].map(e => e.name).filter(Boolean);")
        page_classes = d.execute_script(
            "return [...new Set([...document.querySelectorAll('[class]')]"
            ".flatMap(e => [...e.classList]))].filter(Boolean);")
        ids.update(page_ids)
        names.update(page_names)
        classes.update(page_classes)
        per_page[name] = {"ids": len(page_ids), "names": len(page_names),
                          "classes": len(page_classes)}
        print(f"{name:<16} id={len(page_ids):>3}  name={len(page_names):>3}  class={len(page_classes):>3}")
finally:
    d.quit()

data = {"ids": sorted(ids), "names": sorted(names), "classes": sorted(classes),
        "per_page": per_page, "total_ids": len(ids), "total_names": len(names),
        "total_classes": len(classes)}
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n合计：id {len(ids)} 个，name {len(names)} 个 → {OUT}")
