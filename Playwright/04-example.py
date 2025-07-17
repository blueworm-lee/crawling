from playwright.sync_api import sync_playwright
import time
from common import get_browser_options




with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=get_browser_options(), slow_mo=1000)

    try:
        page = browser.new_page()
        page.goto('http://www.naver.com', wait_until='networkidle')

        search_box = page.locator('#query')  # id="query"인 검색창
        search_box.fill('솔박스')
        search_box.press('Enter')

        page.wait_for_load_state('networkidle')

        time.sleep(5)

        page.goto('http://www.naver.com', wait_until='networkidle')        

        search_box.fill('구글')
        
        button = page.locator('#sform > fieldset > button')
        if button.count() > 0:
            button.click()        
            page.wait_for_load_state('networkidle', timeout=10*1000)

        

        time.sleep(5)
        # 또는 search_box = page.locator('input[name="query"]')
        # 또는 search_box = page.locator('.search_input')

    
    except Exception as e:
        print(f"error={e}")
    finally:
        browser.close()

