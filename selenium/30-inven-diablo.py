import signal
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By

from common import get_chrome_options

totalCnt = 0
driver = None

def signal_handler(sig, frame):
    print('\nCtrl+C 감지됨. 드라이버 종료 중...')
    if driver:
        driver.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def do_parse(driver: webdriver, url: str, page_num: int) -> int:
    global totalCnt
    subList = []
    retCode = 0

    try:
        # 화면 접속
        driver.get(url)

        # 게시판 메인 테이블 접근
        replys = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    except Exception as e:
        print(f"url={url}, error={e}")
        driver.quit()
        return -1
        
    for idx, reply in enumerate(replys):
        try:
            # if idx == 0 and page_num == 1:
            #     continue

            content = reply.find_element(By.CSS_SELECTOR,"a.subject-link").text
            regDate = reply.find_element(By.CSS_SELECTOR,"td.date").text

            subList.append((content, regDate))
        except Exception as e:
            print(f"replys_len={len(replys)}, error={e}")  
            retCode = -1
            break

    writeToFile(subList)

    totalCnt += len(subList)
    print(f"idx={page_num}, totalList_cnt={totalCnt}, subList_cnt={len(subList)}, subList={subList}")

    return retCode


def writeToFile(subList):
    with open("text/32-inven-diablo.txt", "a") as f:
        for content, regDate in subList:
            f.write(f"{content}\t{regDate}\n")



if __name__ == "__main__":
    try:

        driver = webdriver.Chrome(options=get_chrome_options())
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(3)

        page_num = 0
        while True:
            if page_num > 5:
                break

            page_num = page_num +1 
            url = f"https://www.inven.co.kr/board/diablo2/5736?p={page_num}"
            retCode = do_parse(driver, url, page_num)
            if retCode < 0:
                break
            # writeToFile()
    except KeyboardInterrupt:
        print("\n키보드 인터럽트 감지됨. 종료 중...")

    finally:
        if driver:
            driver.quit()

    

   






