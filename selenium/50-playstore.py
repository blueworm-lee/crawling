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

# 리니지M
# url = "https://play.google.com/store/apps/details?id=com.ncsoft.lineagem19&pcampaignid=merch_published_cluster_promotion_battlestar_evergreen_dynasty_games"

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

def collect_reviews_with_scroll(driver, max_reviews=100):
    """실제 HTML 구조 기반 리뷰 수집"""
    
    collected_reviews = []
    seen_review_ids = set()  # 중복 방지용
    scroll_attempts = 0
    max_scroll_attempts = 100
    
    print("리뷰 수집 시작...")
    
    # 모달 확인
    try:
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
        )
        print("모달 발견!")
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
    
    while len(collected_reviews) < max_reviews and scroll_attempts < max_scroll_attempts:
        scroll_attempts += 1
        print(f"\n=== 스크롤 시도 {scroll_attempts}/{max_scroll_attempts} ===")
        
        try:
            # 메인 컨테이너 찾기
            review_container = driver.find_element(By.CSS_SELECTOR, "div.odk6He")
            print(f"✓ 리뷰 컨테이너 발견!")
            
            # 개별 리뷰들 찾기
            review_elements = review_container.find_elements(By.CSS_SELECTOR, "div.RHo1pe")
            print(f"발견된 개별 리뷰: {len(review_elements)}개")
            
            new_reviews_count = 0
            
            for idx, review_element in enumerate(review_elements):
                if len(collected_reviews) >= max_reviews:
                    break
                
                try:
                    # 고유 식별자로 data-review-id 사용
                    review_id = None
                    try:
                        header = review_element.find_element(By.CSS_SELECTOR, "header.c1bOId")
                        review_id = header.get_attribute("data-review-id")
                    except:
                        # data-review-id가 없으면 내용 기반으로 ID 생성
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
                        review_id = f"{author}_{hash(content[:50])}"
                    
                    # 중복 확인
                    if review_id in seen_review_ids:
                        continue
                    
                    seen_review_ids.add(review_id)
                    
                    # 리뷰 저장
                    review_data = {
                        "id": review_id,
                        "author": author,
                        "date": date,
                        "content": content,
                        "rating": rating,
                        "index": len(collected_reviews) + 1
                    }
                    
                    collected_reviews.append(review_data)
                    new_reviews_count += 1
                    
                    print(f"  ✓ [{len(collected_reviews)}] {author}: {content[:50]}...")
                    
                except Exception as e:
                    print(f"  ✗ 리뷰 {idx+1} 처리 실패: {e}")
                    continue
            
            print(f"이번 라운드 수집: +{new_reviews_count}개, 총: {len(collected_reviews)}개")
            
            # 목표 달성 시 종료
            if len(collected_reviews) >= max_reviews:
                print(f"🎉 목표 {max_reviews}개 달성!")
                break
            
            # 새로운 리뷰가 없으면 종료
            if new_reviews_count == 0:
                print("더 이상 새로운 리뷰가 없습니다.")
                break
            
        except Exception as e:
            print(f"리뷰 컨테이너 찾기 실패: {e}")
        
        # 스크롤 수행
        print("스크롤 중...")
        try:
            if scroll_container:
                # 스크롤 컨테이너 내에서 스크롤
                driver.execute_script("""
                    arguments[0].scrollTop += 1000;
                """, scroll_container)
                print("  → 컨테이너 스크롤 완료")
            else:
                # 모달 전체 스크롤
                driver.execute_script("""
                    var modal = document.querySelector('div[role="dialog"]');
                    if (modal) {
                        modal.scrollTop += 1000;
                    }
                """)
                print("  → 모달 스크롤 완료")
        except Exception as e:
            print(f"  ✗ 스크롤 실패: {e}")
        
        # 로딩 대기
        time.sleep(3)
    
    print(f"\n🎯 수집 완료: 총 {len(collected_reviews)}개 리뷰")
    return collected_reviews


# 리뷰 수집 실행
print("=== 리뷰 수집 시작 ===")
reviews = collect_reviews_with_scroll(driver, max_reviews=50)

# 결과 출력 및 저장
print(f"\n=== 수집 결과 ===")
print(f"총 리뷰 개수: {len(reviews)}")

if reviews:
    # 샘플 출력
    print("\n=== 샘플 리뷰 ===")
    for i, review in enumerate(reviews[:3]):
        print(f"\n--- 리뷰 {i+1} ---")
        print(f"작성자: {review['author']}")
        print(f"날짜: {review['date']}")
        print(f"평점: {review['rating']}")
        print(f"내용: {review['content'][:100]}...")
    
    # 파일 저장
    try:
        with open('archeage_war_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        print(f"\n💾 리뷰 데이터를 archeage_war_reviews.json 파일로 저장했습니다.")
    except Exception as e:
        print(f"파일 저장 실패: {e}")
    
    # 통계 출력
    print(f"\n=== 통계 ===")
    rating_counts = {}
    for review in reviews:
        rating = review['rating']
        if '1개' in rating:
            rating_counts['1점'] = rating_counts.get('1점', 0) + 1
        elif '2개' in rating:
            rating_counts['2점'] = rating_counts.get('2점', 0) + 1
        elif '3개' in rating:
            rating_counts['3점'] = rating_counts.get('3점', 0) + 1
        elif '4개' in rating:
            rating_counts['4점'] = rating_counts.get('4점', 0) + 1
        elif '5개' in rating:
            rating_counts['5점'] = rating_counts.get('5점', 0) + 1
    
    for rating, count in rating_counts.items():
        print(f"{rating}: {count}개")

else:
    print("수집된 리뷰가 없습니다.")

print("\n✅ 작업 완료!")

driver.quit()