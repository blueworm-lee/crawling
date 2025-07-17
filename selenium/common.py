import os
import glob
from selenium.webdriver.chrome.options import Options

def removePng():
    [os.remove(f) for f in glob.glob('img/*')]


def get_chrome_options():   
    options = Options()
    # options.add_argument('--headless')  # 헤드리스 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-images')  # 이미지 로딩 안함
    # options.add_argument('--disable-javascript')  # JS 필요없으면 비활성화
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-extensions')
    # options.add_argument('--page-load-strategy=eager')  # 빠른 로딩 전략

    # 언어설정
    options.add_argument('--lang=ko-KR')
    options.add_argument('--accept-lang=ko-KR,ko,en-US,en')
    
    # 지역 설정
    options.add_experimental_option('prefs', {
        'intl.accept_languages': 'ko-KR,ko,en-US,en',
        'profile.default_content_setting_values.geolocation': 1
    })
    
    # User-Agent 설정 (한국 사용자)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
    


    return options
