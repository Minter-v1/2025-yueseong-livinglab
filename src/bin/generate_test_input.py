#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
랜덤 테스트 입력 CSV 생성
-> data/test_input.csv (순번,주민등록번호,이름,세대원수) 3500행
"""

import os
import csv
import random

OUT_PATH = os.path.join("data", "test_input.csv")
TARGET_COUNT = 3500

# 대충 쓸 이름 재료들
LAST_NAMES = ["김", "이", "박", "최", "정", "윤", "한", "강", "임", "송"]
FIRST_PART = ["서", "민", "지", "현", "도", "하", "태", "예", "준", "영"]
SECOND_PART = ["윤", "빈", "수", "영", "진", "우", "연", "현", "민", "아"]


def random_rrn():
    """주민등록번호 형태만 맞춘 랜덤 문자열 (규칙까지는 안 맞춰도 됨)"""
    # 앞 6자리: yymmdd (대충)
    year = random.randint(50, 99)   # 1950~1999 출생이라고 가정
    month = random.randint(1, 12)
    day = random.randint(1, 28)     # 편하게 1~28
    front = f"{year:02d}{month:02d}{day:02d}"

    # 뒤 7자리: 그냥 랜덤 숫자
    back = "".join(str(random.randint(0, 9)) for _ in range(7))

    return f"{front}-{back}"


def random_name():
    """한글 이름 랜덤 생성"""
    return random.choice(LAST_NAMES) + random.choice(FIRST_PART) + random.choice(SECOND_PART)


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    with open(OUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["순번", "주민등록번호", "이름", "세대원수"])

        for i in range(1, TARGET_COUNT + 1):
            rrn = random_rrn()
            name = random_name()
            household = random.randint(1, 4)  # 세대원수 1~4 랜덤

            writer.writerow([i, rrn, name, household])

    print(f"[OK] {OUT_PATH} 생성 완료 (총 {TARGET_COUNT}행)")


if __name__ == "__main__":
    main()
