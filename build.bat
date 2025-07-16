@echo off
echo ========================================
echo           웹 크롤러 빌드 스크립트
echo ========================================
echo.

REM 현재 디렉토리 확인
echo 현재 디렉토리: %CD%

REM Python 및 pip 버전 확인
echo.
echo Python 및 pip 버전 확인 중...
python --version
pip --version

REM 가상환경 활성화 (있는 경우)
if exist venv\Scripts\activate.bat (
    echo.
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 필요한 패키지 설치
echo.
echo 필요한 패키지 설치 중...
pip install -r requirements.txt

REM 이전 빌드 파일 정리
echo.
echo 이전 빌드 파일 정리 중...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "웹크롤러.exe" del "웹크롤러.exe"
if exist "__pycache__" rmdir /s /q __pycache__

REM PyInstaller로 exe 파일 생성
echo.
echo ========================================
echo           PyInstaller 빌드 시작
echo ========================================
echo.

REM .spec 파일이 있으면 사용, 없으면 기본 명령어 사용
if exist crawler_app.spec (
    echo spec 파일을 사용하여 빌드 중...
    pyinstaller crawler_app.spec --clean
) else (
    echo 기본 설정으로 빌드 중...
    pyinstaller --onefile --windowed --name="웹크롤러" --add-data "requirements.txt;." main.py
)

REM 빌드 결과 확인
echo.
echo ========================================
echo           빌드 완료
echo ========================================

if exist dist\웹크롤러.exe (
    echo ✓ 빌드 성공!
    echo 실행 파일 위치: %CD%\dist\웹크롤러.exe
    echo.
    echo 파일 크기:
    dir dist\웹크롤러.exe | find "웹크롤러.exe"
    echo.
    echo 실행 파일을 테스트하시겠습니까? (y/n)
    set /p answer=
    if /i "%answer%"=="y" (
        echo 실행 파일 테스트 중...
        start "" "dist\웹크롤러.exe"
    )
) else (
    echo ✗ 빌드 실패!
    echo dist 폴더를 확인하세요.
)

REM 임시 파일 정리
echo.
echo 임시 파일 정리 중...
if exist build rmdir /s /q build
if exist *.spec.backup del *.spec.backup
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo 빌드 스크립트 완료!
echo.
pause 