from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common import get_chrome_options
import sys
import signal
import time
import platform
import json
import os


driver = None
def signal_handler(sig, frame):
    print('\nCtrl+C 감지됨. 드라이버 종료 중...')
    if driver:
        try:
            driver.quit()
        except:
            pass
    os._exit(0)

if platform.system() == "Windows":
    signal.signal(signal.SIGINT, signal_handler)
else:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

# 아키에이지
url = "https://play.google.com/store/apps/details?id=com.kakaogames.archewar&pcampaignid=merch_published_cluster_promotion_battlestar_evergreen_dynasty_games"

print("Chrome 드라이버 시작...")
driver = webdriver.Chrome(options=get_chrome_options())
driver.set_window_size(1920, 1080)
driver.implicitly_wait(1)

print("페이지 로딩...")
driver.get(url)
time.sleep(3)

def click_see_all_reviews(driver):
    print("리뷰 모두 보기 버튼 찾는 중...")
    
    methods = [
        ("텍스트 기반", lambda: driver.find_element(By.XPATH, "//button[contains(., '리뷰 모두 보기')]")),
        ("span직접", lambda: driver.find_element(By.CSS_SELECTOR, "span[jsname='V67aGc']")),
    ]
    
    for position in [1000, 2000, 3000]:
        driver.execute_script(f"window.scrollTo(0, {position});")
        time.sleep(1)

        for method_name, method in methods:
            try:
                element = method()
                if element.is_displayed() and element.is_enabled():
                    driver.execute_script("arguments[0].click();", element)
                    print(f"{method_name} 방법으로 클릭 성공!")
                    return True
            except:
                continue
    
    return False

if not click_see_all_reviews(driver):    
    print("리뷰 모두 보기 클릭 실패")
    driver.quit()
    sys.exit(0)

########### 리뷰 모두 보기 선택 완료
time.sleep(5)

def get_current_reviews_data(driver):
    """현재 화면의 리뷰 데이터를 가져오는 함수"""
    current_reviews = []
    
    try:
        # 메인 컨테이너 찾기
        review_container = driver.find_element(By.CSS_SELECTOR, "div.odk6He")
        
        # 개별 리뷰들 찾기
        review_elements = review_container.find_elements(By.CSS_SELECTOR, "div.RHo1pe")
        
        for review_element in review_elements:
            try:
                # 고유 식별자로 data-review-id 사용
                review_id = None
                try:
                    header = review_element.find_element(By.CSS_SELECTOR, "header.c1bOId")
                    review_id = header.get_attribute("data-review-id")
                except:
                    pass
                
                # 리뷰 데이터 추출
                author = "Unknown"
                content = "No content"
                date = "Unknown"
                rating = "No rating"
                
                # 작성자 추출
                try:
                    author_elem = review_element.find_element(By.CSS_SELECTOR, "div.X5PpBb")
                    author = author_elem.text.strip()
                except:
                    pass
                
                # 리뷰 내용 추출
                try:
                    content_elem = review_element.find_element(By.CSS_SELECTOR, "div.h3YV2d")
                    content = content_elem.text.strip()
                except:
                    pass
                
                # 날짜 추출
                try:
                    date_elem = review_element.find_element(By.CSS_SELECTOR, "span.bp9Aid")
                    date = date_elem.text.strip()
                except:
                    pass
                
                # 평점 추출
                try:
                    rating_container = review_element.find_element(By.CSS_SELECTOR, "div.Jx4nYe")
                    rating_elem = rating_container.find_element(By.CSS_SELECTOR, "div[role='img']")
                    rating = rating_elem.get_attribute("aria-label")
                    if not rating:
                        # 별 개수 세기
                        filled_stars = rating_container.find_elements(By.CSS_SELECTOR, "span.Z1Dz7b")
                        rating = f"별표 5개 만점에 {len(filled_stars)}개"
                except:
                    pass
                
                # 유효성 검사
                if author == "Unknown" and content == "No content":
                    continue
                
                # 고유 ID 생성 (review_id가 없는 경우)
                if not review_id:
                    review_id = f"{author}_{hash(content[:100])}"
                
                review_data = {
                    "id": review_id,
                    "author": author,
                    "date": date,
                    "content": content,
                    "rating": rating
                }
                
                current_reviews.append(review_data)
                
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"리뷰 컨테이너 찾기 실패: {e}")
    
    return current_reviews

def has_new_reviews(current_reviews, buffer_reviews):
    """현재 리뷰에 버퍼에 없는 새로운 리뷰가 있는지 확인"""
    buffer_ids = {review['id'] for review in buffer_reviews}
    
    for review in current_reviews:
        if review['id'] not in buffer_ids:
            return True
    return False

