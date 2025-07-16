@echo off
echo ========================================
echo      SmartCrawler Pro 인스톨러 빌드
echo ========================================
echo.

REM 현재 디렉토리 확인
echo 현재 디렉토리: %CD%

REM Inno Setup 설치 확인
echo.
echo Inno Setup 설치 확인 중...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    echo ✓ Inno Setup 6 발견
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
    echo ✓ Inno Setup 6 발견
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    echo ✓ Inno Setup 5 발견
) else (
    echo ✗ Inno Setup을 찾을 수 없습니다!
    echo Inno Setup을 다운로드하고 설치하세요: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

REM 필요한 파일 확인
echo.
echo 필요한 파일 확인 중...

if not exist "dist\웹크롤러.exe" (
    echo ✗ 실행 파일이 없습니다: dist\웹크롤러.exe
    echo 먼저 build.bat를 실행하여 exe 파일을 생성하세요.
    pause
    exit /b 1
)
echo ✓ 실행 파일 확인

if not exist "WebCrawler_Setup.iss" (
    echo ✗ Inno Setup 스크립트가 없습니다: WebCrawler_Setup.iss
    pause
    exit /b 1
)
echo ✓ Inno Setup 스크립트 확인

if not exist "LICENSE.txt" (
    echo ✗ 라이선스 파일이 없습니다: LICENSE.txt
    pause
    exit /b 1
)
echo ✓ 라이선스 파일 확인

REM 인스톨러 출력 디렉토리 생성
echo.
echo 인스톨러 출력 디렉토리 생성 중...
if not exist installer mkdir installer
echo ✓ installer 디렉토리 준비

REM 이전 인스톨러 파일 정리
echo.
echo 이전 인스톨러 파일 정리 중...
if exist installer\*.exe del installer\*.exe
echo ✓ 이전 파일 정리 완료

REM Inno Setup으로 인스톨러 빌드
echo.
echo ========================================
echo        Inno Setup 인스톨러 빌드 시작
echo ========================================
echo.

%ISCC% WebCrawler_Setup.iss

REM 빌드 결과 확인
echo.
echo ========================================
echo           인스톨러 빌드 완료
echo ========================================

if exist installer\SmartCrawler_Pro_Setup_v1.0.0.exe (
    echo ✓ 인스톨러 빌드 성공!
    echo.
    echo 인스톨러 위치: %CD%\installer\
    echo 파일명: SmartCrawler_Pro_Setup_v1.0.0.exe
    echo.
    echo 파일 크기:
    dir installer\SmartCrawler_Pro_Setup_v1.0.0.exe | find "SmartCrawler_Pro_Setup_v1.0.0.exe"
    echo.
    echo 인스톨러를 테스트하시겠습니까? (y/n)
    set /p answer=
    if /i "%answer%"=="y" (
        echo 인스톨러 테스트 실행 중...
        start "" "installer\SmartCrawler_Pro_Setup_v1.0.0.exe"
    )
) else (
    echo ✗ 인스톨러 빌드 실패!
    echo installer 폴더와 로그를 확인하세요.
)

echo.
echo 배포 준비 완료!
echo 다음 파일들을 배포하세요:
echo - installer\SmartCrawler_Pro_Setup_v1.0.0.exe (인스톨러)
echo - dist\웹크롤러.exe (독립 실행 파일)
echo.
pause 