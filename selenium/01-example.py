from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
 
try:
    # Chrome 옵션 설정
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
     
    # ChromeDriver 실행
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(3) # 묵시적 대기, 활성화를 위해 3초간 기다린다.
    print("ChromeDriver 실행 성공!")
     
    # 테스트
    driver.get('https://solbox.com')    
    print(f"페이지 제목: {driver.title}")
    print(f"현재 URL: {driver.current_url}")
     
    time.sleep(5)
    driver.quit()
    print("테스트 완료!")
     
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()