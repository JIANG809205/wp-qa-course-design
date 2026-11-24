import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/"
out = sys.argv[2] if len(sys.argv) > 2 else "/opt/qa/shot-clean.png"

o = Options()
for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
          "--window-size=1440,900", "--disable-gpu", "--lang=zh-CN"):
    o.add_argument(a)
d = webdriver.Chrome(options=o)
try:
    d.get(url)
    time.sleep(2)
    print("title:", d.title)
    d.save_screenshot(out)
    print("saved:", out)
finally:
    d.quit()
