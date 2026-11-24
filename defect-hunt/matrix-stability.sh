#!/bin/bash
# 权限矩阵稳定性验证：连跑 3 次，比较 30 格结论是否一致
set -u
DIR="/mnt/e/软件质量保证与测试课程设计/defect-hunt"
OUT="$DIR/matrix-reps"
mkdir -p "$OUT"

for rep in 1 2 3; do
  echo "===== 第 $rep 次 ====="
  cd "$DIR" || exit 1
  /opt/qa-venv/bin/python permission_matrix.py 2>&1 | tail -3
  cp -f "$DIR/permission-matrix-v2.json" "$OUT/rep$rep.json" 2>/dev/null
  # 每次跑完清场，避免污染
  docker cp "$DIR/cleanup.php" wp-app:/tmp/cleanup.php >/dev/null 2>&1
  docker exec wp-app php /tmp/cleanup.php >/dev/null 2>&1
done

echo
echo "===== 三次结果一致性 ====="
/opt/qa-venv/bin/python - <<'PY'
import json, os
d = "/mnt/e/软件质量保证与测试课程设计/defect-hunt/matrix-reps"
reps = []
for i in (1, 2, 3):
    p = os.path.join(d, f"rep{i}.json")
    if os.path.exists(p):
        reps.append(json.load(open(p, encoding="utf-8")))
print(f"读取 {len(reps)} 次结果，每次 {len(reps[0])} 格")
diff = 0
for idx in range(len(reps[0])):
    vals = {json.dumps(r[idx]["api"]) for r in reps}
    if len(vals) > 1:
        diff += 1
        print(f"  不稳定: {reps[0][idx]['role']} {reps[0][idx]['op']} -> {vals}")
print(f"结论不一致格数: {diff} / {len(reps[0])}")
PY
