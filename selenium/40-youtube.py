from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import signal
from common import get_chrome_options, removePng

removePng()

driver = None

def signal_handler(sig, frame):
    print('\nCtrl+C 감지됨. 드라이버 종료 중...')
    if driver:
        driver.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

url = "https://www.youtube.com/watch?v=F3c6bwvCkQw"

driver = webdriver.Chrome(options=get_chrome_options())
driver.set_window_size(1920, 1080)
driver.implicitly_wait(3)

# 화면 접속
driver.get(url)

# 댓글 섹션까지 스크롤
print("댓글 섹션으로 스크롤 중...")
driver.execute_script("window.scrollTo(0, 1000);")
time.sleep(3)

driver.execute_script("window.scrollTo(0, 2000);")
time.sleep(3)

# 댓글 로드 대기
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-comment-thread-renderer"))
    )
    print("댓글 로드 완료!")
except Exception as e:
    print(f"댓글 로드 대기 실패: {e}")
    driver.quit()
    sys.exit(1)

replys = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
print(f"전체개수={len(replys)}")

totalReplys = []
errCnt = 0

for idx, reply in enumerate(replys):
    try:
        # 여러 가능한 셀렉터들을 시도
        author = None
        content = None
        reg_date = None
        
        # 댓글 작성자 찾기
        author_selectors = [
            "#author-text span",
            "#author-text",
            "a#author-text",
            ".author-text"
        ]
        
        for selector in author_selectors:
            try:
                author_element = reply.find_element(By.CSS_SELECTOR, selector)
                author = author_element.text
                break
            except:
                continue
        
        # 댓글 내용 찾기
        content_selectors = [
            "#content-text",
            "yt-formatted-string#content-text",
            "#content-text span",
            ".content-text"
        ]
        
        for selector in content_selectors:
            try:
                content_element = reply.find_element(By.CSS_SELECTOR, selector)
                content = content_element.text
                break
            except:
                continue
        
        # 댓글 시간 찾기
        time_selectors = [
            ".published-time-text a",
            ".published-time-text",
            "a.published-time-text",
            "#published-time-text"
        ]
        
        for selector in time_selectors:
            try:
                time_element = reply.find_element(By.CSS_SELECTOR, selector)
                reg_date = time_element.text
                break
            except:
                continue
        
        # 최소한 내용은 있어야 함
        if content:
            print(f"idx={idx}, author={author}, content={content[:50]}...")
            totalReplys.append({
                'author': author or 'Unknown',
                'content': content,
                'reg_date': reg_date or 'Unknown'
            })
        else:
            print(f"idx={idx}, 댓글 내용을 찾을 수 없음")
            errCnt += 1
        
    except Exception as e:        
        errCnt += 1
        print(f"idx={idx}, error={e}")

print(f"전체개수={len(replys)}, 가져온개수={len(totalReplys)}, 에러개수={errCnt}")

print("-"*100)

for reply in totalReplys:
    print(f"작성자: {reply['author']}")
    print(f"내용: {reply['content']}")
    print(f"시간: {reply['reg_date']}")
    print("-"*50)

driver.quit()