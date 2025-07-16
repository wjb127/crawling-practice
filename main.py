import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import threading
from urllib.parse import urljoin, urlparse
import pandas as pd
from datetime import datetime
import os

class WebCrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("웹 크롤러")
        self.root.geometry("800x600")
        
        # 메인 프레임
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL 입력 섹션
        url_frame = ttk.LabelFrame(main_frame, text="크롤링 설정", padding="5")
        url_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar(value="https://example.com")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.crawl_button = ttk.Button(url_frame, text="크롤링 시작", command=self.start_crawling)
        self.crawl_button.grid(row=0, column=2, padx=(5, 0))
        
        self.stop_button = ttk.Button(url_frame, text="중지", command=self.stop_crawling, state='disabled')
        self.stop_button.grid(row=0, column=3, padx=(5, 0))
        
        # 크롤링 옵션
        options_frame = ttk.Frame(url_frame)
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.extract_links = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="링크 추출", variable=self.extract_links).grid(row=0, column=0, sticky=tk.W)
        
        self.extract_images = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="이미지 추출", variable=self.extract_images).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        self.extract_text = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="텍스트 추출", variable=self.extract_text).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # 진행상황 표시
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 엑셀 저장 버튼
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.export_button = ttk.Button(export_frame, text="엑셀로 저장", command=self.export_to_excel, state='disabled')
        self.export_button.pack(side=tk.RIGHT)
        
        ttk.Label(export_frame, text="크롤링이 완료되면 결과를 엑셀 파일로 저장할 수 있습니다.").pack(side=tk.LEFT)
        
        # 결과 표시 영역
        result_frame = ttk.LabelFrame(main_frame, text="크롤링 결과", padding="5")
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 탭 위젯
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 페이지 정보 탭
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="페이지 정보")
        
        self.info_text = scrolledtext.ScrolledText(self.info_frame, height=8, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 링크 탭
        self.links_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.links_frame, text="링크")
        
        self.links_text = scrolledtext.ScrolledText(self.links_frame, height=8, wrap=tk.WORD)
        self.links_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 이미지 탭
        self.images_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.images_frame, text="이미지")
        
        self.images_text = scrolledtext.ScrolledText(self.images_frame, height=8, wrap=tk.WORD)
        self.images_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 텍스트 탭
        self.content_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.content_frame, text="텍스트 내용")
        
        self.content_text = scrolledtext.ScrolledText(self.content_frame, height=8, wrap=tk.WORD)
        self.content_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 결과 테이블 탭
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="결과 테이블")
        
        # 테이블 뷰 생성
        self.create_table_view()
        
        # 사이트 추천 탭
        self.recommend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recommend_frame, text="사이트 추천")
        
        self.recommend_text = scrolledtext.ScrolledText(self.recommend_frame, height=8, wrap=tk.WORD)
        self.recommend_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 기술스택 설명 탭
        self.tech_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tech_frame, text="기술스택 가이드")
        
        self.tech_text = scrolledtext.ScrolledText(self.tech_frame, height=8, wrap=tk.WORD)
        self.tech_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 상태 표시줄
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 그리드 가중치 설정
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 각 탭의 그리드 설정
        for frame in [self.info_frame, self.links_frame, self.images_frame, self.content_frame, 
                      self.table_frame, self.recommend_frame, self.tech_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        
        url_frame.columnconfigure(1, weight=1)
        
        # 크롤링 상태 및 데이터 저장용 변수
        self.is_crawling = False
        self.crawled_data = []
        
        # 탭 내용 초기화
        self.load_static_content()
    
    def create_table_view(self):
        """결과 테이블 뷰를 생성합니다."""
        # 테이블 프레임
        table_container = ttk.Frame(self.table_frame)
        table_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 테이블 (Treeview) 생성
        columns = ('Type', 'Title', 'URL', 'Description')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # 컬럼 헤더 설정
        self.tree.heading('Type', text='타입')
        self.tree.heading('Title', text='제목/텍스트')
        self.tree.heading('URL', text='URL')
        self.tree.heading('Description', text='설명')
        
        # 컬럼 너비 설정
        self.tree.column('Type', width=80, minwidth=60)
        self.tree.column('Title', width=200, minwidth=150)
        self.tree.column('URL', width=300, minwidth=200)
        self.tree.column('Description', width=150, minwidth=100)
        
        # 스크롤바 추가
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 위젯 배치
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 그리드 가중치 설정
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
    
    def stop_crawling(self):
        """크롤링을 중지합니다."""
        self.is_crawling = False
        self.status_var.set("크롤링 중지됨")
    
    def start_crawling(self):
        """백그라운드에서 크롤링을 시작합니다."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_var.set(url)
        
        # UI 상태 변경
        self.crawl_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.export_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("크롤링 중...")
        self.is_crawling = True
        
        # 결과 영역 초기화
        self.clear_results()
        self.crawled_data = []
        
        # 백그라운드 스레드에서 크롤링 실행
        thread = threading.Thread(target=self.crawl_website, args=(url,))
        thread.daemon = True
        thread.start()
    
    def clear_results(self):
        """결과 영역을 초기화합니다."""
        self.info_text.delete(1.0, tk.END)
        self.links_text.delete(1.0, tk.END)
        self.images_text.delete(1.0, tk.END)
        self.content_text.delete(1.0, tk.END)
        
        # 테이블 초기화
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def load_static_content(self):
        """정적인 탭 내용을 로드합니다."""
        # 사이트 추천 내용
        recommend_content = """
🌐 크롤링하기 쉬운 추천 사이트들

📰 뉴스 사이트
• https://news.ycombinator.com - 해커뉴스 (간단한 HTML 구조)
• https://quotes.toscrape.com - 크롤링 연습용 사이트
• https://books.toscrape.com - 도서 정보 연습 사이트

🏛️ 공공 데이터
• https://httpbin.org - HTTP 테스트용 사이트
• https://jsonplaceholder.typicode.com - JSON API 테스트
• https://reqres.in - API 테스트용

📊 연습용 사이트
• https://scrape.center - 크롤링 연습 전용
• https://webscraper.io/test-sites - 다양한 테스트 케이스
• https://example.com - 가장 기본적인 테스트

🛒 전자상거래 (주의 필요)
• 일부 전자상거래 사이트들 (robots.txt 준수 필수)
• 오픈 마켓 상품 정보 (이용약관 확인 필요)

⚠️ 주의사항
• robots.txt 파일을 항상 확인하세요
• 과도한 요청은 피하세요 (서버 부하 방지)
• 저작권이 있는 콘텐츠는 주의하세요
• 개인정보가 포함된 데이터는 수집하지 마세요
• 웹사이트의 이용약관을 반드시 확인하세요

🎯 초보자 추천 순서
1. quotes.toscrape.com (기본 연습)
2. books.toscrape.com (페이지네이션 연습)
3. news.ycombinator.com (실제 사이트 연습)
4. 원하는 사이트 (단계적 접근)
"""
        
        # 기술스택 가이드 내용
        tech_content = """
🌐 사이트 기술스택별 크롤링 난이도 가이드

📊 크롤링 난이도 분류

🟢 쉬움 (정적 사이트)
• 일반 HTML/CSS 사이트
• 서버 사이드 렌더링 (SSR)
• WordPress, Jekyll 등 정적 사이트 생성기

크롤링 방법:
→ requests + BeautifulSoup로 충분
→ 페이지 소스에 모든 데이터가 포함됨
→ 예: 블로그, 뉴스 사이트, 기업 홈페이지

🟡 보통 (하이브리드)
• jQuery 기반 사이트
• 일부 동적 로딩이 있는 사이트
• AJAX로 일부 콘텐츠 로드

크롤링 방법:
→ requests + BeautifulSoup (기본 콘텐츠)
→ API 엔드포인트 분석 후 직접 호출
→ 필요시 Selenium으로 동적 부분만 처리

🟠 어려움 (SPA - Single Page Application)
• React, Vue.js, Angular 기반
• 클라이언트 사이드 렌더링 (CSR)
• 대부분의 콘텐츠가 JavaScript로 생성

크롤링 방법:
→ Selenium 또는 Playwright 필수
→ 페이지 로딩 완료까지 대기 필요
→ 예: 모던 전자상거래, 소셜미디어

🔴 매우 어려움 (고도화된 SPA)
• Next.js, Nuxt.js (SSR + CSR 혼합)
• 복잡한 상태 관리 (Redux, Vuex)
• 지연 로딩, 무한 스크롤
• 강력한 봇 차단 시스템

크롤링 방법:
→ Playwright + 고급 기법
→ 헤드리스 브라우저 + 프록시 로테이션
→ API 리버스 엔지니어링
→ 예: Netflix, Instagram, LinkedIn

🛠️ 기술스택별 상세 분석

📄 정적 HTML 사이트
특징: 서버에서 완전한 HTML 반환
도구: requests + BeautifulSoup
예시: 정부기관, 학교, 전통적 기업 사이트

🎯 WordPress/Drupal 사이트
특징: PHP 기반, 대부분 서버 렌더링
도구: requests + BeautifulSoup
주의: 플러그인에 따라 동적 요소 있을 수 있음

⚡ jQuery 기반 사이트
특징: 페이지 로드 후 일부 콘텐츠 추가 로드
도구: requests (기본) + Selenium (동적 부분)
전략: Network 탭에서 AJAX 요청 분석

🔥 React/Vue/Angular SPA
특징: 빈 HTML + JavaScript로 모든 콘텐츠 생성
도구: Selenium/Playwright 필수
전략: 
- componentDidMount 대기
- API 호출 직접 분석 (더 효율적)
- SSR 버전 찾기 (SEO용 페이지)

🏪 전자상거래 플랫폼별
• Shopify: Liquid 템플릿, 대부분 서버 렌더링
• WooCommerce: WordPress 기반, 비교적 쉬움
• Magento: 복잡한 구조, 일부 AJAX
• 커스텀 React: 매우 어려움

📱 모바일 앱 기반 웹
특징: 앱과 동일한 API 사용, 고도화된 보안
도구: API 리버스 엔지니어링 + requests
전략: 모바일 앱 패킷 분석

🛡️ 봇 차단 기술별 대응
• Cloudflare: User-Agent, 헤더 조작
• reCAPTCHA: 수동 해결 또는 우회
• Rate Limiting: 요청 간격 조절
• JavaScript Challenge: 헤드리스 브라우저 필수

🎯 실전 판별 방법

1️⃣ 페이지 소스 보기 (Ctrl+U)
→ 내용이 보이면: 정적 (쉬움)
→ 거의 비어있으면: SPA (어려움)

2️⃣ 개발자 도구 Network 탭
→ HTML 하나만: 정적
→ 많은 XHR/Fetch: 동적

3️⃣ JavaScript 비활성화 테스트
→ 내용이 그대로: 정적
→ 내용이 사라짐: 동적

4️⃣ URL 패턴 확인
→ /page/1, /category/tech: 전통적
→ /#/page/1, /app: SPA 가능성

💡 효율적인 접근 전략

1. 정적 분석 우선 (requests + BeautifulSoup)
2. 안 되면 API 분석 (Network 탭)
3. 마지막에 Selenium/Playwright 사용
4. 가능하면 모바일 버전이나 RSS 활용

⚠️ 주의사항
• robots.txt와 이용약관 확인 필수
• 과도한 요청 금지 (서버 부하)
• 개인정보 처리 시 법적 검토 필요
• 저작권 콘텐츠 주의
"""
        
        self.recommend_text.insert(tk.END, recommend_content)
        self.tech_text.insert(tk.END, tech_content)
        
        # 편집 불가능하게 설정
        self.recommend_text.config(state='disabled')
        self.tech_text.config(state='disabled')
    
    def crawl_website(self, url):
        """실제 크롤링을 수행합니다."""
        try:
            # 크롤링 중지 확인
            if not self.is_crawling:
                return
                
            # 요청 헤더 설정
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 웹 페이지 요청
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 결과 업데이트 (메인 스레드에서 실행)
            self.root.after(0, self.update_results, url, response, soup)
            
        except requests.exceptions.RequestException as e:
            self.root.after(0, self.show_error, f"네트워크 오류: {str(e)}")
        except Exception as e:
            self.root.after(0, self.show_error, f"크롤링 오류: {str(e)}")
    
    def update_results(self, url, response, soup):
        """크롤링 결과를 UI에 업데이트합니다."""
        try:
            # 페이지 정보
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "제목 없음"
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '설명 없음') if meta_desc else "설명 없음"
            
            info = f"제목: {title_text}\n"
            info += f"URL: {url}\n"
            info += f"상태 코드: {response.status_code}\n"
            info += f"콘텐츠 타입: {response.headers.get('content-type', '알 수 없음')}\n"
            info += f"콘텐츠 크기: {len(response.content)} bytes\n"
            info += f"설명: {description}\n"
            
            self.info_text.insert(tk.END, info)
            
            # 링크 추출
            if self.extract_links.get():
                links = soup.find_all('a', href=True)
                self.links_text.insert(tk.END, f"총 {len(links)}개의 링크를 발견했습니다:\n\n")
                
                for i, link in enumerate(links[:50], 1):  # 최대 50개만 표시
                    href = link['href']
                    text = link.get_text(strip=True)
                    full_url = urljoin(url, href)
                    self.links_text.insert(tk.END, f"{i}. {text}\n   URL: {full_url}\n\n")
                
                if len(links) > 50:
                    self.links_text.insert(tk.END, f"... 그 외 {len(links) - 50}개 링크가 더 있습니다.")
            
            # 이미지 추출
            if self.extract_images.get():
                images = soup.find_all('img', src=True)
                self.images_text.insert(tk.END, f"총 {len(images)}개의 이미지를 발견했습니다:\n\n")
                
                for i, img in enumerate(images[:30], 1):  # 최대 30개만 표시
                    src = img['src']
                    alt = img.get('alt', '대체 텍스트 없음')
                    full_url = urljoin(url, src)
                    self.images_text.insert(tk.END, f"{i}. {alt}\n   URL: {full_url}\n\n")
                
                if len(images) > 30:
                    self.images_text.insert(tk.END, f"... 그 외 {len(images) - 30}개 이미지가 더 있습니다.")
            
            # 텍스트 내용 추출
            if self.extract_text.get():
                # 스크립트와 스타일 태그 제거
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # 텍스트 길이 제한
                if len(text) > 5000:
                    text = text[:5000] + "\n\n... (텍스트가 너무 길어 일부만 표시됩니다)"
                
                self.content_text.insert(tk.END, text)
            
            # 테이블에 데이터 추가
            self.populate_table(url, soup)
            
            self.status_var.set(f"크롤링 완료 - {title_text}")
            
        except Exception as e:
            self.show_error(f"결과 처리 오류: {str(e)}")
        finally:
            # UI 다시 활성화
            self.progress.stop()
            self.crawl_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.export_button.config(state='normal')
            self.is_crawling = False
    
    def show_error(self, error_message):
        """오류 메시지를 표시합니다."""
        self.progress.stop()
        self.crawl_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.is_crawling = False
        self.status_var.set("오류 발생")
        messagebox.showerror("크롤링 오류", error_message)
    
    def populate_table(self, url, soup):
        """테이블에 크롤링 결과를 추가합니다."""
        try:
            # 페이지 기본 정보
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "제목 없음"
            
            # 페이지 정보 추가
            page_data = {
                'type': '페이지',
                'title': title_text,
                'url': url,
                'description': '웹페이지 기본 정보'
            }
            self.tree.insert('', 'end', values=(page_data['type'], page_data['title'], 
                                              page_data['url'], page_data['description']))
            self.crawled_data.append(page_data)
            
            # 링크 정보 추가
            if self.extract_links.get():
                links = soup.find_all('a', href=True)
                for i, link in enumerate(links[:50]):  # 최대 50개
                    href = link['href']
                    text = link.get_text(strip=True)[:100]  # 텍스트 길이 제한
                    full_url = urljoin(url, href)
                    
                    link_data = {
                        'type': '링크',
                        'title': text or '(텍스트 없음)',
                        'url': full_url,
                        'description': f'링크 #{i+1}'
                    }
                    self.tree.insert('', 'end', values=(link_data['type'], link_data['title'], 
                                                      link_data['url'], link_data['description']))
                    self.crawled_data.append(link_data)
            
            # 이미지 정보 추가
            if self.extract_images.get():
                images = soup.find_all('img', src=True)
                for i, img in enumerate(images[:30]):  # 최대 30개
                    src = img['src']
                    alt = img.get('alt', '대체 텍스트 없음')[:100]
                    full_url = urljoin(url, src)
                    
                    img_data = {
                        'type': '이미지',
                        'title': alt,
                        'url': full_url,
                        'description': f'이미지 #{i+1}'
                    }
                    self.tree.insert('', 'end', values=(img_data['type'], img_data['title'], 
                                                      img_data['url'], img_data['description']))
                    self.crawled_data.append(img_data)
                    
        except Exception as e:
            print(f"테이블 채우기 오류: {str(e)}")
    
    def export_to_excel(self):
        """크롤링 결과를 엑셀 파일로 저장합니다."""
        if not self.crawled_data:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return
        
        try:
            # 파일 저장 대화상자
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"crawling_result_{timestamp}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialvalue=default_filename
            )
            
            if not file_path:
                return
            
            # DataFrame 생성
            df = pd.DataFrame(self.crawled_data)
            df.columns = ['타입', '제목/텍스트', 'URL', '설명']
            
            # 엑셀 파일로 저장
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='크롤링 결과', index=False)
                
                # 워크시트 가져오기 및 서식 설정
                worksheet = writer.sheets['크롤링 결과']
                
                # 컬럼 너비 자동 조정
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # 최대 50자로 제한
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            messagebox.showinfo("완료", f"결과가 성공적으로 저장되었습니다.\n파일: {file_path}")
            
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = WebCrawlerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 