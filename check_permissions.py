#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS 접근성 권한 확인 스크립트
"""

import sys
import platform

def check_macos_permissions():
    """macOS 접근성 권한 확인"""
    
    if platform.system() != 'Darwin':
        print("이 스크립트는 macOS에서만 실행할 수 있습니다.")
        return
    
    print("=" * 60)
    print("macOS 접근성 권한 확인")
    print("=" * 60)
    print()
    
    # 1. 접근성 권한 확인
    print("1. 접근성 권한 확인 중...")
    try:
        import subprocess
        
        # AppleScript로 접근성 권한 확인
        script = '''
        tell application "System Events"
            try
                keystroke "test"
                return "권한 있음"
            on error
                return "권한 없음"
            end try
        end tell
        '''
        
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if "권한 있음" in result.stdout:
            print("   ✓ 접근성 권한이 있습니다.")
        else:
            print("   ✗ 접근성 권한이 없습니다!")
            print()
            print("   해결 방법:")
            print("   1. 시스템 설정 > 개인 정보 보호 및 보안 > 접근성")
            print("   2. 터미널(Terminal) 또는 Python 앱에 체크 표시")
            print("   3. 또는 Cursor/VS Code에 체크 표시 (사용 중인 IDE)")
            print()
    except Exception as e:
        print(f"   권한 확인 실패: {e}")
    
    # 2. pyautogui 테스트
    print()
    print("2. pyautogui 키보드 입력 테스트...")
    try:
        import pyautogui
        import time
        
        print("   3초 후 'test'를 입력합니다...")
        print("   (입력 필드에 포커스를 맞춰주세요)")
        time.sleep(3)
        
        pyautogui.write("test", interval=0.1)
        print("   ✓ 입력 시도 완료")
        print()
        print("   화면에 'test'가 입력되었나요?")
        print("   - 예: 권한이 정상적으로 설정되었습니다.")
        print("   - 아니오: 접근성 권한을 확인하세요.")
        
    except Exception as e:
        print(f"   ✗ 테스트 실패: {e}")
    
    print()
    print("=" * 60)
    print("추가 정보:")
    print("=" * 60)
    print("macOS에서 자동화를 사용하려면:")
    print("1. 시스템 설정 > 개인 정보 보호 및 보안 > 접근성")
    print("2. 사용 중인 앱(터미널/Python/Cursor 등)에 체크 표시")
    print("3. 권한 변경 후 앱을 재시작하세요")
    print("=" * 60)

if __name__ == "__main__":
    check_macos_permissions()
