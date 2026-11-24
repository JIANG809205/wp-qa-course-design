#!/bin/bash
# 收尾：链接 newman、解析 Maven 依赖、抓截图
set -u

echo "===== 1. newman 链接 ====="
ls /opt/node/bin | head -20
for b in newman newman-reporter-html; do
  if [ -e "/opt/node/bin/$b" ]; then
    ln -sf "/opt/node/bin/$b" "/usr/local/bin/$b"
  fi
done
echo "newman -> $(command -v newman || echo missing)"
newman --version 2>&1 | head -1

echo
echo "===== 2. Maven 依赖解析 ====="
cd /opt/qa/mvn-demo || exit 1
ls -l pom.xml
timeout 1200 mvn -B -q dependency:resolve >/tmp/mvn.log 2>&1
echo "rc=$?"
tail -5 /tmp/mvn.log
echo "--- 关键 jar ---"
ls -d ~/.m2/repository/org/testng/testng/* 2>/dev/null | head -1
ls -d ~/.m2/repository/org/seleniumhq/selenium/selenium-java/* 2>/dev/null | head -1
ls -d ~/.m2/repository/io/qameta/allure/allure-testng/* 2>/dev/null | head -1

echo
echo "===== 3. 截图 ====="
cd /opt/qa || exit 1
ls -1 *.py 2>/dev/null
timeout 180 /opt/qa-venv/bin/python shot.py 2>&1 | tail -6
ls -lh docker-*.png 2>/dev/null || echo "无截图"
