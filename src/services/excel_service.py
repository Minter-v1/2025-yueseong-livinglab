"""
Excel 처리 서비스
"""

import pandas as pd
import os


class ExcelService:
    """Excel 파일 읽기/쓰기"""
    
    @staticmethod
    def read_residents(file_path, column_name='주민등록번호'):
        """
        Excel 파일에서 주민등록번호 목록 읽기
        
        Args:
            file_path: Excel 파일 경로
            column_name: 주민등록번호 컬럼 이름
            
        Returns:
            list: [
                {'순번': 1, '주민등록번호': '900101-1234567', '이름': '홍길동'},
                ...
            ]
        """
        # 파일 확장자에 따라 읽기
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path)

        print(f"[EXCEL] 읽은 컬럼: {list(df.columns)}")

        # 컬럼 이름 공백/BOM 제거
        def _clean_column(name):
            if isinstance(name, str):
                return name.replace('\ufeff', '').strip()
            return name

        df.rename(columns=_clean_column, inplace=True)
        column_name = _clean_column(column_name)
        
        # 주민등록번호 컬럼 확인
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in file")

        # 주민등록번호 문자열화 (NaN/공백 처리)
        def _normalize_id(value):
            if value is None:
                return ''
            if pd.isna(value):
                return ''
            return str(value).strip()

        df[column_name] = df[column_name].apply(_normalize_id)

        preview = df.head(3).to_dict('records')
        print(f"[EXCEL] 데이터 샘플 3건: {preview}")
        
        # 딕셔너리 리스트로 변환
        records = df.to_dict('records')
        
        return records
    
    @staticmethod
    def write_results(file_path, results):
        """
        결과를 Excel 파일에 쓰기
        
        Args:
            file_path: 출력 파일 경로
            results: 결과 리스트 [
                {'순번': 1, '주민등록번호': '...', '이름': '...', '세대원 수': 4, '상태': '완료', '메시지': '...'},
                ...
            ]
        """
        df = pd.DataFrame(results)
        
        # 기본 경로
        base_path = os.path.splitext(file_path)[0]

        # Excel 저장
        excel_path = base_path + '.xlsx'
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"Excel 저장: {excel_path}")
    
    @staticmethod
    def append_column(file_path, column_name, values, output_path=None):
        """
        Excel 파일에 컬럼 추가
        
        Args:
            file_path: 파일 경로
            column_name: 추가할 컬럼 이름
            values: 컬럼 값 리스트
            output_path: 파일 경로 (None이면 덮어쓰기)
        """
        # 파일 읽기
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path)
        
        # 컬럼 추가
        df[column_name] = values
        
        # 저장
        if output_path is None:
            output_path = file_path
        
        if output_path.endswith('.csv'):
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(output_path, index=False)
        
        print(f" Column '{column_name}' added to: {output_path}")


if __name__ == "__main__":
    # 테스트
    service = ExcelService()
    
    # 테스트 데이터 읽기
    test_file = "data/test_input.csv"
    if os.path.exists(test_file):
        records = service.read_residents(test_file)
        print(f"Read {len(records)} records from {test_file}")
        for record in records[:3]:
            print(f"  - {record}")
