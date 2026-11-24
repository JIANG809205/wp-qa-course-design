#!/bin/bash
# 探测各软件源可达性与候选包可用性
echo "===== 网络探测 ====="
probe() {
  printf '%-52s ' "$1"
  code=$(curl -s -o /dev/null -m 10 -w '%{http_code}' "$1" 2>/dev/null)
  echo "HTTP $code"
}
probe "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
probe "https://registry.npmmirror.com/"
probe "https://maven.aliyun.com/repository/public/"
probe "https://github.com/"
probe "https://raw.githubusercontent.com/"
probe "https://archive.apache.org/dist/jmeter/binaries/"
probe "https://pypi.tuna.tsinghua.edu.cn/simple/"

echo
echo "===== apt 候选包 ====="
for p in openjdk-17-jdk maven jmeter python3-pip nikto sqlmap chromium-browser firefox nodejs npm jq unzip; do
  printf '%-22s ' "$p"
  if apt-cache policy "$p" 2>/dev/null | grep -q 'Candidate: (none)'; then
    echo "不可用"
  else
    apt-cache policy "$p" 2>/dev/null | awk '/Candidate:/{print $2}' | head -1
  fi
done
