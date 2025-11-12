#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 템플릿 이미지 자동 생성 도구

Mock 시스템이 실행 중일 때 이 스크립트를 실행하면
자동으로 UI 요소를 캡처하여 템플릿 이미지를 생성합니다.
"""

import sys
import os
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyautogui
from PIL import Image
import tkinter as tk
from tkinter import messagebox


class TemplateCreator:
    """템플릿 이미지 생성기"""
    
    def __init__(self):
        self.templates_dir = "data/templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # PyAutoGUI 안전 설정
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True
    
    def show_instructions(self):
        """사용 안내"""
        root = tk.Tk()
        root.withdraw()
        
        message = """
※ UI 템플릿 이미지 자동 생성 도구

※ 준비사항:
1. Mock 시스템이 실행 중이어야 합니다
2. Mock 시스템 창이 화면에 보여야 합니다
3. 다른 창에 가려지지 않아야 합니다

※ 진행 순서:
1. "확인" 버튼을 클릭하면 5초 카운트다운이 시작됩니다
2. 5초 안에 Mock 시스템 창을 활성화하세요
3. 자동으로 화면을 캡처합니다
4. 마우스를 움직여 UI 요소를 선택합니다

※ 주의:
- 마우스 커서를 화면 왼쪽 상단 모서리로 이동하면 중단됩니다
- 각 단계마다 안내 메시지가 표시됩니다

준비되셨나요?
        """
        
        result = messagebox.askokcancel("템플릿 생성 도구", message)
        root.destroy()
        
        return result
    
    def countdown(self, seconds=5):
        """카운트다운"""
        print("\n" + "="*60)
        print("카운트다운 시작!")
        print("="*60)
        
        for i in range(seconds, 0, -1):
            print(f"  {i}초 후 시작... Mock 시스템 창을 활성화하세요!")
            time.sleep(1)
        
        print("시작!\n")
    
    def capture_fullscreen(self):
        """전체 화면 캡처"""
        print("전체 화면 캡처 중...")
        screenshot = pyautogui.screenshot()
        
        # 임시 저장
        temp_path = "tmp/fullscreen_template.png"
        os.makedirs("tmp", exist_ok=True)
        screenshot.save(temp_path)
        
        print(f" 저장됨: {temp_path}")
        return temp_path, screenshot
    
    def select_region_interactive(self, element_name, instruction):
        """대화형 영역 선택"""
        root = tk.Tk()
        root.withdraw()
        
        message = f"""
{element_name} 선택

{instruction}

- 방법:
1. "확인" 클릭 후 5초 안에 마우스를 해당 요소 위로 이동
2. 5초 후 자동으로 그 위치를 기준으로 영역을 캡처합니다

- 주의: 정확히 요소 중앙에 마우스를 위치시키세요!

준비되셨나요?
        """
        
        result = messagebox.askokcancel(f"{element_name} 선택", message)
        root.destroy()
        
        if not result:
            return None
        
        # 카운트다운
        print(f"\n{'='*60}")
        print(f"{element_name} 선택")
        print(f"{'='*60}")
        
        for i in range(5, 0, -1):
            print(f"  {i}초... 마우스를 {element_name} 위로 이동하세요!")
            time.sleep(1)
        
        # 마우스 위치 가져오기
        x, y = pyautogui.position()
        print(f"위치: ({x}, {y})")
        
        return (x, y)
    
    def crop_region(self, screenshot, center_x, center_y, width=200, height=50):
        """영역 자르기"""
        # 중심점 기준으로 영역 계산
        left = max(0, center_x - width // 2)
        top = max(0, center_y - height // 2)
        right = min(screenshot.width, center_x + width // 2)
        bottom = min(screenshot.height, center_y + height // 2)
        
        # 자르기
        cropped = screenshot.crop((left, top, right, bottom))
        
        return cropped
    
    def create_template(self, element_name, instruction, width=200, height=50):
        """템플릿 생성"""
        print(f"\n{'='*60}")
        print(f"{element_name} 템플릿 생성")
        print(f"{'='*60}")
        
        # 영역 선택
        position = self.select_region_interactive(element_name, instruction)
        
        if position is None:
            print(f"{element_name} 생성 취소됨")
            return False
        
        x, y = position
        
        # 화면 캡처
        print(f"화면 캡처 중...")
        screenshot = pyautogui.screenshot()
        
        # 영역 자르기
        print(f"영역 자르기... (중심: {x}, {y}, 크기: {width}x{height})")
        cropped = self.crop_region(screenshot, x, y, width, height)
        
        # 저장
        output_path = os.path.join(self.templates_dir, f"{element_name}.png")
        cropped.save(output_path)
        
        print(f" 저장됨: {output_path}")
        print(f"   크기: {cropped.width}x{cropped.height}")
        
        return True
    
    def run(self):
        """실행"""
        print("="*60)
        print("UI 템플릿 이미지 자동 생성 도구")
        print("="*60)
        
        # 안내 표시
        if not self.show_instructions():
            print("사용자가 취소했습니다.")
            return
        
        # 카운트다운
        self.countdown(5)
        
        # 전체 화면 캡처 (참고용)
        fullscreen_path, screenshot = self.capture_fullscreen()
        
        # 템플릿 생성
        templates = [
            {
                'name': 'input_field',
                'instruction': '주민등록번호 입력 필드 중앙에 마우스를 위치시키세요.',
                'width': 250,
                'height': 40
            },
            {
                'name': 'search_button',
                'instruction': '"조회" 버튼 중앙에 마우스를 위치시키세요.',
                'width': 100,
                'height': 40
            },
            {
                'name': 'checkbox',
                'instruction': '체크박스 하나를 선택하세요 (☑ 부분).',
                'width': 30,
                'height': 30
            }
        ]
        
        success_count = 0
        
        for template in templates:
            if self.create_template(
                template['name'],
                template['instruction'],
                template['width'],
                template['height']
            ):
                success_count += 1
        
        # 완료 메시지
        print("\n" + "="*60)
        print(f"완료! ({success_count}/{len(templates)}개 생성)")
        print("="*60)
        print(f"저장 위치: {self.templates_dir}/")
        print("")
        
        # 생성된 파일 목록
        if success_count > 0:
            print("생성된 템플릿:")
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.templates_dir, filename)
                    img = Image.open(filepath)
                    print(f"{filename} ({img.width}x{img.height})")
        
        # 최종 안내
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showinfo(
            "완료",
            f"템플릿 이미지 생성 완료!\n\n"
            f"생성된 파일: {success_count}개\n"
            f"저장 위치: {self.templates_dir}/\n\n"
            f"이제 메인 프로그램을 실행할 수 있습니다!"
        )
        
        root.destroy()


def main():
    """메인 함수"""
    creator = TemplateCreator()
    creator.run()


if __name__ == "__main__":
    main()

