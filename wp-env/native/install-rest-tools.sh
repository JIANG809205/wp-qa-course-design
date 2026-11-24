#!/bin/bash
# 安装剩余工具：newman、pytest-html、配置 Maven 阿里云镜像并验证依赖解析
set -u

echo "===== 1. 保存 Selenium 截图到工作区 ====="
SHOT_DIR="/mnt/e/软件质量保证与测试课程设计/wp-env/native/screenshots"
mkdir -p "$SHOT_DIR"
cp -f /opt/qa/*.png "$SHOT_DIR"/ 2>/dev/null && ls -lh "$SHOT_DIR" || echo "copy failed"

echo
echo "===== 2. npm 源 + newman ====="
npm config set registry https://registry.npmmirror.com
npm config get registry
timeout 300 npm install -g --silent newman newman-reporter-html 2>&1 | tail -3
echo "newman: $(newman --version 2>&1 | head -1)"

echo
echo "===== 3. pytest-html ====="
/opt/qa-venv/bin/pip install -q pytest-html -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1 | tail -2
/opt/qa-venv/bin/pip list 2>/dev/null | grep -iE '^(selenium|pytest|pytest-html|requests|openai|faker) '

echo
echo "===== 4. Maven 阿里云镜像 ====="
mkdir -p ~/.m2
cat > ~/.m2/settings.xml <<'XML'
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0">
  <mirrors>
    <mirror>
      <id>aliyun</id>
      <mirrorOf>central</mirrorOf>
      <name>Aliyun Central</name>
      <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
  </mirrors>
</settings>
XML
echo "settings.xml 已写入"

echo
echo "===== 5. 验证 Maven 依赖解析（TestNG + Selenium）====="
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
    <dependency><groupId>io.github.bonigarcia</groupId><artifactId>webdrivermanager</artifactId><version>5.9.2</version><scope>test</scope></dependency>
  </dependencies>
</project>
XML
cd /opt/qa/mvn-demo || exit 1
timeout 600 mvn -q -B dependency:resolve 2>&1 | tail -8
echo "mvn_rc=$?"
ls ~/.m2/repository/org/testng 2>/dev/null && echo "TestNG 已下载" || echo "TestNG 未下载"
