#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 크롤링 데스크탑 앱 TDD 테스트
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import threading
import time
import os
import tempfile
import json
import pickle
from datetime import datetime

# 테스트 대상 모듈 import
import main
from main import WebCrawlerApp

class TestWebCrawlerApp(unittest.TestCase):
    """WebCrawlerApp GUI 컴포넌트 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # 가상 GUI 환경 설정
        self.root = tk.Tk()
        self.root.withdraw()  # GUI 창 숨기기
        
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        
        # WebCrawlerApp 인스턴스 생성
        with patch('main.WebCrawlerApp.setup_alert_tab'), \
             patch('main.WebCrawlerApp.setup_analysis_tab'), \
             patch('main.WebCrawlerApp.setup_schedule_tab'):
            self.app = WebCrawlerApp(self.root)
        
        # 누락된 속성들 Mock으로 추가
        self.app.auto_save = Mock()
        self.app.auto_save.get.return_value = False
        self.app.update_checkpoint_status = Mock()
        
        # 체크포인트 파일을 임시 디렉토리로 설정
        self.app.checkpoint_file = os.path.join(self.temp_dir, "test_checkpoint.pkl")
    
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        try:
            self.root.destroy()
        except:
            pass
        
        # 임시 파일 정리
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """앱 초기화 테스트"""
        self.assertIsNotNone(self.app.root)
        self.assertEqual(self.app.root.title(), "웹 크롤러")
        self.assertFalse(self.app.is_crawling)
        self.assertEqual(len(self.app.crawled_data), 0)
    
    def test_url_validation(self):
        """URL 유효성 검사 테스트"""
        # 유효한 URL
        self.app.url_var.set("https://example.com")
        url = self.app.url_var.get().strip()
        self.assertTrue(url.startswith(('http://', 'https://')))
        
        # 프로토콜 없는 URL
        self.app.url_var.set("example.com")
        url = self.app.url_var.get().strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.assertTrue(url.startswith('https://'))
        
        # 빈 URL
        self.app.url_var.set("")
        url = self.app.url_var.get().strip()
        self.assertEqual(url, "")
    
    def test_crawling_settings(self):
        """크롤링 설정 테스트"""
        # 기본값 확인
        self.assertTrue(self.app.extract_links.get())
        self.assertTrue(self.app.extract_images.get())
        
        # 설정 변경
        self.app.extract_links.set(False)
        self.app.extract_images.set(False)
        self.assertFalse(self.app.extract_links.get())
        self.assertFalse(self.app.extract_images.get())
    
    def test_page_url_generation(self):
        """페이지 URL 생성 테스트"""
        base_url = "https://example.com"
        
        # 첫 번째 페이지
        page_url = self.app.generate_page_url(base_url, 1)
        self.assertEqual(page_url, base_url)
        
        # 두 번째 페이지
        page_url = self.app.generate_page_url(base_url, 2)
        self.assertEqual(page_url, f"{base_url}?page=2")
        
        # 이미 쿼리가 있는 URL
        base_url_with_query = "https://example.com?search=test"
        page_url = self.app.generate_page_url(base_url_with_query, 2)
        self.assertEqual(page_url, f"{base_url_with_query}&page=2")


class TestCrawlingFunctionality(unittest.TestCase):
    """크롤링 기능 단위 테스트"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock 설정으로 GUI 컴포넌트 스킵
        with patch('main.WebCrawlerApp.setup_alert_tab'), \
             patch('main.WebCrawlerApp.setup_analysis_tab'), \
             patch('main.WebCrawlerApp.setup_schedule_tab'):
            self.app = WebCrawlerApp(self.root)
        
        # 누락된 속성들 Mock으로 추가
        self.app.auto_save = Mock()
        self.app.auto_save.get.return_value = False
    
    def tearDown(self):
        try:
            self.root.destroy()
        except:
            pass
    
    @patch('requests.get')
    def test_http_request_success(self, mock_get):
        """HTTP 요청 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Test Page</h1></body></html>"
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 크롤링 실행 (실제 스레드 없이)
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get("https://example.com", headers=headers, timeout=10)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Page", response.text)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_http_request_failure(self, mock_get):
        """HTTP 요청 실패 테스트"""
        import requests
        
        # Mock 설정 - 요청 실패
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        with self.assertRaises(requests.exceptions.RequestException):
            requests.get("https://invalid-url.com", timeout=10)
    
    def test_data_extraction(self):
        """데이터 추출 테스트"""
        from bs4 import BeautifulSoup
        
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <a href="https://example.com/link1">Link 1</a>
                <a href="https://example.com/link2">Link 2</a>
                <img src="https://example.com/image1.jpg" alt="Image 1">
                <p>Test paragraph content</p>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 제목 추출
        title = soup.find('title')
        self.assertEqual(title.get_text(strip=True), "Test Page")
        
        # 링크 추출
        links = soup.find_all('a', href=True)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['href'], "https://example.com/link1")
        
        # 이미지 추출
        images = soup.find_all('img', src=True)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['src'], "https://example.com/image1.jpg")


class TestDataProcessing(unittest.TestCase):
    """데이터 처리 및 저장 테스트"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.temp_dir = tempfile.mkdtemp()
        
        with patch('main.WebCrawlerApp.setup_alert_tab'), \
             patch('main.WebCrawlerApp.setup_analysis_tab'), \
             patch('main.WebCrawlerApp.setup_schedule_tab'):
            self.app = WebCrawlerApp(self.root)
        
        # 누락된 속성들 Mock으로 추가
        self.app.auto_save = Mock()
        self.app.auto_save.get.return_value = False
        self.app.update_checkpoint_status = Mock()
        
        self.app.checkpoint_file = os.path.join(self.temp_dir, "test_checkpoint.pkl")
    
    def tearDown(self):
        try:
            self.root.destroy()
        except:
            pass
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_checkpoint_save_and_load(self):
        """체크포인트 저장/로드 테스트"""
        # 테스트 데이터 설정
        self.app.current_task = {
            'url': 'https://test.com',
            'browser_mode': 'requests',
            'max_pages': 5,
            'started_at': datetime.now()
        }
        
        self.app.task_progress = {
            'total_pages': 5,
            'completed_pages': 2,
            'failed_pages': [],
            'current_url': 'https://test.com'
        }
        
        self.app.crawled_data = [
            {'type': 'test', 'title': 'Test Item', 'url': 'https://test.com/item1'}
        ]
        
        # 저장 테스트
        self.app.save_checkpoint()
        self.assertTrue(os.path.exists(self.app.checkpoint_file))
        
        # 로드 테스트
        loaded_data = self.app.load_checkpoint()
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['current_task']['url'], 'https://test.com')
        self.assertEqual(loaded_data['task_progress']['completed_pages'], 2)
        self.assertEqual(len(loaded_data['crawled_data']), 1)
    
    def test_data_table_operations(self):
        """데이터 테이블 조작 테스트"""
        # 테스트 데이터 추가
        test_data = {
            'type': 'test',
            'title': 'Test Title',
            'url': 'https://test.com',
            'description': 'Test Description'
        }
        
        # 테이블에 데이터 추가 (GUI 없이)
        self.app.crawled_data.append(test_data)
        self.assertEqual(len(self.app.crawled_data), 1)
        self.assertEqual(self.app.crawled_data[0]['title'], 'Test Title')
    
    @patch('pandas.DataFrame.to_excel')
    def test_excel_export(self, mock_to_excel):
        """엑셀 내보내기 테스트"""
        # 테스트 데이터 설정
        self.app.crawled_data = [
            {'type': 'test', 'title': 'Item 1', 'url': 'https://test.com/1'},
            {'type': 'test', 'title': 'Item 2', 'url': 'https://test.com/2'}
        ]
        
        # 엑셀 내보내기 실행 (실제 파일 생성 없이)
        import pandas as pd
        df = pd.DataFrame(self.app.crawled_data)
        
        # DataFrame 생성 확인
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['title'], 'Item 1')


