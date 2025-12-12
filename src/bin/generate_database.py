import csv
import os
import random

IN_PATH = os.path.join("data", "test_input.csv")
OUT_PATH = os.path.join("mock_system", "database.csv")

# 랜덤 이름 재료
LAST_NAMES = ["김", "이", "박", "최", "정", "윤", "장", "임", "조", "오"]
FIRST_PART = ["민", "서", "지", "도", "하", "윤", "현", "예", "준", "정"]
SECOND_PART = ["우", "윤", "혁", "수", "진", "연", "호", "빈", "율", "영"]


def random_korean_name():
    """한국식 3글자 이름 생성"""
    return random.choice(LAST_NAMES) + random.choice(FIRST_PART) + random.choice(SECOND_PART)


def make_family_members(count):
    """
    count = 총 인원수 (본인 포함)
    
    return = [
        [세대원1이름, 관계],
        [세대원2이름, 관계],
        [세대원3이름, 관계]
    ]
    """
    members = [["", ""], ["", ""], ["", ""]]

    # count 1 → no family members
    if count == 1:
        return members

    # count >= 2 → 배우자 생성
    spouse = random_korean_name()
    members[0] = [spouse, "배우자"]

    # count >= 3 → 자녀1 생성
    if count >= 3:
        child1 = random_korean_name()
        members[1] = [child1, "자녀"]

    # count >= 4 → 자녀2 생성
    if count >= 4:
        child2 = random_korean_name()
        members[2] = [child2, "자녀"]

    return members


def convert():
    # test_input.csv 읽기
    with open(IN_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # database.csv 쓰기
    with open(OUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # 헤더
        writer.writerow([
            "주민등록번호", "이름", "세대주관계",
            "세대원1", "세대원1관계",
            "세대원2", "세대원2관계",
            "세대원3", "세대원3관계"
        ])

        for r in rows:
            rrn = r["주민등록번호"]
            name = r["이름"]
            count = int(r["세대원수"])  # 1~4

            members = make_family_members(count)

            writer.writerow([
                rrn, name, "본인",
                members[0][0], members[0][1],
                members[1][0], members[1][1],
                members[2][0], members[2][1]
            ])

    print(f"[완료] database.csv 생성 완료 ({len(rows)}명)")


if __name__ == "__main__":
    convert()
