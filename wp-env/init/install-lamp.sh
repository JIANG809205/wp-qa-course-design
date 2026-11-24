#!/bin/bash
# 在 WSL Ubuntu 22.04 中安装 LAMP（Apache + PHP 8.1 + MariaDB）
set -u
export DEBIAN_FRONTEND=noninteractive

apt-get install -y \
  apache2 mariadb-server \
  php8.1 php8.1-mysql php8.1-xml php8.1-mbstring php8.1-curl \
  php8.1-gd php8.1-zip php8.1-intl libapache2-mod-php8.1 \
  wget unzip curl >/tmp/lamp.log 2>&1

code=$?
echo "APT_EXIT=$code"
grep -E '^E:' /tmp/lamp.log | tail -3
echo '----- versions -----'
php -v 2>/dev/null | head -1
apache2 -v 2>/dev/null | head -1
mariadbd --version 2>/dev/null | head -1 || mysqld --version 2>/dev/null | head -1
tail -2 /tmp/lamp.log
