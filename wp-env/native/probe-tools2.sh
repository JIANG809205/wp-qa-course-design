#!/bin/bash
# 第二轮探测：找 chromedriver / jmeter / node 的可用下载源
probe() {
  printf '%-70s ' "$1"
  code=$(curl -s -o /dev/null -m 10 -w '%{http_code}' "$1" 2>/dev/null)
  echo "HTTP $code"
}
probe "https://registry.npmmirror.com/-/binary/chromedriver/"
probe "https://registry.npmmirror.com/-/binary/chromedriver/131.0.6778.87/"
probe "https://mirrors.aliyun.com/apache/jmeter/binaries/"
probe "https://mirrors.tuna.tsinghua.edu.cn/apache/jmeter/binaries/"
probe "https://storage.googleapis.com/chrome-for-testing-public/"
probe "https://registry.npmmirror.com/-/binary/node/v18.20.4/node-v18.20.4-linux-x64.tar.xz"
probe "https://edu.postman.com/"
