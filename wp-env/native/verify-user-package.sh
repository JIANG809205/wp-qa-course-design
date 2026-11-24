#!/bin/bash
# 校验用户下载的官方包：大小、哈希，并与官方校验和接口核对
set -u
ZIP="/mnt/d/迅雷下载/wordpress-7.1.5.zip"

if [ ! -f "$ZIP" ]; then
  echo "文件不存在: $ZIP"
  ls -l /mnt/d/ 2>/dev/null | head
  exit 1
fi

echo "===== 1. 文件信息 ====="
ls -lh "$ZIP"
echo "MD5 : $(md5sum "$ZIP" | awk '{print $1}')"
echo "SHA1: $(sha1sum "$ZIP" | awk '{print $1}')"

echo
echo "===== 2. 解压并核对版本 ====="
rm -rf /tmp/wpuser && mkdir -p /tmp/wpuser
unzip -q "$ZIP" -d /tmp/wpuser
grep -E "wp_version =|wp_db_version" /tmp/wpuser/wordpress/wp-includes/version.php | head -2
echo "文件数: $(find /tmp/wpuser/wordpress -type f | wc -l)"

echo
echo "===== 3. 与官方校验和接口比对 ====="
curl -s -m 60 "https://api.wordpress.org/core/checksums/1.0/?version=7.1.5&locale=en_US" -o /tmp/sums.json
python3 - <<'PY'
import hashlib, json, os

base = "/tmp/wpuser/wordpress"
try:
    data = json.load(open("/tmp/sums.json"))
    sums = data.get("checksums", {})
except Exception as e:
    print("  校验和接口解析失败:", e); raise SystemExit

if not sums:
    print("  接口未返回校验和（可能版本字段不对）")
    raise SystemExit

sample = [k for k in sums if k.startswith(("wp-login.php", "wp-settings.php", "wp-admin/admin.php", "wp-includes/version.php"))]
ok = bad = miss = 0
for rel in sample[:12]:
    p = os.path.join(base, rel)
    if not os.path.isfile(p):
        miss += 1; continue
    md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    if md5 == sums[rel]:
        ok += 1
    else:
        bad += 1
        print(f"  不一致: {rel}")
print(f"  抽样比对 {len(sample[:12])} 个文件：一致 {ok}，不一致 {bad}，缺失 {miss}")
print(f"  校验和条目总数: {len(sums)}")
PY

echo
echo "===== 4. 与官方 tar.gz 的核心文件比对 ====="
for f in wp-login.php wp-settings.php wp-admin/admin.php wp-includes/version.php; do
  a=$(md5sum "/tmp/wp-official/wordpress/$f" 2>/dev/null | awk '{print $1}')
  b=$(md5sum "/tmp/wpuser/wordpress/$f" 2>/dev/null | awk '{print $1}')
  [ "$a" = "$b" ] && s="一致" || s="不同"
  printf '  %-30s %s\n' "$f" "$s"
done
