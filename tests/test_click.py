#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
클릭 테스트 - 마우스가 실제로 어디로 가는지 확인
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.automation import GUIAutomation
import time

def test_click():
    """클릭 테스트"""
    
    print("=" * 60)
    print("클릭 테스트")
    print("=" * 60)
    
    automation = GUIAutomation(delay=1.0)
    
    # 현재 마우스 위치
    import pyautogui
    current_pos = pyautogui.position()
    print(f"\n현재 마우스 위치: {current_pos}")
    
    # 화면 크기
    screen_size = pyautogui.size()
    print(f"화면 크기: {screen_size}")
    
    print("\n" + "=" * 60)
    print("테스트 1: 마우스를 Mock 시스템 입력 필드 위로 이동")
    print("=" * 60)
    print("\n지금 Mock 시스템 창을 보세요!")
    print("5초 후 마우스가 (2208, 373)으로 이동합니다...")
    
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("\n마우스 이동!")
    automation.move_to(2208, 373)
    
    print("\n마우스가 Mock 시스템 입력 필드 위에 있나요?")
    print("   (Y/N): ", end='')
    answer1 = input().strip().lower()
    
    if answer1 != 'y':
        print("\n좌표가 잘못되었습니다!")
        print("\n해결 방법:")
        print("1. Mock 시스템 창을 주 모니터로 이동")
        print("2. 템플릿 이미지를 다시 캡처")
        print("3. 또는 수동으로 마우스를 입력 필드 위에 놓고 좌표 확인")
        
        print("\n\n수동 좌표 확인:")
        print("지금 마우스를 Mock 시스템 입력 필드 위에 놓으세요!")
        print("5초 후 현재 마우스 위치를 출력합니다...")
        
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        correct_pos = pyautogui.position()
        print(f"\n 올바른 입력 필드 좌표: {correct_pos}")
        
        print("\n이제 조회 버튼 위에 마우스를 놓으세요!")
        print("5초 후 좌표를 출력합니다...")
        
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        button_pos = pyautogui.position()
        print(f" 올바른 조회 버튼 좌표: {button_pos}")
        
        print("\n" + "=" * 60)
        print("📝 올바른 좌표:")
        print("=" * 60)
        print(f"입력 필드: {correct_pos}")
        print(f"조회 버튼: {button_pos}")
        print("=" * 60)
        
    else:
        print("\n 좌표가 정확합니다!")
        
        print("\n" + "=" * 60)
        print("테스트 2: 클릭 테스트")
        print("=" * 60)
        print("3초 후 입력 필드를 클릭합니다...")
        
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        automation.click(2208, 373)
        
        print("\n입력 필드가 활성화되었나요? (커서 깜빡임)")
        print("   (Y/N): ", end='')
        answer2 = input().strip().lower()
        
        if answer2 == 'y':
            print("\n 클릭 성공!")
            
            print("\n테스트 3: 텍스트 입력")
            print("3초 후 주민등록번호를 입력합니다...")
            time.sleep(3)
            
            automation.paste_text("900101-1234567")
            
            print("\n주민등록번호가 입력되었나요?")
            print("   (Y/N): ", end='')
            answer3 = input().strip().lower()
            
            if answer3 == 'y':
                print("\n모든 테스트 성공!")
            else:
                print("\n텍스트 입력 실패")
        else:
            print("\n 클릭 실패")

if __name__ == "__main__":
    test_click()

