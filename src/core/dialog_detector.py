"""
MARK: 팝업 대화상자 경계 검출 모듈
"""

import cv2
import numpy as np
from PIL import Image


class DialogDetector:
    """팝업 대화상자 경계 검출기"""

    def __init__(self, min_brightness_diff=30, debug=False):
        """
        초기화

        Args:
            min_brightness_diff: 대화상자와 배경의 최소 밝기 차이 (0-255)
            debug: 디버그 이미지 저장 여부
        """
        self.min_brightness_diff = min_brightness_diff
        self.debug = debug

    def detect_dialog_boundary(self, screenshot_path, output_debug_path=None):
        """
        명암 차이를 이용한 대화상자 경계선 검출

        Args:
            screenshot_path: 스크린샷 이미지 경로
            output_debug_path: 디버그 이미지 저장 경로 (None이면 자동 생성)

        Returns:
            dict or None: {
                'x': 왼쪽 상단 x 좌표,
                'y': 왼쪽 상단 y 좌표,
                'width': 너비,
                'height': 높이,
                'center_x': 중심 x 좌표,
                'center_y': 중심 y 좌표,
                'right': 오른쪽 x 좌표,
                'bottom': 아래쪽 y 좌표
            }
        """
        print("\n대화상자 경계 검출 시작")

        # 이미지 로드
        image = cv2.imread(screenshot_path)
        if image is None:
            raise ValueError(f"이미지 로드 실패: {screenshot_path}")

        print(f"이미지 크기: {image.shape[1]}x{image.shape[0]}")

        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 명암 기반 이진화 (어두운 영역 vs 밝은 영역)
        # 밝은 영역(팝업창)을 찾기 위해 Otsu 이진화 사용
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        print(f"Otsu 임계값 적용 완료")

        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        print("모폴로지 연산 완료 (노이즈 제거)")

        # 윤곽선 검출
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        print(f"검출된 윤곽선 개수: {len(contours)}")

        if len(contours) == 0:
            print("경고: 윤곽선을 찾을 수 없습니다.")
            return None

        # 사각형 영역 찾기 (팝업창 추정)
        # 단, 전체 화면 크기에 가까운 것은 제외 (배경일 가능성)
        img_area = image.shape[0] * image.shape[1]
        max_valid_area = img_area * 0.8  # 전체 화면의 80% 이상은 제외
        min_valid_area = img_area * 0.05  # 전체 화면의 5% 이상만 고려

        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_valid_area < area < max_valid_area:
                valid_contours.append(contour)

        print(f"윤곽선 개수: {len(valid_contours)} (면적 기준)")

        if len(valid_contours) == 0:
            print("경고: 유효한 대화상자를 찾을 수 없습니다.")
            return None

        # 윤곽선 선택
        largest_contour = max(valid_contours, key=cv2.contourArea)

        # 바운딩 박스 추출
        x, y, w, h = cv2.boundingRect(largest_contour)

        # 결과 좌표 계산
        result = {
            'x': x,
            'y': y,
            'width': w,
            'height': h,
            'center_x': x + w // 2,
            'center_y': y + h // 2,
            'right': x + w,
            'bottom': y + h
        }

        # 좌표 정보 출력
        # 좌표 정보 출력
        print("\n[검출된 대화상자 좌표]")
        print(f"왼쪽 상단: ({result['x']}, {result['y']})")
        print(f"오른쪽 하단: ({result['right']}, {result['bottom']})")
        print(f"중심 좌표: ({result['center_x']}, {result['center_y']})")
        print(f"크기: {result['width']} x {result['height']}")
        print(f"면적: {w * h:,} 픽셀 (전체의 {(w * h / img_area * 100):.1f}%)")

        # 디버그 이미지 저장
        if self.debug or output_debug_path:
            debug_image = image.copy()

            # 대화상자 경계 표시 (녹색)
            cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # 중심점 표시 (빨간색)
            cv2.circle(debug_image, (result['center_x'], result['center_y']), 10, (0, 0, 255), -1)

            # 좌표 텍스트 표시
            cv2.putText(debug_image, f"Dialog: ({x}, {y})", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(debug_image, f"Size: {w}x{h}", (x, y + h + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(debug_image, f"Center: ({result['center_x']}, {result['center_y']})",
                       (result['center_x'] - 100, result['center_y']),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 저장 경로 설정
            if output_debug_path is None:
                import os
                base_dir = os.path.dirname(screenshot_path)
                output_debug_path = os.path.join(base_dir, 'debug_dialog_boundary.png')

            cv2.imwrite(output_debug_path, debug_image)
            print(f"디버그 이미지 저장: {output_debug_path}")

        return result

    def find_input_fields_in_dialog(self, screenshot_path, dialog_boundary, template_dir):
        """
        대화상자 내부에서 입력 필드들 찾기

        Args:
            screenshot_path: 스크린샷 이미지 경로
            dialog_boundary: detect_dialog_boundary()의 반환값
            template_dir: 템플릿 디렉토리 경로

        Returns:
            dict: {
                'input_field': {...좌표...},
                'search_button': {...좌표...},
                ...
            }
        """
        import os
        from .image_matcher import ImageMatcher

        print("\n[대화상자 내부 UI 요소 검색]")
        print(f"검색 영역: ({dialog_boundary['x']}, {dialog_boundary['y']}) ~ "
              f"({dialog_boundary['right']}, {dialog_boundary['bottom']})")

        # 이미지 로드
        image = cv2.imread(screenshot_path)

        # 대화상자 영역만 크롭
        roi = image[
            dialog_boundary['y']:dialog_boundary['bottom'],
            dialog_boundary['x']:dialog_boundary['right']
        ]

        # 크롭된 이미지 임시 저장
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            roi_path = tmp.name
            cv2.imwrite(roi_path, roi)

        print(f"ROI 이미지 저장: {roi_path}")
        print(f"ROI 크기: {dialog_boundary['width']}x{dialog_boundary['height']}")

        # 템플릿 매칭으로 UI 요소 찾기
        matcher = ImageMatcher(confidence=0.7)
        results = {}

        # 찾을 UI 요소들
        elements = ['input_field', 'search_button', 'checkbox']

        for element_name in elements:
            template_path = os.path.join(template_dir, f"{element_name}.png")

            if not os.path.exists(template_path):
                print(f"템플릿 없음: {element_name}")
                continue

            try:
                print(f"\n{element_name} 검색 중...")
                match = matcher.find_template(roi_path, template_path)

                if match:
                    # ROI 기준 좌표를 전체 화면 좌표로 변환
                    absolute_coords = {
                        'x': dialog_boundary['x'] + match['x'],
                        'y': dialog_boundary['y'] + match['y'],
                        'width': match['width'],
                        'height': match['height'],
                        'center_x': dialog_boundary['x'] + match['center_x'],
                        'center_y': dialog_boundary['y'] + match['center_y'],
                        'confidence': match['confidence']
                    }

                    results[element_name] = absolute_coords

                    print(f"{element_name} 발견")
                    print(f"  - 전체 화면 좌표: ({absolute_coords['x']}, {absolute_coords['y']})")
                    print(f"  - 중심점: ({absolute_coords['center_x']}, {absolute_coords['center_y']})")
                    print(f"  - 크기: {absolute_coords['width']}x{absolute_coords['height']}")
                    print(f"  - 신뢰도: {absolute_coords['confidence']:.2f}")
                else:
                    print(f"{element_name} 찾지 못함")

            except Exception as e:
                print(f"{element_name} 검색 실패: {e}")

        # 임시 파일 삭제
        try:
            os.unlink(roi_path)
        except:
            pass

        print(f"\n검색 완료: {len(results)}개 요소 발견")

        return results

    def detect_with_edge_lines(self, screenshot_path, output_debug_path=None):
        """
        Hough 직선 검출을 이용한 대화상자 경계 검출 (대안 방법)

        Args:
            screenshot_path: 스크린샷 이미지 경로
            output_debug_path: 디버그 이미지 저장 경로

        Returns:
            dict or None: 경계 좌표 정보
        """
        print("\n[Hough 직선 검출 방식]")

        # 이미지 로드
        image = cv2.imread(screenshot_path)
        if image is None:
            raise ValueError(f"이미지 로드 실패: {screenshot_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Canny 엣지 검출
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        print("Canny 엣지 검출 완료")

        # Hough 직선 변환
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                minLineLength=100, maxLineGap=10)

        if lines is None:
            print("경고: 직선을 찾을 수 없습니다.")
            return None

        print(f"검출된 직선 개수: {len(lines)}")

        # 수평선과 수직선 분리
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            # 각도 계산
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

            if angle < 10 or angle > 170:  # 수평선
                horizontal_lines.append((x1, y1, x2, y2))
            elif 80 < angle < 100:  # 수직선
                vertical_lines.append((x1, y1, x2, y2))

        print(f"수평선: {len(horizontal_lines)}개, 수직선: {len(vertical_lines)}개")

        if len(horizontal_lines) < 2 or len(vertical_lines) < 2:
            print("경고: 사각형을 구성할 충분한 직선이 없습니다.")
            return None

        # 상단, 하단, 좌측, 우측 경계선 찾기
        top_y = min(min(y1, y2) for x1, y1, x2, y2 in horizontal_lines)
        bottom_y = max(max(y1, y2) for x1, y1, x2, y2 in horizontal_lines)
        left_x = min(min(x1, x2) for x1, y1, x2, y2 in vertical_lines)
        right_x = max(max(x1, x2) for x1, y1, x2, y2 in vertical_lines)

        result = {
            'x': left_x,
            'y': top_y,
            'width': right_x - left_x,
            'height': bottom_y - top_y,
            'center_x': (left_x + right_x) // 2,
            'center_y': (top_y + bottom_y) // 2,
            'right': right_x,
            'bottom': bottom_y
        }

        # 좌표 정보 출력
        print("\n[Hough 변환 검출 결과]")
        print(f"왼쪽 상단: ({result['x']}, {result['y']})")
        print(f"오른쪽 하단: ({result['right']}, {result['bottom']})")
        print(f"중심 좌표: ({result['center_x']}, {result['center_y']})")
        print(f"크기: {result['width']} x {result['height']}")

        # 디버그 이미지 저장
        if self.debug or output_debug_path:
            debug_image = image.copy()

            # 검출된 직선들 표시
            for x1, y1, x2, y2 in horizontal_lines:
                cv2.line(debug_image, (x1, y1), (x2, y2), (255, 0, 0), 1)
            for x1, y1, x2, y2 in vertical_lines:
                cv2.line(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 1)

            # 경계 사각형 표시
            cv2.rectangle(debug_image, (left_x, top_y), (right_x, bottom_y), (0, 0, 255), 3)

            if output_debug_path is None:
                import os
                base_dir = os.path.dirname(screenshot_path)
                output_debug_path = os.path.join(base_dir, 'debug_hough_lines.png')

            cv2.imwrite(output_debug_path, debug_image)
            print(f"디버그 이미지 저장: {output_debug_path}")

        return result


if __name__ == "__main__":
    # 테스트
    detector = DialogDetector(debug=True)
    print("Dialog Detector initialized")
    print(f"Min brightness difference: {detector.min_brightness_diff}")
