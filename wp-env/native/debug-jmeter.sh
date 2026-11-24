#!/bin/bash
# JMeter 启动问题排查（全部加超时，避免挂死）
pkill -9 -f fix-jmeter-smoke 2>/dev/null
pkill -9 -f ApacheJMeter 2>/dev/null
sleep 1

echo "===== A. 直接 java -jar ====="
timeout 45 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
  -jar /opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar --version 2>&1 | tail -6
echo "rc=${PIPESTATUS[0]}"

echo
echo "===== B. 包装脚本 jmeter --version ====="
timeout 45 jmeter --version 2>&1 | tail -6
echo "rc=${PIPESTATUS[0]}"

echo
echo "===== C. jmeter -v（老写法）====="
timeout 45 /opt/apache-jmeter-5.6.3/bin/jmeter -v 2>&1 | tail -6
echo "rc=${PIPESTATUS[0]}"

echo
echo "===== D. 残留进程 ====="
ps -eo pid,etime,cmd | grep -E 'ApacheJMeter|jmeter' | grep -v grep | head -5 || echo none
