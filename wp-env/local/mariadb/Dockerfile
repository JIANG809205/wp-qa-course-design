FROM ubuntu:jammy-local

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8

RUN printf '%s\n' \
      'deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse' \
      'deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse' \
      'deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse' \
      > /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends mariadb-server \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /run/mysqld && chown mysql:mysql /run/mysqld

# 允许其他容器访问：覆盖 Ubuntu 默认的 bind-address=127.0.0.1
RUN printf '%s\n' \
      '[mysqld]' \
      'bind-address = 0.0.0.0' \
      'skip-networking = 0' \
      'max_connections = 300' \
      'character-set-server = utf8mb4' \
      'collation-server = utf8mb4_unicode_ci' \
      'innodb_buffer_pool_size = 512M' \
      'innodb_log_buffer_size = 32M' \
      'innodb_flush_log_at_trx_commit = 2' \
      'query_cache_type = 0' \
      > /etc/mysql/mariadb.conf.d/99-qa.cnf \
 && cat /etc/mysql/mariadb.conf.d/99-qa.cnf

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

VOLUME /var/lib/mysql
EXPOSE 3306
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
