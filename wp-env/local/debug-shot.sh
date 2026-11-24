#!/bin/bash
# 直接调试截图脚本（不吞输出）
set -u
cd /opt/qa || exit 1

echo "===== chrome 检查 ====="
google-chrome --version
echo "===== 站点检查 ====="
curl -s -o /dev/null -w "http=%{http_code}\n" http://localhost:8080/

echo "===== 运行 shot.py ====="
timeout 150 /opt/qa-venv/bin/python -u shot.py 2>&1
echo "rc=$?"

echo "===== 结果文件 ====="
ls -lh /opt/qa/*.png 2>/dev/null || echo "无 png"
