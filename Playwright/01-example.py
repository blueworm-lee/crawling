from playwright.sync_api import sync_playwright
import time
from common import get_browser_options

try:
    with sync_playwright() as p:
        # Chrome 브라우저 실행 (옵션 설정)
        browser = p.chromium.launch(
            headless=False,  # chrome_options.add_argument('--headless') 주석처리와 동일
            args=get_browser_options()
        )
        
        # 새 페이지 생성
        page = browser.new_page()
        
        # Playwright는 자동 대기 기능이 내장되어 있어 implicitly_wait 불필요
        print("Playwright 브라우저 실행 성공!")
        
        # 테스트
        page.goto('https://google.co.kr')
        print(f"페이지 제목: {page.title()}")
        print(f"현재 URL: {page.url}")
        
        time.sleep(2)
        browser.close()
        print("테스트 완료!")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()