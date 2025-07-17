from playwright.sync_api import sync_playwright, Page, Locator
import time
import os

def get_browser_options():
    return ['--no-sandbox', '--disable-dev-shm-usage', '--autoplay-policy=no-user-gesture-required', '--disable-background-media-playback']

url = "https://play.google.com/store/apps/details?id=com.kakaogames.archewar&pcampaignid=merch_published_cluster_promotion_battlestar_evergreen_dynasty_games"

# 댓글열기 selector
comment_selectors = [
    "//button[contains(., '리뷰 모두 보기')]",
    "span.VfPpkd-vQzf8d",    
]

# 모달 팝업
modal_scroll_selectors = [
    "div[role='dialog'] div.fysCi",
    "div[role='dialog']",
    ".fysCi",
    "div.fysCi"
]

# 테이블 기본 틀
reply_list_selectors = [
    "div.RHo1pe",
    ".RHo1pe"
]

author_selectors = [
    "div.X5PpBb",
    ".X5PpBb"
]

content_selectors = [
    "div.h3YV2d",
    ".h3YV2d",
]

regDate_selectors = [
    "span.bp9Aid",
    ".bp9Aid"
]

def open_shorts_comments(page: Page):
    """Shorts 댓글창 열기"""
    print("Shorts 댓글창 열기 시도...")

    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight);")       
    
    for selector in comment_selectors:
        try:
            page.wait_for_selector(selector, timeout=3000)
            page.click(selector)
            print(f"댓글 버튼 클릭 성공: {selector}")
            time.sleep(3)  # 댓글창 로드 대기
            return True
        except:
            continue
    
    print("댓글 버튼을 찾을 수 없습니다.")
    return False


def get_scroll_container(page: Page):
    """스크롤 컨테이너를 찾는 함수"""
    for selector in modal_scroll_selectors:
        try:
            container = page.query_selector(selector)
            if container:
                print(f"✓ 스크롤 컨테이너 발견: {selector}")
                return container
        except Exception as e:
            print(f"selector '{selector}' 시도 중 오류: {e}")
            continue
    
    print("! 스크롤 컨테이너를 찾을 수 없습니다.")
    return None



def scroll_playstore_modal(page, scroll_amount=700):
    print("[Play Store 모달팝업 스크롤]")
    
       
    # 스크롤 컨테이너 찾기
    scroll_container = get_scroll_container(page)
    
    # 스크롤 수행
    print("스크롤 중...")
    try:
        if scroll_container:
            # 스크롤 컨테이너 내에서 스크롤
            page.evaluate(f"""
                (element) => element.scrollTop += {scroll_amount}
            """, scroll_container)
            print("  → 컨테이너 스크롤 완료")
            return True
        else:
            # 모달 전체 스크롤 (fallback)
            page.evaluate(f"""
                () => {{
                    const modal = document.querySelector('div[role="dialog"]');
                    if (modal) {{
                        modal.scrollTop += {scroll_amount};
                    }}
                }}
            """)
            print("  → 모달 스크롤 완료 (fallback)")
            return True
    except Exception as e:
        print(f"  ✗ 스크롤 실패: {e}")
        return False
    

# def scroll_playstore_modal(page, scroll_amount=700):
#    print("[Play Store 모달팝업 스크롤]")
   
#    # 스크롤 컨테이너 찾기
#    scroll_container = None
#    try:
#        scroll_container = page.query_selector("div[role='dialog'] div.fysCi")
#        if scroll_container:
#            print("✓ 스크롤 컨테이너 발견!")
#        else:
#            print("! 스크롤 컨테이너를 찾을 수 없어 모달 전체를 사용합니다.")
#    except:
#        print("! 스크롤 컨테이너를 찾을 수 없어 모달 전체를 사용합니다.")
   
