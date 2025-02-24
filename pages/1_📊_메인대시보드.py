import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="메인 대시보드",
    page_icon="📊",
    layout="wide"
)

# 개발을 위해 임시로 로그인 상태 True로 설정
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True

# 데이터 로드
@st.cache_data
def load_data():
    try:
        # 현재 파일의 디렉토리 경로
        current_dir = Path(__file__).parent.parent
        
        # 데이터 파일 경로
        data_path = current_dir / "assets" / "data" / "records_management_budget.csv"
        
        if not data_path.exists():
            st.error(f"데이터 파일을 찾을 수 없습니다: {data_path}")
            st.stop()
            
        # 데이터 타입 지정하여 로드
        df = pd.read_csv(
            data_path,
            dtype={
                'budget_amount': float,  # 예산 금액은 float로 지정
                'region': str,
                'organization': str,
                'org_type': str,
                'project_detail': str,
                'project_type': str
            },
            thousands=','  # 천단위 구분자 처리
        )
        
        # 문자열 컬럼의 공백 제거
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].str.strip()
            
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        st.info("관리자에게 문의하세요.")
        st.stop()

df = load_data()

# 제목
st.title("📊 기록물관리 사업 메인 대시보드")
st.markdown("---")

# 1. 핵심 지표 (Key Metrics)
st.header("1. 핵심 지표")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_budget = df['budget_amount'].sum()
    st.metric("총 예산 규모", f"{total_budget:,.0f}원")

with col2:
    total_projects = len(df)
    st.metric("총 사업 수", f"{total_projects:,}개")

with col3:
    total_orgs = df['organization'].nunique()
    local_govs = df[df['org_type'] == '지방자치단체']['organization'].nunique()
    edu_orgs = df[df['org_type'] == '교육행정기관']['organization'].nunique()
    st.metric("참여 기관 수", f"{total_orgs:,}개", f"지자체 {local_govs}개 / 교육청 {edu_orgs}개")

with col4:
    avg_project = total_budget / total_projects
    st.metric("평균 사업 규모", f"{avg_project:,.0f}원")

with col5:
    total_regions = df['region'].nunique()
    st.metric("참여 지역 수", f"{total_regions:,}개")

st.markdown("---")

# 2. 기관 유형별 분석
st.header("2. 기관 유형별 분석")

# 2.1 광역자치단체 현황
st.subheader("2.1 광역자치단체 현황")

# 광역자치단체 목록 정의
metropolitan_govs = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시',
    '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
    '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도',
    '전라남도', '경상북도', '경상남도', '제주특별자치도'
]

# 차트 컴포넌트를 사용하여 시각화 생성
from components.charts import OrganizationCharts, TableStyles
gov_summary, fig_gov_budget, fig_gov_projects = OrganizationCharts.create_gov_summary(df, metropolitan_govs)

# 광역자치단체 예산 및 사업 수 시각화
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_gov_budget, use_container_width=True)

with col2:
    st.plotly_chart(fig_gov_projects, use_container_width=True)

# 광역자치단체 데이터 테이블 표시
st.markdown("##### 광역자치단체별 상세 현황")
st.dataframe(
    gov_summary,
    column_config=TableStyles.get_column_config({
        "지역": "광역자치단체",
        "예산액": "예산액",
        "사업수": "사업 수"
    }),
    use_container_width=True,
    hide_index=True
)

# 2.2 시도교육청 현황
st.subheader("2.2 시도교육청 현황")

# 광역교육청 목록 정의
metropolitan_edu_offices = [
    '서울특별시교육청', '부산광역시교육청', '대구광역시교육청', 
    '인천광역시교육청', '광주광역시교육청', '대전광역시교육청',
    '울산광역시교육청', '세종특별자치시교육청', '경기도교육청',
    '강원특별자치도교육청', '충청북도교육청', '충청남도교육청',
    '전북특별자치도교육청', '전라남도교육청', '경상북도교육청',
    '경상남도교육청', '제주특별자치도교육청'
]

# 차트 컴포넌트를 사용하여 시각화 생성
edu_summary, fig_edu_budget, fig_edu_projects = OrganizationCharts.create_edu_summary(df, metropolitan_edu_offices)

# 교육청 예산 및 사업 수 시각화
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_edu_budget, use_container_width=True)

with col2:
    st.plotly_chart(fig_edu_projects, use_container_width=True)

# 교육청 데이터 테이블 표시
st.markdown("##### 시도교육청별 상세 현황")
st.dataframe(
    edu_summary,
    column_config=TableStyles.get_column_config({
        "교육청": "시도교육청",
        "예산액": "예산액",
        "사업수": "사업 수"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# 3. 사업 유형별 분석
st.header("3. 사업 유형별 분석")

# 사업 유형 매핑 (한글 -> 한글, 표시용)
type_mapping = {
    '전자화 사업': '디지털화 사업',
    '기록물관리': '기록물관리',
    '특수사업': '특수사업',
    '시스템 관리': '시스템 관리',
    '보존관리': '보존관리'
}

# 차트 컴포넌트를 사용하여 시각화 생성
from components.charts import ProjectTypeCharts, BudgetRangeCharts

# 데이터 테이블 설정
column_config = {
    "사업유형": "사업 유형",
    "총예산액": "총 예산 금액",
    "사업수": "총 사업 수",
    "예산비중": "예산 비중"
}

# 사업 유형별 분석 차트 생성
type_summary, fig_budget, fig_ratio, fig_count = ProjectTypeCharts.create_summary(df, type_mapping)

# 데이터 테이블 표시
st.markdown("##### 5대 사업 유형 현황")
st.dataframe(
    type_summary,
    column_config=TableStyles.get_column_config(column_config),
    use_container_width=True,
    hide_index=True
)

# 시각화 표시
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_budget, use_container_width=True)

with col2:
    st.plotly_chart(fig_ratio, use_container_width=True)

st.plotly_chart(fig_count, use_container_width=True)

st.markdown("---")

# 4. 예산 규모별 분석
st.header("4. 예산 규모별 분석")

# 예산 구간 정의
budget_ranges = [
    (0, 10000000, '1천만원 미만'),
    (10000000, 50000000, '1천만원~5천만원'),
    (50000000, 100000000, '5천만원~1억원'),
    (100000000, 500000000, '1억원~5억원'),
    (500000000, float('inf'), '5억원 이상')
]

# 차트 컴포넌트를 사용하여 시각화 생성
budget_dist_df, fig_budget_dist, fig_budget_amount = BudgetRangeCharts.create_summary(df, budget_ranges)

# 예산 구간별 시각화
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_budget_dist, use_container_width=True)

with col2:
    st.plotly_chart(fig_budget_amount, use_container_width=True)

st.markdown("---")

# 5. 데이터 조회
st.header("5. 데이터 조회")

# 표시할 컬럼 설정
columns_to_show = {
    'region': '지역',
    'organization': '기관명',
    'org_type': '기관유형',
    'project_detail': '사업내용',
    'project_type': '사업유형',
    'budget_amount': '예산금액'
}

# 데이터 테이블 표시
st.dataframe(
    df[columns_to_show.keys()].rename(columns=columns_to_show),
    column_config=TableStyles.get_column_config(columns_to_show),
    use_container_width=True,
    hide_index=True
)

# 데이터 다운로드 버튼
csv = df[columns_to_show.keys()].to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 데이터 다운로드",
    data=csv,
    file_name="records_management_budget.csv",
    mime="text/csv"
) 