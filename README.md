# 웹 크롤러 데스크탑 앱

Python과 tkinter를 사용한 간단한 웹 크롤링 데스크탑 애플리케이션입니다.

## 기능

### 크롤링 엔진
- **requests**: 빠른 정적 페이지 크롤링
- **Selenium**: 동적 페이지 크롤링 (JavaScript 지원)
- **Playwright**: 고성능 브라우저 자동화 (권장)

### 데이터 추출
- 페이지 정보 표시 (제목, URL, 상태코드 등)
- 링크 추출 및 표시
- 이미지 URL 추출 및 표시
- 텍스트 내용 추출 및 표시
- 사이트별 특화 크롤링 (네이버 쇼핑, 인스타그램, 부동산)

### 고급 기능
- 여러 페이지 자동 순회
- 크롤링 간격 설정 (봇 차단 방지)
- 재시도 로직 (최대 3회)
- 엑셀 파일 저장 (한글 지원)
- 실시간 진행률 표시

### 시스템
- 크로스 플랫폼 지원 (Windows, macOS, Linux)
- GUI 인터페이스 (tkinter)
- 독립 실행 파일 생성 (PyInstaller)
- Windows 인스톨러 (Inno Setup)

## 설치 및 실행

### 1. 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
python main.py
```

## 사용 방법

1. 애플리케이션을 실행합니다
2. URL 입력란에 크롤링하고 싶은 웹사이트 주소를 입력합니다
3. 추출하고 싶은 데이터 유형을 체크박스로 선택합니다
4. "크롤링 시작" 버튼을 클릭합니다
5. 결과를 탭별로 확인합니다

## 요구사항

### 기본 요구사항
- Python 3.8+ (권장)
- tkinter (Python 기본 내장)

### 패키지 의존성
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.2
- lxml >= 4.9.3
- openpyxl >= 3.1.2
- pandas >= 2.0.0
- selenium >= 4.15.0
- webdriver-manager >= 4.0.0
- playwright >= 1.40.0 (선택사항)

### Playwright 추가 설치 (고급 기능)
```bash
# Playwright 설치
pip install playwright

# 브라우저 설치 (필수)
playwright install
```

## 주의사항

- 일부 웹사이트는 크롤링을 제한할 수 있습니다
- robots.txt 및 웹사이트 이용약관을 준수해주세요
- 과도한 요청은 서버에 부하를 줄 수 있으니 적절히 사용해주세요 