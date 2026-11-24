#!/bin/bash
# 下载并安装 Chrome、chromedriver、JMeter、Node 18
set -u
TMP=/tmp/dl
mkdir -p "$TMP"

echo "===== 1. Google Chrome ====="
if command -v google-chrome >/dev/null 2>&1; then
  echo "already installed: $(google-chrome --version)"
else
  if curl -fsSL -m 300 -o "$TMP/chrome.deb" "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"; then
    apt-get install -y "$TMP/chrome.deb" >/tmp/chrome-install.log 2>&1
    echo "install_exit=$?  $(google-chrome --version 2>&1)"
  else
    echo "DOWNLOAD_FAILED"
  fi
fi

echo
echo "===== 2. chromedriver（版本与 Chrome 主版本对齐）====="
CHROME_VER=$(google-chrome --version 2>/dev/null | grep -oE '[0-9]+' | head -1)
echo "chrome major = ${CHROME_VER:-unknown}"
if command -v chromedriver >/dev/null 2>&1; then
  echo "already installed: $(chromedriver --version)"
else
  BASE="https://registry.npmmirror.com/-/binary/chromedriver"
  # 列出可用版本，挑与本地 Chrome 主版本一致的最后一个
  curl -fsSL -m 60 "$BASE/" -o "$TMP/cd-index.json" || echo "index failed"
  TARGET=$(grep -oE '"name":"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/"' "$TMP/cd-index.json" 2>/dev/null \
           | sed 's/"name":"//; s|/"||' | grep "^${CHROME_VER}\." | sort -V | tail -1)
  echo "target = ${TARGET:-none}"
  if [ -n "${TARGET:-}" ]; then
    curl -fsSL -m 300 -o "$TMP/chromedriver.zip" "$BASE/$TARGET/chromedriver_linux64.zip" \
      && unzip -o -q "$TMP/chromedriver.zip" -d /usr/local/bin/ \
      && chmod +x /usr/local/bin/chromedriver \
      && echo "installed: $(chromedriver --version)"
  else
    echo "SKIP: 未找到匹配版本的 chromedriver"
  fi
fi

echo
echo "===== 3. Apache JMeter 5.6.3 ====="
if [ -d /opt/jmeter ]; then
  echo "already installed"
else
  JM="https://mirrors.aliyun.com/apache/jmeter/binaries/apache-jmeter-5.6.3.tgz"
  if curl -fsSL -m 600 -o "$TMP/jmeter.tgz" "$JM"; then
    tar xzf "$TMP/jmeter.tgz" -C /opt
    ln -sfn /opt/apache-jmeter-5.6.3 /opt/jmeter
    ln -sf /opt/jmeter/bin/jmeter /usr/local/bin/jmeter
    echo "installed: $(/opt/jmeter/bin/jmeter --version 2>&1 | head -3 | tr '\n' ' ')"
  else
    echo "DOWNLOAD_FAILED"
  fi
fi

echo
echo "===== 4. Node 18（供 newman 使用）====="
if command -v node >/dev/null 2>&1 && [ "$(node -v | grep -oE '[0-9]+' | head -1)" -ge 16 ]; then
  echo "node ok: $(node -v)"
else
  NV=v18.20.4
  if curl -fsSL -m 300 -o "$TMP/node.tar.xz" "https://registry.npmmirror.com/-/binary/node/${NV}/node-${NV}-linux-x64.tar.xz"; then
    tar xJf "$TMP/node.tar.xz" -C /opt
    ln -sfn /opt/node-${NV}-linux-x64 /opt/node
    ln -sf /opt/node/bin/node /usr/local/bin/node
    ln -sf /opt/node/bin/npm /usr/local/bin/npm
    ln -sf /opt/node/bin/npx /usr/local/bin/npx
    echo "installed: $(node -v) / npm $(npm -v)"
  else
    echo "DOWNLOAD_FAILED"
  fi
fi

echo
echo "===== 汇总 ====="
for c in google-chrome chromedriver java mvn jmeter node npm; do
  printf '%-14s ' "$c"
  command -v "$c" >/dev/null 2>&1 && echo "$(command -v $c)" || echo "MISSING"
done
