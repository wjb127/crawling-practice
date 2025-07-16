#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쇼핑몰 가격 모니터링 특화 시스템
실시간 가격 추적, 알림, 분석 기능 제공
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
from threading import Thread
import time

class PriceMonitoringSystem:
    """가격 모니터링 시스템"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.monitoring_items = []
        self.price_history = {}
        self.is_monitoring = False
        
        # 설정
        self.settings = {
            'check_interval': 300,  # 5분
            'price_change_threshold': 5.0,  # 5% 변동
            'email_alerts': False,
            'desktop_alerts': True
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 상단 제어 패널
        self.setup_control_panel(main_container)
        
        # 중간 모니터링 목록
        self.setup_monitoring_list(main_container)
        
        # 하단 차트 및 분석
        self.setup_chart_analysis(main_container)
    
    def setup_control_panel(self, parent):
        """제어 패널 설정"""
        control_frame = ttk.LabelFrame(parent, text="💰 가격 모니터링 제어", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 첫 번째 행: 모니터링 제어
        control_row1 = ttk.Frame(control_frame)
        control_row1.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(control_row1, text="상태: 대기 중", font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        self.start_button = ttk.Button(control_row1, text="🚀 모니터링 시작", 
                                      command=self.start_monitoring)
        self.start_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.stop_button = ttk.Button(control_row1, text="⏹️ 중지", 
                                     command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side=tk.RIGHT)
        
        # 두 번째 행: 설정
        control_row2 = ttk.Frame(control_frame)
        control_row2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(control_row2, text="체크 간격:").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="5")
        interval_combo = ttk.Combobox(control_row2, textvariable=self.interval_var, width=5,
                                     values=["1", "5", "10", "30", "60"])
        interval_combo.pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(control_row2, text="분").pack(side=tk.LEFT)
        
        ttk.Label(control_row2, text="변동 임계값:").pack(side=tk.LEFT, padx=(20, 5))
        self.threshold_var = tk.StringVar(value="5.0")
        ttk.Entry(control_row2, textvariable=self.threshold_var, width=8).pack(side=tk.LEFT)
        ttk.Label(control_row2, text="%").pack(side=tk.LEFT)
        
        # 세 번째 행: 알림 설정
        control_row3 = ttk.Frame(control_frame)
        control_row3.pack(fill=tk.X)
        
        self.desktop_alert_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_row3, text="💻 데스크탑 알림", 
                       variable=self.desktop_alert_var).pack(side=tk.LEFT)
        
        self.email_alert_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_row3, text="📧 이메일 알림", 
                       variable=self.email_alert_var).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(control_row3, text="⚙️ 고급 설정", 
                  command=self.show_advanced_settings).pack(side=tk.RIGHT)
    
    def setup_monitoring_list(self, parent):
        """모니터링 목록 설정"""
        list_frame = ttk.LabelFrame(parent, text="📋 모니터링 목록", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 상단 도구 모음
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="➕ 상품 추가", command=self.add_monitoring_item).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="✏️ 편집", command=self.edit_selected_item).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(toolbar, text="🗑️ 삭제", command=self.remove_selected_item).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(toolbar, text="💾 목록 저장", command=self.save_monitoring_list).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="📂 목록 불러오기", command=self.load_monitoring_list).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 모니터링 리스트 (트리뷰)
        columns = ("name", "url", "current_price", "target_price", "change", "last_check", "status")
        self.monitoring_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # 헤더 설정
        headers = {
            "name": "상품명",
            "url": "URL",
            "current_price": "현재가격",
            "target_price": "목표가격",
            "change": "변동률",
            "last_check": "마지막 체크",
            "status": "상태"
        }
        
        for col, header in headers.items():
            self.monitoring_tree.heading(col, text=header)
        
        # 열 너비 설정
        self.monitoring_tree.column("name", width=200)
        self.monitoring_tree.column("url", width=100)
        self.monitoring_tree.column("current_price", width=100)
        self.monitoring_tree.column("target_price", width=100)
        self.monitoring_tree.column("change", width=80)
        self.monitoring_tree.column("last_check", width=120)
        self.monitoring_tree.column("status", width=80)
        
        # 스크롤바
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.monitoring_tree.yview)
        self.monitoring_tree.configure(yscrollcommand=list_scrollbar.set)
        
        self.monitoring_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 더블클릭으로 상세 정보
        self.monitoring_tree.bind("<Double-1>", self.show_item_details)
    
    def setup_chart_analysis(self, parent):
        """차트 및 분석 영역 설정"""
        chart_frame = ttk.LabelFrame(parent, text="📈 가격 추이 분석", padding="5")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # 차트 노트북
        chart_notebook = ttk.Notebook(chart_frame)
        chart_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 가격 추이 차트 탭
        self.price_chart_frame = ttk.Frame(chart_notebook)
        chart_notebook.add(self.price_chart_frame, text="💹 가격 추이")
        
        # 변동률 분석 탭
        self.change_analysis_frame = ttk.Frame(chart_notebook)
        chart_notebook.add(self.change_analysis_frame, text="📊 변동률 분석")
        
        # 알림 히스토리 탭
        self.alert_history_frame = ttk.Frame(chart_notebook)
        chart_notebook.add(self.alert_history_frame, text="🔔 알림 히스토리")
        
        # 초기 차트 생성
        self.create_price_chart()
        self.setup_alert_history()
    
    def add_monitoring_item(self):
        """모니터링 아이템 추가"""
        dialog = AddMonitoringItemDialog(self.parent_frame)
        if dialog.result:
            item = dialog.result
            item['id'] = f"item_{len(self.monitoring_items)}"
            item['price_history'] = []
            item['alerts'] = []
            item['created_at'] = datetime.now()
            item['status'] = 'active'
            
            self.monitoring_items.append(item)
            self.refresh_monitoring_list()
            messagebox.showinfo("완료", f"'{item['name']}' 모니터링 목록에 추가되었습니다.")
    
    def edit_selected_item(self):
        """선택된 아이템 편집"""
        selection = self.monitoring_tree.selection()
        if not selection:
            messagebox.showwarning("경고", "편집할 아이템을 선택해주세요.")
            return
        
        # 선택된 아이템 찾기
        item_values = self.monitoring_tree.item(selection[0])['values']
        item_name = item_values[0]
        
        for item in self.monitoring_items:
            if item['name'] == item_name:
                dialog = EditMonitoringItemDialog(self.parent_frame, item)
                if dialog.result:
                    item.update(dialog.result)
                    self.refresh_monitoring_list()
                break
    
    def remove_selected_item(self):
        """선택된 아이템 삭제"""
        selection = self.monitoring_tree.selection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 아이템을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "선택된 아이템을 삭제하시겠습니까?"):
            item_values = self.monitoring_tree.item(selection[0])['values']
            item_name = item_values[0]
            
            self.monitoring_items = [item for item in self.monitoring_items if item['name'] != item_name]
            self.refresh_monitoring_list()
    
    def refresh_monitoring_list(self):
        """모니터링 리스트 새로고침"""
        # 기존 항목 제거
        for item in self.monitoring_tree.get_children():
            self.monitoring_tree.delete(item)
        
        # 새 항목 추가
        for item in self.monitoring_items:
            current_price = item.get('current_price', 'N/A')
            target_price = item.get('target_price', 'N/A')
            
            # 변동률 계산
            change_pct = "N/A"
            if item.get('price_history') and len(item['price_history']) > 1:
                old_price = item['price_history'][-2]['price']
                new_price = item['price_history'][-1]['price']
                if old_price > 0:
                    change_pct = f"{((new_price - old_price) / old_price * 100):.2f}%"
            
            last_check = item.get('last_check', 'Never')
            if isinstance(last_check, datetime):
                last_check = last_check.strftime('%m-%d %H:%M')
            
            # 도메인 추출
            domain = "N/A"
            if item.get('url'):
                from urllib.parse import urlparse
                domain = urlparse(item['url']).netloc
            
            values = (
                item['name'],
                domain,
                current_price,
                target_price,
                change_pct,
                last_check,
                item.get('status', 'active')
            )
            
            self.monitoring_tree.insert('', 'end', values=values)
    
    def start_monitoring(self):
        """모니터링 시작"""
        if not self.monitoring_items:
            messagebox.showwarning("경고", "모니터링할 아이템이 없습니다.\n먼저 상품을 추가해주세요.")
            return
        
        self.is_monitoring = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="상태: 모니터링 중", foreground="green")
        
        # 설정 업데이트
        self.settings['check_interval'] = int(self.interval_var.get()) * 60  # 분을 초로 변환
        self.settings['price_change_threshold'] = float(self.threshold_var.get())
        self.settings['desktop_alerts'] = self.desktop_alert_var.get()
        self.settings['email_alerts'] = self.email_alert_var.get()
        
        # 백그라운드 모니터링 스레드 시작
        self.monitoring_thread = Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        messagebox.showinfo("시작", f"{len(self.monitoring_items)}개 상품의 가격 모니터링을 시작합니다.")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="상태: 중지됨", foreground="red")
        
        messagebox.showinfo("중지", "가격 모니터링이 중지되었습니다.")
    
    def monitoring_loop(self):
        """모니터링 루프 (백그라운드 실행)"""
        while self.is_monitoring:
            try:
                for item in self.monitoring_items:
                    if not self.is_monitoring:
                        break
                    
                    if item.get('status') == 'active':
                        self.check_item_price(item)
                
                # 설정된 간격만큼 대기
                for _ in range(self.settings['check_interval']):
                    if not self.is_monitoring:
                        break
                    time.sleep(1)
                
            except Exception as e:
                print(f"[DEBUG] 모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def check_item_price(self, item):
        """개별 아이템 가격 체크"""
        try:
            url = item.get('url')
            if not url:
                return
            
            # HTTP 요청으로 가격 정보 가져오기
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 가격 추출 (사이트별 맞춤형 파싱 필요)
            price = self.extract_price_from_html(response.text, item.get('price_selector'))
            
            if price:
                # 가격 히스토리 업데이트
                price_entry = {
                    'price': price,
                    'timestamp': datetime.now(),
                    'url': url
                }
                
                if 'price_history' not in item:
                    item['price_history'] = []
                
                item['price_history'].append(price_entry)
                item['current_price'] = f"{price:,}원"
                item['last_check'] = datetime.now()
                
                # 가격 변동 체크
                self.check_price_alerts(item, price)
                
                # UI 업데이트 (메인 스레드에서)
                self.parent_frame.after(0, self.refresh_monitoring_list)
                self.parent_frame.after(0, self.update_charts)
                
        except Exception as e:
            print(f"[DEBUG] 가격 체크 오류 ({item.get('name', 'Unknown')}): {e}")
            item['last_check'] = datetime.now()
            item['status'] = 'error'
    
    def extract_price_from_html(self, html, price_selector=None):
        """HTML에서 가격 추출"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 사용자 정의 셀렉터가 있으면 사용
        if price_selector:
            try:
                price_elem = soup.select_one(price_selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    return self.parse_price_text(price_text)
            except:
                pass
        
        # 일반적인 가격 패턴 검색
        price_patterns = [
            r'(\d+,?\d*)\s*원',
            r'\$\s*(\d+,?\d*)',
            r'price["\'\s]*[:\s]*["\']?(\d+,?\d*)',
            r'(\d+,?\d*)\s*KRW'
        ]
        
        text = soup.get_text()
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    price_str = matches[0].replace(',', '')
                    return int(price_str)
                except:
                    continue
        
        return None
    
    def parse_price_text(self, price_text):
        """가격 텍스트에서 숫자 추출"""
        # 콤마 제거하고 숫자만 추출
        numbers = re.findall(r'\d+', price_text.replace(',', ''))
        if numbers:
            # 가장 큰 숫자를 가격으로 간주
            return max(int(num) for num in numbers)
        return None
    
    def check_price_alerts(self, item, current_price):
        """가격 알림 체크"""
        try:
            # 목표 가격 체크
            target_price = item.get('target_price')
            if target_price and isinstance(target_price, (int, float)):
                if current_price <= target_price:
                    self.send_alert(item, f"목표 가격 달성! {current_price:,}원 ≤ {target_price:,}원")
            
            # 변동률 체크
            if len(item.get('price_history', [])) >= 2:
                previous_price = item['price_history'][-2]['price']
                change_pct = ((current_price - previous_price) / previous_price) * 100
                
                if abs(change_pct) >= self.settings['price_change_threshold']:
                    direction = "상승" if change_pct > 0 else "하락"
                    self.send_alert(item, f"가격 {direction}: {change_pct:.2f}% ({previous_price:,}원 → {current_price:,}원)")
        
        except Exception as e:
            print(f"[DEBUG] 알림 체크 오류: {e}")
    
    def send_alert(self, item, message):
        """알림 전송"""
        alert_data = {
            'item_name': item['name'],
            'message': message,
            'timestamp': datetime.now(),
            'url': item.get('url', '')
        }
        
        # 알림 히스토리에 추가
        if 'alerts' not in item:
            item['alerts'] = []
        item['alerts'].append(alert_data)
        
        # 데스크탑 알림
        if self.settings['desktop_alerts']:
            try:
                from plyer import notification
                notification.notify(
                    title=f"가격 알림: {item['name']}",
                    message=message,
                    timeout=10
                )
            except:
                pass
        
        # 이메일 알림 (설정된 경우)
        if self.settings['email_alerts']:
            self.send_email_alert(item, message)
    
    def send_email_alert(self, item, message):
        """이메일 알림 전송"""
        # 이메일 발송 로직 (간단한 예시)
        try:
            # 실제 구현에서는 사용자의 이메일 설정을 사용
            print(f"[이메일 알림] {item['name']}: {message}")
        except Exception as e:
            print(f"[DEBUG] 이메일 알림 오류: {e}")
    
    def create_price_chart(self):
        """가격 추이 차트 생성"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_title('가격 추이')
            ax.set_xlabel('시간')
            ax.set_ylabel('가격 (원)')
            
            # 샘플 데이터로 초기화
            ax.plot([], [], label='가격 데이터 없음')
            ax.legend()
            
            # tkinter에 차트 추가
            canvas = FigureCanvasTkAgg(fig, self.price_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.price_chart_canvas = canvas
            self.price_chart_fig = fig
            self.price_chart_ax = ax
            
        except Exception as e:
            print(f"[DEBUG] 차트 생성 오류: {e}")
            ttk.Label(self.price_chart_frame, text="차트를 표시할 수 없습니다.").pack(pady=20)
    
    def setup_alert_history(self):
        """알림 히스토리 설정"""
        # 알림 히스토리 리스트
        columns = ("item", "message", "time")
        self.alert_tree = ttk.Treeview(self.alert_history_frame, columns=columns, show="headings", height=10)
        
        self.alert_tree.heading("item", text="상품")
        self.alert_tree.heading("message", text="알림 내용")
        self.alert_tree.heading("time", text="시간")
        
        self.alert_tree.column("item", width=150)
        self.alert_tree.column("message", width=300)
        self.alert_tree.column("time", width=150)
        
        alert_scrollbar = ttk.Scrollbar(self.alert_history_frame, orient="vertical", command=self.alert_tree.yview)
        self.alert_tree.configure(yscrollcommand=alert_scrollbar.set)
        
        self.alert_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alert_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_charts(self):
        """차트 업데이트"""
        try:
            if hasattr(self, 'price_chart_ax'):
                self.price_chart_ax.clear()
                self.price_chart_ax.set_title('가격 추이')
                self.price_chart_ax.set_xlabel('시간')
                self.price_chart_ax.set_ylabel('가격 (원)')
                
                # 각 아이템의 가격 히스토리 플롯
                for item in self.monitoring_items:
                    history = item.get('price_history', [])
                    if len(history) > 1:
                        times = [entry['timestamp'] for entry in history]
                        prices = [entry['price'] for entry in history]
                        
                        self.price_chart_ax.plot(times, prices, marker='o', 
                                               label=item['name'][:20], linewidth=2)
                
                self.price_chart_ax.legend()
                self.price_chart_ax.grid(True, alpha=0.3)
                self.price_chart_canvas.draw()
        
        except Exception as e:
            print(f"[DEBUG] 차트 업데이트 오류: {e}")
    
    def show_advanced_settings(self):
        """고급 설정 창 표시"""
        AdvancedSettingsWindow(self.parent_frame, self.settings)
    
    def show_item_details(self, event):
        """아이템 상세 정보 표시"""
        selection = self.monitoring_tree.selection()
        if selection:
            item_values = self.monitoring_tree.item(selection[0])['values']
            item_name = item_values[0]
            
            for item in self.monitoring_items:
                if item['name'] == item_name:
                    ItemDetailsWindow(self.parent_frame, item)
                    break
    
    def save_monitoring_list(self):
        """모니터링 목록 저장"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="모니터링 목록 저장"
        )
        
        if filename:
            try:
                # datetime 객체를 문자열로 변환
                save_data = []
                for item in self.monitoring_items:
                    item_copy = item.copy()
                    
                    # datetime 필드 처리
                    if 'created_at' in item_copy and isinstance(item_copy['created_at'], datetime):
                        item_copy['created_at'] = item_copy['created_at'].isoformat()
                    
                    if 'last_check' in item_copy and isinstance(item_copy['last_check'], datetime):
                        item_copy['last_check'] = item_copy['last_check'].isoformat()
                    
                    # price_history의 datetime 처리
                    if 'price_history' in item_copy:
                        for entry in item_copy['price_history']:
                            if isinstance(entry.get('timestamp'), datetime):
                                entry['timestamp'] = entry['timestamp'].isoformat()
                    
                    save_data.append(item_copy)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("완료", f"모니터링 목록이 저장되었습니다:\n{filename}")
            
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def load_monitoring_list(self):
        """모니터링 목록 불러오기"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="모니터링 목록 불러오기"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    load_data = json.load(f)
                
                # datetime 필드 복원
                for item in load_data:
                    if 'created_at' in item and isinstance(item['created_at'], str):
                        item['created_at'] = datetime.fromisoformat(item['created_at'])
                    
                    if 'last_check' in item and isinstance(item['last_check'], str):
                        item['last_check'] = datetime.fromisoformat(item['last_check'])
                    
                    # price_history의 datetime 복원
                    if 'price_history' in item:
                        for entry in item['price_history']:
                            if isinstance(entry.get('timestamp'), str):
                                entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                
                self.monitoring_items = load_data
                self.refresh_monitoring_list()
                
                messagebox.showinfo("완료", f"{len(load_data)}개 항목을 불러왔습니다.")
            
            except Exception as e:
                messagebox.showerror("오류", f"불러오기 중 오류가 발생했습니다:\n{str(e)}")


class AddMonitoringItemDialog:
    """모니터링 아이템 추가 대화상자"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("상품 추가")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # 중앙 배치
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.dialog.wait_window()
    
    def setup_ui(self):
        """UI 설정"""
        # 상품 정보 입력
        info_frame = ttk.LabelFrame(self.dialog, text="상품 정보", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 상품명
        ttk.Label(info_frame, text="상품명:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, sticky="ew", pady=2)
        
        # URL
        ttk.Label(info_frame, text="URL:").grid(row=1, column=0, sticky="w", pady=2)
        self.url_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.url_var, width=50).grid(row=1, column=1, sticky="ew", pady=2)
        
        # 목표 가격
        ttk.Label(info_frame, text="목표 가격:").grid(row=2, column=0, sticky="w", pady=2)
        self.target_price_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.target_price_var, width=20).grid(row=2, column=1, sticky="w", pady=2)
        
        info_frame.grid_columnconfigure(1, weight=1)
        
        # 고급 설정
        advanced_frame = ttk.LabelFrame(self.dialog, text="고급 설정 (선택사항)", padding="10")
        advanced_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 가격 셀렉터
        ttk.Label(advanced_frame, text="가격 CSS 셀렉터:").grid(row=0, column=0, sticky="w", pady=2)
        self.selector_var = tk.StringVar()
        ttk.Entry(advanced_frame, textvariable=self.selector_var, width=50).grid(row=0, column=1, sticky="ew", pady=2)
        
        # 설명
        ttk.Label(advanced_frame, text="설명:").grid(row=1, column=0, sticky="nw", pady=2)
        self.description_text = tk.Text(advanced_frame, height=4, width=50)
        self.description_text.grid(row=1, column=1, sticky="ew", pady=2)
        
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        # 버튼
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="URL에서 정보 가져오기", command=self.fetch_from_url).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="추가", command=self.ok).pack(side=tk.RIGHT, padx=(0, 5))
    
    def fetch_from_url(self):
        """URL에서 상품 정보 자동 추출"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("경고", "URL을 입력해주세요.")
            return
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목 추출
            title = soup.find('title')
            if title and not self.name_var.get():
                self.name_var.set(title.get_text(strip=True)[:100])
            
            # 가격 추출 시도
            price_patterns = [
                r'(\d+,?\d*)\s*원',
                r'\$\s*(\d+,?\d*)',
                r'price["\'\s]*[:\s]*["\']?(\d+,?\d*)'
            ]
            
            text = soup.get_text()
            for pattern in price_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    try:
                        price = int(matches[0].replace(',', ''))
                        if not self.target_price_var.get():
                            self.target_price_var.set(str(price))
                        break
                    except:
                        continue
            
            messagebox.showinfo("완료", "URL에서 정보를 가져왔습니다.")
        
        except Exception as e:
            messagebox.showerror("오류", f"정보 가져오기 실패:\n{str(e)}")
    
    def ok(self):
        """확인 버튼"""
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        
        if not name:
            messagebox.showerror("오류", "상품명을 입력해주세요.")
            return
        
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
            return
        
        try:
            target_price = None
            if self.target_price_var.get().strip():
                target_price = int(self.target_price_var.get().replace(',', ''))
        except ValueError:
            messagebox.showerror("오류", "올바른 목표 가격을 입력해주세요.")
            return
        
        self.result = {
            'name': name,
            'url': url,
            'target_price': target_price,
            'price_selector': self.selector_var.get().strip() or None,
            'description': self.description_text.get(1.0, tk.END).strip()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """취소 버튼"""
        self.dialog.destroy()


class EditMonitoringItemDialog:
    """모니터링 아이템 편집 대화상자"""
    
    def __init__(self, parent, item):
        self.parent = parent
        self.item = item
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("상품 편집")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_item_data()
        
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.dialog.wait_window()
    
    def setup_ui(self):
        """UI 설정 (AddMonitoringItemDialog와 동일)"""
        # 동일한 UI 구성
        info_frame = ttk.LabelFrame(self.dialog, text="상품 정보", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="상품명:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(info_frame, text="URL:").grid(row=1, column=0, sticky="w", pady=2)
        self.url_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.url_var, width=50).grid(row=1, column=1, sticky="ew", pady=2)
        
        ttk.Label(info_frame, text="목표 가격:").grid(row=2, column=0, sticky="w", pady=2)
        self.target_price_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.target_price_var, width=20).grid(row=2, column=1, sticky="w", pady=2)
        
        info_frame.grid_columnconfigure(1, weight=1)
        
        advanced_frame = ttk.LabelFrame(self.dialog, text="고급 설정", padding="10")
        advanced_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(advanced_frame, text="가격 CSS 셀렉터:").grid(row=0, column=0, sticky="w", pady=2)
        self.selector_var = tk.StringVar()
        ttk.Entry(advanced_frame, textvariable=self.selector_var, width=50).grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(advanced_frame, text="설명:").grid(row=1, column=0, sticky="nw", pady=2)
        self.description_text = tk.Text(advanced_frame, height=4, width=50)
        self.description_text.grid(row=1, column=1, sticky="ew", pady=2)
        
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="저장", command=self.ok).pack(side=tk.RIGHT, padx=(0, 5))
    
    def load_item_data(self):
        """기존 아이템 데이터 로드"""
        self.name_var.set(self.item.get('name', ''))
        self.url_var.set(self.item.get('url', ''))
        
        if self.item.get('target_price'):
            self.target_price_var.set(str(self.item['target_price']))
        
        self.selector_var.set(self.item.get('price_selector', ''))
        self.description_text.insert(1.0, self.item.get('description', ''))
    
    def ok(self):
        """저장 버튼"""
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        
        if not name or not url:
            messagebox.showerror("오류", "상품명과 URL을 입력해주세요.")
            return
        
        try:
            target_price = None
            if self.target_price_var.get().strip():
                target_price = int(self.target_price_var.get().replace(',', ''))
        except ValueError:
            messagebox.showerror("오류", "올바른 목표 가격을 입력해주세요.")
            return
        
        self.result = {
            'name': name,
            'url': url,
            'target_price': target_price,
            'price_selector': self.selector_var.get().strip() or None,
            'description': self.description_text.get(1.0, tk.END).strip()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """취소 버튼"""
        self.dialog.destroy()


class AdvancedSettingsWindow:
    """고급 설정 창"""
    
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        
        self.window = tk.Toplevel(parent)
        self.window.title("고급 설정")
        self.window.geometry("400x300")
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        # 알림 설정
        alert_frame = ttk.LabelFrame(self.window, text="알림 설정", padding="10")
        alert_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 이메일 설정은 여기에 추가 가능
        ttk.Label(alert_frame, text="이메일 알림 기능은 향후 추가 예정").pack()
        
        # 네트워크 설정
        network_frame = ttk.LabelFrame(self.window, text="네트워크 설정", padding="10")
        network_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(network_frame, text="요청 타임아웃 (초):").pack(anchor="w")
        self.timeout_var = tk.StringVar(value="10")
        ttk.Entry(network_frame, textvariable=self.timeout_var, width=10).pack(anchor="w")
        
        ttk.Label(network_frame, text="재시도 횟수:").pack(anchor="w", pady=(10, 0))
        self.retry_var = tk.StringVar(value="3")
        ttk.Entry(network_frame, textvariable=self.retry_var, width=10).pack(anchor="w")
        
        # 버튼
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="저장", command=self.save).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="취소", command=self.window.destroy).pack(side=tk.RIGHT, padx=(0, 5))
    
    def save(self):
        """설정 저장"""
        try:
            self.settings['timeout'] = int(self.timeout_var.get())
            self.settings['max_retries'] = int(self.retry_var.get())
            
            messagebox.showinfo("완료", "설정이 저장되었습니다.")
            self.window.destroy()
        
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자 값을 입력해주세요.")


class ItemDetailsWindow:
    """아이템 상세 정보 창"""
    
    def __init__(self, parent, item):
        self.window = tk.Toplevel(parent)
        self.window.title(f"상세 정보: {item.get('name', 'Unknown')}")
        self.window.geometry("600x500")
        
        self.setup_ui(item)
    
    def setup_ui(self, item):
        """UI 설정"""
        # 상품 정보
        info_frame = ttk.LabelFrame(self.window, text="상품 정보", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = f"""
