# 웹 크롤러 실행 파일 빌드 가이드

## 개요
이 가이드는 웹 크롤러 Python 앱을 독립 실행 파일(.exe, 실행파일)로 변환하는 방법을 설명합니다.

## 필요한 준비사항

### 1. Python 환경
- Python 3.8 이상 설치
- pip 최신 버전

### 2. 아이콘 파일 (선택사항)
- `app_icon.ico` 파일을 실제 아이콘으로 교체
- 권장 크기: 256x256 또는 32x32 픽셀
- 무료 아이콘 사이트:
  - [Flaticon](https://www.flaticon.com/)
  - [IconFinder](https://www.iconfinder.com/)
  - [Iconify](https://iconify.design/)

## 빌드 방법

### Windows에서 빌드

#### 방법 1: 빌드 스크립트 사용 (권장)
```batch
# 빌드 스크립트 실행
build.bat
```

#### 방법 2: 수동 빌드
```batch
# 1. 가상환경 활성화 (있는 경우)
venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. PyInstaller로 빌드
pyinstaller crawler_app.spec --clean

# 또는 기본 명령어
pyinstaller --onefile --windowed --name="웹크롤러" --icon=app_icon.ico main.py
```

### macOS/Linux에서 빌드

#### 방법 1: 빌드 스크립트 사용 (권장)
```bash
# 스크립트 실행 권한 부여
chmod +x build.sh

# 빌드 스크립트 실행
./build.sh
```

#### 방법 2: 수동 빌드
```bash
# 1. 가상환경 활성화 (있는 경우)
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. PyInstaller로 빌드
pyinstaller crawler_app.spec --clean

# 또는 기본 명령어
pyinstaller --onefile --windowed --name="웹크롤러" main.py
```

## 빌드 옵션 설명

### PyInstaller 주요 옵션
- `--onefile`: 모든 의존성을 하나의 실행 파일로 패키징
- `--windowed`: 콘솔 창 숨김 (GUI 앱용)
- `--icon`: 실행 파일 아이콘 설정
- `--name`: 실행 파일 이름 지정
- `--clean`: 빌드 전 캐시 정리
- `--add-data`: 추가 데이터 파일 포함

### .spec 파일 옵션
- `console=False`: 콘솔 창 숨김
- `upx=True`: UPX 압축 사용 (파일 크기 감소)
- `datas`: 포함할 데이터 파일들
- `hiddenimports`: 자동 감지되지 않는 모듈들

## 빌드 결과

### 성공적인 빌드
```
dist/
└── 웹크롤러.exe (Windows)
└── 웹크롤러 (macOS/Linux)
```

### 예상 파일 크기
- Windows: 약 150-200MB
- macOS: 약 120-180MB
- Linux: 약 120-180MB

## 문제 해결

### 1. 모듈을 찾을 수 없음 오류
```bash
# 누락된 모듈을 hiddenimports에 추가
# crawler_app.spec 파일 수정
hiddenimports += ['누락된_모듈명']
```

### 2. tkinter 관련 오류
```bash
# Windows에서 tkinter 설치
pip install tk

# macOS에서 tkinter 설치
brew install python-tk
```

### 3. selenium webdriver 오류
- WebDriver는 자동으로 다운로드됨
- 인터넷 연결 필요
- 방화벽에서 Chrome/Firefox 허용 필요

### 4. 파일 크기가 너무 큰 경우
```python
# .spec 파일에서 불필요한 모듈 제외
excludes=['module1', 'module2']
```

### 5. 실행 시 오류
- 백신 프로그램에서 실행 파일 허용
- Windows Defender 예외 추가
- 관리자 권한으로 실행

## 배포 전 확인사항

### 1. 테스트 환경에서 실행
- 다른 컴퓨터에서 테스트
- Python이 설치되지 않은 환경에서 테스트

### 2. 기능 확인
- 모든 크롤링 기능 정상 작동
- 엑셀 저장 기능 정상 작동
- Selenium 브라우저 자동 설치 확인

### 3. 성능 확인
- 실행 속도 확인
- 메모리 사용량 확인
- 임시 파일 자동 정리 확인

## 고급 최적화

### 1. 파일 크기 최소화
```python
# .spec 파일에 추가
excludes=['test', 'unittest', 'pdb', 'doctest']
```

### 2. 시작 속도 개선
```python
# lazy import 사용
import importlib
module = importlib.import_module('module_name')
```

### 3. 메모리 최적화
```python
# 불필요한 의존성 제거
# requirements.txt에서 사용하지 않는 패키지 제거
```

## 자동화 스크립트

### GitHub Actions (CI/CD)
```yaml
name: Build Release
on:
  push:
    tags:
      - 'v*'
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pyinstaller crawler_app.spec --clean
      - uses: actions/upload-artifact@v2
        with:
          name: 웹크롤러
          path: dist/
```

이제 `build.bat` (Windows) 또는 `./build.sh` (macOS/Linux)를 실행하면 독립 실행 파일이 생성됩니다! 