def smart_scroll(driver, scroll_container, step_size=300, max_attempts=100):
    """스마트 스크롤: 새로운 리뷰가 나타날 때까지 스크롤"""
    buffer_reviews = get_current_reviews_data(driver)
    
    for attempt in range(max_attempts):
        # 스크롤 수행
        try:
            if scroll_container:
                driver.execute_script(f"arguments[0].scrollTop += {step_size};", scroll_container)
            else:
                driver.execute_script(f"""
                    var modal = document.querySelector('div[role="dialog"]');
                    if (modal) {{
                        modal.scrollTop += {step_size};
                    }}
                """)
        except Exception as e:
            print(f"스크롤 실패: {e}")
            return False
        
        # 로딩 대기
        time.sleep(2)
        
        # 현재 리뷰 확인
        current_reviews = get_current_reviews_data(driver)
        
        print(f"  스크롤 시도 {attempt + 1}: 현재 {len(current_reviews)}개 리뷰 발견")
        
        # 새로운 리뷰가 있는지 확인
        if has_new_reviews(current_reviews, buffer_reviews):
            print(f"  ✓ 새로운 리뷰 발견! {step_size * (attempt + 1)}px 스크롤 완료")
            return True
        
        # 스크롤이 더 이상 안 되는지 확인 (페이지 끝)
        try:
            if scroll_container:
                current_scroll = driver.execute_script("return arguments[0].scrollTop;", scroll_container)
                max_scroll = driver.execute_script("return arguments[0].scrollHeight - arguments[0].clientHeight;", scroll_container)
            else:
                current_scroll = driver.execute_script("""
                    var modal = document.querySelector('div[role="dialog"]');
                    return modal ? modal.scrollTop : 0;
                """)
                max_scroll = driver.execute_script("""
                    var modal = document.querySelector('div[role="dialog"]');
                    return modal ? modal.scrollHeight - modal.clientHeight : 0;
                """)
            
            if current_scroll >= max_scroll:
                print("  ! 페이지 끝에 도달했습니다.")
                return False
                
        except:
            pass
    
    print(f"  ! {max_attempts}번 시도 후에도 새로운 리뷰가 없습니다.")
    return False

def collect_reviews_with_smart_scroll(driver, max_reviews=1000):
    """스마트 스크롤 및 메모리 관리가 적용된 리뷰 수집"""
    
    total_collected_reviews = []  # 전체 리뷰 저장소
    buffer_reviews = []  # 현재 버퍼 (중복 체크용)
    buffer_max_size = 100  # 버퍼 최대 크기
    buffer_keep_size = 50   # 버퍼 정리 시 유지할 크기
    
    scroll_attempts = 0
    max_scroll_attempts = 200
    consecutive_no_new = 0
    max_consecutive_no_new = 3
    
    print("리뷰 수집 시작...")
    
    # 모달 확인
    try:
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
        )
        print("✓ 모달 발견!")
    except:
        print("✗ 모달을 찾을 수 없습니다.")
        return []
    
    # 스크롤 컨테이너 찾기
    scroll_container = None
    try:
        scroll_container = driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] div.fysCi")
        print("✓ 스크롤 컨테이너 발견!")
    except:
        print("! 스크롤 컨테이너를 찾을 수 없어 모달 전체를 사용합니다.")
    
    while len(total_collected_reviews) < max_reviews and scroll_attempts < max_scroll_attempts:
        scroll_attempts += 1
        print(f"\n=== 스크롤 라운드 {scroll_attempts}/{max_scroll_attempts} ===")
        
        # 현재 화면의 리뷰 데이터 가져오기
        current_reviews = get_current_reviews_data(driver)
        print(f"현재 화면에서 {len(current_reviews)}개 리뷰 발견")
        
        # 버퍼에서 ID 세트 생성 (중복 체크용)
        buffer_ids = {review['id'] for review in buffer_reviews}
        
        # 새로운 리뷰만 필터링
        new_reviews = []
        for review in current_reviews:
            if review['id'] not in buffer_ids:
                new_reviews.append(review)
                buffer_reviews.append(review)
        
        if new_reviews:
            print(f"✓ {len(new_reviews)}개 새로운 리뷰 수집!")
            consecutive_no_new = 0
            
            # 새로운 리뷰 출력
            for review in new_reviews:
                print(f"  [{len(total_collected_reviews) + len(buffer_reviews)}] {review['author']}: {review['content'][:50]}...")
        else:
            consecutive_no_new += 1
            print(f"! 새로운 리뷰 없음 (연속 {consecutive_no_new}회)")
        
        # 연속으로 새로운 리뷰가 없으면 종료
        if consecutive_no_new >= max_consecutive_no_new:
            print(f"연속 {max_consecutive_no_new}회 새로운 리뷰가 없어 종료합니다.")
            break
        
        # 버퍼 크기 관리
        if len(buffer_reviews) >= buffer_max_size:
            print(f"버퍼 크기 관리: {len(buffer_reviews)}개 -> {buffer_keep_size}개 유지")
            
            # 오래된 리뷰들을 전체 저장소로 이동
            reviews_to_move = buffer_reviews[:-buffer_keep_size]
            total_collected_reviews.extend(reviews_to_move)
            
            # 버퍼에는 최근 리뷰들만 유지
            buffer_reviews = buffer_reviews[-buffer_keep_size:]
            
            print(f"전체 저장소: {len(total_collected_reviews)}개, 버퍼: {len(buffer_reviews)}개")
        
        # 목표 달성 확인
        total_count = len(total_collected_reviews) + len(buffer_reviews)
        if total_count >= max_reviews:
            print(f"🎉 목표 {max_reviews}개 달성! (전체: {total_count}개)")
            break
        
        # 스마트 스크롤 수행
        print("스마트 스크롤 수행...")
        if not smart_scroll(driver, scroll_container):
            print("더 이상 스크롤할 수 없습니다.")
            break
        
        print(f"현재 진행상황: 전체저장소 {len(total_collected_reviews)}개 + 버퍼 {len(buffer_reviews)}개 = {len(total_collected_reviews) + len(buffer_reviews)}개")
    
    # 남은 버퍼의 리뷰들도 전체 저장소로 이동
    total_collected_reviews.extend(buffer_reviews)
    
    print(f"\n🎯 수집 완료: 총 {len(total_collected_reviews)}개 리뷰")
    return total_collected_reviews

