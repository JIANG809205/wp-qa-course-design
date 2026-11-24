#!/bin/bash
# Selenium + headless Chrome 冒烟测试
set -u
mkdir -p /opt/qa && cd /opt/qa || exit 1

cat > smoke.py <<'PY'
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1366,768")
opts.add_argument("--disable-gpu")

print("启动 Chrome ...", flush=True)
driver = webdriver.Chrome(options=opts)
print("浏览器版本:", driver.capabilities.get("browserVersion"), flush=True)
try:
    driver.get("http://localhost:8080/")
    print("首页标题:", driver.title, flush=True)
    print("H1:", driver.find_element(By.TAG_NAME, "h1").text[:50], flush=True)

    driver.get("http://localhost:8080/wp-login.php")
    driver.find_element(By.ID, "user_login").send_keys("admin")
    driver.find_element(By.ID, "user_pass").send_keys("Admin@2026")
    driver.find_element(By.ID, "wp-submit").click()
    import time; time.sleep(3)
    ok = "wp-admin" in driver.current_url
    print("后台登录:", "OK" if ok else "FAILED", driver.current_url, flush=True)

    driver.save_screenshot("/opt/qa/smoke-admin.png")
    driver.get("http://localhost:8080/")
    driver.save_screenshot("/opt/qa/smoke-front.png")
    print("截图已保存", flush=True)
finally:
    driver.quit()
PY

echo "===== 执行 ====="
timeout 240 /opt/qa-venv/bin/python smoke.py 2>&1 | tail -20
echo "rc=$?"
ls -lh /opt/qa/*.png 2>/dev/null || echo "no screenshot"
