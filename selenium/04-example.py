#Ch_selenium/example/tutorial4.py
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from common import removePng, get_chrome_options

removePng()
driver = webdriver.Chrome(options=get_chrome_options())
driver.implicitly_wait(3)

# 페이지 가져오기(이동)
driver.get('https://www.naver.com')
driver.save_screenshot('img/naver-1.png')

# 요소 찾기 - 검색창찾고 키 전송
# search = driver.find_element_by_css_selector('#query')
search = driver.find_element(By.CSS_SELECTOR, '#query')
search.send_keys('솔박스')
search.send_keys(Keys.ENTER)
driver.save_screenshot('img/solbox.png')

# 다시 처음으로 이동
driver.get('https://www.naver.com')
driver.save_screenshot('img/naver-2.png')


search = driver.find_element(By.CSS_SELECTOR, '#query')
search.send_keys('google')

button = driver.find_element(By.CSS_SELECTOR, '#sform > fieldset > button')
button.click()
driver.save_screenshot('img/google.png')


