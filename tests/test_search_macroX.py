"""
test_search.py
자동 검색 없이 Excel 생성 (세대원수 자동 계산)
"""

import os
import csv
import sys
import time
from datetime import datetime
from src.services.excel_service import ExcelService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

LOG_DIR = os.path.join(BASE_DIR, "logs")

USE_DATABASE = True

if USE_DATABASE:
    INPUT_PATH = os.path.join(BASE_DIR, "mock_system", "database.csv")
else:
    INPUT_PATH = os.path.join(BASE_DIR, "data", "test_input.csv")


def count_household(row):
    """database.csv 기반 세대원수 계산"""
    count = 1  # 본인
    for i in range(1, 4):
        member = row.get(f"세대원{i}", "").strip()
        if member:
            count += 1
    return count


def load_residents():
    print(f" Loading data from: {INPUT_PATH}")

    residents = []

    with open(INPUT_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            household = count_household(row)

            residents.append({
                "주민등록번호": row.get("주민등록번호", "").strip(),
                "이름": row.get("이름", "").strip(),
                "세대원수": household,
                "상태": "완료"
            })

    print(f" Loaded {len(residents)} residents")
    return residents


def main():
    print("=" * 60)
    print("자동 검색 없이 Excel 생성")
    print("=" * 60)

    os.makedirs(LOG_DIR, exist_ok=True)

    residents = load_residents()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(LOG_DIR, f"excel_only_{ts}.xlsx")

    ExcelService.write_results(excel_path, residents)

    print(f"\n Excel 저장 완료: {excel_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
