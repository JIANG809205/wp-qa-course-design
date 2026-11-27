from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
            "--window-size=1440,900", "--disable-gpu"):
    opts.add_argument(arg)

driver = webdriver.Chrome(options=opts)
try:
    driver.get("http://localhost:8080/")
    print("title:", driver.title)
    print("admin bar present:", len(driver.find_elements("id", "wpadminbar")))
    driver.save_screenshot("/opt/qa/shot-front-anon.png")
finally:
    driver.quit()
