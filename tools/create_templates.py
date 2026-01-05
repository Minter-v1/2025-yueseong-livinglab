"""
템플릿 이미지 생성 도구
마우스로 영역을 선택하여 템플릿 이미지 저장
"""

import os
import sys
import time
import pyautogui
from PIL import Image

# 프로젝트 루트 경로 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def capture_region_by_clicks(template_name, output_dir):
    """
    마우스 클릭으로 영역 선택 후 캡처

    Args:
        template_name: 템플릿 이름 (예: 'input_field')
        output_dir: 저장할 디렉토리
    """
    print(f"\n=== 템플릿 생성: {template_name} ===")
    print("5초 후 시작됩니다. 목표 화면으로 이동하세요...")
    time.sleep(5)

    print("\n[1단계] 영역의 왼쪽 상단 모서리를 클릭하세요...")
    print("(마우스를 정확한 위치에 놓고 기다리면 3초 후 자동 캡처)")

    # 첫 번째 점 캡처 (3초간 위치 모니터링)
    time.sleep(3)
    x1, y1 = pyautogui.position()
    print(f"✓ 첫 번째 점: ({x1}, {y1})")

    print("\n[2단계] 영역의 오른쪽 하단 모서리를 클릭하세요...")
    print("(마우스를 정확한 위치에 놓고 기다리면 3초 후 자동 캡처)")

    # 두 번째 점 캡처
    time.sleep(3)
    x2, y2 = pyautogui.position()
    print(f"✓ 두 번째 점: ({x2}, {y2})")

    # 좌표 정규화 (왼쪽 상단이 x1, y1이 되도록)
    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)

    width = right - left
    height = bottom - top

    print(f"\n영역 정보:")
    print(f"  위치: ({left}, {top})")
    print(f"  크기: {width} x {height}")

    if width <= 0 or height <= 0:
        print("❌ 오류: 잘못된 영역입니다.")
        return False

    # 화면 캡처
    print("\n캡처 중...")
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    # 저장
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{template_name}.png")
    screenshot.save(output_path)

    print(f"✓ 저장 완료: {output_path}")
    print(f"  실제 저장된 크기: {screenshot.size}")

    return True


def main():
    """메인 함수"""
    import platform

    # OS에 따라 출력 디렉토리 결정
    system = platform.system()
    if system == "Windows":
        output_dir = os.path.join(project_root, "data/templates/templates_window")
    elif system == "Darwin":
        output_dir = os.path.join(project_root, "data/templates/templates_mac")
    else:
        output_dir = os.path.join(project_root, "data/templates/templates_window")

    print("=" * 60)
    print("템플릿 이미지 생성 도구")
    print("=" * 60)
    print(f"OS: {system}")
    print(f"저장 경로: {output_dir}")
    print()
    print("생성할 템플릿:")
    print("  1. input_field  (입력 필드)")
    print("  2. search_button (검색 버튼)")
    print("  3. checkbox (체크박스)")
    print("  4. custom (사용자 정의)")
    print()

    choice = input("선택 (1-4): ").strip()

    template_map = {
        '1': 'input_field',
        '2': 'search_button',
        '3': 'checkbox',
    }

    if choice == '4':
        template_name = input("템플릿 이름 입력: ").strip()
        if not template_name:
            print("❌ 템플릿 이름이 비어있습니다.")
            return
    elif choice in template_map:
        template_name = template_map[choice]
    else:
        print("❌ 잘못된 선택입니다.")
        return

    # 템플릿 캡처
    success = capture_region_by_clicks(template_name, output_dir)

    if success:
        print("\n✓ 템플릿 생성 완료!")
        print(f"\n다른 템플릿도 생성하려면 다시 실행하세요:")
        print(f"  python tools/create_templates.py")
    else:
        print("\n❌ 템플릿 생성 실패")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
