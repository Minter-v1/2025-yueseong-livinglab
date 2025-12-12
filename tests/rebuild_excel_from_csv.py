"""
CSV 로그를 다시 읽어서 Excel 파일로 재생성하는 스크립트
"""

import os
import sys
import csv
from datetime import datetime

# ------------------------------------------------------
# 🔥 가장 먼저 src 경로 등록
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

LOG_DIR = os.path.join(BASE_DIR, "logs")

from src.services.excel_service import ExcelService


def rebuild(csv_path):
    print(f"📌 CSV 불러오는 중 : {csv_path}")

    results_list = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            results_list.append({
                "순번": i,
                "주민등록번호": row.get("주민등록번호", ""),
                "세대원수": row.get("household_count", 0),
                "상태": "완료" if row.get("status") == "success" else "오류"
            })

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(LOG_DIR, f"rebuild_{ts}.xlsx")

    ExcelService.write_results(excel_path, results_list)

    print(f"📁 EXCEL 재생성 완료: {excel_path}")


if __name__ == "__main__":

    target_csv = input(
        "\n변환할 CSV 경로를 입력하거나 Enter를 눌러 최신 파일을 사용하세요:\n➡  "
    ).strip()

    if target_csv:
        # 직접 입력한 경로 사용
        if not os.path.exists(target_csv):
            print("❌ 입력한 파일이 존재하지 않습니다.")
            sys.exit(1)
        csv_path = target_csv

    else:
        # 자동으로 최신 CSV 선택
        csv_files = [f for f in os.listdir(LOG_DIR) if f.endswith(".csv")]
        csv_files.sort(reverse=True)

        if not csv_files:
            print("❌ logs 폴더에 CSV가 없습니다.")
            sys.exit(1)

        csv_path = os.path.join(LOG_DIR, csv_files[0])

    rebuild(csv_path)
