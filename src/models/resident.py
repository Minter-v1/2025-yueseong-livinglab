#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주민 정보 데이터 모델
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Resident:
    """주민 정보"""
    
    order: int
    unique_number: str
    name: Optional[str] = None
    family_count: Optional[int] = None
    status: str = "wait"
    message: str = ""
    time: Optional[datetime] = None
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'order': self.order,
            'unique_number': self.unique_number,
            'name': self.name,
            'family_count': self.family_count,
            'status': self.status,
            'message': self.message,
            'time': self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 생성"""
        return cls(
            order=data.get('order', 0),
            unique_number=data.get('unique_number', ''),
            name=data.get('name'),
            family_count=data.get('family_count'),
            status=data.get('status', 'wait'),
            message=data.get('message', ''),
            time=None
        )


@dataclass
class SearchResult:
    """검색 결과"""
    
    resident_number: str
    household_count: int = 0
    status: str = "pending"  # pending, success, error
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'resident_number': self.resident_number,
            'household_count': self.household_count,
            'status': self.status,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

