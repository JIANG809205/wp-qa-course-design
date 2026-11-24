#!/bin/bash
# 诊断 JMeter，并寻找可用的浏览器下载源
echo "===== JMeter 诊断 ====="
echo "link: $(readlink -f /usr/local/bin/jmeter)"
/opt/apache-jmeter-5.6.3/bin/jmeter --version 2>&1 | head -6
echo "--- 直接用 java 启动 ---"
java -jar /opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar --version 2>&1 | head -6

echo
echo "===== 浏览器下载源探测（只取前 1KB 验证连通）====="
try() {
  printf '%-88s ' "$1"
  code=$(curl -s -o /dev/null -m 20 -r 0-1023 -w '%{http_code}' "$1" 2>/dev/null)
  echo "HTTP $code"
}
try "https://storage.googleapis.com/chrome-for-testing-public/known-good-versions-with-downloads.json"
try "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.87/linux64/chrome-linux64.zip"
try "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.87/linux64/chromedriver-linux64.zip"
try "https://cdn.playwright.dev/dbazure/download/playwright/builds/chromium/1148/chromium-linux.zip"
try "https://registry.npmmirror.com/-/binary/chrome-for-testing/131.0.6778.87/linux64/chrome-linux64.zip"

echo
echo "===== 下载重试：Chrome deb（断点续传）====="
mkdir -p /tmp/dl
if curl -fSL -C - -m 240 --retry 2 -o /tmp/dl/chrome.deb \
   "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"; then
  ls -lh /tmp/dl/chrome.deb
  echo "OK"
else
  echo "FAILED (exit=$?) size=$(stat -c%s /tmp/dl/chrome.deb 2>/dev/null || echo 0)"
fi
