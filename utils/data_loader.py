import pandas as pd
import numpy as np
import streamlit as st
import os
import re
from src.config.config import DATA_PATH

def categorize_budget(amount):
    """예산 규모를 카테고리로 분류"""
    if amount < 50_000_000:  # 5천만원 미만
        return '소규모'
    elif amount < 500_000_000:  # 5억원 미만
        return '중규모'
    else:
        return '대규모'

def categorize_project(detail):
    """사업 유형 분류"""
    detail = str(detail).lower()
    
    # 시스템 관련 사업
    if any(keyword in detail for keyword in ['ismp', '차세대', '시스템 구축', '시스템 개발']):
        return '시스템 구축/개발'
    elif any(keyword in detail for keyword in ['유지보수', '운영', '통합기록관리시스템']):
        return '시스템 운영'
    elif any(keyword in detail for keyword in ['s/w', '소프트웨어', '안티바이러스']):
        return '소프트웨어'
    
    # 기록물 디지털화 사업
    elif any(keyword in detail for keyword in ['전산화', 'db구축', '디지털화', '전자화']):
        return '기록물 디지털화'
    elif any(keyword in detail for keyword in ['멀티미디어', '시청각']):
        return '멀티미디어'
    
    # 기록물 관리 사업
    elif any(keyword in detail for keyword in ['정리', '이관', '인수', '검수']):
        return '정리/이관'
    elif any(keyword in detail for keyword in ['복원', '보존', '보관']):
        return '보존/복원'
    elif any(keyword in detail for keyword in ['분류', '기술', '검색', '공개재분류']):
        return '분류/기술'
    
    # 시설/환경 관리
    elif any(keyword in detail for keyword in ['소독', '방역', '항균', '환경']):
        return '시설/환경'
    
    return '기타'

def categorize_department(dept):
    """부서 분류"""
    # NaN 값이나 숫자 처리
    if pd.isna(dept) or not isinstance(dept, str):
        return '미상'
    
    dept = str(dept).lower()
    if any(keyword in dept for keyword in ['정보', '디지털', '전산']):
        return '정보화'
    elif any(keyword in dept for keyword in ['기록원', '기록관']):
        return '기록관리'
    else:
        return '행정'

def standardize_org_type(row):
    """기관유형과 등급을 결합하여 표준화"""
    org_type = row['기관유형']
    org_grade = row['기관등급']
    
    if pd.isna(org_type) or pd.isna(org_grade):
        return '미상'
    
    if org_type == '지방자치단체':
        if org_grade == '광역':
            return '광역자치단체'
        elif org_grade == '기초':
            return '기초자치단체'
    elif org_type == '교육행정기관':
        if org_grade == '광역':
            return '시도교육청'
        elif org_grade == '기초':
            return '지역교육지원청'
    
    return '기타'

def extract_year_from_filename(filepath):
    """파일명에서 연도 추출"""
    # 파일명에서 숫자 4자리 추출 (예: budget_2025.csv -> 2025)
    year_match = re.search(r'(\d{4})', os.path.basename(filepath))
    if year_match:
        return int(year_match.group(1))
    return None

def load_multiple_years_data(data_paths):
    """여러 연도의 데이터를 로드하고 병합"""
    dfs = []
    for path in data_paths:
        df = pd.read_csv(path)
        year = extract_year_from_filename(path)
        if year:
            df['연도'] = year
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    try:
        # 데이터 파일 존재 여부 확인
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
        
        # 데이터 로드
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
        
        # 필수 컬럼 확인
        required_columns = ['연도', '지역', '기관', '부서', '항목1', '항목2', '상세', '금액']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")
        
        # 데이터 전처리
        df['금액'] = pd.to_numeric(df['금액'].astype(str).str.replace(',', ''), errors='coerce')
        df['예산규모'] = df['금액'].apply(categorize_budget)
        df['사업유형'] = df['상세'].apply(categorize_project)
        df['부서유형'] = df['부서'].apply(categorize_department)
        df['기관구분'] = df.apply(standardize_org_type, axis=1)
        
        # 결측치 처리
        df = df.fillna({
            '연도': df['연도'].mode()[0],
            '지역': '기타',
            '기관': '미상',
            '부서': '미상',
            '항목1': '기타',
            '항목2': '기타',
            '상세': '상세내용없음',
            '금액': 0
        })
        
        return df
        
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        return None

def filter_data(df, region='전체', budget_range=None, org_type=None, 
                project_type=None, dept_type=None, exclude_outliers=False,
                year=None):
    """
    데이터를 필터링하는 함수
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        region (str): 선택된 지역 (기본값: '전체')
        budget_range (tuple): 예산 범위 (min, max)
        org_type (str): 기관구분
        project_type (str): 사업유형
        dept_type (str): 부서유형
        exclude_outliers (bool): 이상치 제외 여부
        year (int): 선택된 연도
    
    Returns:
        pd.DataFrame: 필터링된 데이터프레임
    """
    # 기본 필터
    if budget_range:
        mask = (df['금액'] >= budget_range[0]) & (df['금액'] <= budget_range[1])
        if region != '전체':
            mask &= (df['지역'] == region)
        df_filtered = df[mask]
    elif region != '전체':
        df_filtered = df[df['지역'] == region]
    else:
        df_filtered = df.copy()
    
    # 연도 필터
    if year:
        df_filtered = df_filtered[df_filtered['연도'] == year]
    
    # 추가 필터
    if org_type:
        df_filtered = df_filtered[df_filtered['기관구분'] == org_type]
    if project_type:
        df_filtered = df_filtered[df_filtered['사업유형'] == project_type]
    if dept_type:
        df_filtered = df_filtered[df_filtered['부서유형'] == dept_type]
    if exclude_outliers:
        df_filtered = df_filtered[~df_filtered['이상치여부']]
    
    return df_filtered 