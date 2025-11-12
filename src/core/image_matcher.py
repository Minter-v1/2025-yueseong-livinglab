"""
MARK:
이미지 매칭 모듈
OpenCV를 사용한 템플릿 매칭으로 UI 요소 찾기
"""

import cv2
import numpy as np
from PIL import Image


class ImageMatcher:
    """이미지 템플릿 매칭"""
    
    def __init__(self, confidence=0.8):
        """
        초기화
        
        Args:
            confidence: 매칭 신뢰도 임계값 (0.0 ~ 1.0)
        """
        self.confidence = confidence
    
    def find_template(self, screenshot_path, template_path, method=cv2.TM_CCOEFF_NORMED):
        """
        스크린샷에서 템플릿 이미지 찾기
        
        Args:
            screenshot_path: 스크린샷 이미지 경로
            template_path: 템플릿 이미지 경로
            method: OpenCV 매칭 방법
            
        Returns:
            dict or None: {
                'x': x 좌표,
                'y': y 좌표,
                'width': 너비,
                'height': 높이,
                'confidence': 신뢰도,
                'center_x': 중심 x,
                'center_y': 중심 y
            }
        """
        # 이미지 로드 (그레이스케일)
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if screenshot is None or template is None:
            raise ValueError("Failed to load images")
        
        # 템플릿 크기
        h, w = template.shape
        
        # 템플릿 매칭
        result = cv2.matchTemplate(screenshot, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 매칭 방법에 따라 최적 위치 선택
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
            confidence = 1 - min_val
        else:
            top_left = max_loc
            confidence = max_val
        
        # 신뢰도 체크
        print(f"     매칭 신뢰도: {confidence:.2f} (임계값: {self.confidence:.2f})")
        if confidence < self.confidence:
            print(f"     신뢰도가 임계값보다 낮습니다!")
            return None
        print(f"     매칭 성공!")
        
        # 결과 반환
        x, y = top_left
        center_x = x + w // 2
        center_y = y + h // 2
        
        return {
            'x': x,
            'y': y,
            'width': w,
            'height': h,
            'confidence': confidence,
            'center_x': center_x,
            'center_y': center_y
        }
    
    def find_all_templates(self, screenshot_path, template_path, threshold=None):
        """
        스크린샷에서 템플릿의 모든 매칭 위치 찾기
        
        Args:
            screenshot_path: 스크린샷 이미지 경로
            template_path: 템플릿 이미지 경로
            threshold: 신뢰도 임계값 (None이면 self.confidence 사용)
            
        Returns:
            list: 매칭 결과 리스트
        """
        if threshold is None:
            threshold = self.confidence
        
        # 이미지 로드
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if screenshot is None or template is None:
            raise ValueError("Failed to load images")
        
        # 템플릿 크기
        h, w = template.shape
        
        # 템플릿 매칭
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        
        # 임계값 이상인 위치 찾기
        locations = np.where(result >= threshold)
        
        matches = []
        for pt in zip(*locations[::-1]):
            x, y = pt
            confidence = result[y, x]
            center_x = x + w // 2
            center_y = y + h // 2
            
            matches.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'confidence': float(confidence),
                'center_x': center_x,
                'center_y': center_y
            })
        
        return matches
    
    def draw_matches(self, screenshot_path, matches, output_path):
        """
        매칭 결과를 이미지에 표시
        
        Args:
            screenshot_path: 스크린샷 이미지 경로
            matches: 매칭 결과 리스트
            output_path: 출력 이미지 경로
        """
        # 이미지 로드 (컬러)
        screenshot = cv2.imread(screenshot_path)
        
        # 매칭 위치에 사각형 그리기
        for match in matches:
            x, y = match['x'], match['y']
            w, h = match['width'], match['height']
            confidence = match['confidence']
            
            # 사각형
            cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 신뢰도 텍스트
            text = f"{confidence:.2f}"
            cv2.putText(screenshot, text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 저장
        cv2.imwrite(output_path, screenshot)
        
        return output_path


class ColorMatcher:
    """색상 기반 매칭 (체크박스 등)"""
    
    @staticmethod
    def find_by_color(image_path, lower_color, upper_color):
        """
        특정 색상 범위의 영역 찾기
        
        Args:
            image_path: 이미지 경로
            lower_color: 하한 색상 (B, G, R)
            upper_color: 상한 색상 (B, G, R)
            
        Returns:
            list: 매칭된 영역 리스트 [(x, y, w, h), ...]
        """
        # 이미지 로드
        image = cv2.imread(image_path)
        
        # 색상 범위로 마스크 생성
        mask = cv2.inRange(image, np.array(lower_color), np.array(upper_color))
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 바운딩 박스 추출
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            regions.append((x, y, w, h))
        
        return regions


if __name__ == "__main__":
    # 테스트
    matcher = ImageMatcher(confidence=0.7)
    print("Image Matcher initialized")
    print(f"Confidence threshold: {matcher.confidence}")

