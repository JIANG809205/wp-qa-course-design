# -*- coding: utf-8 -*-
"""把自动更新常量写入 wp-config.php（在宿主机编辑后拷回容器）。"""

import subprocess

TMP = r"E:\软件质量保证与测试课程设计\wp-env\native\wp-config.tmp.php"

subprocess.run(["wsl", "-d", "Ubuntu-22.04", "-u", "root", "--",
                "docker", "cp", "wp-app:/var/www/html/wp-config.php",
                "/mnt/e/软件质量保证与测试课程设计/wp-env/native/wp-config.tmp.php"], check=True)

text = open(TMP, encoding="utf-8").read()
CONST = 'define("AUTOMATIC_UPDATER_DISABLED", true);\n'
if "AUTOMATIC_UPDATER_DISABLED" in text:
    print("已存在，跳过")
else:
    anchor = "require_once ABSPATH . 'wp-settings.php';"
    if anchor in text:
        text = text.replace(anchor, CONST + "\n" + anchor, 1)
    else:
        text = text.rstrip() + "\n" + CONST
    open(TMP, "w", encoding="utf-8").write(text)
    print("已插入常量")

subprocess.run(["wsl", "-d", "Ubuntu-22.04", "-u", "root", "--",
                "docker", "cp",
                "/mnt/e/软件质量保证与测试课程设计/wp-env/native/wp-config.tmp.php",
                "wp-app:/var/www/html/wp-config.php"], check=True)
subprocess.run(["wsl", "-d", "Ubuntu-22.04", "-u", "root", "--",
                "docker", "exec", "wp-app", "chown", "www-data:www-data",
                "/var/www/html/wp-config.php"], check=True)

out = subprocess.run(["wsl", "-d", "Ubuntu-22.04", "-u", "root", "--", "bash", "-lc",
                      "docker exec wp-app grep -n AUTOMATIC_UPDATER_DISABLED /var/www/html/wp-config.php; "
                      "docker exec -u www-data wp-app wp core version; "
                      "curl -s -o /dev/null -w 'HTTP %{http_code}\\n' http://localhost:8080/"],
                     capture_output=True, text=True)
print(out.stdout)
