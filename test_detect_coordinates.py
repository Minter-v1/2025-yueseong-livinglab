"""
이미지 파일에서 대화상자 경계 및 UI 요소 좌표 검출 테스트
"""

import sys
import cv2
import os
from pathlib import Path

from src.core.dialog_detector import DialogDetector
from src.core.image_matcher import ImageMatcher


def detect_and_visualize(image_path, template_dir='data/templates/templates_real', output_dir=None):
    """
    이미지에서 좌표를 검출하고 결과 이미지를 생성

    Args:
        image_path: 입력 이미지 경로
        template_dir: 템플릿 디렉토리 경로
        output_dir: 출력 디렉토리 (None이면 입력 이미지와 같은 폴더)
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
    templates = ['input_field_id', 'input_field_name', 'search_button', 'reset_button']

    results = {}

    for template_name in templates:
        template_path = os.path.join(template_dir, f'{template_name}.png')

        if not os.path.exists(template_path):
            print(f'  ⚠ {template_name}: 템플릿 파일 없음')
            continue

        try:
            scale_candidates = None
            # HiDPI 환경을 고려해 보조 배율 목록 구성 (템플릿 크기 변화 허용)
            template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template_img is not None:
                template_h, template_w = template_img.shape
                if template_w > 0 and template_h > 0:
                    # ROI에 비례한 상대 배율 추정 (너무 넓은 경우를 위한 클램프 추가)
                    roi_height, roi_width = roi.shape[:2]
                    width_ratio = roi_width / template_w
                    height_ratio = roi_height / template_h
                    estimated = min(max(width_ratio / 4, 0.5), 2.5)
                    # 중심 배율 주변으로 세분화
                    base_scales = [estimated * factor for factor in (0.9, 1.0, 1.1)]
                    # 기본 배율과 병합
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
            print(f'  ✗ {template_name}: 오류')

    # 임시 파일 삭제
    if os.path.exists(roi_path):
        os.remove(roi_path)

    print(f'\n✅ {len(results)}개 UI 요소 검출 완료\n')

    # 4. 결과 이미지 생성
    print('[4단계] 결과 이미지 생성 중...')
    result_img = img.copy()

    # 대화상자 경계 표시 (녹색)
    cv2.rectangle(result_img,
                  (boundary['x'], boundary['y']),
                  (boundary['right'], boundary['bottom']),
                  (0, 255, 0), 3)

    cv2.putText(result_img, f"Dialog Boundary",
                (boundary['x'], boundary['y'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # UI 요소 표시 (빨간색)
    for name, coords in results.items():
        # 사각형
        cv2.rectangle(result_img,
                      (coords['x'], coords['y']),
                      (coords['x'] + coords['width'], coords['y'] + coords['height']),
                      (0, 0, 255), 2)

        # 중심점
        cv2.circle(result_img, (coords['center_x'], coords['center_y']), 5, (255, 0, 0), -1)

        # 라벨
        label = f"{name}: ({coords['center_x']}, {coords['center_y']})"
        cv2.putText(result_img, label,
                    (coords['x'], coords['y'] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # 결과 이미지 저장
    cv2.imwrite(output_path, result_img)
    print(f'✅ 결과 이미지 저장: {output_path}\n')

    # 5. 좌표 출력
    print('=' * 80)
    print('검출된 좌표 정보')
    print('=' * 80)

    print(f'\n📦 대화상자 경계:')
    print(f'   X 왼쪽:  {boundary["x"]}')
    print(f'   X 오른쪽: {boundary["right"]}')
    print(f'   Y 위:    {boundary["y"]}')
    print(f'   Y 아래:  {boundary["bottom"]}')
    print(f'   중심:    ({boundary["center_x"]}, {boundary["center_y"]})')

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


if __name__ == '__main__':
    # 기본 이미지 경로
    default_image = Path("data/templates/img_org.png")


    # 명령행 인자로 이미지 경로 받기
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = default_image

    # 파일 존재 확인
    if not os.path.exists(image_path):
        print(f'❌ 파일을 찾을 수 없습니다: {image_path}')
        print(f'\n사용법: python test_detect_coordinates.py [이미지경로]')
        sys.exit(1)

    # 검출 실행
    detect_and_visualize(image_path)
