from playwright.sync_api import sync_playwright, Page, Locator
import time
import os

# common.py 대신 임시 함수
def get_browser_options():
    return ['--no-sandbox', '--disable-dev-shm-usage', '--autoplay-policy=no-user-gesture-required', '--disable-background-media-playback']
        

# url = "https://www.youtube.com/watch?v=F3c6bwvCkQw"
url = "https://www.youtube.com/watch?v=fywReMb3iXk"
# YouTube 댓글 selector 우선순위
reply_list_selectors = [
    "ytd-comment-thread-renderer"    
]

author_selectors = [
    "#author-text span",
    "#author-text", 
    "a#author-text",
    ".author-text"
]

content_selectors = [
    "#content-text",
    "yt-formatted-string#content-text",
    "#content-text span",
    ".content-text"
]

regDate_selectors = [
    ".published-time-text a",
    ".published-time-text",
    "a.published-time-text", 
    "#published-time-text"
]

def stop_video(page: Page, timeout=5*1000):
    stop_methods = [
        lambda: page.keyboard.press("Space"),
        lambda: page.click(".ytp-play-button", timeout=timeout),
    ]
     
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        page.wait_for_selector(".ytp-play-button", timeout=timeout)

        for i, method in enumerate(stop_methods):
            try:
                method()
                time.sleep(1)                

                 # 실제로 동영상이 정지되었는지 확인
                is_paused = page.evaluate("document.querySelector('video')?.paused || false")
                
                if is_paused:
                    print(f"Video play stopped. method={i}")
                    return
                else:
                    print(f"Method {i} 시도했지만 여전히 재생 중")
                    
            except Exception as e1:
                continue
    except Exception as e:
        print(f"video stop error={e}")    

    


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

def get_text_content(element):
    """안전하게 텍스트 내용을 가져오는 함수"""
    try:
        if element and element.count() > 0:
            return element.first.inner_text(timeout=1000)
        return None
    except:
        return None
    

def scroll_to_load_comments(page: Page, max_comments: int = 100):
    """YouTube 댓글을 스크롤하여 로드"""
    print("댓글 섹션으로 스크롤 중...")
    
    # 초기 댓글 섹션까지 스크롤
    page.evaluate("window.scrollTo(0, 1000);")
    time.sleep(3)
    page.evaluate("window.scrollTo(0, 2000);")
    time.sleep(3)

    
    # 댓글 개수 확인하면서 스크롤
    scroll_count = 0
    last_comment_count = 0
    stale_count = 0  # 댓글 수가 변하지 않은 횟수
    
    while True:
        # 현재 댓글 개수 확인
        reply_elements = get_selector(page, reply_list_selectors)
        if reply_elements:
            current_comments = reply_elements.count()
        else:
            current_comments = 0
            print("cannot find reply_list_selectors")
        
        print(f"스크롤 {scroll_count}회, 현재 댓글 수: {current_comments}")

        # 최대 댓글 수 도달시 중단
        if current_comments >= max_comments:
            print(f"최대 댓글 수 {max_comments}개 도달. 스크롤 중단.")
            break
        
        # 댓글 수가 변하지 않으면 stale_count 증가
        if current_comments == last_comment_count:
            stale_count += 1
            if stale_count >= 3:  # 3번 연속 변화 없으면 중단
                print("더 이상 댓글이 로드되지 않습니다. 스크롤 중단.")
                break
        else:
            stale_count = 0
        
        last_comment_count = current_comments
        
        # 페이지 끝까지 스크롤
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight);")

        time.sleep(2)
        
        scroll_count += 1
        
        # 무한 스크롤 방지 (최대 50회)
        if scroll_count >= 50:
            print("최대 스크롤 횟수 도달. 중단.")
            break
    
    return current_comments


def collect_all_comments_optimized(page: Page, max_comments: int = 100):
    print("\n=== YouTube 댓글 수집 시작 ===")
    
    
    stop_video(page)

    # 1단계: 스크롤하여 댓글 로드
    total_loaded = scroll_to_load_comments(page, max_comments)
    
    # 2단계: 페이지 맨 위로 이동
    print("\n페이지 맨 위로 이동...")
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    
    # 3단계: 전체 댓글 개수 파악
    print("전체 댓글 개수 파악 중...")
    reply_elements = get_selector(page, reply_list_selectors)
    
    if reply_elements:
        comment_count = min(reply_elements.count(), max_comments)  # 최대 개수 제한
    else:
        comment_count = 0
        print("댓글을 찾을 수 없습니다.")
        return []

    # 4단계: for문으로 순차 처리
    comments = []
    seen_keys = set()
    errCnt = 0
    
    print(f"\nfor문으로 {comment_count}개 댓글 순차 처리...")
    
    for i in range(comment_count):
        try:
            # i번째 댓글 처리
            reply = reply_elements.nth(i)
            
            # 요소 존재 확인
            author_elem = get_selector(reply, author_selectors)
            regDate_elem = get_selector(reply, regDate_selectors)
            content_elem = get_selector(reply, content_selectors)
            
            # 텍스트 추출
            author = get_text_content(author_elem) or 'Unknown'
            regDate = get_text_content(regDate_elem) or 'Unknown'
            content = get_text_content(content_elem)
            
            # 최소한 내용은 있어야 함
            if content:
                # 중복 체크 (작성자 + 내용 앞 50자 + 시간)
                comment_key = f"{author}|{content[:50]}|{regDate}"
                
                if comment_key not in seen_keys:
                    comments.append({
                        "author": author,
                        "regDate": regDate,
                        "content": content
                    })
                    seen_keys.add(comment_key)
                    # print(f"idx={i}, author={author}, content={content[:50]}...")
                else:
                    print(f"idx={i}, 중복 댓글 제거")
            else:
                print(f"idx={i}, 댓글 내용을 찾을 수 없음")
                errCnt += 1
            
            # 진행 상황 출력 (50개마다)
            if (i + 1) % 50 == 0:
                print(f"  진행: {i + 1}/{comment_count} ({(i+1)/comment_count*100:.1f}%)")
                
        except Exception as e:
            print(f"idx={i}, error={e}")
            errCnt += 1
            continue
    
    print(f"\n댓글 수집 완료!")
    print(f"처리된 댓글: {comment_count}개")
    print(f"수집된 댓글: {len(comments)}개 (중복 제거 후)")
    print(f"에러 개수: {errCnt}")
    
    return comments

def do_crawling(max_comments: int = 100):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=get_browser_options())
        
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(url, wait_until='load')
            
            # 댓글 수집
            all_comments = collect_all_comments_optimized(page, max_comments)
            
            return all_comments
            
        except Exception as e:
            print(f"전체 오류: {e}")
            return []
        finally:
            browser.close()

if __name__ == "__main__":
    # 최대 댓글 수 설정 (기본값: 100개)
    max_comments = 50
    
    comments = do_crawling(max_comments)    

    # # 결과 출력
    # print("-" * 100)
    # for comment in comments:
    #     print(f"작성자: {comment['author']}")
    #     print(f"내용: {comment['content']}")
    #     print(f"시간: {comment['regDate']}")
    #     print("-" * 50)

    # 파일 저장 (common 모듈이 있는 경우)
    try:
        import common as comm
        comm.save_to_file(comments, os.path.splitext(os.path.basename(__file__))[0])
    except ImportError:
        print("common 모듈을 찾을 수 없습니다. 파일 저장 생략.")
    
    print(f"전체개수={len(comments)}")