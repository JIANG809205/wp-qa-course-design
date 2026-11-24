#!/bin/bash
# 安装 Firefox + geckodriver（用于真正的跨浏览器测试）
set -u
echo "===== 1. geckodriver（apt 优先）====="
apt-cache policy firefox-geckodriver 2>/dev/null | head -4
if apt-get install -y -qq firefox-geckodriver >/tmp/gd.log 2>&1; then
  echo "apt 安装成功"; geckodriver --version | head -1
else
  echo "apt 失败，尝试 GitHub 直链"
  URL=$(curl -s -m 20 -L -o /dev/null -w '%{url_effective}' https://github.com/mozilla/geckodriver/releases/latest)
  VER=$(echo "$URL" | sed 's#.*/tag/v##')
  echo "最新版本: $VER"
  curl -fsSL -m 300 -o /tmp/gd.tar.gz \
    "https://github.com/mozilla/geckodriver/releases/download/v${VER}/geckodriver-v${VER}-linux64.tar.gz" \
    && tar xzf /tmp/gd.tar.gz -C /usr/local/bin && chmod +x /usr/local/bin/geckodriver \
    && geckodriver --version | head -1 || echo "geckodriver 安装失败"
fi

echo
echo "===== 2. Firefox ====="
if [ -x /opt/firefox/firefox ]; then
  echo "已存在: $(/opt/firefox/firefox --version 2>/dev/null)"
else
  curl -fsSL -m 600 -o /tmp/firefox.tar.xz \
    "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=zh-CN" \
    && tar xJf /tmp/firefox.tar.xz -C /opt \
    && echo "解压完成: $(/opt/firefox/firefox --version 2>/dev/null)" || echo "Firefox 下载失败"
fi

echo
echo "===== 3. 依赖库检查 ====="
ldd /opt/firefox/firefox 2>/dev/null | grep -c "not found" | xargs -I{} echo "缺失库数量: {}"
ldd /opt/firefox/firefox 2>/dev/null | grep "not found" | head -5
