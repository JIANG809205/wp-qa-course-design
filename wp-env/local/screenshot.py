import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
            "--window-size=1440,900", "--disable-gpu"):
    opts.add_argument(arg)

driver = webdriver.Chrome(options=opts)
try:
    print("chrome:", driver.capabilities.get("browserVersion"), flush=True)

    driver.get("http://localhost:8080/wp-login.php")
    driver.find_element(By.ID, "user_login").send_keys("admin")
    driver.find_element(By.ID, "user_pass").send_keys("Admin@2026")
    driver.find_element(By.ID, "wp-submit").click()
    time.sleep(3)
    print("login url:", driver.current_url, flush=True)
    driver.save_screenshot("/opt/qa/shot-admin.png")

    driver.get("http://localhost:8080/")
    print("front title:", driver.title, flush=True)
    driver.save_screenshot("/opt/qa/shot-front.png")

    driver.get("http://localhost:8080/wp-admin/edit.php")
    print("posts list:", driver.title, flush=True)
    driver.save_screenshot("/opt/qa/shot-posts.png")
finally:
    driver.quit()
