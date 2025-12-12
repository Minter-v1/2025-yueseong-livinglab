"""
이미지 파일에서 대화상자 경계 및 UI 요소 좌표 검출 테스트
"""

import argparse
import os
from pathlib import Path

import cv2

from src.core.dialog_detector import DialogDetector
from src.core.image_matcher import ImageMatcher


def score_boundary(boundary, img_shape):
    """검출된 경계가 팝업으로 적절한지 간단히 평가"""
    if boundary is None or img_shape is None:
        return 0.0, 0.0, 0.0

    img_h, img_w = img_shape[:2]
    img_area = img_w * img_h

    box_w = boundary['width']
    box_h = boundary['height']
    area = box_w * box_h
    area_ratio = area / img_area if img_area else 0.0
    aspect_ratio = box_w / box_h if box_h else 0.0

    # 이상적인 대화상자는 화면의 20~70%를 차지하고, 종횡비는 0.8~2.5 범위라고 가정
    area_score = max(0.0, 1.0 - abs(area_ratio - 0.4) / 0.4)
    aspect_score = max(0.0, 1.0 - abs(aspect_ratio - 1.4) / 1.4)
    total_score = (area_score + aspect_score) / 2.0

    return total_score, area_ratio, aspect_ratio


def choose_boundary(detector, image_path, mode):
    """요청된 모드에 따라 대화상자 경계를 선택"""
    if mode == 'edge':
        boundary = detector.detect_with_edge_lines(image_path)
        return boundary, 'edge'

    # brightness 또는 auto
    boundary = detector.detect_dialog_boundary(image_path)
    if mode == 'brightness':
        return boundary, 'brightness'

    # auto 모드: 품질 평가 후 부족하면 edge 방식으로 대체
    img = cv2.imread(image_path)
    auto_score, area_ratio, aspect_ratio = score_boundary(boundary, img.shape if img is not None else None)

    print(f'   ▷ brightness 후보 평가: score={auto_score:.2f}, area={area_ratio:.2%}, aspect={aspect_ratio:.2f}')
    if auto_score >= 0.45:
        return boundary, 'brightness'

    print('   ⚠ brightness 결과가 불안정하여 edge 기반 검출을 시도합니다...')
    edge_boundary = detector.detect_with_edge_lines(image_path)
    edge_score, edge_area_ratio, edge_aspect_ratio = score_boundary(edge_boundary, img.shape if img is not None else None)
    print(f'   ▷ edge 후보 평가: score={edge_score:.2f}, area={edge_area_ratio:.2%}, aspect={edge_aspect_ratio:.2f}')

    if edge_score > auto_score:
        return edge_boundary, 'edge'

    return boundary, 'brightness'


