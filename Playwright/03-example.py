from playwright.sync_api import sync_playwright
from common import get_browser_options
import time

browser = None

try:
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False, args=get_browser_options())

        page = browser.new_page()
        
        page.goto('http://www.solbox.com', wait_until='networkidle')
        print('페이지 로딩 완료')                
        time.sleep(10)
        browser.close()

except Exception as e:
    print(f"error={e}")