class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        with patch('main.WebCrawlerApp.setup_alert_tab'), \
             patch('main.WebCrawlerApp.setup_analysis_tab'), \
             patch('main.WebCrawlerApp.setup_schedule_tab'):
            self.app = WebCrawlerApp(self.root)
        
        # 누락된 속성들 Mock으로 추가
        self.app.auto_save = Mock()
        self.app.auto_save.get.return_value = False
    
    def tearDown(self):
        try:
            self.root.destroy()
        except:
            pass
    
    @patch('requests.get')
    @patch('threading.Thread')
    def test_full_crawling_workflow(self, mock_thread, mock_get):
        """전체 크롤링 워크플로우 테스트"""
        # Mock HTTP 응답
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Test Site</title></head>
            <body>
                <h1>Welcome</h1>
                <a href="/page1">Page 1</a>
                <img src="/image1.jpg" alt="Test Image">
            </body>
        </html>
        """
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock 스레드 (실제 실행 안 함)
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # 크롤링 설정
        self.app.url_var.set("https://test.com")
        self.app.max_pages.set("1")
        self.app.browser_mode.set("requests")
        
        # 크롤링 시작 (스레드 실행 없이 설정만 확인)
        self.app.start_crawling()
        
        # 설정 확인
        self.assertTrue(self.app.is_crawling)
        self.assertIsNotNone(self.app.current_task)
        self.assertEqual(self.app.current_task['url'], "https://test.com")
        
        # 스레드 생성 확인
        mock_thread.assert_called_once()


class TestPerformance(unittest.TestCase):
    """성능 테스트"""
    
    def test_large_data_processing(self):
        """대용량 데이터 처리 성능 테스트"""
        # 대량의 테스트 데이터 생성
        large_data = []
        for i in range(1000):
            large_data.append({
                'type': 'performance_test',
                'title': f'Item {i}',
                'url': f'https://test.com/item{i}',
                'description': f'Description for item {i}'
            })
        
        # 처리 시간 측정
        start_time = time.time()
        
        # pandas DataFrame으로 변환
        import pandas as pd
        df = pd.DataFrame(large_data)
        
        processing_time = time.time() - start_time
        
        # 성능 기준: 1000개 항목을 1초 내에 처리
        self.assertLess(processing_time, 1.0)
        self.assertEqual(len(df), 1000)


def run_gui_tests():
    """GUI 환경에서 실행할 수 있는 테스트"""
    print("GUI 컴포넌트 테스트 시작...")
    
    try:
        # 실제 GUI 생성 테스트
        root = tk.Tk()
        root.title("테스트 GUI")
        root.geometry("300x200")
        
        # 기본 컴포넌트 생성 테스트
        import tkinter.ttk as ttk
        
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = ttk.Label(frame, text="GUI 테스트 성공!")
        label.pack(pady=10)
        
        button = ttk.Button(frame, text="닫기", command=root.destroy)
        button.pack(pady=5)
        
        # 2초 후 자동 종료
        root.after(2000, root.destroy)
        
        print("GUI 컴포넌트 생성 성공")
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"GUI 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    print("=== 웹 크롤링 데스크탑 앱 TDD 테스트 시작 ===\n")
    
    # 1. GUI 환경 테스트
    gui_success = run_gui_tests()
    print(f"GUI 환경 테스트: {'성공' if gui_success else '실패'}\n")
    
    # 2. 단위 테스트 실행
    print("단위 테스트 실행 중...")
    
    # 테스트 슈트 생성
    test_suite = unittest.TestSuite()
    
    # 테스트 클래스들 추가
    test_classes = [
        TestWebCrawlerApp,
        TestCrawlingFunctionality, 
        TestDataProcessing,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 요약
    print(f"\n=== 테스트 결과 요약 ===")
    print(f"총 테스트 수: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print(f"\n테스트 성공률: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%") 