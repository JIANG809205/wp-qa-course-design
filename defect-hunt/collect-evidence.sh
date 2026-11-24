#!/bin/bash
# 收集缺陷复现证据：响应码、响应头、页面截图
set -u
BASE="http://localhost:8080"
DIR="/mnt/e/软件质量保证与测试课程设计/defect-hunt/evidence"
mkdir -p "$DIR"

echo "===== 1. 响应码 ====="
probe() {
  code=$(curl -sL -o /dev/null -w '%{http_code}' -m 10 "$BASE$1")
  size=$(curl -sL -m 10 "$BASE$1" | wc -c)
  printf '%-32s HTTP %s  %s 字节\n' "$1" "$code" "$size"
  echo "$1,HTTP $code,$size" >> "$DIR/status.csv"
}
: > "$DIR/status.csv"
echo "path,status,bytes" > "$DIR/status.csv"
probe "/wp-content/debug.log"
probe "/wp-content/uploads/"
probe "/xmlrpc.php"
probe "/?author=1"
probe "/readme.html"
probe "/wp-json/wp/v2/users"

echo
echo "===== 2. 安全响应头（D-05）====="
curl -sI -m 10 "$BASE/" | tr -d '\r' > "$DIR/headers.txt"
grep -iE "^(HTTP|server|x-|content-type|referrer|permissions)" "$DIR/headers.txt" || echo "（无安全头）"

echo
echo "===== 3. debug.log 内容前 5 行（DEF-002）====="
curl -sL -m 10 "$BASE/wp-content/debug.log" | head -5 | tee "$DIR/debug-log-head.txt"

echo
echo "===== 4. 用户枚举（DEF-012）====="
for id in 1 2 3; do
  loc=$(curl -s -o /dev/null -m 10 -w '%{redirect_url}' "$BASE/?author=$id")
  echo "  ?author=$id -> ${loc:-无跳转}" | tee -a "$DIR/authors.txt"
done

echo
echo "===== 5. 截图 ====="
cd /opt/qa || exit 1
for pair in "debug-log:$BASE/wp-content/debug.log" "uploads-index:$BASE/wp-content/uploads/"; do
  name=${pair%%:*}; url=${pair#*:}
  /opt/qa-venv/bin/python -u shot-url.py "$url" "$DIR/$name.png" 2>&1 | tail -1
done
ls -1 "$DIR" | sed 's/^/  /'