#    # 스크롤 수행
#    print("스크롤 중...")
#    try:
#        if scroll_container:
#            # 스크롤 컨테이너 내에서 스크롤
#            page.evaluate(f"""
#                (element) => element.scrollTop += {scroll_amount}
#            """, scroll_container)
#            print("  → 컨테이너 스크롤 완료")
#            return True
#        else:
#            # 모달 전체 스크롤
#            page.evaluate(f"""
#                () => {{
#                    const modal = document.querySelector('div[role="dialog"]');
#                    if (modal) {{
#                        modal.scrollTop += {scroll_amount};
#                    }}
#                }}
#            """)
#            print("  → 모달 스크롤 완료")
#            return True
#    except Exception as e:
#        print(f"  ✗ 스크롤 실패: {e}")
#        return False



def get_selector(element: any, selectors, timeout=1000):
    for selector in selectors:
        try:
            if isinstance(element, Page):
                element.wait_for_selector(selector, timeout=timeout)
                select_element = element.locator(selector)
            elif isinstance(element, Locator):
                element.wait_for(state="attached", timeout=timeout)
                select_element = element.locator(selector)
            else:
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

def scroll_to_load_shorts_comments(page: Page, max_comments: int = 100):
    """Shorts 댓글을 스크롤하여 로드"""
    print("Shorts 댓글 로드 중...")
    
    # 댓글창 열기 시도
    if not open_shorts_comments(page):
        return []
    
    # 댓글 개수 확인하면서 스크롤
    scroll_count = 0
    last_comment_count = 0
    stale_count = 0
    
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
            if stale_count >= 20:  # Shorts는 더 오래 기다림
                print("더 이상 댓글이 로드되지 않습니다. 스크롤 중단.")
                break
        else:
            stale_count = 0
        
        last_comment_count = current_comments
        
        # Shorts 댓글 영역에서 스크롤 시도

        scroll_playstore_modal(page)
        
        time.sleep(5)  # Shorts는 로딩이 느릴 수 있어서 더 오래 대기
        
        scroll_count += 1
        
        # 무한 스크롤 방지 (Shorts는 댓글이 적을 수 있어서 더 적게)
        if scroll_count >= 20:
            print("최대 스크롤 횟수 도달. 중단.")
            break
    
    return current_comments

def collect_all_comments_optimized(page: Page, max_comments: int = 100):
    print("\n=== YouTube Shorts 댓글 수집 시작 ===")
    
    # Shorts 동영상 정지
    # stop_video(page)
    
    # 1단계: 스크롤하여 댓글 로드
    total_loaded = scroll_to_load_shorts_comments(page, max_comments)
    
    # 2단계: 페이지 맨 위로 이동
    print("\n페이지 맨 위로 이동...")
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    
    # 3단계: 전체 댓글 개수 파악
    print("전체 댓글 개수 파악 중...")
    reply_elements = get_selector(page, reply_list_selectors)
    
    if reply_elements:
        comment_count = min(reply_elements.count(), max_comments)
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
                # 중복 체크
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
            
            # 진행 상황 출력 (20개마다)
            if (i + 1) % 20 == 0:
                print(f"  진행: {i + 1}/{comment_count} ({(i+1)/comment_count*100:.1f}%)")
                
        except Exception as e:
            print(f"idx={i}, error={e}")
            errCnt += 1
            continue
    
    print(f"\nShorts 댓글 수집 완료!")
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
            
            # Shorts 댓글 수집
            all_comments = collect_all_comments_optimized(page, max_comments)
            
            return all_comments
            
        except Exception as e:
            print(f"전체 오류: {e}")
            return []
        finally:
            browser.close()

if __name__ == "__main__":
    # 최대 댓글 수 설정
    max_comments = 100
    
    print(f"URL: {url}")
    
    comments = do_crawling(max_comments)    

    # # 결과 출력
    # print("-" * 100)
    # for comment in comments:
    #     print(f"작성자: {comment['author']}")
    #     print(f"내용: {comment['content']}")
    #     print(f"시간: {comment['regDate']}")
    #     print("-" * 50)

    # 파일 저장
    try:
        import common as comm
        comm.save_to_file(comments, os.path.splitext(os.path.basename(__file__))[0])
    except ImportError:
        print("common 모듈을 찾을 수 없습니다. 파일 저장 생략.")
    
    print(f"전체개수={len(comments)}")