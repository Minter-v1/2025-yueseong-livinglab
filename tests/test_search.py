"""
test_search.py
행복e음 Mock 시스템 자동 주민조회 테스트 스크립트
"""

import os
import csv
import sys
import time
from datetime import datetime
from src.services.search_service import SearchAutomationService
from src.services.excel_service import ExcelService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 로그 저장 위치
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 입력 데이터 선택
USE_DATABASE = True

if USE_DATABASE:
    INPUT_PATH = os.path.join(BASE_DIR, "mock_system", "database.csv")
else:
    INPUT_PATH = os.path.join(BASE_DIR, "data", "test_input.csv")


def load_resident_numbers():
    print(f"Loading data from: {INPUT_PATH}")

    resident_numbers = []

    with open(INPUT_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rrn = row.get("주민등록번호", "").strip()
            if rrn:
                resident_numbers.append(rrn)

    print(f"Loaded {len(resident_numbers)} resident numbers")
    return resident_numbers


def format_excel_record(index, result):
    """검색 결과를 엑셀 저장용 포맷으로 변환한다"""
    return {
        "순번": index,
        "주민등록번호": result.get("resident_number", ""),
        "세대원수": result.get("household_count", 0),
        "상태": "완료" if result.get("status") == "success" else "오류"
    }


def main():
    print("=" * 60)
    print(" 자동 주민조회 테스트 시작")
    print(" 먼저 mock_system/app.py를 실행해 두세요")
    print("=" * 60)

    print("5초 뒤에 자동 테스트 시작됩니다...")
    time.sleep(5)

    # 자동화 서비스 초기화
    service = SearchAutomationService()

    # 입력 데이터 로드
    numbers = load_resident_numbers()

    # 로그 폴더 생성
    os.makedirs(LOG_DIR, exist_ok=True)

    # CSV 로그 파일 생성
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_DIR, f"auto_test_{ts}.csv")

    # Excel 결과 리스트
    results_list = []

    with open(log_path, "w", newline="", encoding="utf-8-sig") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["주민등록번호", "household_count", "status", "message"])

        total = len(numbers)
        success = 0
        fail = 0

        for i, rrn in enumerate(numbers, 1):
            print(f"\n[{i}/{total}] Searching: {rrn}")

            result = service.search_resident(rrn)

            # CSV 저장
            writer.writerow([
                result["resident_number"],
                result["household_count"],
                result["status"],
                result["message"]
            ])

            # Excel 저장용 포맷 변환
            excel_record = format_excel_record(i, result)
            results_list.append(excel_record)

            if result["status"] == "success":
                success += 1
            else:
                fail += 1

    # Excel 저장
    excel_path = os.path.join(LOG_DIR, f"auto_test_{ts}.xlsx")
    ExcelService.write_results(excel_path, results_list)
    print(f"\n엑셀 저장 완료 : {excel_path}")

    # 요약 출력
    print("\n" + "=" * 60)
    print(" 자동 테스트 요약 ")
    print("=" * 60)
    print(f"총 건수   : {total}")
    print(f"성공 건수 : {success}")
    print(f"실패 건수 : {fail}")
    print(f"로그 저장 : {log_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
