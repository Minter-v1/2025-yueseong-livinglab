"""
MARK:
검색 자동화 서비스
행복e음 시스템에서 주민등록번호 검색 자동화
"""

import time
import pyautogui
import os
import platform
from ..core.automation import GUIAutomation
from ..core.screen_capture import ScreenCapture
from ..core.image_matcher import ImageMatcher


def get_template_dir():
    """
    OS를 자동으로 탐지하여 적절한 템플릿 디렉토리 경로 반환
    
    Returns:
        str: OS에 맞는 템플릿 디렉토리 경로
    """
    system = platform.system()
    
    if system == "Windows":
        return "data/templates/templates_window"
    elif system == "Darwin":  # macOS
        return "data/templates/templates_mac"
    else:
        # Linux나 기타 OS의 경우 기본값 사용
        print(f"경고: 알 수 없는 OS ({system}), 기본 템플릿 디렉토리를 사용합니다.")
        return "data/templates/templates_window"


class SearchAutomationService:
    """검색 자동화 서비스"""
    
    def __init__(self, template_dir=None, target_window=None):
        """
        Args:
            template_dir: UI 템플릿 이미지 디렉토리 (None이면 OS 자동 탐지)
            target_window: 타겟 윈도우 이름 (None이면 전체 화면)
        """
        # template_dir이 지정되지 않으면 OS에 따라 자동 설정
        if template_dir is None:
            template_dir = get_template_dir()
        
        self.automation = GUIAutomation(delay=0.5)
        self.capture = ScreenCapture(target_window=target_window)
        self.matcher = ImageMatcher(confidence=0.7)  # 템플릿 매칭 신뢰도
        self.template_dir = template_dir
        
        # 사용 중인 템플릿 디렉토리 출력
        print(f"템플릿 디렉토리: {self.template_dir} (OS: {platform.system()})")

        # UI 요소 위치 캐시
        self.ui_cache = {}
    
    def find_ui_element(self, element_name, screenshot_path=None):
        """
        UI 요소 찾기 (OpenCV 템플릿 매칭)

        Args:
            element_name: 요소 이름 ('input_field', 'search_button', etc.)
            screenshot_path: 스크린샷 경로 (None이면 새로 캡처)

        Returns:
            dict: {'x', 'y', 'width', 'height', 'center_x', 'center_y'}
        """
        # 캐시 확인
        if element_name in self.ui_cache:
            print(f"Using cached position for '{element_name}'")
            return self.ui_cache[element_name]

        # 스크린샷 캡처
        if screenshot_path is None:
            print(f"Capturing screen for '{element_name}'...")
            screenshot_path = self.capture.capture_full_screen()
            print(f"Screenshot saved: {screenshot_path}")

        # 템플릿 경로
        template_path = os.path.join(self.template_dir, f"{element_name}.png")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")

        print(f"Searching for '{element_name}' using template matching...")

        # OpenCV 템플릿 매칭
        result = self.matcher.find_template(screenshot_path, template_path)

        if result is None:
            raise ValueError(f"UI element '{element_name}' not found")

        print(f"Found '{element_name}' at ({result['center_x']}, {result['center_y']})")

        # 캐시 저장
        self.ui_cache[element_name] = result

        return result
    
    def search_resident(self, resident_number):
        """
        주민등록번호 검색

        Args:
            resident_number: 주민등록번호

        Returns:
            dict: {
                'resident_number': 주민등록번호,
                'household_count': 세대원 수,
                'status': 'success' or 'error',
                'message': 메시지
            }
        """
        try:            
            print(f"\n[검색 시작] 주민등록번호: {resident_number}")
            
            # 1. 입력 필드 찾기
            input_field = self.find_ui_element('input_field')
            print(f"[1단계] 입력 필드 찾기 완료: ({input_field['center_x']}, {input_field['center_y']})")
            
            # 2. 입력 필드 클릭 (더블 클릭으로 선택 영역 확보)
            print("[2단계] 입력 필드 더블 클릭...")
            self.automation.double_click(
                input_field['center_x'],
                input_field['center_y']
            )
            time.sleep(0.5)  # 포커스 대기 시간 증가

            # 3. 기존 내용 삭제
            print("[3단계] 기존 내용 삭제...")
            import platform
            if platform.system() == 'Darwin':  # macOS
                pyautogui.hotkey('command', 'a')
            else:  # Windows/Linux
                pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)

            pyautogui.press('delete')
            time.sleep(0.3)

            # 4. 주민등록번호 입력
            print(f"[4단계] 주민등록번호 입력: {resident_number}")
            self.automation.paste_text(resident_number, delay=0.3)
            time.sleep(0.5)  # 입력 완료 대기
            print("[4단계] 주민등록번호 입력 완료")

            # 5. 검색 버튼 찾기
            print("[5단계] 검색 버튼 찾기...")
            search_button = self.find_ui_element('search_button')
            print(f"[5단계] 검색 버튼 찾기 완료: ({search_button['center_x']}, {search_button['center_y']})")
            
            # 6. 검색 버튼 클릭
            print("[6단계] 검색 버튼 클릭...")
            self.automation.click(
                search_button['center_x'],
                search_button['center_y']
            )
            print("[6단계] 검색 버튼 클릭 완료")
            
            # 7. 결과 로딩 대기
            print("[7단계] 검색 결과 대기 중...")
            time.sleep(2.0)  # 결과 로딩 대기 (2초)

            # 결과 영역 캡처
            result_screenshot = self.capture.capture_full_screen()

            # 세대원 수 추출 (이미지 매칭 방식)
            print("Counting checkboxes with image matching...")
            household_count = self._count_checkboxes_by_image(result_screenshot)
            print(f"   Found {household_count} household members (Image Matching)")
            
            return {
                'resident_number': resident_number,
                'household_count': household_count,
                'status': 'success',
                'message': f'Found {household_count} members'
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return {
                'resident_number': resident_number,
                'household_count': 0,
                'status': 'error',
                'message': str(e)
            }
    
    def _count_checkboxes_by_image(self, screenshot_path):
        """
        이미지 매칭으로 체크박스 개수 세기

        Args:
            screenshot_path: 스크린샷 파일 경로

        Returns:
            int: 체크박스 개수
        """
        try:
            # 체크박스 템플릿 경로
            checkbox_template = os.path.join(self.template_dir, 'checkbox.png')

            if not os.path.exists(checkbox_template):
                print(f"체크박스 템플릿이 없습니다: {checkbox_template}")
                print(f"템플릿 생성 도구를 실행하세요: ./venv/bin/python tools/create_templates.py")
                return 0

            # 템플릿 매칭으로 모든 체크박스 찾기
            import cv2
            import numpy as np

            # 이미지 로드
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(checkbox_template)

            if screenshot is None or template is None:
                print(f"이미지 로드 실패")
                return 0

            # 그레이스케일 변환
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # 템플릿 매칭
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

            # 임계값 이상인 위치 찾기
            threshold = 0.7  # 70% 이상 일치
            locations = np.where(result >= threshold)

            print(f"체크박스 매칭 시도 (임계값: {threshold})")
            print(f"매칭 후보: {len(locations[0])}개")

            # 중복 제거 (가까운 위치는 하나로 간주)
            matches = []
            for pt in zip(*locations[::-1]):
                # 기존 매치와 너무 가까우면 스킵
                is_duplicate = False
                for existing_pt in matches:
                    distance = np.sqrt((pt[0] - existing_pt[0])**2 + (pt[1] - existing_pt[1])**2)
                    if distance < 20:  # 20픽셀 이내면 중복
                        is_duplicate = True
                        break

                if not is_duplicate:
                    matches.append(pt)

            count = len(matches)
            print(f"매칭된 체크박스: {count}개 (임계값: {threshold})")

            return count

        except Exception as e:
            print(f"체크박스 카운팅 오류: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def batch_search(self, resident_numbers, callback=None):
        """
        일괄 검색
        
        Args:
            resident_numbers: 주민등록번호 리스트
            callback: 진행 상황 콜백 함수 (index, total, result)
            
        Returns:
            list: 검색 결과 리스트
        """
        results = []
        total = len(resident_numbers)
        
        for i, resident_number in enumerate(resident_numbers, 1):
            print(f"\n{'='*60}")
            print(f"Progress: {i}/{total}")
            print(f"{'='*60}")
            
            result = self.search_resident(resident_number)
            results.append(result)
            
            if callback:
                callback(i, total, result)
            
            # 다음 검색 전 대기
            if i < total:
                time.sleep(0.2)
        
        return results
    
    def clear_cache(self):
        """UI 위치 캐시 초기화"""
        self.ui_cache.clear()


if __name__ == "__main__":
    # 테스트
    service = SearchAutomationService()
    print("Search Automation Service initialized")

