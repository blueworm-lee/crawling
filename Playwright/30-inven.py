from playwright.sync_api import sync_playwright, Page
import time
from common import get_browser_options
import pprint

def get_list(page: Page, pageNum: int):
    reviewList = []


    try:
        page.wait_for_selector("tbody tr")
        reviews = page.locator("tbody tr")
    except:
        print('error')
        return None

    print(f"pageNum={pageNum}, totalReview={reviews.count()}")


    for idx in range(reviews.count()):        
        review = reviews.nth(idx)     

        category = review.locator("a.subject-link span.category").text_content().strip()
        content = review.locator("a.subject-link").text_content().replace(review.locator("a.subject-link span.category").text_content(), "").strip()
        writer = review.locator("span.layerNickName").text_content().strip()
        regDate = review.locator("td.date").text_content().strip()
        viewCnt = review.locator("td.view").text_content().strip()
        recoCnt = review.locator("td.reco").text_content().strip()

        print(f"regDate={regDate}, category={category}, content={content}")

        reviewList.append([category, content, writer, regDate, viewCnt, recoCnt])

    
    return reviewList
    


if __name__ == "__main__":

    pageNum = 0
    maxPage = 3
    allReviews = []

    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False, args=get_browser_options())
            page = browser.new_page()        
            page.set_viewport_size({"width": 1920, "height": 1080})

            while True:
                pageNum += 1
                if pageNum > maxPage:
                    break

                # 디아블로 인벤
                # url = f"https://www.inven.co.kr/board/diablo2/5736?p={pageNum}"

                # 라그나로크
                url = "https://www.inven.co.kr/board/ro/1955"

                # 리니지
                url ="https://www.inven.co.kr/board/lineagem/5056?category=%EC%8B%A4%ED%97%98"
                page.goto(url, wait_until='load')                

                reviewList = get_list(page, pageNum)
                if reviewList:
                    allReviews.append(reviewList)
                else:
                    print('reviewList is None')
                    break
                    
            pprint.pprint(allReviews)

            print(f"전체페이지={len(allReviews)}")
        except Exception as e:
            print(f"error={e}")

        finally:
            browser.close()

        
