#!/bin/bash
# 编译校验：把三个模型生成的 Java 类用 javac 真编译，统计通过率与错误类型
set -u
BASE="/mnt/e/软件质量保证与测试课程设计/llm-qa"
OUT="$BASE/outputs"
WORK=/opt/qa/javac-check
CP_FILE=/tmp/cp.txt

echo "===== 1. 构建 classpath ====="
cd /opt/qa/mvn-demo || exit 1
if [ ! -s "$CP_FILE" ]; then
  timeout 300 mvn -q dependency:build-classpath -Dmdep.outputFile="$CP_FILE" >/tmp/cpbuild.log 2>&1
fi
if [ -s "$CP_FILE" ]; then
  echo "classpath 长度: $(wc -c < "$CP_FILE") 字节"
else
  echo "classpath 构建失败"; tail -3 /tmp/cpbuild.log; exit 1
fi

rm -rf "$WORK"; mkdir -p "$WORK"

total=0; ok=0
declare -A okByModel
report="$BASE/outputs/compile-result.md"

echo "# Java 编译校验结果" > "$report"
echo "" >> "$report"
echo "| 模型 | 文件数 | 编译通过 | 通过率 |" >> "$report"
echo "|---|---|---|---|" >> "$report"

echo
echo "===== 2. 逐文件编译 ====="
for d in "$OUT"/cmp-*; do
  model=$(basename "$d" | sed 's/^cmp-//')
  m_total=0; m_ok=0
  for f in "$d"/scripts/*.java; do
    [ -e "$f" ] || continue
    m_total=$((m_total + 1)); total=$((total + 1))

    # 提取 public class 名，重命名后再编译（否则文件名与类名不匹配）
    cls=$(grep -oE 'public class [A-Za-z0-9_]+' "$f" | head -1 | awk '{print $3}')
    [ -z "$cls" ] && cls="Generated$m_total"
    dir="$WORK/$model"; mkdir -p "$dir"
    cp "$f" "$dir/$cls.java"

    if javac -encoding UTF-8 -nowarn -cp "$(cat "$CP_FILE")" -d "$dir/out" "$dir/$cls.java" >/tmp/javac.log 2>&1; then
      m_ok=$((m_ok + 1)); ok=$((ok + 1))
    else
      echo "  [FAIL] $model/$(basename "$f")"
      grep -E "error:" /tmp/javac.log | head -2 | sed 's/^/        /'
    fi
  done
  okByModel["$model"]=$m_ok
  rate=$(awk "BEGIN{printf \"%.1f\", ($m_total>0? $m_ok/$m_total*100 : 0)}")
  printf '  %-26s %d/%d  (%s%%)\n' "$model" "$m_ok" "$m_total" "$rate"
  echo "| $model | $m_total | $m_ok | $rate% |" >> "$report"
done

echo "" >> "$report"
echo "合计：$ok/$total 通过（$(awk "BEGIN{printf \"%.1f\", ($total>0? $ok/$total*100 : 0)}")）" >> "$report"

echo
echo "===== 3. 汇总 ====="
echo "总计 $ok/$total 通过"
echo "结果写入 $report"
