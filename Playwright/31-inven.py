from playwright.sync_api import sync_playwright, Page, Locator
import time
from common import get_browser_options
import pprint
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os
import common as comm


# 디아블로
# url = "https://www.inven.co.kr/board/diablo2/5736?p={pageNum}"

# 라그나로크
url = "https://www.inven.co.kr/board/ro/1955"

# 리니지
# url ="https://www.inven.co.kr/board/lineagem/5056?category=%EC%8B%A4%ED%97%98"


comment_list_selectors = [
    "tbody tr"
]
category_selectors = [
    "a.subject-link span.category"
]
content_selectors = [
    "a.subject-link"
]
writer_selectors = [
    "span.layerNickName"
]
regDate_selectors = [
    "td.date"
]
viewCnt_selectors = [
    "td.view"
]
recoCnt_selectors = [
    "td.reco"
]


def gen_parameter(url: str, pageNum: int):

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
   
    # 있으면 overwrite, 없으면 생성
    query_params['p'] = [str(pageNum)]
    
    # 새로운 쿼리 문자열 생성
    new_query = urlencode(query_params, doseq=True)
    
    # 새로운 URL 생성
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return new_url

def get_selector(element: any, selectors, timeout=1000):
    
    for selector in selectors:
        try:     
            
             # Page 객체인 경우 wait_for_selector 사용
            if isinstance(element, Page):
                element.wait_for_selector(selector, timeout=timeout)
                select_element = element.locator(selector)
            # Locator 객체인 경우 wait_for 사용
            elif isinstance(element, Locator):
                element.wait_for(state="attached", timeout=timeout)
                select_element = element.locator(selector)
            else:
                # 기타 경우 그냥 locator만 사용
                select_element = element.locator(selector)

            if select_element.count() > 0:
                return select_element
        except:
            continue    
    return None    


def get_text(element: Locator, removeText: str = None):
    try:
        text = element.text_content().strip()

        if removeText:
            text = text.replace(removeText, "").strip()
            text = '  '.join(text.split())
        return text
    except Exception as e:
        return None

def get_list(page: Page, pageNum: int):
    reviewList = []

    reviewsElement = get_selector(page, comment_list_selectors)
    if reviewsElement:
        review_cnt = reviewsElement.count()
    else:
        review_cnt = 0

    print(f"pageNum={pageNum}, totalReview={review_cnt}")


    for idx in range(review_cnt):        
        review = reviewsElement.nth(idx)
        
        category = get_text(get_selector(review, category_selectors))
        content = get_text(get_selector(review, content_selectors), category)
        # content = review.locator("a.subject-link").text_content().strip()
        # content = content.replace(category, "").strip()
        # content = '  '.join(content.split())
        # # content = review.locator("a.subject-link").text_content().replace(review.locator("a.subject-link span.category").text_content(), "").strip()

        writer = get_text(get_selector(review, writer_selectors))
        regDate = get_text(get_selector(review, regDate_selectors))
        viewCnt = get_text(get_selector(review, viewCnt_selectors))
        recoCnt = get_text(get_selector(review, recoCnt_selectors))

        if category and content and writer and regDate and viewCnt and recoCnt:
            print(f"regDate={regDate}, category={category}, content={content}")
            reviewList.append([category, content, writer, regDate, viewCnt, recoCnt])
        else:
            print(f"missing : regDate={regDate}, category={category}, content={content}")

    
    return reviewList
    


if __name__ == "__main__":

    pageNum = 0
    maxPage = 3
    allReviews = []
    saveFileName = os.path.splitext(os.path.basename(__file__))[0]
    mode = 'w' 
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False, args=get_browser_options())
            page = browser.new_page()        
            page.set_viewport_size({"width": 1920, "height": 1080})

            while True:
                pageNum += 1
                if pageNum > maxPage:
                    break

                url = gen_parameter(url, pageNum)
                page.goto(url, wait_until='load')
                reviewList = get_list(page, pageNum)
                
                
                if reviewList:                    
                    comm.save_to_file(reviewList, saveFileName, mode) 
                    allReviews.append(reviewList)

                    if mode == 'w': mode='a'
                else:
                    print('reviewList is None')
                    break
                    
            # pprint.pprint(allReviews)

            print(f"전체페이지={len(allReviews)}")
        except Exception as e:
            print(f"main-error={e}")

        finally:
            browser.close()

        
