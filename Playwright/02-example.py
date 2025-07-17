from playwright.sync_api import sync_playwright
import time
import os

# img 폴더가 없으면 생성
os.makedirs('img', exist_ok=True)
os.makedirs('video', exist_ok=True)

try:
    with sync_playwright() as p:
        # 브라우저 실행 (동영상 녹화 활성화)
        browser = p.chromium.launch(
            headless=False,  # headless 모드
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # 새 페이지 생성 (동영상 녹화 설정)
        context = browser.new_context(
            record_video_dir="video/",  # 동영상 저장 폴더
            record_video_size={"width": 1920, "height": 1080}  # 동영상 해상도
        )
        page = context.new_page()
        
        print("Playwright 브라우저 실행 성공!")
        
        # 테스트 페이지 이동 (스크린샷 촬영을 위해)
        page.goto('https://google.co.kr')
        page.wait_for_load_state('networkidle')
        
        # 1. 전체화면 모드 (Playwright에서는 viewport 설정으로 구현)
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.screenshot(path='img/fullscreen.png', full_page=True)
        viewport = page.viewport_size
        print(f'fullscreen=width: {viewport["width"]}, height: {viewport["height"]}')
        time.sleep(1)
        
        # 2. 최대 창 크기 (데스크톱 크기)
        page.set_viewport_size({"width": 1366, "height": 768})
        page.screenshot(path='img/maximize.png')
        viewport = page.viewport_size
        print(f'maximize=width: {viewport["width"]}, height: {viewport["height"]}')
        time.sleep(1)
        
        # 3. 특정 크기로 설정
        page.set_viewport_size({"width": 500, "height": 500})
        page.screenshot(path='img/set_rect.png')
        viewport = page.viewport_size
        print(f'set_rect=width: {viewport["width"]}, height: {viewport["height"]}')
        time.sleep(1)
        
        # 4. 모바일 사이즈 (iPhone 6/7/8)
        page.set_viewport_size({"width": 375, "height": 667})
        page.screenshot(path='img/mobile.png')
        viewport = page.viewport_size
        print(f'mobile=width: {viewport["width"]}, height: {viewport["height"]}')
        time.sleep(1)
        
        # 5. 태블릿 사이즈 (iPad)
        page.set_viewport_size({"width": 768, "height": 1024})
        page.screenshot(path='img/tablet.png')
        viewport = page.viewport_size
        print(f'tablet=width: {viewport["width"]}, height: {viewport["height"]}')
        time.sleep(1)
        
        # 6. 최종 크기 설정
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 3초 대기
        time.sleep(3)
        
        # 전체 페이지 스크린샷 (스크롤 포함)
        page.screenshot(path='img/full_page.png', full_page=True)
        print("전체 페이지 스크린샷 저장 완료!")
        
        # 브라우저 종료 (동영상 자동 저장됨)
        context.close()
        browser.close()
        
        print("테스트 완료!")
        print("스크린샷: img/ 폴더에 저장됨")
        print("동영상: videos/ 폴더에 저장됨")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()