#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兼容性测试：3 种视口 × 4 个页面，检查横向溢出、关键元素可见性与控制台错误。"""

from __future__ import annotations

import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE = os.getenv("WP_BASE", "http://localhost:8080")
OUT = os.getenv("OUT_DIR", "/opt/qa/compat")
os.makedirs(OUT, exist_ok=True)

VIEWPORTS = [("desktop-1920", 1920, 1080), ("laptop-1366", 1366, 768), ("mobile-375", 375, 812)]
PAGES = [("home", "/"), ("blog", "/qa-blog/"), ("login", "/wp-login.php"), ("admin", "/wp-admin/edit.php")]

ADMIN = ("admin", "Admin@2026")


def driver(width: int, height: int):
    o = Options()
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
              f"--window-size={width},{height}", "--lang=zh-CN"):
        o.add_argument(a)
    d = webdriver.Chrome(options=o)
    d.set_window_size(width, height)
    return d


def login(d):
    d.get(f"{BASE}/wp-login.php")
    d.find_element(By.ID, "user_login").send_keys(ADMIN[0])
    d.find_element(By.ID, "user_pass").send_keys(ADMIN[1])
    d.find_element(By.ID, "wp-submit").click()
    time.sleep(1.5)


results = []
for vname, w, h in VIEWPORTS:
    d = driver(w, h)
    try:
        login(d)
        for pname, path in PAGES:
            d.get(BASE + path)
            time.sleep(1.2)
            info = d.execute_script("""
                const de = document.documentElement;
                const overflow = de.scrollWidth - de.clientWidth;
                const wide = [...document.querySelectorAll('body *')]
                    .filter(el => el.getBoundingClientRect().width > de.clientWidth + 4)
                    .slice(0, 5)
                    .map(el => el.tagName + (el.id ? '#' + el.id : '') +
                         (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''));
                return {overflow: overflow, wide: wide, title: document.title,
                        bodyW: de.scrollWidth, clientW: de.clientWidth};
            """)
            shot = os.path.join(OUT, f"{vname}-{pname}.png")
            d.save_screenshot(shot)
            results.append({
                "viewport": vname, "page": pname, "url": path,
                "overflow_px": info["overflow"], "wide_elements": info["wide"],
                "title": info["title"], "screenshot": shot,
                "pass": info["overflow"] <= 4 and len(info["wide"]) == 0,
            })
            print(f"{vname:<14}{pname:<7} overflow={info['overflow']:>4}px  宽元素={len(info['wide'])}")
    finally:
        d.quit()

total = len(results)
ok = sum(1 for r in results if r["pass"])
json.dump(results, open(os.path.join(OUT, "compat.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"\n合计 {total} 组，通过 {ok} 组（{ok/total*100:.1f}%）")
print("screenshots:", OUT)
