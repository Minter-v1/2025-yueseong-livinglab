"""
MARK:
이미지 매칭 모듈
OpenCV를 사용한 템플릿 매칭으로 UI 요소 찾기
"""

import cv2
import numpy as np
import math


class ImageMatcher:
    """이미지 템플릿 매칭"""

    SUPPORTED_MODES = ('gray', 'color', 'canny', 'sat')
    MASK_SUPPORTED_METHODS = (cv2.TM_SQDIFF, cv2.TM_CCORR, cv2.TM_CCORR_NORMED)
    SUPPORTED_METHODS = (
        cv2.TM_CCOEFF,
        cv2.TM_CCOEFF_NORMED,
        cv2.TM_CCORR,
        cv2.TM_CCORR_NORMED,
        cv2.TM_SQDIFF,
        cv2.TM_SQDIFF_NORMED,
    )

    def __init__(
        self,
        confidence=0.8,
        search_scales=None,
        match_modes=None,
        canny_thresholds=(50, 150),
        method=(cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED),
        pre_blur=(3, 3),
    ):
        """
        초기화

        Args:
            confidence: 매칭 신뢰도 임계값 (0.0 ~ 1.0)
            search_scales: 템플릿을 확대/축소하며 탐색할 배율 목록 (None이면 [1.0])
            match_modes: 사용할 매칭 모드 목록 ('gray', 'color', 'canny', 'sat')
            canny_thresholds: canny 모드 사용 시 하한/상한 임계값
            method: OpenCV 매칭 방법 또는 후보 튜플
            pre_blur: 매칭 전 적용할 가우시안 블러 커널 (None이면 미사용)
        """
        self.confidence = confidence
        # 배율은 1.0이 항상 포함되도록 보정
        if search_scales is None:
            search_scales = [1.0]
        elif 1.0 not in search_scales:
            search_scales = list(search_scales) + [1.0]
        # 음수나 0 배율은 무효 처리
        self.search_scales = [scale for scale in search_scales if scale > 0]
        if match_modes is None:
            match_modes = ('gray', 'canny', 'sat')
        # 중복 제거 및 지원 모드만 유지
        filtered_modes = []
        for mode in match_modes:
            if mode in self.SUPPORTED_MODES and mode not in filtered_modes:
                filtered_modes.append(mode)
        self.match_modes = tuple(filtered_modes) if filtered_modes else ('gray',)
        self.canny_thresholds = canny_thresholds
        if method is None:
            methods = [cv2.TM_CCORR_NORMED]
        elif isinstance(method, (list, tuple, set)):
            methods = [m for m in method if m in self.SUPPORTED_METHODS]
        else:
            methods = [method] if method in self.SUPPORTED_METHODS else [cv2.TM_CCORR_NORMED]
        self.methods = tuple(methods) if methods else (cv2.TM_CCORR_NORMED,)
        self.pre_blur = pre_blur if pre_blur and pre_blur[0] > 1 and pre_blur[1] > 1 else None
    
    def _load_template_variants(self, template_path):
        """템플릿을 로드하여 모드별 이미지와 마스크를 반환"""
        raw = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
        if raw is None:
            raise ValueError(f"Failed to load template image: {template_path}")

        template_variants = {}
        mask_variants = {}

        if raw.ndim == 2:
            gray = raw
            color = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)
            alpha = None
        elif raw.shape[2] == 3:
            color = raw
            gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
            alpha = None
        else:
            color = raw[:, :, :3]
            gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
            alpha = raw[:, :, 3]
            _, alpha = cv2.threshold(alpha, 0, 255, cv2.THRESH_BINARY)

        template_variants['gray'] = gray
        template_variants['color'] = color
        hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
        template_variants['sat'] = hsv[:, :, 1]

        lower, upper = self.canny_thresholds
        canny = cv2.Canny(gray, lower, upper)
        if alpha is not None:
            canny = cv2.bitwise_and(canny, alpha)
            mask_variants['canny'] = alpha
        template_variants['canny'] = canny

        # 엣지 기반 마스크 생성 (내부 콘텐츠 차이 완화)
        edge_mask = cv2.Canny(gray, max(10, lower // 2), upper)
        if alpha is not None:
            edge_mask = cv2.bitwise_and(edge_mask, alpha)
        # 가장자리만 남기기 위해 굵기 보정
        if np.count_nonzero(edge_mask) > 0:
            kernel = np.ones((3, 3), np.uint8)
            edge_mask = cv2.dilate(edge_mask, kernel, iterations=1)
            mask_variants['gray'] = edge_mask
            mask_variants['color'] = edge_mask
            mask_variants['sat'] = edge_mask
            if 'canny' not in mask_variants:
                mask_variants['canny'] = edge_mask
        elif alpha is not None:
            mask_variants['gray'] = alpha
            mask_variants['color'] = alpha
            mask_variants['sat'] = alpha

        return template_variants, mask_variants

    def find_template(self, screenshot_path, template_path, method=None, scale_search=None):
        """
        스크린샷에서 템플릿 이미지 찾기
        
        Args:
            screenshot_path: 스크린샷 이미지 경로
            template_path: 템플릿 이미지 경로
            method: OpenCV 매칭 방법
            scale_search: 탐색 시 사용할 배율 목록 (None이면 self.search_scales 사용)
            
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
        if method is None:
            methods = self.methods
        elif isinstance(method, (list, tuple, set)):
            methods = tuple(m for m in method if m in self.SUPPORTED_METHODS) or self.methods
        else:
            methods = (method,) if method in self.SUPPORTED_METHODS else self.methods

        # 원본 이미지 로드
        screenshot_gray = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        screenshot_color = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)

        if screenshot_gray is None or screenshot_color is None:
            raise ValueError("Failed to load images")

        template_variants, mask_variants = self._load_template_variants(template_path)

        screenshot_variants = {
            'gray': screenshot_gray,
            'color': screenshot_color,
        }

        if 'canny' in self.match_modes:
            lower, upper = self.canny_thresholds
            screenshot_canny = cv2.Canny(screenshot_gray, lower, upper)
            screenshot_variants['canny'] = screenshot_canny
        if 'sat' in self.match_modes:
            hsv = cv2.cvtColor(screenshot_color, cv2.COLOR_BGR2HSV)
            screenshot_variants['sat'] = hsv[:, :, 1]

        scales = scale_search if scale_search is not None else self.search_scales
        best_match = None

        for scale in scales:
            for mode in self.match_modes:
                template_img = template_variants.get(mode)
                screenshot_img = screenshot_variants.get(mode)
                template_mask = mask_variants.get(mode)

                if template_img is None or screenshot_img is None:
                    continue

                if self.pre_blur and mode not in ('canny',):
                    template_current = cv2.GaussianBlur(template_img, self.pre_blur, 0)
                    screenshot_current = cv2.GaussianBlur(screenshot_img, self.pre_blur, 0)
                else:
                    template_current = template_img
                    screenshot_current = screenshot_img

                # 템플릿 축소/확대
                if scale == 1.0:
                    resized_template = template_current
                    resized_mask = template_mask
                    if resized_mask is not None:
                        if resized_mask.dtype != np.uint8:
                            resized_mask = resized_mask.astype(np.uint8, copy=False)
                        if np.count_nonzero(resized_mask) < 5:
                            resized_mask = None
                else:
                    resized_size = (int(template_current.shape[1] * scale), int(template_current.shape[0] * scale))
                    if resized_size[0] < 5 or resized_size[1] < 5:
                        continue
                    interpolation = (
                        cv2.INTER_NEAREST if mode == 'canny'
                        else cv2.INTER_AREA if scale < 1.0
                        else cv2.INTER_CUBIC
                    )
                    resized_template = cv2.resize(template_current, resized_size, interpolation=interpolation)
                    resized_mask = None
                    if template_mask is not None:
                        resized_mask = cv2.resize(
                            template_mask,
                            resized_size,
                            interpolation=cv2.INTER_NEAREST
                        )
                        if resized_mask.dtype != np.uint8:
                            resized_mask = resized_mask.astype(np.uint8, copy=False)
                        if np.count_nonzero(resized_mask) < 5:
                            resized_mask = None

                if (
                    resized_template.shape[0] > screenshot_current.shape[0]
                    or resized_template.shape[1] > screenshot_current.shape[1]
                ):
                    continue

                for method_candidate in methods:
                    mask_arg = None
                    if resized_mask is not None and method_candidate in self.MASK_SUPPORTED_METHODS:
                        mask_arg = resized_mask

                    if mask_arg is not None:
                        result = cv2.matchTemplate(
                            screenshot_current,
                            resized_template,
                            method_candidate,
                            mask=mask_arg
                        )
                    else:
                        result = cv2.matchTemplate(
                            screenshot_current,
                            resized_template,
                            method_candidate
                        )

                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                    if method_candidate in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
                        top_left = min_loc
                        confidence = 1 - min_val
                    else:
                        top_left = max_loc
                        confidence = max_val

                    if not np.isfinite(confidence):
                        print("     신뢰도(inf/nan) 결과 - 마스크를 제거하고 재시도합니다.")
                        if mask_arg is not None:
                            # 마스크를 제거하고 한 번만 다시 시도
                            result = cv2.matchTemplate(
                                screenshot_current,
                                resized_template,
                                method_candidate
                            )
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            if method_candidate in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
                                top_left = min_loc
                                confidence = 1 - min_val
                            else:
                                top_left = max_loc
                                confidence = max_val
                        if not np.isfinite(confidence):
                            continue

                    print(
                        f"     method={method_candidate} mode={mode:<5} "
                        f"scale={scale:.2f}, confidence={confidence:.2f} "
                        f"(임계값: {self.confidence:.2f})"
                    )

                    if confidence < self.confidence:
                        continue

                    if best_match is None or confidence > best_match['confidence']:
                        x, y = top_left
                        h, w = resized_template.shape[:2]
                        best_match = {
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'confidence': confidence,
                            'center_x': x + w // 2,
                            'center_y': y + h // 2,
                            'scale': scale,
                            'mode': mode,
                            'method': method_candidate,
                        }

        color_candidate = None
        template_color = template_variants.get('color')
        screenshot_color = screenshot_variants.get('color')
        if template_color is not None and screenshot_color is not None:
            color_candidate = self._find_color_candidate(
                screenshot_color,
                template_color
            )
            if color_candidate and (best_match is None or color_candidate['confidence'] > best_match['confidence']):
                print("     색상 힌트 기반 매칭 결과를 사용합니다.")
                best_match = color_candidate

        if best_match:
            print(
                f"     매칭 성공! (method={best_match['method']}, "
                f"mode={best_match['mode']}, scale={best_match['scale']:.2f})"
            )
            best_match.pop('scale', None)
            best_match.pop('mode', None)
            best_match.pop('method', None)
            return best_match

        print("     신뢰도가 임계값보다 낮습니다!")
        return None
    
    def _find_color_candidate(self, screenshot_color, template_color):
        """색상 힌트를 사용해 템플릿과 유사한 영역을 찾습니다."""
        template_h, template_w = template_color.shape[:2]
        template_area = template_h * template_w

        template_hsv = cv2.cvtColor(template_color, cv2.COLOR_BGR2HSV)
        sat_mask = template_hsv[:, :, 1] > 40
        if np.count_nonzero(sat_mask) < 20:
            return None

        selected = template_hsv[sat_mask]
        h_vals = selected[:, 0].astype(np.float32)
        s_vals = selected[:, 1].astype(np.float32)
        v_vals = selected[:, 2].astype(np.float32)

        h_rad = h_vals * (np.pi / 90.0)  # convert to radians (0-2pi)
        mean_sin = float(np.sin(h_rad).mean())
        mean_cos = float(np.cos(h_rad).mean())
        if math.isclose(mean_sin, 0.0, abs_tol=1e-3) and math.isclose(mean_cos, 0.0, abs_tol=1e-3):
            return None
        mean_angle = math.degrees(math.atan2(mean_sin, mean_cos))
        if mean_angle < 0:
            mean_angle += 360
        h_mean = mean_angle / 2.0  # convert back to OpenCV hue range (0-180)
        h_std = float(np.std(h_vals)) if h_vals.size > 1 else 0.0
        h_tol = max(6.0, h_std * 2.0)

        s_mean = float(np.mean(s_vals))
        v_mean = float(np.mean(v_vals))
        s_std = float(np.std(s_vals)) if s_vals.size > 1 else 0.0
        v_std = float(np.std(v_vals)) if v_vals.size > 1 else 0.0
        s_tol = max(40.0, s_std * 2.5)
        v_tol = max(40.0, v_std * 2.5)

        def clamp(val, low, high):
            return max(low, min(high, val))

        lower_h = clamp(h_mean - h_tol, 0, 179)
        upper_h = clamp(h_mean + h_tol, 0, 179)
        sat_low = clamp(s_mean - s_tol, 0, 255)
        sat_high = clamp(s_mean + s_tol, 0, 255)
        val_low = clamp(v_mean - v_tol, 0, 255)
        val_high = clamp(v_mean + v_tol, 0, 255)

        hsv_screen = cv2.cvtColor(screenshot_color, cv2.COLOR_BGR2HSV)

        lower_vec = np.array([int(round(lower_h)), int(round(sat_low)), int(round(val_low))], dtype=np.uint8)
        upper_vec = np.array([int(round(upper_h)), int(round(sat_high)), int(round(val_high))], dtype=np.uint8)
        if lower_h <= upper_h:
            color_mask = cv2.inRange(hsv_screen, lower_vec, upper_vec)
        else:
            lower_wrap = np.array([0, lower_vec[1], lower_vec[2]], dtype=np.uint8)
            upper_wrap = np.array([int(round(upper_h)), upper_vec[1], upper_vec[2]], dtype=np.uint8)
            lower_wrap2 = np.array([int(round(lower_h)), lower_vec[1], lower_vec[2]], dtype=np.uint8)
            upper_wrap2 = np.array([179, upper_vec[1], upper_vec[2]], dtype=np.uint8)
            mask1 = cv2.inRange(hsv_screen, lower_wrap, upper_wrap)
            mask2 = cv2.inRange(hsv_screen, lower_wrap2, upper_wrap2)
            color_mask = cv2.bitwise_or(mask1, mask2)

        if np.count_nonzero(color_mask) == 0:
            return None

        kernel = np.ones((5, 5), np.uint8)
        mask_clean = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        template_ratio = template_w / template_h
        best_candidate = None
        best_score = 0.0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area < template_area * 0.5 or area > template_area * 3.5:
                continue

            ratio = w / h if h > 0 else 0
            ratio_score = max(0.0, 1.0 - abs(ratio - template_ratio) / template_ratio)
            if ratio_score < 0.4:
                continue

            mask_roi = mask_clean[y:y + h, x:x + w]
            coverage = np.count_nonzero(mask_roi) / float(w * h)
            if coverage < 0.55:
                continue

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            if len(approx) < 4:
                continue

            roi_gray = cv2.cvtColor(screenshot_color[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(roi_gray, 60, 150)
            line_threshold = max(20, int(min(w, h) * 0.3))
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi / 180,
                threshold=line_threshold,
                minLineLength=int(min(w, h) * 0.6),
                maxLineGap=int(min(w, h) * 0.25),
            )
            if lines is None:
                continue

            horizontal = sum(1 for line in lines if abs(line[0][1] - line[0][3]) <= 5)
            vertical = sum(1 for line in lines if abs(line[0][0] - line[0][2]) <= 5)
            if horizontal < 2 or vertical < 2:
                continue

            area_score = min(area, template_area) / max(area, template_area)
            score = min(ratio_score, area_score, coverage)

            if score > best_score:
                best_score = score
                confidence = 0.65 + 0.3 * score
                best_candidate = {
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2,
                    'confidence': min(confidence, 0.98),
                    'mode': 'color',
                    'method': 'color_mask',
                    'scale': 1.0,
                }

        if best_candidate:
            print(
                f"     후보 발견: "
                f"({best_candidate['x']}, {best_candidate['y']}) "
                f"size={best_candidate['width']}x{best_candidate['height']} "
                f"conf={best_candidate['confidence']:.2f}"
            )
        return best_candidate
    
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
