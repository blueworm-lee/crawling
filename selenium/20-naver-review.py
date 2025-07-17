from selenium import webdriver
from selenium.webdriver.common.by import By

from common import get_chrome_options


url = "https://n.news.naver.com/article/comment/421/0008347328"
# url = "https://n.news.naver.com/article/comment/119/0002975034"

driver = webdriver.Chrome(options=get_chrome_options())
driver.set_window_size(1920, 1080)
driver.implicitly_wait(3)

# 화면 접속
driver.get(url)

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


