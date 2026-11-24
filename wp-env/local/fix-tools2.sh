#!/bin/bash
# 排查并修复：newman / Maven pom / 截图
set -u

echo "===== A. npm 状态 ====="
npm config get registry
npm root -g
ls -l "$(npm root -g)" 2>/dev/null | head -5
echo "--- 重新安装 newman（显示错误）---"
export npm_config_registry=https://registry.npmmirror.com
timeout 420 npm install -g newman 2>&1 | tail -12
echo "--- 结果 ---"
command -v newman && newman --version || echo "newman 仍未安装"

echo
echo "===== B. Maven 工程 ====="
ls -l /opt/qa/mvn-demo/ 2>&1 | head -5
if [ ! -f /opt/qa/mvn-demo/pom.xml ]; then
  echo "pom.xml 不存在，重新生成"
  mkdir -p /opt/qa/mvn-demo
  cat > /opt/qa/mvn-demo/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>edu.qa</groupId>
  <artifactId>wp-autotest</artifactId>
  <version>1.0</version>
  <properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <dependency><groupId>org.seleniumhq.selenium</groupId><artifactId>selenium-java</artifactId><version>4.27.0</version></dependency>
    <dependency><groupId>org.testng</groupId><artifactId>testng</artifactId><version>7.10.2</version><scope>test</scope></dependency>
    <dependency><groupId>io.qameta.allure</groupId><artifactId>allure-testng</artifactId><version>2.29.0</version><scope>test</scope></dependency>
  </dependencies>
</project>
XML
fi
cd /opt/qa/mvn-demo || exit 1
echo "--- 解析依赖 ---"
timeout 900 mvn -B dependency:resolve 2>&1 | tail -8
echo "--- 本地仓库 ---"
ls -d ~/.m2/repository/org/testng/testng/* 2>/dev/null | head -1
ls -d ~/.m2/repository/org/seleniumhq/selenium/selenium-java/* 2>/dev/null | head -1

echo
echo "===== C. 截图 ====="
ls -lh /opt/qa/*.png 2>/dev/null || echo "无截图"
cd /opt/qa || exit 1
timeout 180 /opt/qa-venv/bin/python shot.py 2>&1 | tail -8
ls -lh /opt/qa/*.png 2>/dev/null
