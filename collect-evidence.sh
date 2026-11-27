#!/bin/bash
# 采集测试执行的控制台证据（供报告截图）
set -u
ROOT="/mnt/e/软件质量保证与测试课程设计"
OUT="$ROOT/evidence"
mkdir -p "$OUT"

reset_throttle() {
  docker exec wp-app wp transient delete --all --allow-root >/dev/null 2>&1
}

echo "===== 1. TestNG ====="
reset_throttle
cd "$ROOT/wp-autotest" || exit 1
mvn -q test -DbaseUrl=http://localhost:8080 > "$OUT/mvn-test.log" 2>&1
tail -12 "$OUT/mvn-test.log"

echo "===== 2. pytest ====="
reset_throttle
cd "$ROOT/wp-api-tests" || exit 1
bash setup-all-auth.sh >/dev/null 2>&1
WP_BASE=http://localhost:8080 /opt/qa-venv/bin/python -m pytest -q > "$OUT/pytest.log" 2>&1
tail -6 "$OUT/pytest.log"

echo "===== 3. 权限矩阵摘要 ====="
reset_throttle
cd "$ROOT/defect-hunt" || exit 1
/opt/qa-venv/bin/python permission_matrix.py > "$OUT/matrix.log" 2>&1
tail -8 "$OUT/matrix.log"

echo "===== 4. 修复前后探针对照 ====="
cd "$ROOT/hardening" || exit 1
/opt/qa-venv/bin/python - <<'PY' > "$OUT/probe-compare.log" 2>&1
import json
b=json.load(open('before.json')); a=json.load(open('after.json'))
print(f"{'编号':<5}{'探针':<18}{'修复前':<8}{'修复后':<8}证据(修复前 → 修复后)")
for x,y in zip(b['items'],a['items']):
    print(f"{x['id']:<5}{x['name']:<16}{'命中' if x['hit'] else '未命中':<8}"
          f"{'命中' if y['hit'] else '未命中':<8}{x['evidence'][:34]} → {y['evidence'][:34]}")
print(f"\n命中数：{b['hits']}/{b['total']} → {a['hits']}/{a['total']}")
PY
cat "$OUT/probe-compare.log"
