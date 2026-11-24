#!/bin/bash
# 抓取 JMeter 完整错误栈 + 安装 Python 测试依赖
set -u

echo "===== JMeter 完整错误 ====="
java -jar /opt/apache-jmeter-5.6.3/bin/ApacheJMeter.jar --version 2>&1 | head -30
echo
echo "===== 试试指定 jmeter.home 与日志路径 ====="
cd /opt/apache-jmeter-5.6.3
JMETER_HOME=/opt/apache-jmeter-5.6.3 ./bin/jmeter --version 2>&1 | head -12

echo
echo "===== Python 测试依赖 ====="
python3 -m venv /opt/qa-venv >/dev/null 2>&1 || true
/opt/qa-venv/bin/pip install -q --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1 | tail -2
/opt/qa-venv/bin/pip install -q \
  selenium pytest pytest-html requests openai faker \
  -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1 | tail -3
echo "--- 版本 ---"
/opt/qa-venv/bin/python -c "import selenium, pytest, requests; print('selenium', selenium.__version__); print('pytest', pytest.__version__); print('requests', requests.__version__)"
/opt/qa-venv/bin/python -c "import openai; print('openai', openai.__version__)" 2>/dev/null || echo "openai 未安装"
