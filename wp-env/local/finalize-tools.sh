#!/bin/bash
# 补齐 newman、Maven 依赖，并抓取后台截图作为环境证据
set -u

echo "===== 1. newman ====="
export npm_config_registry=https://registry.npmmirror.com
timeout 420 npm install -g --silent newman newman-reporter-html 2>&1 | tail -3
echo "newman: $(newman --version 2>&1 | head -1)"

echo
echo "===== 2. Maven 依赖（TestNG + Selenium + Allure）====="
mkdir -p /opt/qa/mvn-demo
cd /opt/qa/mvn-demo || exit 1
timeout 900 mvn -B -q dependency:resolve 2>&1 | tail -6
echo "mvn_rc=$?"
ls -d ~/.m2/repository/org/testng/testng/* 2>/dev/null | head -2
ls -d ~/.m2/repository/org/seleniumhq/selenium/selenium-java/* 2>/dev/null | head -2

echo
echo "===== 3. 抓取后台截图 ====="
cd /opt/qa || exit 1
cat > shot.py <<'PY'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

o = Options()
for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1440,900", "--disable-gpu"):
    o.add_argument(a)
d = webdriver.Chrome(options=o)
try:
    d.get("http://localhost:8080/wp-login.php")
    d.find_element(By.ID, "user_login").send_keys("admin")
    d.find_element(By.ID, "user_pass").send_keys("Admin@2026")
    d.find_element(By.ID, "wp-submit").click()
    time.sleep(3)
    d.save_screenshot("/opt/qa/docker-admin.png")
    print("admin shot ok:", d.current_url)
    d.get("http://localhost:8080/")
    d.save_screenshot("/opt/qa/docker-front.png")
    print("front shot ok:", d.title)
finally:
    d.quit()
PY
timeout 180 /opt/qa-venv/bin/python shot.py 2>&1 | tail -5

SHOTS="/mnt/e/软件质量保证与测试课程设计/wp-env/screenshots"
mkdir -p "$SHOTS"
cp -f /opt/qa/docker-*.png "$SHOTS"/ 2>/dev/null && ls -lh "$SHOTS" || echo "copy failed"
