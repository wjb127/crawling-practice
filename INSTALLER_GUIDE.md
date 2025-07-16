# SmartCrawler Pro 인스톨러 생성 가이드

## 개요
이 가이드는 SmartCrawler Pro용 전문적인 Windows 인스톨러를 생성하는 방법을 설명합니다.

## 필요한 도구

### 1. Inno Setup 다운로드 및 설치
- **다운로드**: [https://jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php)
- **권장 버전**: Inno Setup 6.x (최신 버전)
- **설치 경로**: 기본 경로 사용 권장

### 2. 필요한 파일 확인
```
프로젝트 폴더/
├── dist/웹크롤러.exe          # PyInstaller로 생성된 실행 파일
├── WebCrawler_Setup.iss       # Inno Setup 스크립트
├── LICENSE.txt                # 라이선스 파일
├── README_INSTALL.txt         # 설치 전 안내
├── INSTALLATION_COMPLETE.txt  # 설치 완료 안내
├── app_icon.ico              # 아이콘 파일 (실제 ico 파일로 교체)
└── build_installer.bat       # 자동 빌드 스크립트
```

## 인스톨러 생성 과정

### 방법 1: 자동 빌드 스크립트 사용 (권장)
```batch
# 1단계: exe 파일 생성
build.bat

# 2단계: 인스톨러 생성
build_installer.bat
```

### 방법 2: 수동 빌드
```batch
# Inno Setup 컴파일러 실행
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" WebCrawler_Setup.iss
```

### 방법 3: Inno Setup IDE 사용
1. Inno Setup을 실행
2. `WebCrawler_Setup.iss` 파일 열기
3. Build → Compile 메뉴 선택

## 인스톨러 설정 상세

### 기본 정보
- **앱 이름**: SmartCrawler Pro
- **회사명**: CrawlTech Solutions
- **버전**: 1.0.0
- **설치 경로**: `C:\Program Files\SmartCrawler Pro\`

### 설치 기능
✅ **바탕화면 바로가기** (선택 가능)
✅ **시작 메뉴 등록** (자동)
✅ **빠른 실행 바로가기** (선택 가능)
✅ **언인스톨러 포함** (자동)
✅ **라이선스 동의** (필수)

### 고급 기능
- **이전 버전 자동 제거**
- **시스템 요구사항 확인** (Windows 7+)
- **레지스트리 등록**
- **임시 파일 자동 정리**

## 인스톨러 커스터마이징

### 1. 아이콘 변경
```iss
SetupIconFile=app_icon.ico
```
- 실제 .ico 파일로 교체 필요
- 권장 크기: 32x32, 48x48, 256x256

### 2. 회사 정보 수정
```iss
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://yourwebsite.com"
```

### 3. 버전 정보 변경
```iss
#define MyAppVersion "1.0.0"
```

### 4. 설치 경로 변경
```iss
DefaultDirName={autopf}\{#MyAppName}
```

### 5. 언어 추가
```iss
[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
```

## 배포 파일 생성

### 인스톨러 빌드 결과
```
installer/
└── SmartCrawler_Pro_Setup_v1.0.0.exe
```

### 배포 패키지 구성
1. **인스톨러**: `SmartCrawler_Pro_Setup_v1.0.0.exe`
2. **독립 실행 파일**: `dist/웹크롤러.exe` (선택사항)
3. **문서**: README, 라이선스 등

## 디지털 서명 (고급)

### 코드 서명 인증서 적용
```iss
[Setup]
SignTool=signtool sign /f "certificate.pfx" /p "password" $f
```

### 인증서 없이 배포 시 주의사항
- Windows Defender SmartScreen 경고 발생 가능
- 사용자가 "추가 정보" → "실행" 선택 필요
- 평판 축적으로 시간이 지나면 경고 감소

## 배포 전 테스트

### 1. 깨끗한 환경에서 테스트
- 가상머신 또는 다른 컴퓨터 사용
- Python이 설치되지 않은 환경에서 테스트

### 2. 기능 테스트
- [ ] 정상 설치 확인
- [ ] 바탕화면 바로가기 생성 확인
- [ ] 시작 메뉴 등록 확인
- [ ] 프로그램 정상 실행 확인
- [ ] 모든 크롤링 기능 확인
- [ ] 언인스톨 정상 작동 확인

### 3. 호환성 테스트
- Windows 7, 8, 10, 11
- 32비트/64비트 시스템
- 다양한 화면 해상도

## 문제 해결

### 1. 빌드 오류
```
Error: Cannot find file 'dist\웹크롤러.exe'
```
→ 먼저 `build.bat`로 exe 파일 생성

### 2. 권한 오류
```
Error: Access denied
```
→ 관리자 권한으로 명령 프롬프트 실행

### 3. 파일 경로 오류
```
Error: File not found
```
→ 모든 파일이 올바른 위치에 있는지 확인

### 4. 한글 파일명 문제
- Inno Setup은 유니코드 지원
- 파일명에 특수문자 주의

## 자동화 및 CI/CD

### GitHub Actions 예제
```yaml
name: Build Installer
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Inno Setup
        run: choco install innosetup
      - name: Build Installer
        run: |
          build.bat
          build_installer.bat
      - name: Upload Installer
        uses: actions/upload-artifact@v2
        with:
          name: SmartCrawler-Installer
          path: installer/*.exe
```

## 배포 플랫폼

### 1. 직접 배포
- 웹사이트에서 직접 다운로드 제공
- 파일 호스팅 서비스 이용

### 2. 소프트웨어 저장소
- Microsoft Store (패키징 필요)
- Chocolatey (Windows 패키지 관리자)
- Ninite (소프트웨어 설치 플랫폼)

### 3. 기업 배포
- Group Policy를 통한 자동 설치
- SCCM을 통한 중앙 관리
- MSI 변환 (필요시)

## 보안 고려사항

### 1. 안티바이러스 대응
- VirusTotal에서 사전 스캔
- 주요 백신사에 false positive 신고
- 코드 서명으로 신뢰성 확보

### 2. 사용자 데이터 보호
- 설치 시 개인정보 수집 최소화
- 크롤링 데이터 로컬 저장
- 네트워크 통신 최소화

이제 전문적인 Windows 인스톨러를 생성할 수 있습니다!
`build_installer.bat`를 실행하여 시작하세요. 