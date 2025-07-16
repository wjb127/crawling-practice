#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 크롤링 결과 시각화 및 검색 시스템
상용 서비스 수준의 UI/UX 제공
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
from datetime import datetime, timedelta
import pandas as pd
from urllib.parse import urlparse
import webbrowser

class AdvancedResultsViewer:
    """고급 크롤링 결과 뷰어"""
    
    def __init__(self, parent_frame, crawled_data):
        self.parent_frame = parent_frame
        self.crawled_data = crawled_data
        self.filtered_data = crawled_data.copy()
        self.tags = set()
        
        # 초기 태그 추출
        self.extract_initial_tags()
        
        # UI 구성
        self.setup_ui()
        
        # 초기 데이터 로드
        self.refresh_display()
    
    def extract_initial_tags(self):
        """초기 태그 추출"""
        for item in self.crawled_data:
            # 자동 태그 생성
            auto_tags = self.generate_auto_tags(item)
            item['tags'] = item.get('tags', []) + auto_tags
            self.tags.update(item['tags'])
    
    def generate_auto_tags(self, item):
        """아이템에 대한 자동 태그 생성"""
        tags = []
        
        # URL 기반 태그
        if 'url' in item:
            domain = urlparse(item['url']).netloc.lower()
            if 'shopping' in domain or 'mall' in domain:
                tags.append('쇼핑몰')
            if 'news' in domain:
                tags.append('뉴스')
            if 'blog' in domain:
                tags.append('블로그')
        
        # 제목 기반 태그
        if 'title' in item:
            title = item['title'].lower()
            if any(word in title for word in ['할인', 'sale', '특가', '세일']):
                tags.append('할인')
            if any(word in title for word in ['신상', '새로운', 'new']):
                tags.append('신상품')
            if re.search(r'\d+원|\$\d+|￥\d+', item['title']):
                tags.append('가격정보')
        
        # 가격 기반 태그
        if 'price' in item and item['price']:
            price_str = str(item['price']).replace(',', '').replace('원', '')
            try:
                price = int(re.search(r'\d+', price_str).group())
                if price < 10000:
                    tags.append('저가')
                elif price < 100000:
                    tags.append('중가')
                else:
                    tags.append('고가')
            except:
                pass
        
        return tags
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 상단 검색/필터 영역
        self.setup_search_area(main_container)
        
        # 중간 태그 영역
        self.setup_tag_area(main_container)
        
        # 하단 결과 표시 영역
        self.setup_results_area(main_container)
        
        # 통계 및 액션 영역
        self.setup_stats_area(main_container)
    
    def setup_search_area(self, parent):
        """검색 영역 설정"""
        search_frame = ttk.LabelFrame(parent, text="🔍 스마트 검색", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 첫 번째 행: 키워드 검색
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_row1, text="키워드:").pack(side=tk.LEFT)
        self.keyword_var = tk.StringVar()
        self.keyword_entry = ttk.Entry(search_row1, textvariable=self.keyword_var, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.keyword_entry.bind('<KeyRelease>', self.on_search_change)
        
        # 검색 옵션
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(search_row1, text="대소문자 구분", variable=self.case_sensitive, 
                       command=self.apply_filters).pack(side=tk.LEFT, padx=(5, 0))
        
        # 두 번째 행: 가격 범위 검색
        search_row2 = ttk.Frame(search_frame)
        search_row2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_row2, text="가격 범위:").pack(side=tk.LEFT)
        self.min_price_var = tk.StringVar()
        ttk.Entry(search_row2, textvariable=self.min_price_var, width=10).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(search_row2, text="~").pack(side=tk.LEFT)
        self.max_price_var = tk.StringVar()
        ttk.Entry(search_row2, textvariable=self.max_price_var, width=10).pack(side=tk.LEFT, padx=(2, 10))
        ttk.Label(search_row2, text="원").pack(side=tk.LEFT)
        
        # 가격 검색 바인딩
        self.min_price_var.trace('w', lambda *args: self.apply_filters())
        self.max_price_var.trace('w', lambda *args: self.apply_filters())
        
        # 세 번째 행: 날짜 및 도메인 필터
        search_row3 = ttk.Frame(search_frame)
        search_row3.pack(fill=tk.X)
        
        ttk.Label(search_row3, text="도메인:").pack(side=tk.LEFT)
        self.domain_var = tk.StringVar()
        self.domain_combo = ttk.Combobox(search_row3, textvariable=self.domain_var, width=20)
        self.domain_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.domain_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # 초기화 버튼
        ttk.Button(search_row3, text="🔄 초기화", command=self.reset_filters).pack(side=tk.RIGHT)
        ttk.Button(search_row3, text="📊 통계", command=self.show_statistics).pack(side=tk.RIGHT, padx=(0, 5))
    
    def setup_tag_area(self, parent):
        """태그 영역 설정"""
        tag_frame = ttk.LabelFrame(parent, text="🏷️ 스마트 태그", padding="10")
        tag_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 태그 관리 버튼들
        tag_controls = ttk.Frame(tag_frame)
        tag_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(tag_controls, text="+ 태그 추가", command=self.add_custom_tag).pack(side=tk.LEFT)
        ttk.Button(tag_controls, text="🤖 자동 태그", command=self.auto_tag_all).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(tag_controls, text="💾 태그 저장", command=self.save_tags).pack(side=tk.LEFT, padx=(5, 0))
        
        # 태그 표시 영역 (스크롤 가능)
        self.tag_canvas = tk.Canvas(tag_frame, height=80)
        tag_scrollbar = ttk.Scrollbar(tag_frame, orient="horizontal", command=self.tag_canvas.xview)
        self.tag_canvas.configure(xscrollcommand=tag_scrollbar.set)
        
        self.tag_inner_frame = ttk.Frame(self.tag_canvas)
        self.tag_canvas.create_window((0, 0), window=self.tag_inner_frame, anchor="nw")
        
        self.tag_canvas.pack(fill=tk.X)
        tag_scrollbar.pack(fill=tk.X)
        
        # 선택된 태그들
        self.selected_tags = set()
    
    def setup_results_area(self, parent):
        """결과 표시 영역 설정"""
        results_frame = ttk.LabelFrame(parent, text="📋 크롤링 결과", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 결과 표시 방식 선택
        view_controls = ttk.Frame(results_frame)
        view_controls.pack(fill=tk.X, pady=(0, 5))
        
        self.view_mode = tk.StringVar(value="card")
        ttk.Radiobutton(view_controls, text="🃏 카드뷰", variable=self.view_mode, 
                       value="card", command=self.change_view_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(view_controls, text="📊 테이블뷰", variable=self.view_mode, 
                       value="table", command=self.change_view_mode).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(view_controls, text="📝 리스트뷰", variable=self.view_mode, 
                       value="list", command=self.change_view_mode).pack(side=tk.LEFT, padx=(10, 0))
        
        # 정렬 옵션
        ttk.Label(view_controls, text="정렬:").pack(side=tk.LEFT, padx=(20, 5))
        self.sort_var = tk.StringVar(value="default")
        sort_combo = ttk.Combobox(view_controls, textvariable=self.sort_var, width=15,
                                 values=["기본순", "제목순", "가격 낮은순", "가격 높은순", "날짜순"])
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_display())
        
        # 결과 컨테이너 (스크롤 가능)
        self.results_container = ttk.Frame(results_frame)
        self.results_container.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바
        self.results_canvas = tk.Canvas(self.results_container)
        self.results_scrollbar = ttk.Scrollbar(self.results_container, orient="vertical", 
                                              command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)
        
        self.results_inner_frame = ttk.Frame(self.results_canvas)
        self.results_canvas.create_window((0, 0), window=self.results_inner_frame, anchor="nw")
        
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 스크롤 이벤트 바인딩
        self.results_canvas.bind('<Configure>', self.on_canvas_configure)
        self.results_inner_frame.bind('<Configure>', self.on_frame_configure)
    
    def setup_stats_area(self, parent):
        """통계 및 액션 영역 설정"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X)
        
        # 통계 정보
        self.stats_label = ttk.Label(stats_frame, text="총 0개 항목")
        self.stats_label.pack(side=tk.LEFT)
        
        # 액션 버튼들
        action_frame = ttk.Frame(stats_frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="📤 선택 내보내기", 
                  command=self.export_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📈 가격 모니터링", 
                  command=self.setup_price_monitoring).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🔗 외부 링크", 
                  command=self.open_selected_links).pack(side=tk.LEFT)
    
    def on_search_change(self, event=None):
        """검색어 변경 시 실행"""
        # 0.5초 지연 후 검색 (타이핑 완료 기다림)
        if hasattr(self, 'search_timer'):
            self.parent_frame.after_cancel(self.search_timer)
        self.search_timer = self.parent_frame.after(500, self.apply_filters)
    
    def apply_filters(self):
        """필터 적용"""
        self.filtered_data = []
        keyword = self.keyword_var.get().strip()
        min_price = self.min_price_var.get().strip()
        max_price = self.max_price_var.get().strip()
        domain = self.domain_var.get().strip()
        
        for item in self.crawled_data:
            # 키워드 필터
            if keyword:
                text_to_search = f"{item.get('title', '')} {item.get('description', '')}"
                if not self.case_sensitive.get():
                    text_to_search = text_to_search.lower()
                    keyword = keyword.lower()
                
                if keyword not in text_to_search:
                    continue
            
            # 가격 필터
            if min_price or max_price:
                item_price = self.extract_price(item.get('price', ''))
                if item_price is not None:
                    try:
                        if min_price and item_price < int(min_price):
                            continue
                        if max_price and item_price > int(max_price):
                            continue
                    except ValueError:
                        pass
            
            # 도메인 필터
            if domain and domain != "전체":
                item_domain = urlparse(item.get('url', '')).netloc
                if domain not in item_domain:
                    continue
            
            # 태그 필터
            if self.selected_tags:
                item_tags = set(item.get('tags', []))
                if not self.selected_tags.intersection(item_tags):
                    continue
            
            self.filtered_data.append(item)
        
        self.refresh_display()
    
    def extract_price(self, price_str):
        """가격 문자열에서 숫자 추출"""
        if not price_str:
            return None
        
        # 숫자만 추출
        numbers = re.findall(r'\d+', str(price_str).replace(',', ''))
        if numbers:
            return int(numbers[0])
        return None
    
    def refresh_display(self):
        """화면 새로고침"""
        # 기존 위젯 제거
        for widget in self.results_inner_frame.winfo_children():
            widget.destroy()
        
        # 정렬 적용
        sorted_data = self.sort_data(self.filtered_data)
        
        # 선택된 뷰 모드에 따라 표시
        if self.view_mode.get() == "card":
            self.display_card_view(sorted_data)
        elif self.view_mode.get() == "table":
            self.display_table_view(sorted_data)
        else:
            self.display_list_view(sorted_data)
        
        # 도메인 콤보박스 업데이트
        self.update_domain_combo()
        
        # 태그 영역 업데이트
        self.update_tag_display()
        
        # 통계 업데이트
        self.update_stats()
        
        # 스크롤 영역 업데이트
        self.results_inner_frame.update_idletasks()
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
    
    def sort_data(self, data):
        """데이터 정렬"""
        sort_option = self.sort_var.get()
        
        if sort_option == "제목순":
            return sorted(data, key=lambda x: x.get('title', '').lower())
        elif sort_option == "가격 낮은순":
            return sorted(data, key=lambda x: self.extract_price(x.get('price', '')) or 0)
        elif sort_option == "가격 높은순":
            return sorted(data, key=lambda x: self.extract_price(x.get('price', '')) or 0, reverse=True)
        elif sort_option == "날짜순":
            return sorted(data, key=lambda x: x.get('crawl_time', datetime.now()), reverse=True)
        else:
            return data
    
    def display_card_view(self, data):
        """카드 뷰 표시"""
        # 카드들을 그리드로 배치
        cols = 3  # 한 행에 3개씩
        
        for i, item in enumerate(data):
            row = i // cols
            col = i % cols
            
            # 카드 프레임
            card = ttk.Frame(self.results_inner_frame, relief="solid", borderwidth=1)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # 제목
            title = item.get('title', 'No Title')[:50] + ('...' if len(item.get('title', '')) > 50 else '')
            title_label = ttk.Label(card, text=title, font=('Arial', 10, 'bold'))
            title_label.pack(anchor="w", padx=5, pady=(5, 2))
            
            # 가격 (있는 경우)
            if item.get('price'):
                price_label = ttk.Label(card, text=f"💰 {item['price']}", foreground="red")
                price_label.pack(anchor="w", padx=5)
            
            # URL
            if item.get('url'):
                domain = urlparse(item['url']).netloc
                url_label = ttk.Label(card, text=f"🌐 {domain}", foreground="blue", cursor="hand2")
                url_label.pack(anchor="w", padx=5)
                url_label.bind("<Button-1>", lambda e, url=item['url']: webbrowser.open(url))
            
            # 태그들
            if item.get('tags'):
                tag_text = " ".join([f"#{tag}" for tag in item['tags'][:3]])
                if len(item['tags']) > 3:
                    tag_text += f" +{len(item['tags'])-3}"
                tag_label = ttk.Label(card, text=tag_text, foreground="gray")
                tag_label.pack(anchor="w", padx=5, pady=(2, 5))
            
            # 그리드 열 크기 조정
            self.results_inner_frame.grid_columnconfigure(col, weight=1)
    
    def display_table_view(self, data):
        """테이블 뷰 표시"""
        # 트리뷰 생성
        columns = ("title", "price", "domain", "tags")
        tree = ttk.Treeview(self.results_inner_frame, columns=columns, show="headings", height=20)
        
        # 헤더 설정
        tree.heading("title", text="제목")
        tree.heading("price", text="가격")
        tree.heading("domain", text="도메인")
        tree.heading("tags", text="태그")
        
        # 열 너비 설정
        tree.column("title", width=300)
        tree.column("price", width=100)
        tree.column("domain", width=150)
        tree.column("tags", width=200)
        
        # 데이터 추가
        for item in data:
            title = item.get('title', '')[:50] + ('...' if len(item.get('title', '')) > 50 else '')
            price = item.get('price', '')
            domain = urlparse(item.get('url', '')).netloc
            tags = ", ".join(item.get('tags', [])[:3])
            
            tree.insert("", tk.END, values=(title, price, domain, tags))
        
        # 스크롤바
        tree_scrollbar = ttk.Scrollbar(self.results_inner_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 더블클릭으로 상세 정보
        tree.bind("<Double-1>", lambda e: self.show_item_detail(tree, data))
    
    def display_list_view(self, data):
        """리스트 뷰 표시"""
        for i, item in enumerate(data):
            # 리스트 아이템 프레임
            item_frame = ttk.Frame(self.results_inner_frame)
            item_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # 번호
            num_label = ttk.Label(item_frame, text=f"{i+1}.", width=5)
            num_label.pack(side=tk.LEFT)
            
            # 내용 프레임
            content_frame = ttk.Frame(item_frame)
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 제목과 가격을 같은 줄에
            title_price_frame = ttk.Frame(content_frame)
            title_price_frame.pack(fill=tk.X)
            
            title = item.get('title', 'No Title')
            title_label = ttk.Label(title_price_frame, text=title, font=('Arial', 9, 'bold'))
            title_label.pack(side=tk.LEFT)
            
            if item.get('price'):
                price_label = ttk.Label(title_price_frame, text=f"[{item['price']}]", foreground="red")
                price_label.pack(side=tk.RIGHT)
            
            # URL과 태그
            if item.get('url') or item.get('tags'):
                detail_frame = ttk.Frame(content_frame)
                detail_frame.pack(fill=tk.X)
                
                if item.get('url'):
                    domain = urlparse(item['url']).netloc
                    domain_label = ttk.Label(detail_frame, text=domain, foreground="blue", cursor="hand2")
                    domain_label.pack(side=tk.LEFT)
                    domain_label.bind("<Button-1>", lambda e, url=item['url']: webbrowser.open(url))
                
                if item.get('tags'):
                    tag_text = " ".join([f"#{tag}" for tag in item['tags']])
                    tag_label = ttk.Label(detail_frame, text=tag_text, foreground="gray")
                    tag_label.pack(side=tk.RIGHT)
            
            # 구분선
            ttk.Separator(self.results_inner_frame, orient='horizontal').pack(fill=tk.X, pady=1)
    
    def update_domain_combo(self):
        """도메인 콤보박스 업데이트"""
        domains = set()
        for item in self.crawled_data:
            if item.get('url'):
                domain = urlparse(item['url']).netloc
                domains.add(domain)
        
        domain_list = ["전체"] + sorted(list(domains))
        self.domain_combo['values'] = domain_list
        if not self.domain_var.get():
            self.domain_var.set("전체")
    
    def update_tag_display(self):
        """태그 표시 영역 업데이트"""
        # 기존 태그 버튼들 제거
        for widget in self.tag_inner_frame.winfo_children():
            widget.destroy()
        
        # 태그 버튼들 생성
        row = 0
        col = 0
        max_cols = 8
        
        for tag in sorted(self.tags):
            # 태그 사용 빈도 계산
            tag_count = sum(1 for item in self.crawled_data if tag in item.get('tags', []))
            
            # 태그 버튼 생성
            is_selected = tag in self.selected_tags
            tag_button = ttk.Button(
                self.tag_inner_frame,
                text=f"{tag} ({tag_count})",
                command=lambda t=tag: self.toggle_tag(t)
            )
            
            if is_selected:
                tag_button.configure(style="Accent.TButton")
            
            tag_button.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 태그 영역 스크롤 설정
        self.tag_inner_frame.update_idletasks()
        self.tag_canvas.configure(scrollregion=self.tag_canvas.bbox("all"))
    
    def update_stats(self):
        """통계 정보 업데이트"""
        total = len(self.crawled_data)
        filtered = len(self.filtered_data)
        
        if filtered == total:
            stats_text = f"총 {total}개 항목"
        else:
            stats_text = f"{filtered}개 항목 (전체 {total}개 중)"
        
        # 가격 정보가 있는 항목들의 통계
        prices = []
        for item in self.filtered_data:
            price = self.extract_price(item.get('price', ''))
            if price:
                prices.append(price)
        
        if prices:
            avg_price = sum(prices) // len(prices)
            stats_text += f" | 평균가격: {avg_price:,}원"
        
        self.stats_label.config(text=stats_text)
    
    def toggle_tag(self, tag):
        """태그 선택/해제"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        else:
            self.selected_tags.add(tag)
        
        self.apply_filters()
    
    def reset_filters(self):
        """필터 초기화"""
        self.keyword_var.set("")
        self.min_price_var.set("")
        self.max_price_var.set("")
        self.domain_var.set("전체")
        self.selected_tags.clear()
        self.case_sensitive.set(False)
        self.apply_filters()
    
    def change_view_mode(self):
        """뷰 모드 변경"""
        self.refresh_display()
    
    def add_custom_tag(self):
        """사용자 정의 태그 추가"""
        dialog = CustomTagDialog(self.parent_frame, self.filtered_data)
        if dialog.result:
            # 선택된 항목들에 태그 추가
            for item in dialog.selected_items:
                if 'tags' not in item:
                    item['tags'] = []
                if dialog.result not in item['tags']:
                    item['tags'].append(dialog.result)
                    self.tags.add(dialog.result)
            self.refresh_display()
    
    def auto_tag_all(self):
        """모든 항목에 자동 태그 적용"""
        for item in self.crawled_data:
            auto_tags = self.generate_auto_tags(item)
            existing_tags = item.get('tags', [])
            item['tags'] = list(set(existing_tags + auto_tags))
            self.tags.update(item['tags'])
        self.refresh_display()
        messagebox.showinfo("완료", "자동 태깅이 완료되었습니다!")
    
    def save_tags(self):
        """태그 정보 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="태그 정보 저장"
        )
        
        if filename:
            tag_data = {
                'tags': list(self.tags),
                'tagged_items': self.crawled_data
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tag_data, f, ensure_ascii=False, indent=2, default=str)
            messagebox.showinfo("완료", f"태그 정보가 저장되었습니다:\n{filename}")
    
    def show_statistics(self):
        """상세 통계 창 표시"""
        stats_window = StatisticsWindow(self.parent_frame, self.crawled_data, self.filtered_data)
    
    def setup_price_monitoring(self):
        """가격 모니터링 설정"""
        monitor_window = PriceMonitoringWindow(self.parent_frame, self.filtered_data)
    
    def export_selected(self):
        """선택된 결과 내보내기"""
        export_window = ExportWindow(self.parent_frame, self.filtered_data)
    
    def open_selected_links(self):
        """선택된 링크들 외부 브라우저에서 열기"""
        # 상위 5개 항목의 링크만 열기
        links = [item.get('url') for item in self.filtered_data[:5] if item.get('url')]
        
        if not links:
            messagebox.showwarning("경고", "열 수 있는 링크가 없습니다.")
            return
        
        if len(links) > 5:
            if not messagebox.askyesno("확인", f"{len(links)}개의 링크를 모두 열겠습니까?\n(상위 5개만 열 것을 권장)"):
                return
            links = links[:5]
        
        for link in links:
            webbrowser.open(link)
    
    def show_item_detail(self, tree, data):
        """아이템 상세 정보 표시"""
        selection = tree.selection()
        if selection:
            item_id = tree.index(selection[0])
            item = data[item_id]
            DetailWindow(self.parent_frame, item)
    
    def on_canvas_configure(self, event):
        """캔버스 크기 조정"""
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
    
    def on_frame_configure(self, event):
        """프레임 크기 조정"""
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))


class CustomTagDialog:
    """사용자 정의 태그 추가 대화상자"""
    
    def __init__(self, parent, items):
        self.parent = parent
        self.items = items
        self.result = None
        self.selected_items = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("사용자 정의 태그 추가")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # 중앙 배치
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        
        self.dialog.wait_window()
    
    def setup_ui(self):
        """UI 설정"""
        # 태그 입력
        tag_frame = ttk.Frame(self.dialog)
        tag_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(tag_frame, text="새 태그 이름:").pack(anchor="w")
        self.tag_var = tk.StringVar()
        tag_entry = ttk.Entry(tag_frame, textvariable=self.tag_var)
        tag_entry.pack(fill=tk.X, pady=(5, 0))
        tag_entry.focus()
        
        # 항목 선택
        items_frame = ttk.LabelFrame(self.dialog, text="태그를 적용할 항목 선택")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 체크박스가 있는 리스트
        self.item_vars = []
        canvas = tk.Canvas(items_frame)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, item in enumerate(self.items):
            var = tk.BooleanVar()
            self.item_vars.append(var)
            
            title = item.get('title', f'항목 {i+1}')[:50]
            cb = ttk.Checkbutton(scrollable_frame, text=title, variable=var)
            cb.pack(anchor="w", padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 버튼
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="전체 선택", command=self.select_all).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="전체 해제", command=self.deselect_all).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="확인", command=self.ok).pack(side=tk.RIGHT, padx=(0, 5))
    
    def select_all(self):
        for var in self.item_vars:
            var.set(True)
    
    def deselect_all(self):
        for var in self.item_vars:
            var.set(False)
    
    def ok(self):
        tag_name = self.tag_var.get().strip()
        if not tag_name:
            messagebox.showerror("오류", "태그 이름을 입력해주세요.")
            return
        
        selected_indices = [i for i, var in enumerate(self.item_vars) if var.get()]
        if not selected_indices:
            messagebox.showerror("오류", "태그를 적용할 항목을 선택해주세요.")
            return
        
        self.result = tag_name
        self.selected_items = [self.items[i] for i in selected_indices]
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


class StatisticsWindow:
    """통계 창"""
    
    def __init__(self, parent, all_data, filtered_data):
        self.window = tk.Toplevel(parent)
        self.window.title("📊 크롤링 통계")
        self.window.geometry("600x500")
        
        self.setup_ui(all_data, filtered_data)
    
    def setup_ui(self, all_data, filtered_data):
        """UI 설정"""
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 기본 통계 탭
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="기본 통계")
        
        stats_text = tk.Text(basic_frame, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=stats_text.yview)
        stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        # 통계 계산
        basic_stats = self.calculate_basic_stats(all_data, filtered_data)
        stats_text.insert(tk.END, basic_stats)
        stats_text.config(state=tk.DISABLED)
        
        stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 도메인 분석 탭
        domain_frame = ttk.Frame(notebook)
        notebook.add(domain_frame, text="도메인 분석")
        
        # 태그 분석 탭
        tag_frame = ttk.Frame(notebook)
        notebook.add(tag_frame, text="태그 분석")
    
    def calculate_basic_stats(self, all_data, filtered_data):
        """기본 통계 계산"""
        stats = []
        
        stats.append("=== 기본 정보 ===")
        stats.append(f"전체 항목 수: {len(all_data)}개")
        stats.append(f"필터된 항목 수: {len(filtered_data)}개")
        stats.append(f"필터 적용률: {len(filtered_data)/len(all_data)*100:.1f}%")
        stats.append("")
        
        # 가격 분석
        prices = []
        for item in filtered_data:
            price_str = item.get('price', '')
            if price_str:
                price_match = re.search(r'\d+', str(price_str).replace(',', ''))
                if price_match:
                    prices.append(int(price_match.group()))
        
        if prices:
            stats.append("=== 가격 분석 ===")
            stats.append(f"가격 정보가 있는 항목: {len(prices)}개")
            stats.append(f"최저 가격: {min(prices):,}원")
            stats.append(f"최고 가격: {max(prices):,}원")
            stats.append(f"평균 가격: {sum(prices)//len(prices):,}원")
            stats.append(f"중간 가격: {sorted(prices)[len(prices)//2]:,}원")
            stats.append("")
        
        # 도메인 분석
        domains = {}
        for item in filtered_data:
            if item.get('url'):
                domain = urlparse(item['url']).netloc
                domains[domain] = domains.get(domain, 0) + 1
        
        if domains:
            stats.append("=== 도메인 분석 ===")
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
                stats.append(f"{domain}: {count}개")
            stats.append("")
        
        # 태그 분석
        tags = {}
        for item in filtered_data:
            for tag in item.get('tags', []):
                tags[tag] = tags.get(tag, 0) + 1
        
        if tags:
            stats.append("=== 태그 분석 ===")
            for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True)[:15]:
                stats.append(f"#{tag}: {count}개")
        
        return "\n".join(stats)


class PriceMonitoringWindow:
    """가격 모니터링 창"""
    
    def __init__(self, parent, data):
        self.window = tk.Toplevel(parent)
        self.window.title("📈 가격 모니터링 설정")
        self.window.geometry("500x400")
        
        self.setup_ui(data)
    
    def setup_ui(self, data):
        """UI 설정"""
        # 가격 정보가 있는 항목들만 필터링
        price_items = [item for item in data if item.get('price')]
        
        if not price_items:
            ttk.Label(self.window, text="가격 정보가 있는 항목이 없습니다.").pack(pady=20)
            return
        
        # 설명
        ttk.Label(self.window, text="가격 변동을 모니터링할 항목들을 선택하세요:").pack(pady=10)
        
        # 항목 목록
        frame = ttk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        self.monitor_vars = []
        
        for item in price_items:
            var = tk.BooleanVar()
            self.monitor_vars.append((var, item))
            
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            cb = ttk.Checkbutton(item_frame, variable=var)
            cb.pack(side=tk.LEFT)
            
            title = item.get('title', 'No Title')[:40]
            price = item.get('price', '')
            label = ttk.Label(item_frame, text=f"{title} - {price}")
            label.pack(side=tk.LEFT, padx=(5, 0))
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 알림 설정
        settings_frame = ttk.LabelFrame(self.window, text="알림 설정")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="가격 변동률 임계값:").pack(anchor="w")
        self.threshold_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.threshold_var, width=10).pack(anchor="w")
        ttk.Label(settings_frame, text="% 이상 변동 시 알림").pack(anchor="w")
        
        # 버튼
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="모니터링 시작", command=self.start_monitoring).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side=tk.RIGHT, padx=(0, 5))
    
    def start_monitoring(self):
        """모니터링 시작"""
        selected_items = [item for var, item in self.monitor_vars if var.get()]
        
        if not selected_items:
            messagebox.showwarning("경고", "모니터링할 항목을 선택해주세요.")
            return
        
        threshold = self.threshold_var.get()
        try:
            threshold = float(threshold)
        except ValueError:
            messagebox.showerror("오류", "올바른 임계값을 입력해주세요.")
            return
        
        messagebox.showinfo("완료", f"{len(selected_items)}개 항목의 가격 모니터링을 시작합니다.\n임계값: {threshold}%")
        self.window.destroy()


class ExportWindow:
    """내보내기 창"""
    
    def __init__(self, parent, data):
        self.window = tk.Toplevel(parent)
        self.window.title("📤 데이터 내보내기")
        self.window.geometry("400x300")
        
        self.data = data
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        # 내보내기 옵션
        options_frame = ttk.LabelFrame(self.window, text="내보내기 옵션")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.format_var = tk.StringVar(value="excel")
        ttk.Radiobutton(options_frame, text="Excel 파일 (.xlsx)", variable=self.format_var, value="excel").pack(anchor="w")
        ttk.Radiobutton(options_frame, text="CSV 파일 (.csv)", variable=self.format_var, value="csv").pack(anchor="w")
        ttk.Radiobutton(options_frame, text="JSON 파일 (.json)", variable=self.format_var, value="json").pack(anchor="w")
        
        # 포함할 필드 선택
        fields_frame = ttk.LabelFrame(self.window, text="포함할 필드")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.field_vars = {}
        fields = ["title", "url", "price", "description", "tags"]
        
        for field in fields:
            var = tk.BooleanVar(value=True)
            self.field_vars[field] = var
            ttk.Checkbutton(fields_frame, text=field.title(), variable=var).pack(anchor="w")
        
        # 버튼
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="내보내기", command=self.export_data).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side=tk.RIGHT, padx=(0, 5))
    
    def export_data(self):
        """데이터 내보내기"""
        selected_fields = [field for field, var in self.field_vars.items() if var.get()]
        
        if not selected_fields:
            messagebox.showwarning("경고", "내보낼 필드를 선택해주세요.")
            return
        
        format_type = self.format_var.get()
        
        if format_type == "excel":
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Excel 파일로 저장"
            )
        elif format_type == "csv":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="CSV 파일로 저장"
            )
        else:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="JSON 파일로 저장"
            )
        
        if filename:
            try:
                # 데이터 필터링
                filtered_data = []
                for item in self.data:
                    filtered_item = {field: item.get(field, '') for field in selected_fields}
                    if 'tags' in filtered_item and isinstance(filtered_item['tags'], list):
                        filtered_item['tags'] = ', '.join(filtered_item['tags'])
                    filtered_data.append(filtered_item)
                
                if format_type == "excel":
                    df = pd.DataFrame(filtered_data)
                    df.to_excel(filename, index=False)
                elif format_type == "csv":
                    df = pd.DataFrame(filtered_data)
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("완료", f"데이터가 성공적으로 내보내졌습니다:\n{filename}")
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("오류", f"내보내기 중 오류가 발생했습니다:\n{str(e)}")


class DetailWindow:
    """상세 정보 창"""
    
    def __init__(self, parent, item):
        self.window = tk.Toplevel(parent)
        self.window.title("📋 상세 정보")
        self.window.geometry("500x600")
        
        self.setup_ui(item)
    
    def setup_ui(self, item):
        """UI 설정"""
        # 스크롤 가능한 텍스트 영역
        text_frame = ttk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # 상세 정보 표시
        details = []
        
        if item.get('title'):
            details.append(f"제목: {item['title']}")
        
        if item.get('url'):
            details.append(f"URL: {item['url']}")
        
        if item.get('price'):
            details.append(f"가격: {item['price']}")
        
        if item.get('description'):
            details.append(f"설명: {item['description']}")
        
        if item.get('tags'):
            details.append(f"태그: {', '.join(item['tags'])}")
        
        if item.get('crawl_time'):
            details.append(f"크롤링 시간: {item['crawl_time']}")
        
        text_widget.insert(tk.END, '\n\n'.join(details))
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 액션 버튼
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if item.get('url'):
            ttk.Button(button_frame, text="🔗 브라우저에서 열기", 
                      command=lambda: webbrowser.open(item['url'])).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="닫기", command=self.window.destroy).pack(side=tk.RIGHT)


if __name__ == "__main__":
    # 테스트용 샘플 데이터
    sample_data = [
        {
            'title': '아이폰 15 프로 할인 특가',
            'url': 'https://shop.example.com/iphone15',
            'price': '1,200,000원',
            'description': '최신 아이폰 15 프로 특가 판매',
            'tags': ['스마트폰', '할인', '고가']
        },
        {
            'title': '노트북 게이밍 특가',
            'url': 'https://electronics.example.com/laptop',
            'price': '800,000원',
            'description': '고성능 게이밍 노트북',
            'tags': ['노트북', '게이밍', '중가']
        }
    ]
    
    root = tk.Tk()
    root.title("고급 크롤링 결과 뷰어 테스트")
    root.geometry("1200x800")
    
    viewer = AdvancedResultsViewer(root, sample_data)
    
    root.mainloop() 