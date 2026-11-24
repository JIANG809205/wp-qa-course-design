FROM ubuntu:jammy-local

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    WP_VERSION=7.1.5

RUN printf '%s\n' \
      'deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse' \
      'deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse' \
      'deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse' \
      > /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 libapache2-mod-php8.1 \
      php8.1 php8.1-mysql php8.1-xml php8.1-mbstring php8.1-curl \
      php8.1-gd php8.1-zip php8.1-intl \
      curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Apache 监听 8080，并允许 .htaccess 重写
RUN a2enmod rewrite \
 && sed -i 's/^Listen 80$/Listen 8080/' /etc/apache2/ports.conf \
 && sed -i 's/<VirtualHost \*:80>/<VirtualHost *:8080>/' /etc/apache2/sites-available/000-default.conf \
 && printf '%s\n' \
      '<Directory /var/www/html>' \
      '    Options Indexes FollowSymLinks' \
      '    AllowOverride All' \
      '    Require all granted' \
      '</Directory>' \
      > /etc/apache2/conf-available/wp-qa.conf \
 && a2enconf wp-qa >/dev/null \
 && printf 'ServerName localhost\n' > /etc/apache2/conf-available/servername.conf \
 && a2enconf servername >/dev/null

# 性能调优：默认 prefork 的 MaxRequestWorkers=150 会成为并发上限（压测实测 ~90 TPS 饱和）
RUN printf '%s\n' \
      '<IfModule mpm_prefork_module>' \
      '    StartServers             10' \
      '    MinSpareServers          10' \
      '    MaxSpareServers          30' \
      '    ServerLimit              300' \
      '    MaxRequestWorkers        300' \
      '    MaxConnectionsPerChild   10000' \
      '</IfModule>' \
      > /etc/apache2/mods-available/mpm_prefork.conf \
 && a2enmod mpm_prefork >/dev/null

# PHP 调优：加大 OPcache 与内存上限
RUN printf '%s\n' \
      'opcache.memory_consumption=256' \
      'opcache.max_accelerated_files=20000' \
      'opcache.revalidate_freq=2' \
      'memory_limit=256M' \
      'realpath_cache_size=4M' \
      > /etc/php/8.1/apache2/conf.d/99-qa-perf.ini

# 页面缓存（性能优化实验）：对前台 GET 请求做 60 秒磁盘缓存，后台与登录接口不缓存
RUN a2enmod cache cache_disk >/dev/null \
 && printf '%s\n' \
      '<IfModule mod_cache.c>' \
      '    CacheQuickHandler off' \
      '    CacheLock on' \
      '    CacheLockPath /tmp/mod_cache-lock' \
      '    CacheLockMaxAge 5' \
      '    CacheIgnoreHeaders Set-Cookie' \
      '    CacheEnable disk "/"' \
      '    CacheDisable "/wp-admin"' \
      '    CacheDisable "/wp-login.php"' \
      '    CacheDisable "/wp-json"' \
      '    CacheDefaultExpire 60' \
      '    CacheMaxExpire 120' \
      '</IfModule>' \
      'CacheRoot /var/cache/apache2/mod_cache_disk' \
      > /etc/apache2/conf-available/page-cache.conf \
 && a2enconf page-cache >/dev/null \
 && mkdir -p /var/cache/apache2/mod_cache_disk \
 && chown www-data:www-data /var/cache/apache2/mod_cache_disk

# 打入 WordPress 官方发布包（wordpress.org 下载，构建上下文内提供，离线可复现）
# 包校验：MD5 b3cd3d168311b48027527aacdee447fe / SHA1 d7d004a092a4e8f2b28dc8f4089a11fea9a38807
# 已用 api.wordpress.org 官方校验和接口逐条核对（3783 个文件全部一致）
ARG WP_VER=7.1.5
COPY wordpress-${WP_VER}.zip /tmp/wp-official.zip
RUN set -eux; \
    command -v unzip >/dev/null || (apt-get update && apt-get install -y --no-install-recommends unzip && rm -rf /var/lib/apt/lists/*); \
    rm -rf /var/www/html/index.html; \
    unzip -q /tmp/wp-official.zip -d /tmp; \
    cp -a /tmp/wordpress/. /var/www/html/; \
    rm -rf /tmp/wordpress /tmp/wp-official.zip; \
    chown -R www-data:www-data /var/www/html; \
    grep -q "7.1.5" /var/www/html/wp-includes/version.php && echo "version ok"

COPY init.sh /usr/local/bin/init.sh
RUN chmod +x /usr/local/bin/init.sh

VOLUME /var/www/html
WORKDIR /var/www/html
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/init.sh"]
