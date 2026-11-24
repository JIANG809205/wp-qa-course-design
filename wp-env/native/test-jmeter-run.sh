#!/bin/bash
# 用非 GUI 模式验证 JMeter 可用（必须在 ASCII 路径下运行）
set -u
rm -f /usr/local/bin/jmeter
ln -sf /opt/apache-jmeter-5.6.3/bin/jmeter /usr/local/bin/jmeter

mkdir -p /opt/qa
cp "/mnt/e/软件质量保证与测试课程设计/wp-env/native/jmeter/smoke-test.jmx" /opt/qa/smoke-test.jmx 2>/dev/null || echo "COPY_FAILED"

cd /opt
echo "===== 非 GUI 压测（10 线程 × 5 次）====="
timeout 180 java -Djmeter.home=/opt/apache-jmeter-5.6.3 \
  -jar /opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar \
  -n -t /opt/qa/smoke-test.jmx -l /opt/qa/smoke.jtl 2>&1 | tail -12
echo "rc=$?"
echo "--- 结果采样数 ---"
wc -l < /opt/qa/smoke.jtl 2>/dev/null || echo "no jtl"
