#Ch_selenium/example/tutorial2.py
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(options=chrome_options) #또는 chromedriver.exe
driver.implicitly_wait(3) # 묵시적 대기, 활성화를 최대 15초가지 기다린다.

driver.get("http://www.solbox.com")
# 화면 크기 지정
driver.fullscreen_window() # 전체화면 모드로 변경
driver.save_screenshot('img/fullscreen.png')  # 설정된 화면 크기로 저장됨
print(f'fullscreen={driver.get_window_rect()}')

time.sleep(1)
driver.maximize_window() # 최대 창 크기로 변경
driver.save_screenshot('img/maximize.png')  # 설정된 화면 크기로 저장됨
print(f'maximize={driver.get_window_rect()}')

time.sleep(1)
driver.set_window_rect(100,100,500,500) # 특정 좌표(x,y)와 크기(width,height)로 변경
driver.save_screenshot('img/set_react.png')  # 설정된 화면 크기로 저장됨
print(f'set_react={driver.get_window_rect()}')

time.sleep(1)
driver.set_window_size(375, 667)  # 모바일 사이즈
driver.save_screenshot('img/mobile.png')  # 설정된 화면 크기로 저장됨
print(f'mobile={driver.get_window_rect()}')

time.sleep(1)
driver.set_window_size(768, 1024) #테블릿 사이즈
driver.save_screenshot('img/tablet.png')  # 설정된 화면 크기로 저장됨
print(f'tablet={driver.get_window_rect()}')


driver.set_window_size(1920, 1080)


# 3초후 종료
time.sleep(3)
# driver.quit() # 웹 브라우저 종료. driver.close()는 탭 종료
driver.set_window_position(0,0)
driver.quit()
