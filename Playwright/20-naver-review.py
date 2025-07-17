from playwright.sync_api import sync_playwright
import time
from common import get_browser_options

url = "https://n.news.naver.com/article/comment/421/0008347328"
# url = "https://n.news.naver.com/article/comment/119/0002975034"


totalReviews = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=get_browser_options())

    try:
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(url, wait_until='networkidle')
        
        # List 부분 찾기
        page.wait_for_selector("ul.u_cbox_list")        
        replys = page.locator("ul.u_cbox_list > li.u_cbox_comment")

        print(f"댓글 개수={replys.count()}")

        errCnt = 0
        for i in range(replys.count()):
            try:
                reply = replys.nth(i)

                author_elem = reply.locator("span.u_cbox_nick")
                regDate_elem = reply.locator("span.u_cbox_date")
                content_elem = reply.locator("span.u_cbox_contents")


                if (author_elem.count() > 0 and regDate_elem.count() > 0 and content_elem.count() > 0):
                    author = author_elem.inner_text()
                    regDate = regDate_elem.inner_text()
                    content = content_elem.inner_text()                
                    totalReviews.append([author, regDate, content])
                else:
                    alt_content = reply.locator(".u_cbox_delete_contents, .u_cbox_blocked")
                    if alt_content.count() > 0:
                        print(f"  → 삭제되거나 차단된 댓글")
                        totalReviews.append(["삭제된사용자", "날짜없음", "삭제된 댓글"])
                    else:
                        print(f"  → 알 수 없는 구조")
            except Exception as e:
                errCnt += 1
                print(f"TotalErrCnt={errCnt}, for_loop_cnt={i}, error={e}")



        time.sleep(2)

        print(totalReviews)


        


    except Exception as e:
        print(f"error={e}")
    finally:
        browser.close()


    