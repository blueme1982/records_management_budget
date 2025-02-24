import pandas as pd
from .budget_classifier import BudgetClassifier

class DataProcessor:
    # 프로젝트 타입 한글 매핑
    PROJECT_TYPE_KR = {
        'SYSTEM_MGMT': '시스템 관리',
        'DIGITALIZATION': '디지털화',
        'PRESERVATION': '보존관리',
        'RECORDS_MGMT': '기록물관리',
        'SPECIAL_PROJECT': '특수사업'
    }
    
    # 프로젝트 서브타입 한글 매핑
    PROJECT_SUBTYPE_KR = {
        # SYSTEM_MGMT
        'SYS_OPERATION': '시스템 운영/유지보수',
        'SYS_ENHANCEMENT': '시스템 고도화/개선',
        'SECURITY_MGMT': '보안관리',
        'INFRA_ESTABLISH': '인프라 구축',
        
        # DIGITALIZATION
        'RECORDS_DIGITIZATION': '기록물 디지털화',
        'DB_CONSTRUCTION': '데이터베이스 구축',
        'DIGITAL_ARCHIVE': '디지털 아카이브 구축',
        
        # PRESERVATION
        'ENVIRONMENT_CONTROL': '보존환경 관리',
        'PEST_PREVENTION': '해충방제/방균관리',
        'STORAGE_MGMT': '서고관리',
        'SUPPLIES_MGMT': '보존용품관리',
        'REPAIR_RESTORE': '복원/복구처리',
        
        # RECORDS_MGMT
        'RECORDS_ARRANGE': '기록물 정리/기술',
        'RECORDS_TRANSFER': '이관/인수',
        'RECORDS_APPRAISAL': '평가/폐기',
        'RECORDS_INSPECTION': '실태점검/정수점검',
        'ACCESS_CONTROL': '공개재분류/접근관리',
        
        # SPECIAL_PROJECT
        'CONSULTING': '컨설팅/연구용역',
        'PLANNING': '전략/계획수립',
        'EDUCATION': '교육/훈련',
        'FACILITY_IMPROVE': '시설개선'
    }

    def __init__(self, csv_path: str):
        """
        데이터 처리기를 초기화합니다.
        
        Args:
            csv_path (str): CSV 파일 경로 (예: 'assets/data/records_management_budget.csv')
        """
        self.csv_path = csv_path
        self.classifier = BudgetClassifier()
        
    def get_processed_data(self) -> pd.DataFrame:
        """
        전처리된 데이터를 반환합니다.
        
        Returns:
            pd.DataFrame: 전처리된 데이터프레임
        """
        # CSV 파일 읽기
        df = pd.read_csv(self.csv_path)
        
        # 예산 금액 전처리
        df['budget_amount'] = df['budget_amount'].str.replace(',', '').astype(float)
        
        # 문자열 컬럼 초기화
        df['project_type'] = ''
        df['project_subtype'] = ''
        
        # 프로젝트 분류 적용
        for idx, row in df.iterrows():
            project_type, project_subtype = self.classifier.classify_project(row['project_detail'])
            df.at[idx, 'project_type'] = self.PROJECT_TYPE_KR[project_type]
            df.at[idx, 'project_subtype'] = self.PROJECT_SUBTYPE_KR[project_subtype]
        
        # 컬럼 타입 명시적 지정
        df = df.astype({
            'fiscal_year': int,
            'region': str,
            'org_type': str,
            'org_level': str,
            'organization': str,
            'department': str,
            'budget_category': str,
            'sub_category': str,
            'project_detail': str,
            'project_type': str,
            'project_subtype': str,
            'budget_amount': float,
            'reference_url': str
        })
        
        return df
    
    def get_filtered_data(self, df: pd.DataFrame, 
                         selected_regions: list = None,
                         selected_types: list = None,
                         budget_range: tuple = None) -> pd.DataFrame:
        """
        필터링된 데이터를 반환합니다.
        
        Args:
            df (pd.DataFrame): 원본 데이터프레임
            selected_regions (list, optional): 선택된 지역 목록
            selected_types (list, optional): 선택된 사업 유형 목록
            budget_range (tuple, optional): 예산 범위 (최소, 최대)
            
        Returns:
            pd.DataFrame: 필터링된 데이터프레임
        """
        filtered_df = df.copy()
        
        # 필터 적용 전 데이터 수
        initial_count = len(filtered_df)
        
        # 지역 필터 적용
        if selected_regions and len(selected_regions) > 0:
            filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
            print(f"지역 필터 적용 후: {len(filtered_df)}건 (선택된 지역: {selected_regions})")
            
        # 사업 유형 필터 적용
        if selected_types and len(selected_types) > 0:
            filtered_df = filtered_df[filtered_df['project_type'].isin(selected_types)]
            print(f"사업 유형 필터 적용 후: {len(filtered_df)}건 (선택된 유형: {selected_types})")
            
        # 예산 범위 필터 적용
        if budget_range and len(budget_range) == 2:
            min_budget, max_budget = budget_range
            filtered_df = filtered_df[
                (filtered_df['budget_amount'] >= min_budget) & 
                (filtered_df['budget_amount'] <= max_budget)
            ]
            print(f"예산 범위 필터 적용 후: {len(filtered_df)}건 (범위: {min_budget:,}원 ~ {max_budget:,}원)")
        
        # 필터 적용 결과 요약
        final_count = len(filtered_df)
        if final_count == 0 and initial_count > 0:
            print("경고: 필터 적용 후 데이터가 없습니다!")
            
        return filtered_df 