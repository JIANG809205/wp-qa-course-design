import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE = "http://localhost:8080"

o = Options()
for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
          "--window-size=1440,900", "--disable-gpu", "--lang=zh-CN"):
    o.add_argument(a)
d = webdriver.Chrome(options=o)
try:
    d.get(BASE + "/wp-login.php")
    d.find_element(By.ID, "user_login").send_keys("contributor")
    d.find_element(By.ID, "user_pass").send_keys("Contributor@2026")
    d.find_element(By.ID, "wp-submit").click()

    WebDriverWait(d, 15).until(lambda x: "wp-admin" in x.current_url)
    print("登录后 URL:", d.current_url)

    d.get(BASE + "/wp-admin/post-new.php")
    WebDriverWait(d, 15).until(lambda x: x.execute_script("return document.readyState") == "complete"
                               or "post-new" in x.current_url)
    time.sleep(3)
    print("新建页 URL:", d.current_url)
    body = d.find_element(By.TAG_NAME, "body").text
    print("BODY 前 200 字:", body[:200].replace("\n", " | "))
    print("含 提交审核:", "提交审核" in body)

    pubs = d.find_elements(By.ID, "publish")
    print("#publish 数量:", len(pubs))
    if pubs:
        el = pubs[0]
        print("  value =", el.get_attribute("value"))
        print("  text  =", el.text.strip())
        print("  visible =", el.is_displayed())

    for el in d.find_elements(By.CSS_SELECTOR, "input[type=submit]"):
        if el.is_displayed():
            print("可见提交按钮: id=%s value=%s text=%s" % (
                el.get_attribute("id"), el.get_attribute("value"), el.text.strip()))
finally:
    d.quit()
