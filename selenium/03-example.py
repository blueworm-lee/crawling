#Ch_selenium/example/tutorial3.py
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from common import removePng, get_chrome_options

removePng()
driver = webdriver.Chrome(options=get_chrome_options())
driver.implicitly_wait(3)


# 페이지 가져오기(이동)
driver.get('https://www.google.co.kr')
driver.save_screenshot('img/google.png')
time.sleep(2)

driver.get('https://www.youtube.com')
driver.save_screenshot('img/youtube.png')
time.sleep(2)

driver.get('https://www.naver.com')
driver.save_screenshot('img/naver.png')

# 이전 창으로 이동 2번하기
time.sleep(2)
driver.back()
time.sleep(10)
driver.save_screenshot('img/back-1.png')

driver.back()
time.sleep(2)
driver.save_screenshot('img/back-2.png')

# 다음 창으로 2번 이동하기
driver.forward()
time.sleep(2)
driver.save_screenshot('img/forward-1.png')

driver.forward()
time.sleep(2)
driver.save_screenshot('img/forward-2.png')

driver.quit() # 웹 브라우저 종료. driver.close()는 탭 종료


