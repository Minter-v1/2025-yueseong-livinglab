#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고정 좌표로 매크로 테스트
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyautogui
import pyperclip
import cv2
import numpy as np

def test_macro_fixed():
    """고정 좌표로 매크로 테스트"""
    print("=" * 60)
    print("🧪 고정 좌표 매크로 테스트")
    print("=" * 60)
    
    print("\n⚠️  Mock 시스템을 전체화면으로 실행하세요!")
    print("\n5초 후 자동으로 시작합니다...\n")
    
    for i in range(5, 0, -1):
        print(f"⏱️  {i}초...")
        time.sleep(1)
    
    print("\n🚀 시작!\n")
    
    # 고정 좌표
    INPUT_FIELD = (179, 153)
    SEARCH_BUTTON = (353, 159)
    
    # 테스트 주민등록번호
    test_number = "900101-1234567"
    
    print(f"🔍 검색: {test_number}\n")
    
    # 1. 입력 필드 클릭
    print(f"  1️⃣  입력 필드 클릭: {INPUT_FIELD}")
    pyautogui.click(INPUT_FIELD[0], INPUT_FIELD[1])
    time.sleep(0.5)
    
    # 2. 기존 내용 삭제
    print("  2️⃣  기존 내용 삭제")
    pyautogui.hotkey('command', 'a')
    pyautogui.press('delete')
    time.sleep(0.3)
    
    # 3. 주민등록번호 입력
    print(f"  3️⃣  입력: {test_number}")
    pyperclip.copy(test_number)
    pyautogui.hotkey('command', 'v')
    time.sleep(0.5)
    
    # 4. 조회 버튼 클릭
    print(f"  4️⃣  조회 버튼 클릭: {SEARCH_BUTTON}")
    pyautogui.click(SEARCH_BUTTON[0], SEARCH_BUTTON[1])
    time.sleep(2)
    
    # 5. 결과 캡처
    print("  5️⃣  결과 캡처")
    screenshot_path = "tmp/screenshots/result_test.png"
    os.makedirs("tmp/screenshots", exist_ok=True)
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print(f"  ✓ 저장: {screenshot_path}")
    
    # 6. 체크박스 개수 세기
    print("  6️⃣  체크박스 개수 세기")
    
    checkbox_template = "data/templates/checkbox.png"
    
    if not os.path.exists(checkbox_template):
        print(f"  ❌ 체크박스 템플릿 없음: {checkbox_template}")
        print("\n  💡 체크박스 템플릿을 만들어야 합니다!")
        print("     1. Mock 시스템에서 체크된 체크박스 하나를 스크린샷")
        print("     2. data/templates/checkbox.png로 저장")
        return
    
    # 이미지 로드
    screenshot_img = cv2.imread(screenshot_path)
    template = cv2.imread(checkbox_template)
    
    if screenshot_img is None or template is None:
        print("  ❌ 이미지 로드 실패")
        return
    
    # 그레이스케일 변환
    screenshot_gray = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # 템플릿 매칭
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # 임계값
    threshold = 0.5
    locations = np.where(result >= threshold)
    
    print(f"  🔍 매칭 후보: {len(locations[0])}개 (임계값: {threshold})")
    
    # 중복 제거
    matches = []
    h, w = template_gray.shape
    
    for pt in zip(*locations[::-1]):
        # 기존 매치와 너무 가까우면 스킵
        is_duplicate = False
        for existing_pt in matches:
            distance = np.sqrt((pt[0] - existing_pt[0])**2 + (pt[1] - existing_pt[1])**2)
            if distance < 20:
                is_duplicate = True
                break
        
        if not is_duplicate:
            matches.append(pt)
    
    count = len(matches)
    
    print(f"체크박스 개수: {count}개")
    
    # 시각화
    output = screenshot_img.copy()
    for pt in matches:
        cv2.rectangle(output, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
    
    output_path = "tmp/checkbox_result.png"
    cv2.imwrite(output_path, output)
    print(f"  ✓ 시각화 저장: {output_path}")
    
    print("\n" + "=" * 60)
    print("📊 결과")
    print("=" * 60)
    print(f"주민등록번호: {test_number}")
    print(f"세대원 수: {count}명")
    print("=" * 60)
    
    print("\n💡 시각화 이미지 확인:")
    print(f"   open {output_path}")

if __name__ == "__main__":
    test_macro_fixed()

