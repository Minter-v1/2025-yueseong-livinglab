#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메인 GUI 윈도우
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime


class MainWindow:
    """메인 애플리케이션 윈도우"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("행복e음 자동화 프로그램")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # 변수
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.is_running = False
        self.total_count = 0
        self.current_index = 0
        
        # UI 구성
        self.create_widgets()
        
    def create_widgets(self):
        """UI 위젯 생성"""
        
        # 상단: 제목
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="행복e음 자동화 프로그램",
            font=("맑은 고딕", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # 파일 선택 영역
        file_frame = tk.LabelFrame(
            self.root,
            text="파일 선택",
            font=("맑은 고딕", 11, "bold"),
            bg="#f5f5f5",
            padx=20,
            pady=15
        )
        file_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 입력 파일
        tk.Label(
            file_frame,
            text="입력 파일 (Excel/CSV):",
            font=("맑은 고딕", 10),
            bg="#f5f5f5"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        tk.Entry(
            file_frame,
            textvariable=self.input_file_path,
            font=("맑은 고딕", 10),
            width=50,
            state='readonly'
        ).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Button(
            file_frame,
            text="찾아보기",
            font=("맑은 고딕", 9),
            command=self.browse_input_file,
            bg="#3498db",
            fg="black",
            width=10
        ).grid(row=0, column=2, pady=5)
        
        # 출력 파일
        tk.Label(
            file_frame,
            text="출력 파일 (Excel/CSV):",
            font=("맑은 고딕", 10),
            bg="#f5f5f5"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        tk.Entry(
            file_frame,
            textvariable=self.output_file_path,
            font=("맑은 고딕", 10),
            width=50,
            state='readonly'
        ).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Button(
            file_frame,
            text="찾아보기",
            font=("맑은 고딕", 9),
            command=self.browse_output_file,
            bg="#3498db",
            fg="black",
            width=10
        ).grid(row=1, column=2, pady=5)
        
        # 진행 상황 영역
        progress_frame = tk.LabelFrame(
            self.root,
            text="진행 상황",
            font=("맑은 고딕", 11, "bold"),
            bg="#f5f5f5",
            padx=20,
            pady=15
        )
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 진행률 표시
        self.progress_label = tk.Label(
            progress_frame,
            text="대기 중... (0/0)",
            font=("맑은 고딕", 10),
            bg="#f5f5f5"
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 프로그레스 바
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 로그 영역
        log_frame = tk.LabelFrame(
            self.root,
            text="로그",
            font=("맑은 고딕", 11, "bold"),
            bg="#f5f5f5",
            padx=20,
            pady=15
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            height=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 버튼 영역
        button_frame = tk.Frame(self.root, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.start_button = tk.Button(
            button_frame,
            text="시작",
            font=("맑은 고딕", 12, "bold"),
            bg="#27ae60",
            fg="black",
            width=15,
            height=2,
            command=self.start_automation
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="중지",
            font=("맑은 고딕", 12, "bold"),
            bg="#e74c3c",
            fg="black",
            width=15,
            height=2,
            command=self.stop_automation,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="로그 지우기",
            font=("맑은 고딕", 10),
            bg="#95a5a6",
            fg="black",
            width=15,
            command=self.clear_log
        ).pack(side=tk.RIGHT, padx=5)
    
    def browse_input_file(self):
        """입력 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="입력 파일 선택",
            filetypes=[
                ("Excel/CSV files", "*.xlsx *.xls *.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)
            self.log(f"입력 파일 선택: {file_path}")
            
            # 출력 파일 자동 설정
            if not self.output_file_path.get():
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_결과{ext}"
                self.output_file_path.set(output_path)
    
    def browse_output_file(self):
        """출력 파일 선택"""
        file_path = filedialog.asksaveasfilename(
            title="출력 파일 선택",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_file_path.set(file_path)
            self.log(f"출력 파일 선택: {file_path}")
    
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, current, total):
        """진행 상황 업데이트"""
        self.current_index = current
        self.total_count = total
        
        percentage = (current / total * 100) if total > 0 else 0
        self.progress_label.config(text=f"진행 중... ({current}/{total}) - {percentage:.1f}%")
        self.progress_bar['value'] = percentage
        self.root.update()
    
    def start_automation(self):
        """자동화 시작"""
        # 입력 파일 확인
        if not self.input_file_path.get():
            messagebox.showwarning("경고", "입력 파일을 선택하세요.")
            return
        
        if not self.output_file_path.get():
            messagebox.showwarning("경고", "출력 파일을 선택하세요.")
            return
        
        # 확인 메시지
        if not messagebox.askyesno(
            "확인",
            "자동화를 시작하시겠습니까?\n\n"
            "주의사항:\n"
            "1. 행복e음 시스템이 열려 있어야 합니다.\n"
            "2. 실행 중에는 마우스/키보드를 사용하지 마세요.\n"
            "3. 화면이 가려지지 않도록 주의하세요."
        ):
            return
        
        # UI 상태 변경
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self.run_automation)
        thread.daemon = True
        thread.start()
    
    def stop_automation(self):
        """자동화 중지"""
        self.is_running = False
        self.log("중지 요청됨...")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def run_automation(self):
        """자동화 실행 (별도 스레드)"""
        try:
            self.log("=" * 60)
            self.log("자동화 시작")
            self.log("=" * 60)

            # 1. Excel 파일 읽기
            from ..services.excel_service import ExcelService
            excel_service = ExcelService()

            self.log(f"입력 파일 읽기: {self.input_file_path.get()}")
            records = excel_service.read_residents(self.input_file_path.get())

            self.log(f"총 {len(records)}건 로드됨")

            # 2. 검색 자동화 서비스 초기화 (템플릿 매칭 모드)
            from ..services.search_service import SearchAutomationService
            search_service = SearchAutomationService()

            self.log("- 검색 자동화 서비스 초기화 완료")
            self.log("- 모드: OpenCV 템플릿 매칭")
            self.log("- 주의: 이제부터 마우스/키보드를 사용하지 마세요!")
            self.log("")

            # 5초 대기 (사용자가 Mock 시스템으로 전환할 시간)
            import time
            for i in range(5, 0, -1):
                self.log(f"{i}초 후 시작...")
                time.sleep(1)

            self.log("")

            # 3. 각 주민등록번호 검색
            results = []
            total = len(records)

            for i, record in enumerate(records, 1):
                # 중지 요청 확인
                if not self.is_running:
                    self.log("사용자가 중지했습니다.")
                    break

                resident_number = record.get('주민등록번호', '')
                name = record.get('이름', '')

                self.log(f"\n{'='*60}")
                self.log(f"[{i}/{total}] {name} ({resident_number})")
                self.log(f"{'='*60}")

                # 검색 실행 (이미지 매칭 사용)
                result = search_service.search_resident(resident_number)

                # 결과 기록
                record['세대원수'] = result['household_count']
                record['상태'] = '완료' if result['status'] == 'success' else '오류'
                record['메시지'] = result['message']
                results.append(record)

                # 진행 상황 업데이트
                self.update_progress(i, total)

                if result['status'] == 'success':
                    self.log(f"완료: {result['household_count']}명")
                else:
                    self.log(f"오류: {result['message']}")

                # 다음 검색 전 대기 (1초)
                if i < total:
                    time.sleep(1)

            # 4. 결과 저장
            self.log("")
            self.log("=" * 60)
            self.log("결과 저장 중...")

            excel_service.write_results(self.output_file_path.get(), results)

            self.log(f"결과 저장 완료: {self.output_file_path.get()}")
            self.log("=" * 60)
            self.log(f"전체 작업 완료: (총 {len(results)}건 처리)")
            self.log("=" * 60)

            # 완료 메시지
            messagebox.showinfo(
                "완료",
                f"자동화가 완료되었습니다!\n\n"
                f"처리 건수: {len(results)}건\n"
                f"결과 파일: {self.output_file_path.get()}"
            )

        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            self.log(f"\n오류 발생:\n{error_msg}")
            messagebox.showerror("오류", f"자동화 중 오류가 발생했습니다:\n\n{error_msg}")

        finally:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)


def main():
    """메인 함수"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

