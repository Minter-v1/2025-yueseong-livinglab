import sys
import os
import tkinter as tk

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import MainWindow


def main():
    """메인 함수"""
    print("행복e음 자동화 프로그램")
    print("개발: 2025 by ys-ongyeol")
    
    # GUI 실행
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

