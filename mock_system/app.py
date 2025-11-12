"""
행복e음 주민조회 Mock 시스템
실제 행정망 시스템을 모방한 테스트 환경
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os


class HaengbokEumMockSystem:
    """행복e음 주민조회 시스템 Mock"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("행복e음 - 주민조회")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # 데이터베이스 로드
        self.db_path = os.path.join(os.path.dirname(__file__), "database.csv")
        self.load_database()
        
        # UI 구성
        self.create_widgets()
        
    def load_database(self):
        """CSV 데이터베이스 로드"""
        try:
            self.df = pd.read_csv(self.db_path, encoding='utf-8')
            print(f"데이터베이스 로드 완료: {len(self.df)}건")
        except Exception as e:
            print(f"데이터베이스 로드 실패: {e}")
            self.df = pd.DataFrame()
    
    def create_widgets(self):
        """UI 위젯 생성"""
        
        # 상단: 제목
        title_frame = tk.Frame(self.root, bg="#003366", height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(
            title_frame,
            text="행복e음 - 주민조회",
            font=("맑은 고딕", 18, "bold"),
            bg="#003366",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # 검색 영역
        search_frame = tk.LabelFrame(
            self.root,
            text="조회 조건",
            font=("맑은 고딕", 11, "bold"),
            bg="#f0f0f0",
            padx=20,
            pady=15
        )
        search_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 주민등록번호 입력
        tk.Label(
            search_frame,
            text="주민등록번호:",
            font=("맑은 고딕", 10),
            bg="#f0f0f0"
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.resident_number_entry = tk.Entry(
            search_frame,
            font=("맑은 고딕", 11),
            width=20
        )
        self.resident_number_entry.grid(row=0, column=1, padx=5, pady=5)
        self.resident_number_entry.bind('<Return>', lambda e: self.search())
        
        # 검색 버튼
        self.search_button = tk.Button(
            search_frame,
            text="조회",
            font=("맑은 고딕", 10, "bold"),
            bg="#666666",
            fg="black",
            width=10,
            command=self.search
        )
        self.search_button.grid(row=0, column=2, padx=10, pady=5)
        
        # 초기화 버튼
        reset_button = tk.Button(
            search_frame,
            text="초기화",
            font=("맑은 고딕", 10),
            bg="#666666",
            fg="black",
            width=10,
            command=self.reset
        )
        reset_button.grid(row=0, column=3, padx=5, pady=5)
        
        # 결과 영역
        result_frame = tk.LabelFrame(
            self.root,
            text="조회 결과",
            font=("맑은 고딕", 11, "bold"),
            bg="#f0f0f0",
            padx=20,
            pady=15
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 스크롤바
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 결과 표시 영역 (Canvas + Frame)
        self.result_canvas = tk.Canvas(
            result_frame,
            bg="white",
            yscrollcommand=scrollbar.set
        )
        self.result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_canvas.yview)
        
        # 결과 내용을 담을 프레임
        self.result_content_frame = tk.Frame(self.result_canvas, bg="white")
        self.result_canvas_window = self.result_canvas.create_window(
            (0, 0),
            window=self.result_content_frame,
            anchor=tk.NW
        )
        
        # Canvas 크기 조정 이벤트
        self.result_content_frame.bind(
            '<Configure>',
            lambda e: self.result_canvas.configure(
                scrollregion=self.result_canvas.bbox("all")
            )
        )
        
        # 초기 메시지
        self.show_initial_message()
        
        # 하단: 상태바
        status_frame = tk.Frame(self.root, bg="#e0e0e0", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text="대기 중...",
            font=("맑은 고딕", 9),
            bg="#e0e0e0",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def show_initial_message(self):
        """초기 메시지 표시"""
        msg = tk.Label(
            self.result_content_frame,
            text="주민등록번호를 입력하고 '조회' 버튼을 클릭하세요.",
            font=("맑은 고딕", 11),
            bg="white",
            fg="#666666"
        )
        msg.pack(pady=50)
    
    def clear_results(self):
        """결과 영역 초기화"""
        for widget in self.result_content_frame.winfo_children():
            widget.destroy()
    
    def search(self):
        """주민등록번호 검색"""
        resident_number = self.resident_number_entry.get().strip()
        
        if not resident_number:
            messagebox.showwarning("입력 오류", "주민등록번호를 입력하세요.")
            return
        
        # 데이터베이스에서 검색
        result = self.df[self.df['주민등록번호'] == resident_number]
        
        if result.empty:
            self.show_no_result()
            self.status_label.config(text=f"조회 결과: 0건")
        else:
            self.show_result(result.iloc[0])
            household_count = self.count_household_members(result.iloc[0])
            self.status_label.config(text=f"조회 결과: {household_count}명")
    
    def count_household_members(self, row):
        """세대원 수 계산"""
        count = 1  # 본인
        for i in range(1, 4):  # 세대원1, 세대원2, 세대원3
            col_name = f'세대원{i}'
            if col_name in row and pd.notna(row[col_name]) and row[col_name].strip():
                count += 1
        return count
    
    def show_no_result(self):
        """검색 결과 없음 표시"""
        self.clear_results()
        
        msg = tk.Label(
            self.result_content_frame,
            text="조회 결과가 없습니다.",
            font=("맑은 고딕", 12, "bold"),
            bg="white",
            fg="#cc0000"
        )
        msg.pack(pady=50)
    
    def show_result(self, row):
        """검색 결과 표시 (체크박스 형태)"""
        self.clear_results()
        
        # 제목
        title = tk.Label(
            self.result_content_frame,
            text=f"세대원 정보 ({row['이름']})",
            font=("맑은 고딕", 12, "bold"),
            bg="white",
            fg="#003366"
        )
        title.pack(anchor=tk.W, padx=20, pady=(20, 10))
        
        # 구분선
        separator = tk.Frame(self.result_content_frame, height=2, bg="#cccccc")
        separator.pack(fill=tk.X, padx=20, pady=5)
        
        # 세대주 (본인)
        self.create_checkbox_item(
            row['이름'],
            row['세대주관계'],
            checked=True
        )
        
        # 세대원들
        for i in range(1, 4):
            member_col = f'세대원{i}'
            relation_col = f'세대원{i}관계'
            
            if member_col in row and pd.notna(row[member_col]) and row[member_col].strip():
                self.create_checkbox_item(
                    row[member_col],
                    row[relation_col],
                    checked=True
                )
    
    def create_checkbox_item(self, name, relation, checked=False):
        """체크박스 항목 생성"""
        item_frame = tk.Frame(self.result_content_frame, bg="white")
        item_frame.pack(fill=tk.X, padx=30, pady=5)
        
        # 체크박스
        var = tk.BooleanVar(value=checked)
        checkbox = tk.Checkbutton(
            item_frame,
            variable=var,
            bg="white",
            font=("맑은 고딕", 10)
        )
        checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # 이름
        name_label = tk.Label(
            item_frame,
            text=name,
            font=("맑은 고딕", 10),
            bg="white",
            width=10,
            anchor=tk.W
        )
        name_label.pack(side=tk.LEFT, padx=5)
        
        # 관계
        relation_label = tk.Label(
            item_frame,
            text=f"({relation})",
            font=("맑은 고딕", 9),
            bg="white",
            fg="#666666"
        )
        relation_label.pack(side=tk.LEFT, padx=5)
    
    def reset(self):
        """초기화"""
        self.resident_number_entry.delete(0, tk.END)
        self.clear_results()
        self.show_initial_message()
        self.status_label.config(text="대기 중...")


def main():
    """메인 함수"""
    root = tk.Tk()
    app = HaengbokEumMockSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()

