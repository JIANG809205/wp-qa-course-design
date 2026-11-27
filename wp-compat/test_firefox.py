# -*- coding: utf-8 -*-
"""跨浏览器兼容性测试：Windows 本机 Firefox + 三种视口 × 四个页面。"""

from __future__ import annotations

import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

BASE = os.getenv("WP_BASE", "http://localhost:8080")
OUT = os.getenv("OUT_DIR", r"E:\软件质量保证与测试课程设计\wp-compat\firefox")
FF = os.getenv("FIREFOX_BIN", r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe")
DRIVER = os.getenv("GECKO", r"E:\软件质量保证与测试课程设计\wp-compat\geckodriver.exe")

os.makedirs(OUT, exist_ok=True)

VIEWPORTS = [("desktop-1920", 1920, 1080), ("laptop-1366", 1366, 768), ("mobile-375", 375, 812)]
PAGES = [("home", "/"), ("blog", "/qa-blog/"), ("login", "/wp-login.php"), ("admin", "/wp-admin/edit.php")]

def new_driver(w, h):
    o = Options()
    o.binary_location = FF
    o.add_argument("-headless")
    o.add_argument(f"--width={w}")
    o.add_argument(f"--height={h}")
    svc = Service(DRIVER) if os.path.exists(DRIVER) else Service()
    return webdriver.Firefox(options=o, service=svc)

results = []
for vname, w, h in VIEWPORTS:
    d = None
    try:
        d = new_driver(w, h)
        d.set_window_size(w, h)
        # 登录
        d.get(f"{BASE}/wp-login.php")
        d.find_element(By.ID, "user_login").send_keys("admin")
        d.find_element(By.ID, "user_pass").send_keys("Admin@2026")
        d.find_element(By.ID, "wp-submit").click()
        time.sleep(1.5)

        for pname, path in PAGES:
            d.get(BASE + path)
            time.sleep(1.2)
            info = d.execute_script("""
                const de = document.documentElement;
                const overflow = de.scrollWidth - de.clientWidth;
                const wide = [...document.querySelectorAll('body *')]
                    .filter(el => el.getBoundingClientRect().width > de.clientWidth + 4)
                    .slice(0, 5)
                    .map(el => el.tagName + (el.id ? '#' + el.id : ''));
                return {overflow: overflow, wide: wide, title: document.title};
            """)
            shot = os.path.join(OUT, f"ff-{vname}-{pname}.png")
            d.save_screenshot(shot)
            ok = info["overflow"] <= 4 and len(info["wide"]) == 0
            results.append({"browser": "Firefox", "viewport": vname, "page": pname,
                            "overflow_px": info["overflow"], "wide": info["wide"],
                            "title": info["title"], "pass": ok, "screenshot": shot})
            print(f"Firefox {vname:<13}{pname:<6} overflow={info['overflow']:>4}px 宽元素={len(info['wide'])}")
    except Exception as e:  # noqa: BLE001
        print("错误:", type(e).__name__, str(e)[:200])
    finally:
        if d:
            d.quit()

if results:
    ok = sum(1 for r in results if r["pass"])
    json.dump(results, open(os.path.join(OUT, "compat-firefox.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\nFirefox 合计 {len(results)} 组，通过 {ok} 组")
