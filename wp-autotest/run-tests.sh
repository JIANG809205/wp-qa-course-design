#!/bin/bash
# 运行 Selenium + TestNG 自动化测试，并把报告与截图带回工作区
set -u
SRC="/mnt/e/软件质量保证与测试课程设计/wp-autotest"
DST=/opt/qa/wp-autotest
OUT="/mnt/e/软件质量保证与测试课程设计/wp-autotest/result"

echo "===== 1. 确认站点可用 ====="
code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8080/ || echo 000)
echo "首页 HTTP=$code"
if [ "$code" != "200" ]; then
  echo "站点不可用，尝试拉起容器栈..."
  bash "/mnt/e/软件质量保证与测试课程设计/wp-env/local/stack.sh" start
fi

echo
echo "===== 2. 同步工程到 ASCII 路径（规避 Java 中文路径问题）====="
rm -rf "$DST"
mkdir -p "$DST"
cp -r "$SRC"/. "$DST"/
rm -rf "$DST/result"
ls "$DST"

echo
echo "===== 3. 执行测试 ====="
cd "$DST" || exit 1
timeout 1800 mvn -B test >/tmp/mvn-test.log 2>&1
rc=$?
echo "mvn rc=$rc"
grep -E "Tests run:|BUILD|ERROR.*Test" /tmp/mvn-test.log | tail -12

echo
echo "===== 4. 汇总 ====="
python3 - <<'PY'
import glob, xml.etree.ElementTree as ET
t=f=e=s=0
for p in glob.glob('/opt/qa/wp-autotest/target/surefire-reports/*.xml'):
    r=ET.parse(p).getroot()
    t+=int(r.get('tests',0)); f+=int(r.get('failures',0)); e+=int(r.get('errors',0)); s+=int(r.get('skipped',0))
print(f"用例总数={t} 通过={t-f-e-s} 失败={f} 错误={e} 跳过={s}")
PY

echo
echo "===== 5. 回传结果 ====="
mkdir -p "$OUT"
cp -r "$DST/target/surefire-reports" "$OUT"/ 2>/dev/null
cp -r "$DST/target/screenshots" "$OUT"/ 2>/dev/null || echo "无失败截图"
cp /tmp/mvn-test.log "$OUT"/build.log 2>/dev/null
ls -R "$OUT" | head -30
