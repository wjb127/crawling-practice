# Playwright 설치 및 설정 가이드

## Playwright란?

Playwright는 Microsoft에서 개발한 현대적인 웹 브라우저 자동화 도구입니다. Selenium보다 빠르고 안정적이며, 더 많은 기능을 제공합니다.

## 주요 장점

### 성능
- **속도**: Selenium보다 2-3배 빠름
- **안정성**: 요소 대기 및 선택이 더 안정적
- **병렬 처리**: 여러 브라우저 컨텍스트 동시 실행

### 기능
- **네트워크 인터셉션**: 요청/응답 가로채기 및 수정
- **스크린샷**: 전체 페이지 또는 요소별 캡처
- **다중 브라우저**: Chromium, Firefox, WebKit 지원
- **모바일 에뮬레이션**: 다양한 디바이스 시뮬레이션

### 개발자 경험
- **디버깅**: 향상된 디버깅 도구
- **추적**: 실행 과정 시각화
- **코드 생성**: 브라우저 작업을 코드로 자동 생성

## 설치 방법

### 1. Python 패키지 설치

```bash
# 가상환경 활성화 (권장)
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# Playwright 설치
pip install playwright
```

### 2. 브라우저 설치

Playwright는 브라우저를 별도로 다운로드해야 합니다:

```bash
# 모든 브라우저 설치 (권장)
playwright install

# 특정 브라우저만 설치
playwright install chromium
playwright install firefox
playwright install webkit
```

### 3. 시스템 의존성 설치 (Linux)

Linux에서는 추가 시스템 패키지가 필요할 수 있습니다:

```bash
# Ubuntu/Debian
playwright install-deps

# 또는 수동으로
sudo apt-get install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

## 웹 크롤러에서 사용법

### 브라우저 모드 선택

프로그램 실행 후:
1. 브라우저 모드 드롭다운에서 **"playwright"** 선택
2. 크롤링하고 싶은 URL 입력
3. "크롤링 시작" 버튼 클릭

### 권장 사용 시나리오

#### Playwright 사용 권장:
- ✅ React, Vue, Angular 등 SPA 사이트
- ✅ 무한 스크롤이 있는 사이트
- ✅ 로그인이 필요한 사이트
- ✅ JavaScript로 동적으로 로드되는 콘텐츠
- ✅ 복잡한 상호작용이 필요한 사이트

#### requests 사용 권장:
- ✅ 정적 HTML 사이트
- ✅ 빠른 속도가 중요한 경우
- ✅ 간단한 페이지 구조

#### Selenium vs Playwright:
- 🔄 Selenium: 기존 프로젝트와의 호환성
- 🚀 Playwright: 새로운 프로젝트, 더 나은 성능

## 브라우저별 특징

### Chromium (기본)
- **장점**: 가장 빠름, 높은 호환성
- **용도**: 일반적인 크롤링 작업
- **단점**: 메모리 사용량이 높음

### Firefox
- **장점**: 개인정보 보호 기능
- **용도**: 특정 사이트에서 더 나은 호환성
- **단점**: 약간 느림

### WebKit (Safari 엔진)
- **장점**: macOS/iOS 호환성 테스트
- **용도**: Safari 사용자 대상 사이트
- **단점**: 일부 기능 제한

## 고급 설정

### 1. 헤드리스 모드 비활성화 (디버깅용)

```python
# setup_playwright_browser 메서드에서
self.browser = self.playwright.chromium.launch(
    headless=False,  # 브라우저 창 표시
    slow_mo=1000     # 1초씩 천천히 실행
)
```

### 2. 프록시 설정

```python
self.browser = self.playwright.chromium.launch(
    proxy={
        "server": "http://proxy-server:port",
        "username": "username",
        "password": "password"
    }
)
```

### 3. 사용자 에이전트 변경

```python
context = self.browser.new_context(
    user_agent="Custom User Agent String"
)
```

## 문제 해결

### 1. 설치 오류

**문제**: `playwright install` 실패
```bash
# 해결: 관리자 권한으로 실행
sudo playwright install  # Linux/macOS
# 또는 PowerShell을 관리자로 실행 후 설치 (Windows)
```

**문제**: 브라우저 다운로드 실패
```bash
# 해결: 네트워크 설정 확인
export PLAYWRIGHT_DOWNLOAD_HOST=https://playwright.azureedge.net
playwright install
```

### 2. 실행 오류

**문제**: "Browser executable not found"
```bash
# 해결: 브라우저 재설치
playwright install --force
```

**문제**: 리눅스에서 라이브러리 오류
```bash
# 해결: 의존성 설치
playwright install-deps
```

### 3. 성능 최적화

**메모리 사용량 줄이기**:
```python
# 컨텍스트 옵션 조정
context = self.browser.new_context(
    viewport={'width': 1280, 'height': 720},  # 작은 뷰포트
    java_script_enabled=False,  # JS 비활성화 (필요시)
    images_enabled=False        # 이미지 로드 비활성화
)
```

**속도 향상**:
```python
# 페이지 로드 타임아웃 단축
page.goto(url, timeout=5000)  # 5초로 제한
```

## 버전별 호환성

### Python 버전
- **Python 3.8+**: 완전 지원
- **Python 3.7**: 제한적 지원
- **Python 3.6 이하**: 지원 안 함

### 운영체제
- **Windows 10+**: 완전 지원
- **macOS 10.14+**: 완전 지원
- **Linux**: Ubuntu 18.04+ 권장

## 라이선스

Playwright는 Apache 2.0 라이선스로 무료로 사용할 수 있습니다.

## 추가 자료

- [공식 문서](https://playwright.dev/python/)
- [GitHub 저장소](https://github.com/microsoft/playwright-python)
- [예제 코드](https://github.com/microsoft/playwright-python/tree/main/examples)
- [커뮤니티 포럼](https://github.com/microsoft/playwright/discussions)

---

이제 더 빠르고 안정적인 Playwright로 웹 크롤링을 시작해보세요! 🚀 