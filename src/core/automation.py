# MARK: gui 제어  모듈

import pyautogui
import time
import pyperclip
import platform

# Windows DPI 스케일링 문제 해결
if platform.system() == "Windows":
    try:
        import ctypes
        # DPI awareness 설정 (Windows 8.1 이상)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            # Windows Vista/7/8용 fallback
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass  # DPI 설정 실패해도 계속 진행


class GUIAutomation:
    """GUI 자동화 유틸리티"""
    
    def __init__(self, delay=0.5):
        """
        초기화
        
        Args:
            delay: 동작 간 기본 지연 시간 (초)
        """
        self.delay = delay
        
        pyautogui.PAUSE = 0.1  # 각 동작 후 0.1초 대기
        pyautogui.FAILSAFE = True  # 마우스를 화면 모서리로 이동 시 중단
    
    def click(self, x, y, clicks=1, button='left', delay=None):
        """
        위치 클릭
        
        Args:
            x, y: 클릭 좌표
            clicks: 클릭 횟수
            button: 'left', 'right', 'middle'
            delay: 클릭 후 대기 시간
        """
        pyautogui.click(x, y, clicks=clicks, button=button)
        time.sleep(delay if delay is not None else self.delay)
    
    def double_click(self, x, y, delay=None):
        self.click(x, y, clicks=2, delay=delay)
    
    def right_click(self, x, y, delay=None):
        self.click(x, y, button='right', delay=delay)
    
    def move_to(self, x, y, duration=0.5):
        """
        마우스 이동
        
        Args:
            x, y: 목표 좌표
            duration: 이동 시간 (초)
        """
        pyautogui.moveTo(x, y, duration=duration)
    
    def type_text(self, text, interval=0.05, delay=None):
        """
        텍스트 입력 (타이핑)
        
        Args:
            text: 입력할 텍스트
            interval: 글자 간 간격
            delay: 입력 후 대기 시간
        """
        pyautogui.write(text, interval=interval)
        time.sleep(delay if delay is not None else self.delay)
    
    def paste_text(self, text, delay=None):
        """
        텍스트 붙여넣기
        
        Args:
            text: 붙여넣을 텍스트
            delay: 붙여넣기 후 대기 시간
        """
        # 클립보드에 복사
        pyperclip.copy(text)
        
        # Cmd+V (macOS) 또는 Ctrl+V (Windows)
        import platform
        if platform.system() == 'Darwin':  # macOS
            pyautogui.hotkey('command', 'v')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'v')
        
        time.sleep(delay if delay is not None else self.delay)
    
    def press_key(self, key, delay=None):
        """
        키 입력
        
        Args:
            key: 키 이름 ('enter', 'tab', 'esc', etc.)
            delay: 입력 후 대기 시간
        """
        pyautogui.press(key)
        time.sleep(delay if delay is not None else self.delay)
    
    def hotkey(self, *keys, delay=None):
        """
        단축키 입력
        
        Args:
            *keys: 키 조합 (예: 'ctrl', 'c')
            delay: 입력 후 대기 시간
        """
        pyautogui.hotkey(*keys)
        time.sleep(delay if delay is not None else self.delay)
    
    def scroll(self, clicks, x=None, y=None):
        """
        스크롤
        
        Args:
            clicks: 스크롤 양 (양수: 위, 음수: 아래)
            x, y: 스크롤 위치 (None이면 현재 위치)
        """
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)
    
    def wait(self, seconds):
        """대기"""
        time.sleep(seconds)
    
    def get_mouse_position(self):
        """
        현재 마우스 위치 반환
        
        Returns:
            tuple: (x, y)
        """
        return pyautogui.position()
    
    def screenshot_region(self, x, y, width, height):
        """
        영역 스크린샷
        
        Args:
            x, y: 시작 좌표
            width, height: 영역 크기
            
        Returns:
            PIL.Image: 스크린샷 이미지
        """
        return pyautogui.screenshot(region=(x, y, width, height))


class SafeAutomation(GUIAutomation):
    """안전 모드 자동화 (확인 메시지 포함)"""
    
    def __init__(self, delay=0.5, confirm=True):
        """
        Args:
            delay: 동작 간 기본 지연 시간
            confirm: 중요 동작 전 확인 여부
        """
        super().__init__(delay)
        self.confirm = confirm
    
    def click(self, x, y, clicks=1, button='left', delay=None):
        """확인 후 클릭"""
        super().click(x, y, clicks, button, delay)
    
    def paste_text(self, text, delay=None):
        """확인 후 텍스트 붙여넣기"""
        super().paste_text(text, delay)


if __name__ == "__main__":
    # 테스트
    auto = GUIAutomation()
    
    print("GUI Automation Test")
    print(f"Current mouse position: {auto.get_mouse_position()}")
    print(f"Screen size: {pyautogui.size()}")
    
    # 5초 후 현재 마우스 위치 출력
    print("Move your mouse to the target position...")
    time.sleep(5)
    pos = auto.get_mouse_position()
    print(f"Target position: {pos}")

