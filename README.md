## Selenium 설치 for Windows
```
> python --version
Python 3.13.3
 
> pip install selenium
 
> pip install webdriver-manager
```

## Selenium 설치 for Linux  
```
######### Chrome 브라우저 설치
# Google 서명 키 다운로드 및 추가
> sudo rpm --import https://dl.google.com/linux/linux_signing_key.pub
 
# Chrome 저장소 파일 생성
> sudo tee /etc/yum.repos.d/google-chrome.repo > /dev/null <<'EOF'
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF
 
# 설치
> sudo dnf install -y google-chrome-stable
 
# 설치 확인
> google-chrome --version
Google Chrome 138.0.7204.92
>

######### ChromeDriver 설치
# 버전 확인
> curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
{"timestamp":"2025-06-30T21:09:36.285Z","channels":{"Stable":{"channel":"Stable","version":"138.0.7204.92","revision":"1465706"},"Beta":{"channel":"Beta","version":"139.0.7258.5","revision":"1477651"},"Dev":{"channel":"Dev","version":"140.0.7259.2","revision":"1478297"},"Canary":{"channel":"Canary","version":"140.0.7269.0","revision":"1480320"}}}
 
> LATEST_VERSION="138.0.7204.92"
> echo "Using version: $LATEST_VERSION"
 
# 다운로드
> wget -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/${LATEST_VERSION}/linux64/chromedriver-linux64.zip"
 
 
# 압축해제 및 파일 이동
> cd /tmp
> unzip chromedriver-linux64.zip
> mv chromedriver-linux64/chromedriver /usr/local/bin/
> chmod +x /usr/local/bin/chromedriver
> ./chromedriver --version
ChromeDriver 138.0.7204.92 (f079b9bc781e3c2adb1496ea1d72812deb0ddb3d-refs/branch-heads/7204_50@{#8})
```



## Playwright 설치
```
# Playwright 패키지 설치
> pip install playwright
 
# 전용 브라우저 설치
> python -m playwright install chromium
```