상품명: {item.get('name', 'N/A')}
URL: {item.get('url', 'N/A')}
목표 가격: {item.get('target_price', 'N/A')}
현재 가격: {item.get('current_price', 'N/A')}
상태: {item.get('status', 'N/A')}
생성일: {item.get('created_at', 'N/A')}
마지막 체크: {item.get('last_check', 'N/A')}
        """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor="w")
        
        # 가격 히스토리
        history_frame = ttk.LabelFrame(self.window, text="가격 히스토리", padding="5")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 히스토리 테이블
        columns = ("time", "price")
        history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        history_tree.heading("time", text="시간")
        history_tree.heading("price", text="가격")
        
        history_tree.column("time", width=200)
        history_tree.column("price", width=100)
        
        # 히스토리 데이터 추가
        for entry in item.get('price_history', []):
            timestamp = entry.get('timestamp', 'N/A')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            price = entry.get('price', 'N/A')
            if isinstance(price, (int, float)):
                price = f"{price:,}원"
            
            history_tree.insert('', 'end', values=(timestamp, price))
        
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 닫기 버튼
        ttk.Button(self.window, text="닫기", command=self.window.destroy).pack(pady=10)


if __name__ == "__main__":
    # 테스트용
    root = tk.Tk()
    root.title("가격 모니터링 시스템 테스트")
    root.geometry("1200x800")
    
    price_monitor = PriceMonitoringSystem(root)
    
    root.mainloop() 