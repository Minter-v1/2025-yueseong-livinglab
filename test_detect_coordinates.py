"""
이미지 파일에서 대화상자 경계 및 UI 요소 좌표 검출 테스트
(체크박스 다중 검출 및 개수 카운트 로직 추가)
"""

import sys
import cv2
import os
import numpy as np  # numpy 추가
from pathlib import Path

from src.core.dialog_detector import DialogDetector
from src.core.image_matcher import ImageMatcher


def detect_and_visualize(image_path, template_dir='data/templates/templates_real', output_dir=None):
    """
    이미지에서 좌표를 검출하고 결과 이미지를 생성
    """

    print('=' * 80)
    print('대화상자 및 UI 요소 좌표 검출 테스트')
    print('=' * 80)
    print(f'\n입력 이미지: {image_path}')
    print(f'템플릿 폴더: {template_dir}\n')

    # 출력 디렉토리 설정
    if output_dir is None:
        output_dir = os.path.dirname(image_path)

    output_path = os.path.join(output_dir, 'result_coordinates.png')

    # 1. 대화상자 경계 검출
    print('[1단계] 대화상자 경계 검출 중...')
    detector = DialogDetector(debug=False)
    boundary = detector.detect_dialog_boundary(image_path)

    if not boundary:
        print('❌ 대화상자 경계를 찾을 수 없습니다.')
        return

    print(f'\n✅ 대화상자 경계 검출 완료!')
    print(f'   X: {boundary["x"]} ~ {boundary["right"]}')
    print(f'   Y: {boundary["y"]} ~ {boundary["bottom"]}')
    print(f'   크기: {boundary["width"]} x {boundary["height"]}\n')

    # 2. ROI 추출
    print('[2단계] 대화상자 영역 추출 중...')
    img = cv2.imread(image_path)
    roi = img[boundary['y']:boundary['bottom'], boundary['x']:boundary['right']]
    
    # 그레이스케일 변환 (매칭 정확도 향상용)
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    roi_path = 'temp_roi.png'
    cv2.imwrite(roi_path, roi)
    print('✅ 영역 추출 완료\n')

    # 3. 템플릿 매칭
    print('[3단계] UI 요소 검색 중...')
    matcher = ImageMatcher(
        confidence=0.55,
        search_scales=[0.6, 0.75, 0.9, 1.0, 1.1, 1.25, 1.4, 1.6, 1.8, 2.0],
        match_modes=('gray', 'canny', 'color', 'sat'),
        canny_thresholds=(30, 120),
        method=(cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED),
        pre_blur=(3, 3)
    )
    
    # 템플릿 목록
    templates = ['input_field_id', 'input_field_name', 'search_button', 'reset_button', 'checkbox']
    results = {}

    for template_name in templates:
        template_path = os.path.join(template_dir, f'{template_name}.png')

        if not os.path.exists(template_path):
            print(f'  ⚠ {template_name}: 템플릿 파일 없음')
            continue

        try:
            # ----------------------------------------------------------------
            # [수정] 체크박스는 여러 개를 찾아야 하므로 별도 로직 처리
            # ----------------------------------------------------------------
            if template_name == 'checkbox':
                print(f'  🔎 {template_name}: 최적 스케일 탐색 및 다중 검출 시작...')
                tpl_img_orig = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                
                if tpl_img_orig is None:
                    print(f'  ⚠️ 오류: {template_name}.png 파일을 읽을 수 없습니다.')
                    continue

                # 1. 최적의 스케일 찾기 (0.8배 ~ 1.2배 사이 탐색)
                best_score = -1
                best_scale = 1.0
                best_tpl = tpl_img_orig

                # 탐색할 배율 범위 설정 (필요하면 0.5 ~ 2.0 등으로 넓히세요)
                scales = [0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2]
                
                for scale in scales:
                    # 템플릿 리사이징
                    w = int(tpl_img_orig.shape[1] * scale)
                    h = int(tpl_img_orig.shape[0] * scale)
                    if w == 0 or h == 0: continue
                    
                    resized_tpl = cv2.resize(tpl_img_orig, (w, h))
                    
                    # ROI보다 템플릿이 크면 패스
                    if resized_tpl.shape[0] > roi_gray.shape[0] or resized_tpl.shape[1] > roi_gray.shape[1]:
                        continue

                    # 매칭 테스트
                    res = cv2.matchTemplate(roi_gray, resized_tpl, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    
                    if max_val > best_score:
                        best_score = max_val
                        best_scale = scale
                        best_tpl = resized_tpl

                print(f'    👉 최적 스케일: {best_scale:.2f} (최고 점수: {best_score:.2f})')

                # 2. 임계값 설정 (검출이 안 되면 이 값을 0.55 정도로 더 낮추세요)
                threshold = 0.60  
                
                if best_score < threshold:
                    print(f'    ⚠️ 경고: 유사도가 너무 낮습니다 ({best_score:.2f} < {threshold}). 템플릿 이미지를 다시 캡처해보세요.')
                    continue

                # 3. 최적화된 템플릿으로 전체 다중 검출 시작
                th, tw = best_tpl.shape
                res = cv2.matchTemplate(roi_gray, best_tpl, cv2.TM_CCOEFF_NORMED)
                
                res_copy = res.copy()
                found_checkboxes = []
                loop_count = 0
                
                while True:
                    loop_count += 1
                    if loop_count > 100: break # 무한루프 방지

                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res_copy)
                    
                    if max_val < threshold:
                        break
                        
                    # 좌표 저장
                    top_left = max_loc
                    
                    found_checkboxes.append({
                        'x': boundary['x'] + top_left[0],
                        'y': boundary['y'] + top_left[1],
                        'center_x': boundary['x'] + top_left[0] + tw // 2,
                        'center_y': boundary['y'] + top_left[1] + th // 2,
                        'width': tw,
                        'height': th,
                        'confidence': max_val
                    })
                    
                    # 마스킹 (찾은 곳 지우기)
                    start_x = max(0, top_left[0] - tw // 2)
                    start_y = max(0, top_left[1] - th // 2)
                    end_x = min(res_copy.shape[1], top_left[0] + tw // 2)
                    end_y = min(res_copy.shape[0], top_left[1] + th // 2)
                    res_copy[start_y:end_y, start_x:end_x] = -1 # 확실히 지움

                # 정렬 및 결과 저장
                found_checkboxes.sort(key=lambda k: k['y'])
                total_cnt = len(found_checkboxes)

                print(f'  ✓ {template_name}: {total_cnt}개 발견')
                
                for idx, box in enumerate(found_checkboxes):
                    key = f"{template_name}_{idx}"
                    results[key] = box
                
                continue

            # ----------------------------------------------------------------
            # 일반 UI 요소 (단일 검출) - 기존 로직 유지
            # ----------------------------------------------------------------
            scale_candidates = None
            template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            
            if template_img is not None:
                template_h, template_w = template_img.shape
                if template_w > 0 and template_h > 0:
                    roi_height, roi_width = roi.shape[:2]
                    width_ratio = roi_width / template_w
                    estimated = min(max(width_ratio / 4, 0.5), 2.5)
                    base_scales = [estimated * factor for factor in (0.9, 1.0, 1.1)]
                    scale_candidates = sorted({
                        round(scale, 2)
                        for scale in list(matcher.search_scales) + base_scales
                        if 0.4 <= scale <= 3.0
                    })

            match = matcher.find_template(roi_path, template_path, scale_search=scale_candidates)

            if match:
                results[template_name] = {
                    'x': boundary['x'] + match['x'],
                    'y': boundary['y'] + match['y'],
                    'center_x': boundary['x'] + match['center_x'],
                    'center_y': boundary['y'] + match['center_y'],
                    'width': match['width'],
                    'height': match['height'],
                    'confidence': match['confidence']
                }
                print(f'  ✓ {template_name}: 검출 (신뢰도 {match["confidence"]:.1%})')
            else:
                print(f'  ✗ {template_name}: 찾지 못함')

        except Exception as e:
            print(f'  ✗ {template_name}: 오류 - {e}')

    # 임시 파일 삭제
    if os.path.exists(roi_path):
        os.remove(roi_path)

    print(f'\n✅ {len(results)}개 UI 요소 검출 완료\n')

    # 4. 결과 이미지 생성
    print('[4단계] 결과 이미지 생성 중...')
    result_img = img.copy()

    # 대화상자 경계 표시
    cv2.rectangle(result_img,
                  (boundary['x'], boundary['y']),
                  (boundary['right'], boundary['bottom']),
                  (0, 255, 0), 3)

    cv2.putText(result_img, "Dialog", (boundary['x'], boundary['y'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # UI 요소 표시
    checkbox_count = 0
    
    for name, coords in results.items():
        color = (0, 0, 255) # 기본: 빨강
        thickness = 2
        
        # 체크박스는 색상을 다르게 표시 (노랑)
        if 'checkbox' in name:
            color = (0, 255, 255)
        
        # 사각형
        cv2.rectangle(result_img,
                      (coords['x'], coords['y']),
                      (coords['x'] + coords['width'], coords['y'] + coords['height']),
                      color, thickness)

        # 중심점
        cv2.circle(result_img, (coords['center_x'], coords['center_y']), 4, (255, 0, 0), -1)

        # 라벨 (체크박스가 아니거나, 체크박스인 경우 간소화)
        if 'checkbox' not in name:
            label = f"{name}"
            cv2.putText(result_img, label,
                        (coords['x'], coords['y'] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 결과 요약 텍스트 이미지 좌상단에 표시
    checkbox_items = [k for k in results.keys() if 'checkbox' in k]
    if checkbox_items:
        total = len(checkbox_items)
        info_text = f"Checkboxes: {total}"
        cv2.putText(result_img, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4) # 그림자
        cv2.putText(result_img, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # 결과 이미지 저장
    cv2.imwrite(output_path, result_img)
    print(f'✅ 결과 이미지 저장: {output_path}\n')

    # 5. 좌표 출력
    print('=' * 80)
    print('검출된 좌표 정보')
    print('=' * 80)
    
    # 체크박스 결과 요약 출력
    chk_keys = [k for k in results.keys() if 'checkbox' in k]
    if chk_keys:
        # 정렬된 키 순서대로 (0, 1, 2...)
        chk_keys.sort(key=lambda x: int(x.split('_')[1]))
        print(f'\n☑️  체크박스 목록 (총 {len(chk_keys)}개)')
        for key in chk_keys:
            c = results[key]
            print(f"   - {key}: ({c['x']}, {c['y']})")
            
    print(f'\n📦 대화상자 경계: ({boundary["x"]}, {boundary["y"]})')

    if results:
        print(f'\n🎯 기타 UI 요소:')
        for name, coords in results.items():
            if 'checkbox' in name: continue
            print(f'   [{name}]: ({coords["center_x"]}, {coords["center_y"]})')
    
    print('\n' + '=' * 80)
    print('✅ 검출 완료!')


if __name__ == '__main__':
    default_image = Path("data/templates/img_org.png")
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = default_image

    if not os.path.exists(image_path):
        print(f'❌ 파일을 찾을 수 없습니다: {image_path}')
        sys.exit(1)

    detect_and_visualize(image_path)