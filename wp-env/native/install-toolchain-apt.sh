#!/bin/bash
# 安装测试工具链基础组件（apt 部分）
set -u
export DEBIAN_FRONTEND=noninteractive

apt-get install -y \
  openjdk-17-jdk maven jq unzip zip \
  python3-pip python3-venv python3-dev \
  nikto sqlmap \
  fonts-liberation fonts-noto-cjk \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
  libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 \
  >/tmp/tools-apt.log 2>&1
echo "APT_EXIT=$?"
grep -E '^E:' /tmp/tools-apt.log | tail -3
echo "--- versions ---"
java -version 2>&1 | head -1
mvn -v 2>&1 | head -1
python3 --version
pip3 --version 2>/dev/null | head -1
nikto -Version 2>/dev/null | head -2 | tail -1
sqlmap --version 2>/dev/null | head -1
