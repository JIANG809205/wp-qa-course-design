#!/bin/bash
# 跑接口/功能自动化用例，并把结果回填 Excel
set -u
APP="/mnt/e/软件质量保证与测试课程设计/wp-env"
DIR="/mnt/e/软件质量保证与测试课程设计/wp-api-tests"

echo "===== 1. 环境 ====="
if ! docker info >/dev/null 2>&1; then
  pkill -9 dockerd 2>/dev/null; sleep 2; rm -f /var/run/docker.pid
  nohup setsid dockerd >/var/log/dockerd.log 2>&1 &
  for i in $(seq 1 20); do sleep 2; docker info >/dev/null 2>&1 && break; done
fi
cd "$APP/local" && docker compose -f docker-compose.local.yml up -d 2>&1 | tail -2
code=000
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/ 2>/dev/null)
  [ "$code" != "000" ] && break
  sleep 2
done
echo "站点: $code"

echo
echo "===== 2. 准备各角色应用密码 ====="
bash "$DIR/setup-all-auth.sh" 2>&1 | tail -8

echo
echo "===== 3. 执行用例 ====="
cd "$DIR" || exit 1
WP_BASE=http://localhost:8080 /opt/qa-venv/bin/python -m pytest test_cases.py -q \
  --no-header -p no:cacheprovider 2>&1 | tail -30

echo
echo "===== 4. 结果汇总 ====="
/opt/qa-venv/bin/python - <<'PY'
import json, os
p = "/mnt/e/软件质量保证与测试课程设计/wp-api-tests/results.json"
rs = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
print(f"共 {len(rs)} 条：通过 {sum(1 for r in rs if r['outcome']=='passed')}，"
      f"失败 {sum(1 for r in rs if r['outcome']=='failed')}")
for r in rs:
    if r["outcome"] == "failed":
        print(f"  [FAIL] {r['case'] or r['nodeid']}")
PY