def detect_and_visualize(image_path, template_dir='data/templates/templates_real',
                         output_dir=None, mode='auto'):
    """
    이미지에서 좌표를 검출하고 결과 이미지를 생성

    Args:
        image_path: 입력 이미지 경로
        template_dir: 템플릿 디렉토리 경로
        output_dir: 결과 이미지 저장 디렉토리 (None이면 입력 이미지와 동일 폴더)
        mode: 경계 검출 방식 ('auto', 'brightness', 'edge')
    """
    print('=' * 80)
    print('대화상자 및 UI 요소 좌표 검출 테스트')
    print('=' * 80)
    print(f'\n입력 이미지: {image_path}')
    print(f'템플릿 폴더: {template_dir}')
    print(f'경계 검출 방식: {mode}\n')

    if output_dir is None:
        output_dir = os.path.dirname(str(image_path))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'result_coordinates.png')

    # 1. 대화상자 경계 검출
    print('[1단계] 대화상자 경계 검출 중...')
    detector = DialogDetector(debug=False)
    boundary, detector_used = choose_boundary(detector, str(image_path), mode)

    if not boundary:
        print('❌ 대화상자 경계를 찾을 수 없습니다.')
        return

    print(f'\n✅ 대화상자 경계 검출 완료! (사용한 방식: {detector_used})')
    print(f'   X: {boundary["x"]} ~ {boundary["right"]}')
    print(f'   Y: {boundary["y"]} ~ {boundary["bottom"]}')
    print(f'   크기: {boundary["width"]} x {boundary["height"]}\n')

    # 2. ROI 추출
    print('[2단계] 대화상자 영역 추출 중...')
    img = cv2.imread(str(image_path))
    if img is None:
        print('❌ 이미지를 불러올 수 없습니다.')
        return
    roi = img[boundary['y']:boundary['bottom'], boundary['x']:boundary['right']]
    roi_path = os.path.join(output_dir, 'temp_roi.png')
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
    templates = ['input_field_id', 'input_field_name', 'search_button', 'reset_button']
    results = {}

    for template_name in templates:
        template_path = os.path.join(template_dir, f'{template_name}.png')
        if not os.path.exists(template_path):
            print(f'  ⚠ {template_name}: 템플릿 파일 없음')
            continue

        try:
            scale_candidates = None
            template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template_img is not None:
                temp_h, temp_w = template_img.shape
                if temp_w > 0 and temp_h > 0:
                    roi_height, roi_width = roi.shape[:2]
                    width_ratio = roi_width / temp_w
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
        except Exception as exc:
            print(f'  ✗ {template_name}: 오류 ({exc})')

    if os.path.exists(roi_path):
        os.remove(roi_path)

    print(f'\n✅ {len(results)}개 UI 요소 검출 완료\n')

    # 4. 결과 이미지 생성
    print('[4단계] 결과 이미지 생성 중...')
    result_img = img.copy()

    cv2.rectangle(result_img,
                  (boundary['x'], boundary['y']),
                  (boundary['right'], boundary['bottom']),
                  (0, 255, 0), 3)

    cv2.putText(result_img, "Dialog Boundary",
                (boundary['x'], max(boundary['y'] - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    for name, coords in results.items():
        cv2.rectangle(result_img,
                      (coords['x'], coords['y']),
                      (coords['x'] + coords['width'], coords['y'] + coords['height']),
                      (0, 0, 255), 2)
        cv2.circle(result_img, (coords['center_x'], coords['center_y']), 5, (255, 0, 0), -1)
        label = f"{name}: ({coords['center_x']}, {coords['center_y']})"
        cv2.putText(result_img, label,
                    (coords['x'], max(coords['y'] - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imwrite(output_path, result_img)
    print(f'✅ 결과 이미지 저장: {output_path}\n')

    # 5. 좌표 출력
    print('=' * 80)
    print('검출된 좌표 정보')
    print('=' * 80)
    print(f'\n📦 대화상자 경계:')
    print(f'   X 왼쪽:   {boundary["x"]}')
    print(f'   X 오른쪽: {boundary["right"]}')
    print(f'   Y 위:     {boundary["y"]}')
    print(f'   Y 아래:   {boundary["bottom"]}')
    print(f'   중심:     ({boundary["center_x"]}, {boundary["center_y"]})')

    if results:
        print(f'\n🎯 UI 요소 좌표:')
        for name, coords in results.items():
            print(f'\n  [{name}]')
            print(f'     좌표: ({coords["x"]}, {coords["y"]})')
            print(f'     중심: ({coords["center_x"]}, {coords["center_y"]})')
            print(f'     크기: {coords["width"]} x {coords["height"]}')
            print(f'     신뢰도: {coords["confidence"]:.1%}')
            print(f'     클릭 명령: pyautogui.click({coords["center_x"]}, {coords["center_y"]})')
    else:
        print('\n⚠ UI 요소를 찾지 못했습니다.')

    print('\n' + '=' * 80)
    print('✅ 검출 완료!')
    print('=' * 80)


def parse_args():
    parser = argparse.ArgumentParser(
        description='대화상자 경계 및 UI 요소 좌표 검출 테스트 도구'
    )
    parser.add_argument('image', nargs='?', default=Path("data/templates/img_org.jpeg"),
                        help='입력 이미지 경로 (기본값: data/templates/img_org.jpeg)')
    parser.add_argument('--templates', default='data/templates/templates_real',
                        help='템플릿 디렉토리 경로')
    parser.add_argument('--output', default=None,
                        help='결과 이미지 저장 폴더 (기본값: 입력 이미지와 동일)')
    parser.add_argument('--method', choices=['auto', 'brightness', 'edge'], default='auto',
                        help='대화상자 경계 검출 방식 (기본값: auto)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    image_path = args.image

    if not os.path.exists(image_path):
        print(f'❌ 파일을 찾을 수 없습니다: {image_path}')
        exit(1)

    detect_and_visualize(
        image_path,
        template_dir=args.templates,
        output_dir=args.output,
        mode=args.method,
    )
