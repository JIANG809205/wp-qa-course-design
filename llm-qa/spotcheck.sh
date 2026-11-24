#!/bin/bash
# 抽查 Qwen 与 Flash 生成的脚本，确认 0% 结构可运行的原因
echo "===== Qwen 样本 ====="
f=$(ls /opt/qa/s96-qwen-plus/java/*.java | head -1)
echo "文件: $(basename "$f")"
head -15 "$f"
echo "--- 统计 ---"
echo "class 出现次数: $(grep -c 'class ' "$f" || true)"
echo "URL: $(grep -oE 'localhost:8080|example\.com|https?://[a-zA-Z0-9.:-]+' "$f" | sort -u | tr '\n' ' ')"
echo
echo "===== Flash 样本（结构可运行的）====="
g=$(ls /opt/qa/s96-deepseek-v4.1-flash/java/*.java | head -1)
echo "文件: $(basename "$g")"
head -15 "$g"