# 리뷰 수집 실행
print("=== 리뷰 수집 시작 ===")
reviews = collect_reviews_with_smart_scroll(driver, max_reviews=200)

# 결과 출력 및 저장
print(f"\n=== 수집 결과 ===")
print(f"총 리뷰 개수: {len(reviews)}")

# if reviews:
#     # 중복 제거 (혹시 모를 중복 제거)
#     unique_reviews = []
#     seen_ids = set()
#     for review in reviews:
#         if review['id'] not in seen_ids:
#             unique_reviews.append(review)
#             seen_ids.add(review['id'])
    
#     print(f"중복 제거 후: {len(unique_reviews)}개")
    
#     # 인덱스 번호 재할당
#     for i, review in enumerate(unique_reviews):
#         review['index'] = i + 1
    
#     # 샘플 출력
#     print("\n=== 샘플 리뷰 ===")
#     for i, review in enumerate(unique_reviews[:5]):
#         print(f"\n--- 리뷰 {i+1} ---")
#         print(f"작성자: {review['author']}")
#         print(f"날짜: {review['date']}")
#         print(f"평점: {review['rating']}")
#         print(f"내용: {review['content'][:100]}...")
    
#     # 파일 저장
#     try:
#         with open('archeage_war_reviews_smart.json', 'w', encoding='utf-8') as f:
#             json.dump(unique_reviews, f, ensure_ascii=False, indent=2)
#         print(f"\n💾 리뷰 데이터를 archeage_war_reviews_smart.json 파일로 저장했습니다.")
#     except Exception as e:
#         print(f"파일 저장 실패: {e}")
    
#     # 통계 출력
#     print(f"\n=== 통계 ===")
#     rating_counts = {}
#     for review in unique_reviews:
#         rating = review['rating']
#         if '1개' in rating:
#             rating_counts['1점'] = rating_counts.get('1점', 0) + 1
#         elif '2개' in rating:
#             rating_counts['2점'] = rating_counts.get('2점', 0) + 1
#         elif '3개' in rating:
#             rating_counts['3점'] = rating_counts.get('3점', 0) + 1
#         elif '4개' in rating:
#             rating_counts['4점'] = rating_counts.get('4점', 0) + 1
#         elif '5개' in rating:
#             rating_counts['5점'] = rating_counts.get('5점', 0) + 1
    
#     for rating, count in rating_counts.items():
#         print(f"{rating}: {count}개")

# else:
#     print("수집된 리뷰가 없습니다.")

print("\n✅ 작업 완료!")
driver.quit()