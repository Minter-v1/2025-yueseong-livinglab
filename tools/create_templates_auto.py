#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 템플릿 이미지 자동 생성 도구 (완전 자동화)

Mock 시스템 화면을 캡처하고 자동으로 UI 요소를 추출합니다.
"""

import sys
import os
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyautogui
import cv2
import numpy as np
from PIL import Image


def create_templates_from_screenshot():
    """스크린샷에서 자동으로 템플릿 생성"""
    
    print("=" * 60)
    print("UI 템플릿 자동 생성 도구")
    print("=" * 60)
    
    # 템플릿 디렉토리 생성
    templates_dir = "data/templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    # 1. 전체 화면 캡처
    print("\nMock 시스템 창을 활성화하고 5초 기다리세요...")
    for i in range(5, 0, -1):
        print(f"  {i}초...")
        time.sleep(1)
    
    print("\n2화면 캡처 중...")
    screenshot = pyautogui.screenshot()
    screenshot_path = "tmp/fullscreen_capture.png"
    os.makedirs("tmp", exist_ok=True)
    screenshot.save(screenshot_path)
    print(f"   저장됨: {screenshot_path}")
    
    # OpenCV로 이미지 로드
    img = cv2.imread(screenshot_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. 입력 필드 템플릿 생성 (흰색 사각형 영역)
    print("\n입력 필드 템플릿 생성 중...")
    
    # 간단한 방법: 화면 중앙 상단 영역에서 흰색 사각형 찾기
    # Mock 시스템의 입력 필드는 보통 상단 중앙에 위치
    height, width = gray.shape
    
    # 입력 필드 예상 위치 (화면 상단 1/3, 중앙)
    input_field_region = img[int(height*0.1):int(height*0.3), int(width*0.3):int(width*0.7)]
    input_field_path = os.path.join(templates_dir, "input_field.png")
    
    # 작은 영역으로 저장 (100x30 정도)
    input_field_resized = cv2.resize(input_field_region, (100, 30))
    cv2.imwrite(input_field_path, input_field_resized)
    print(f"   저장됨: {input_field_path}")
    
    # 4. 조회 버튼 템플릿 생성
    print("\n조회 버튼 템플릿 생성 중...")
    
    # 버튼 예상 위치 (입력 필드 오른쪽)
    button_region = img[int(height*0.1):int(height*0.3), int(width*0.6):int(width*0.8)]
    button_path = os.path.join(templates_dir, "search_button.png")
    
    # 작은 영역으로 저장 (80x30 정도)
    button_resized = cv2.resize(button_region, (80, 30))
    cv2.imwrite(button_path, button_resized)
    print(f"   저장됨: {button_path}")
    
    # 5. 체크박스 템플릿 생성
    print("\n체크박스 템플릿 생성 중...")
    
    # 체크박스 예상 위치 (화면 중앙 왼쪽)
    checkbox_region = img[int(height*0.4):int(height*0.6), int(width*0.1):int(width*0.3)]
    checkbox_path = os.path.join(templates_dir, "checkbox.png")
    
    # 작은 영역으로 저장 (20x20 정도)
    checkbox_resized = cv2.resize(checkbox_region, (20, 20))
    cv2.imwrite(checkbox_path, checkbox_resized)
    print(f"   저장됨: {checkbox_path}")
    
    print("\n" + "=" * 60)
    print(" 템플릿 생성 완료!")
    print("=" * 60)
    print(f"\n생성된 파일:")
    print(f"  - {input_field_path}")
    print(f"  - {button_path}")
    print(f"  - {checkbox_path}")
    print("\n주의: 자동 생성된 템플릿이 정확하지 않을 수 있습니다.")
    print("   필요시 수동으로 스크린샷을 찍어 교체하세요.")


def create_templates_manual():
    """수동으로 템플릿 생성 (간단한 방법)"""
    
    print("=" * 60)
    print("UI 템플릿 수동 생성 가이드")
    print("=" * 60)
    
    templates_dir = "data/templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    print("\n다음 3개의 스크린샷을 찍어주세요:")
    print("\n1. 입력 필드 (input_field.png)")
    print("   - Mock 시스템의 주민등록번호 입력 필드만 캡처")
    print("   - 크기: 약 100x30 픽셀")
    print(f"   - 저장 위치: {os.path.join(templates_dir, 'input_field.png')}")
    
    print("\n2. 조회 버튼 (search_button.png)")
    print("   - '조회' 버튼만 캡처")
    print("   - 크기: 약 80x30 픽셀")
    print(f"   - 저장 위치: {os.path.join(templates_dir, 'search_button.png')}")
    
    print("\n3. 체크박스 (checkbox.png)")
    print("   - 체크된 체크박스 하나만 캡처")
    print("   - 크기: 약 20x20 픽셀")
    print(f"   - 저장 위치: {os.path.join(templates_dir, 'checkbox.png')}")
    
    print("\n" + "=" * 60)



if __name__ == "__main__":
    print("\n템플릿 생성 방법을 선택하세요:")
    print("1. 자동 생성 (권장하지 않음 - 정확도 낮음)")
    print("2. 수동 생성 가이드 보기 (권장)")
    
    choice = input("\n선택 (1 또는 2): ").strip()
    
    if choice == "1":
        create_templates_from_screenshot()
    elif choice == "2":
        create_templates_manual()
    else:
        print("잘못된 선택입니다.")

