#!/bin/bash
# 修复 JMeter（中文路径 + locale）并做 Selenium 冒烟测试
set -u

echo "===== 1. 安装 jmeter 包装脚本（固定 UTF-8 且脱离中文路径）====="
cat > /usr/local/bin/jmeter <<'EOF'
#!/bin/sh
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export JMETER_HOME=/opt/apache-jmeter-5.6.3
cd /opt || exit 1
exec /opt/apache-jmeter-5.6.3/bin/jmeter "$@"
EOF
chmod +x /usr/local/bin/jmeter
echo "wrapper -> $(head -1 /usr/local/bin/jmeter)"
echo "--- 版本 ---"
jmeter --version 2>&1 | grep -E '5\.6\.3|version' | head -2

echo
echo "===== 2. Java 路径编码 ====="
LANG=C.UTF-8 LC_ALL=C.UTF-8 java -XshowSettings:properties -version 2>&1 | grep -E 'sun.jnu.encoding|file.encoding'

echo
echo "===== 3. Selenium 冒烟测试（headless Chrome 打开 WordPress）====="
mkdir -p /opt/qa && cd /opt/qa
cat > smoke.py <<'PY'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1366,768")

driver = webdriver.Chrome(options=opts)
try:
    driver.get("http://localhost:8080/")
    print("title  :", driver.title)
    print("url    :", driver.current_url)
    print("h1     :", driver.find_element(By.TAG_NAME, "h1").text[:60])
    driver.get("http://localhost:8080/wp-login.php")
    driver.find_element(By.ID, "user_login").send_keys("admin")
    driver.find_element(By.ID, "user_pass").send_keys("Admin@2026")
    driver.find_element(By.ID, "wp-submit").click()
    driver.implicitly_wait(5)
    ok = "wp-admin" in driver.current_url or driver.find_elements(By.ID, "wpadminbar")
    print("login  :", "OK" if ok else "FAILED", driver.current_url)
    driver.save_screenshot("/opt/qa/smoke.png")
    print("shot   : /opt/qa/smoke.png")
finally:
    driver.quit()
PY
/opt/qa-venv/bin/python smoke.py 2>&1 | tail -15
echo "--- 截图 ---"
ls -lh /opt/qa/smoke.png 2>/dev/null || echo "no screenshot"
