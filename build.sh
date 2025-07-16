#!/bin/bash

echo "========================================"
echo "         웹 크롤러 빌드 스크립트"
echo "========================================"
echo

# 현재 디렉토리 확인
echo "현재 디렉토리: $(pwd)"

# Python 및 pip 버전 확인
echo
echo "Python 및 pip 버전 확인 중..."
python3 --version
pip3 --version

# 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    echo
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 설치
echo
echo "필요한 패키지 설치 중..."
pip install -r requirements.txt

# 이전 빌드 파일 정리
echo
echo "이전 빌드 파일 정리 중..."
rm -rf build/
rm -rf dist/
rm -f "웹크롤러"
rm -rf __pycache__/

# PyInstaller로 실행 파일 생성
echo
echo "========================================"
echo "         PyInstaller 빌드 시작"
echo "========================================"
echo

# .spec 파일이 있으면 사용, 없으면 기본 명령어 사용
if [ -f "crawler_app.spec" ]; then
    echo "spec 파일을 사용하여 빌드 중..."
    pyinstaller crawler_app.spec --clean
else
    echo "기본 설정으로 빌드 중..."
    pyinstaller --onefile --windowed --name="웹크롤러" --add-data "requirements.txt:." main.py
fi

# 빌드 결과 확인
echo
echo "========================================"
echo "         빌드 완료"
echo "========================================"

if [ -f "dist/웹크롤러" ]; then
    echo "✓ 빌드 성공!"
    echo "실행 파일 위치: $(pwd)/dist/웹크롤러"
    echo
    echo "파일 크기:"
    ls -lh dist/웹크롤러
    echo
    echo "실행 권한 설정 중..."
    chmod +x dist/웹크롤러
    echo
    read -p "실행 파일을 테스트하시겠습니까? (y/n): " answer
    if [[ $answer == [Yy]* ]]; then
        echo "실행 파일 테스트 중..."
        ./dist/웹크롤러 &
    fi
else
    echo "✗ 빌드 실패!"
    echo "dist 폴더를 확인하세요."
fi

# 임시 파일 정리
echo
echo "임시 파일 정리 중..."
rm -rf build/
rm -f *.spec.backup
rm -rf __pycache__/

echo
echo "빌드 스크립트 완료!" 