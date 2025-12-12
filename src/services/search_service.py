"""
MARK:
검색 자동화 서비스
행복e음 시스템에서 주민등록번호 검색 자동화
"""

import time
import pyautogui
import os
from ..core.automation import GUIAutomation
from ..core.screen_capture import ScreenCapture
from ..core.image_matcher import ImageMatcher
from ..core.dialog_detector import DialogDetector


class SearchAutomationService:
    """검색 자동화 서비스"""
 
    def __init__(self, template_dir="data/templates", target_window=None):

        """
        Args:
            template_dir: UI 템플릿 이미지 디렉토리
            target_window: 타겟 윈도우 이름 (None이면 전체 화면)
            use_dialog_detector: 대화상자 검출 기능 사용 여부
        """
      
        # UI 요소 위치 캐시
        self.ui_cache = {}

    def find_ui_element(self, element_name, screenshot_path=None, use_dialog_roi=True):
        """
        UI 요소 찾기 (OpenCV 템플릿 매칭)

        Args:
            element_name: 요소 이름 ('input_field', 'search_button', etc.)
            screenshot_path: 스크린샷 경로 (None이면 새로 캡처)
            use_dialog_roi: 대화상자 ROI 내부에서만 검색할지 여부

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

        # 대화상자 검출 기능 사용
        if self.dialog_detector and use_dialog_roi:
            # 대화상자 경계가 캐시되어 있지 않으면 검출
            if self.dialog_boundary is None:
                print("\n[대화상자 ROI 기반 검색 모드]")
                self.dialog_boundary = self.dialog_detector.detect_dialog_boundary(screenshot_path)

            # 대화상자 내부에서 UI 요소 검색
            if self.dialog_boundary:
                ui_elements = self.dialog_detector.find_input_fields_in_dialog(
                    screenshot_path,
                    self.dialog_boundary,
                    self.template_dir
                )

                if element_name in ui_elements:
                    result = ui_elements[element_name]
                    normalized, _ = self._normalize_coordinates(result, screenshot_path)

                    # 캐시 저장
                    self.ui_cache[element_name] = normalized
                    return normalized

        # 전체 화면 검색 (fallback)
        print(f"\n[전체 화면 검색 모드]")
        print(f"Searching for '{element_name}' using template matching...")

        # 템플릿 경로
        template_path = os.path.join(self.template_dir, f"{element_name}.png")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")

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
            input_field = self.find_ui_element('input_field')
            
            self.automation.click(
                input_field['center_x'],
                input_field['center_y']
            )
            time.sleep(0.1)

            pyautogui.hotkey('ctrl','a')
            pyautogui.press('delete')
            time.sleep(0.1)

            # 주민등록번호 입력 (타이핑 방식)
            pyautogui.write(resident_number, interval=0.01)
            time.sleep(0.1)

            # 검색 버튼 찾기
            search_button = self.find_ui_element('search_button')
            
            # 검색 버튼 클릭
            self.automation.click(
                search_button['center_x'],
                search_button['center_y']
            )
            
            time.sleep(0.1)

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
        self.dialog_boundary = None

    def get_dialog_boundary(self):
        """
        현재 대화상자 경계 정보 반환

        Returns:
            dict or None: 대화상자 경계 좌표
        """
        return self.dialog_boundary

    def print_all_coordinates(self):
        """
        검출된 모든 좌표 정보 출력
        """
        print(f"\n{'='*60}")
        print("[좌표 정보 출력]")
        print(f"{'='*60}\n")

        if self.dialog_boundary:
            print(" 대화상자 경계:")
            print(f"  - 왼쪽 상단: ({self.dialog_boundary['x']}, {self.dialog_boundary['y']})")
            print(f"  - 오른쪽 하단: ({self.dialog_boundary['right']}, {self.dialog_boundary['bottom']})")
            print(f"  - 중심: ({self.dialog_boundary['center_x']}, {self.dialog_boundary['center_y']})")
            print(f"  - 크기: {self.dialog_boundary['width']} x {self.dialog_boundary['height']}\n")

        if self.ui_cache:
            print(" UI 요소 좌표:")
            for element_name, coords in self.ui_cache.items():
                print(f"\n  [{element_name}]")
                print(f"    - 왼쪽 상단: ({coords['x']}, {coords['y']})")
                print(f"    - 중심: ({coords['center_x']}, {coords['center_y']})")
                print(f"    - 크기: {coords['width']} x {coords['height']}")
                if 'confidence' in coords:
                    print(f"    - 신뢰도: {coords['confidence']:.2f}")

        if not self.dialog_boundary and not self.ui_cache:
            print("⚠ 검출된 좌표 정보가 없습니다.")

        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # 테스트
    service = SearchAutomationService()
    print("Search Automation Service initialized")

