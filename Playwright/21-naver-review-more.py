from playwright.sync_api import sync_playwright, Page
import time

# common.py 대신 임시 함수
def get_browser_options():
    return ['--no-sandbox', '--disable-dev-shm-usage']

url = "https://n.news.naver.com/article/015/0005157505?cds=news_media_pc&type=editn"

def clicks_more_button(page: Page):
    """모든 더보기 버튼 클릭"""
    moreCnt = 0    
    height = 1080

    print("모든 더보기 버튼 클릭 중...")
    
    while True:
        if moreCnt >= 10:  # 최대 10번만
            break

        page.evaluate(f"window.scrollTo(0, {height})")
        time.sleep(1)

        try:
            page.wait_for_selector("span.u_cbox_page_more", timeout=5*1000)
            more_button = page.locator("span.u_cbox_page_more")
            more_button.scroll_into_view_if_needed()
            time.sleep(0.5)
            more_button.click()

            moreCnt += 1
            height += 1080
            print(f"  더보기 클릭 {moreCnt}회")

        except Exception as e:
            print(f"더보기 버튼이 없습니다. 총 클릭: {moreCnt}회")
            break
    
    return moreCnt

def collect_all_comments_optimized(page: Page):
    """✅ 최적화된 댓글 수집 - for문 방식"""
    
    print("\n=== 최적화된 댓글 수집 시작 ===")
    
    # 1단계: 모든 더보기 버튼 클릭
    more_count = clicks_more_button(page)
    
    # 2단계: 페이지 맨 위로 이동
    print("\n페이지 맨 위로 이동...")
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    
    # 3단계: 전체 댓글 개수 파악
    print("전체 댓글 개수 파악 중...")
    reply_elements = page.locator("ul.u_cbox_list > li.u_cbox_comment")
    comment_count = reply_elements.count()
    print(f"DOM에서 총 {comment_count}개 댓글 발견")
    
    # 4단계: for문으로 순차 처리
    comments = []
    seen_keys = set()
    
    print(f"\nfor문으로 {comment_count}개 댓글 순차 처리...")
    
    for i in range(comment_count):
        try:
            
            # i번째 댓글 처리
            reply = reply_elements.nth(i)
            
            # 요소 존재 확인
            author_elem = reply.locator("span.u_cbox_nick")
            regDate_elem = reply.locator("span.u_cbox_date")
            content_elem = reply.locator("span.u_cbox_contents")
            
            if (author_elem.count() > 0 and 
                regDate_elem.count() > 0 and 
                content_elem.count() > 0):
                
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
            
            # 진행 상황 출력 (100개마다)
            if (i + 1) % 100 == 0:
                print(f"  진행: {i + 1}/{comment_count} ({(i+1)/comment_count*100:.1f}%)")
                
        except Exception as e:
            # 개별 댓글 실패는 넘어감
            continue
    
    print(f"\n✅ for문 처리 완료!")
    print(f"처리된 댓글: {comment_count}개")
    print(f"수집된 댓글: {len(comments)}개 (중복 제거 후)")
    print(f"더보기 클릭: {more_count}회")
    
    return comments

def correct_approach_improved():
    """✅ 개선된 방식"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=get_browser_options())
        
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(url, wait_until='networkidle')
            
            page.wait_for_selector("ul.u_cbox_list")
            
            print("✅ 개선된 방식: 더보기 전체 클릭 → for문 순차 처리")
            
            # 최적화된 댓글 수집
            all_comments = collect_all_comments_optimized(page)
            
            return all_comments
            
        except Exception as e:
            print(f"❌ 전체 오류: {e}")
            return []
        finally:
            browser.close()


if __name__ == "__main__":        
    
    comments = correct_approach_improved()    
    
    print(f"전체개수={len(comments)}")
    
    import pprint
    pprint.pprint(comments)