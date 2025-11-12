#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지 매크로 테스트
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.search_service import SearchAutomationService

def test_macro():
    """매크로 테스트"""
    print("=" * 60)
    print("🧪 이미지 매크로 테스트")
    print("=" * 60)

    # Mock 시스템이 실행 중인지 확인
    print("\n⚠️  Mock 시스템이 전체화면으로 실행 중이어야 합니다!")
    print("   ./venv/bin/python mock_system/app.py")

    print("\n5초 후 자동으로 시작합니다...")
    print("Mock 시스템 창으로 전환하세요!\n")

    for i in range(5, 0, -1):
        print(f"⏱️  {i}초...")
        time.sleep(1)

    print("\n🚀 시작!\n")
    
    # 서비스 초기화 (템플릿 매칭 모드)
    print("\n서비스 초기화 중...")
    print("모드: OpenCV 템플릿 매칭")
    service = SearchAutomationService()
    
    # 테스트 주민등록번호
    test_number = "900101-1234567"
    
    print(f"\n2️⃣  테스트 검색 시작: {test_number}")
    print("   (Mock 시스템 창을 보세요!)")
    
    # 검색 실행
    result = service.search_resident(test_number)
    
    print("\n" + "=" * 60)
    print("📊 결과:")
    print("=" * 60)
    print(f"주민등록번호: {result['resident_number']}")
    print(f"세대원 수: {result['household_count']}")
    print(f"상태: {result['status']}")
    print(f"메시지: {result['message']}")
    print("=" * 60)

if __name__ == "__main__":
    test_macro()

