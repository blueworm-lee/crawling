from selenium import webdriver
from selenium.webdriver.common.by import By

from common import get_chrome_options
import sys
import signal

def signal_handler(sig, frame):
    print('\nCtrl+C 감지됨. 드라이버 종료 중...')
    if driver:
        driver.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# url = "https://n.news.naver.com/article/comment/421/0008347328"
url = "https://n.news.naver.com/article/comment/119/0002975034"

driver = webdriver.Chrome(options=get_chrome_options())
driver.set_window_size(1920, 1080)
driver.implicitly_wait(3)

# 화면 접속
driver.get(url)


# 더보기 클릭
try_cnt = 0
more_cnt = 0
while True:
    try:
        driver.find_element(By.CSS_SELECTOR, "span.u_cbox_page_more").click()
        try_cnt = 0
        more_cnt += 1
    except Exception as e:
        try_cnt += 1
        if try_cnt > 3:
            print(f"더 이상 더 보기가 없습니다. more_cnt={more_cnt}, try_cnt={try_cnt}")
            break
    

replys = driver.find_elements(By.CSS_SELECTOR, "ul.u_cbox_list > li.u_cbox_comment")
print(f"전체개수={len(replys)}")

totalReplys = []
errCnt = 0

for reply in replys:
    try:
        author = reply.find_element(By.CSS_SELECTOR, "span.u_cbox_nick").text
        regDate = reply.find_element(By.CSS_SELECTOR, "span.u_cbox_date").text
        content = reply.find_element(By.CSS_SELECTOR, "span.u_cbox_contents").text

        totalReplys.append({"author": author, "regDate": regDate, "content": content})
        
    except Exception as e:
        errCnt += 1
        # print(f"error={e}")


print(f"전체개수={len(replys)}, 가져온개수={len(totalReplys)}, 에러개수={errCnt}")

print("-"*100)

for reply in totalReplys:
    print(f"작성자={reply['author']}, 일자={reply['regDate']}, 내용{reply['content']}")





driver.quit()


