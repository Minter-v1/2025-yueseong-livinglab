#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
화면 캡처 모듈
"""

import pyautogui
from PIL import Image
import os
from datetime import datetime
import subprocess
import platform


class ScreenCapture:
    """화면 캡처 유틸리티"""
    
    def __init__(self, output_dir="tmp/screenshots", target_window=None):
        """
        초기화

        Args:
            output_dir: 스크린샷 저장 디렉토리
            target_window: 타겟 윈도우 이름 (예: "행복e음 Mock System")
        """
        self.output_dir = output_dir
        self.target_window = target_window
        os.makedirs(output_dir, exist_ok=True)
    
    def capture_full_screen(self, save_path=None):
        """
        전체 화면 캡처 (target_window가 설정되어 있으면 해당 윈도우만 캡처)

        Args:
            save_path: 저장 경로 (None이면 자동 생성)

        Returns:
            str: 저장된 파일 경로
        """
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"fullscreen_{timestamp}.png")

        # 타겟 윈도우가 설정되어 있으면 해당 윈도우만 캡처
        if self.target_window:
            return self._capture_window_macos(self.target_window, save_path)

        # 전체 화면 캡처
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)

        return save_path
    
    def capture_region(self, x, y, width, height, save_path=None):
        """
        특정 영역 캡처
        
        Args:
            x, y: 시작 좌표
            width, height: 영역 크기
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"region_{timestamp}.png")
        
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(save_path)
        
        return save_path
    
    def capture_window(self, window_title=None, save_path=None):
        """
        특정 윈도우 캡처 (macOS/Windows 호환)
        
        Args:
            window_title: 윈도우 제목 (None이면 활성 윈도우)
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        # 현재는 전체 화면 캡처로 대체
        # 추가 라이브러리 필요 시 구현 확장
        return self.capture_full_screen(save_path)
    
    def get_screen_size(self):
        """
        화면 크기 반환

        Returns:
            tuple: (width, height)
        """
        return pyautogui.size()

    def _capture_window_macos(self, window_name, save_path):
        """
        macOS에서 특정 윈도우 캡처 (AppleScript 사용)

        Args:
            window_name: 윈도우 이름 (부분 일치)
            save_path: 저장 경로

        Returns:
            str: 저장된 파일 경로
        """
        if platform.system() != 'Darwin':
            # macOS가 아니면 전체 화면 캡처
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return save_path

        # AppleScript로 윈도우 찾기 및 활성화
        applescript = f'''
        tell application "System Events"
            set targetApp to first application process whose name contains "{window_name}"
            set frontmost of targetApp to true
            delay 0.2

            -- 윈도우 위치와 크기 가져오기
            tell first window of targetApp
                set {{x, y}} to position
                set {{w, h}} to size
            end tell

            return {{x, y, w, h}}
        end tell
        '''

        try:
            # AppleScript 실행
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print(f"윈도우 '{window_name}' 찾기 실패, 전체 화면 캡처")
                screenshot = pyautogui.screenshot()
                screenshot.save(save_path)
                return save_path

            # 결과 파싱: "x, y, w, h"
            coords = result.stdout.strip().split(', ')
            x, y, w, h = map(int, coords)

            print(f"윈도우 '{window_name}' 찾음: ({x}, {y}, {w}x{h})")

            # 윈도우 영역만 캡처
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot.save(save_path)

            return save_path

        except Exception as e:
            print(f"윈도우 캡처 실패: {e}, 전체 화면 캡처")
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return save_path


if __name__ == "__main__":
    # 테스트
    capture = ScreenCapture()

    print("Screen Capture Test")
    print(f"Screen size: {capture.get_screen_size()}")

    # 전체 화면 캡처
    path = capture.capture_full_screen()
    print(f"Full screen captured: {path}")

