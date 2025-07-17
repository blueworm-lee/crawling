from playwright.sync_api import sync_playwright, Page, Locator
import time
import os

# common.py 대신 임시 함수
def get_browser_options():
    return ['--no-sandbox', '--disable-dev-shm-usage']

url = "https://n.news.naver.com/article/015/0005157505?cds=news_media_pc&type=editn"
# url = "https://n.news.naver.com/article/655/0000026362"
# url = "https://n.news.naver.com/article/655/0000026384?type=breakingnews"

# 더보기 버튼 selector 우선순위
more_selectors = [
    "span.u_cbox_page_more",
    ".u_cbox_page_more",     
    "text=댓글 보기",
    "text=댓글 더보기",
    "text=더보기"
]

reply_list_selectors = [
    "ul.u_cbox_list > li.u_cbox_comment"
]

author_selectors = [
    "span.u_cbox_nick"
]
content_selectors = [
    "span.u_cbox_contents"
]
regDate_selectors = [
    "span.u_cbox_date"
]


def clicks_more_button(page: Page, moreMaxCnt: int = 2):
   """모든 더보기 버튼 클릭"""
   moreCnt = 0    

   print("모든 더보기 버튼 클릭 중...")
  
  
   while moreCnt < moreMaxCnt:
       page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
       time.sleep(1)

       button_found = False
       
       # 여러 selector를 순차적으로 시도
       for selector in more_selectors:
           try:
               page.wait_for_selector(selector, timeout=2*1000)
               if page.locator(selector).count() > 0:
                   more_button = page.locator(selector)
                   more_button.scroll_into_view_if_needed()
                   time.sleep(0.5)
                   more_button.click()
                   moreCnt += 1
                   print(f"  더보기 클릭 {moreCnt}회 (selector: {selector})")
                   button_found = True
                   break  # 버튼 클릭 성공하면 selector 루프 종료하고 처음부터 다시
           except Exception as e:
               continue  # 이 selector로 실패하면 다음 selector 시도
       
       # 모든 selector를 시도했는데 버튼을 찾지 못했으면 종료
       if not button_found:
           print(f"더보기 버튼이 없습니다. 총 클릭: {moreCnt}회")
           break
  
   return moreCnt

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
    


def collect_all_comments_optimized(page: Page):
    print("\n=== 최적화된 댓글 수집 시작 ===")
    
    reply_elements = None
    comment_count = 0
    blockUserCnt = 0

    # 1단계: 모든 더보기 버튼 클릭
    more_count = clicks_more_button(page)
    
    # 2단계: 페이지 맨 위로 이동
    print("\n페이지 맨 위로 이동...")
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    
    # 3단계: 전체 댓글 개수 파악
    print("전체 댓글 개수 파악 중...")
    # reply_elements = page.locator("ul.u_cbox_list > li.u_cbox_comment")

    reply_elements = get_selector(page, reply_list_selectors)
    if reply_elements:
        comment_count = reply_elements.count()
    else:
        comment_count = 0
        print("cannot find reply_list_selectors")

    # 4단계: for문으로 순차 처리
    comments = []
    seen_keys = set()
    
    print(f"\nfor문으로 {comment_count}개 댓글 순차 처리...")
    
    for i in range(comment_count):
        try:
            
            # i번째 댓글 처리
            reply = reply_elements.nth(i)
            
            
            # 요소 존재 확인
            author_elem = get_selector(reply, author_selectors)
            regDate_elem = get_selector(reply, regDate_selectors)
            content_elem = get_selector(reply, content_selectors)
            
            if author_elem and regDate_elem and content_elem:               
                # 텍스트 추출
                author = author_elem.inner_text(timeout=1000)
                regDate = regDate_elem.inner_text(timeout=1000)
                content = content_elem.inner_text(timeout=1000)
                
                # 중복 체크
                comment_key = f"{author}|{content[:50]}|{regDate}"
                
                if comment_key not in seen_keys:
                    comments.append({
                        "author": author,
                        "regDate": regDate,
                        "content": content
                    })
                    seen_keys.add(comment_key)
            else:
                blockUserCnt += 1                
            
            # 진행 상황 출력 (100개마다)
            if (i + 1) % 100 == 0:
                print(f"  진행: {i + 1}/{comment_count} ({(i+1)/comment_count*100:.1f}%)")
                
        except Exception as e:
            print(f"error={e}")
            
            continue
    
    print(f"\nfor문 처리 완료!")
    print(f"처리된 댓글: {comment_count}개")
    print(f"수집된 댓글: {len(comments)}개 (중복 제거 후), 삭제된 댓글: {blockUserCnt}")
    print(f"더보기 클릭: {more_count}회")
    
    return comments

def do_crawling():
   
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=get_browser_options())
        
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(url, wait_until='load')
                        
            # 최적화된 댓글 수집
            all_comments = collect_all_comments_optimized(page)
            
            return all_comments
            
        except Exception as e:
            print(f"전체 오류: {e}")
            return []
        finally:
            browser.close()


if __name__ == "__main__":        
    
    comments = do_crawling()    

    import common as comm
    comm.save_to_file(comments, os.path.splitext(os.path.basename(__file__))[0])    
    
    print(f"전체개수={len(comments)}")

    