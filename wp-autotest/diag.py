import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE = "http://localhost:8080"


def new_driver():
    o = Options()
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
              "--window-size=1440,900", "--disable-gpu", "--lang=zh-CN"):
        o.add_argument(a)
    return webdriver.Chrome(options=o)


def login(d, user, pwd):
    d.get(BASE + "/wp-login.php")
    d.find_element(By.ID, "user_login").send_keys(user)
    d.find_element(By.ID, "user_pass").send_keys(pwd)
    d.find_element(By.ID, "wp-submit").click()
    time.sleep(2)


print("==== 投稿者新建文章页 ====")
d = new_driver()
try:
    login(d, "contributor", "Contributor@2026")
    d.get(BASE + "/wp-admin/post-new.php")
    time.sleep(3)
    for el in d.find_elements(By.CSS_SELECTOR, "input[type=submit], button"):
        print("ID=%s NAME=%s VALUE=%s TEXT=%s VISIBLE=%s" % (
            el.get_attribute("id"), el.get_attribute("name"),
            el.get_attribute("value"), el.text.strip(), el.is_displayed()))
    body = d.find_element(By.TAG_NAME, "body").text
    print("BODY_HAS_提交审核:", "提交审核" in body)
finally:
    d.quit()

print()
print("==== 含脚本评论 ====")
d = new_driver()
try:
    d.get(BASE + "/")
    time.sleep(2)
    links = d.find_elements(By.CSS_SELECTOR, "h2.entry-title a, h2 a")
    d.get(links[0].get_attribute("href"))
    time.sleep(2)
    d.find_element(By.ID, "comment").send_keys("<script>alert('xss')</script>自动化XSS测试2")
    d.find_element(By.ID, "author").send_keys("测试访客")
    d.find_element(By.ID, "email").send_keys("guest2@example.com")
    d.find_element(By.ID, "submit").click()
    time.sleep(4)
    body = d.find_element(By.TAG_NAME, "body").text
    print("URL:", d.current_url)
    print("TEXT:", body[:500].replace("\n", " | "))
    print("HAS_RAW_SCRIPT:", "<script>alert('xss')</script>" in d.page_source)
    print("HAS_MODERATION:", "等待审核" in body)
finally:
    d.quit()
