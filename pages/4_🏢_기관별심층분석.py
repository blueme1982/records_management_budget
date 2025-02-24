import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from components.charts import (
    StreamlitIntegration, TableStyles,
    BarChart, PieChart
)

# 페이지 설정
st.set_page_config(
    page_title="기관별 심층 분석",
    page_icon="🏢",
    layout="wide"
)

# 차트 설정 초기화
StreamlitIntegration.initialize_chart_settings()

# 사이드바에 차트 설정 추가
with st.sidebar:
    st.subheader("📊 차트 설정")
    
    # 색상 테마 선택
    st.session_state.chart_settings['color_set'] = st.selectbox(
        "색상 테마",
        options=['primary', 'pastel', 'sequential', 'categorical'],
        key="inst_color_set"
    )
    
    # 정렬 기준
    st.session_state.chart_settings['sort_by'] = st.radio(
        "정렬 기준",
        options=['금액', '사업수'],
        key="inst_sort_by"
    )

# 데이터 로드
@st.cache_data
def load_data():
    try:
        current_dir = Path(__file__).parent.parent
        data_path = current_dir / "assets" / "data" / "records_management_budget.csv"
        
        if not data_path.exists():
            st.error(f"데이터 파일을 찾을 수 없습니다: {data_path}")
            st.stop()
            
        df = pd.read_csv(
            data_path,
            dtype={
                'budget_amount': float,
                'region': str,
                'organization': str,
                'org_type': str,
                'project_detail': str,
                'project_type': str,
                'parent_org': str
            },
            thousands=','
        )
        
        # 문자열 컬럼의 공백 제거
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].str.strip()
            
        # '사업없음' 데이터 제외
        df = df[df['project_type'] != '사업없음']
            
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        st.stop()

df = load_data()

# 제목
st.title("🏢 기관별 심층 분석")
st.markdown("---")

# 기관 유형 선택
org_type = st.radio(
    "분석할 기관 유형을 선택하세요",
    options=["지방자치단체", "교육행정기관"],
    horizontal=True
)

if org_type == "지방자치단체":
    # 광역자치단체 목록
    metropolitan_govs = sorted(df[
        (df['org_type'] == '지방자치단체') & 
        (df['parent_org'].notna())
    ]['parent_org'].unique())
    
    # 광역자치단체 선택
    selected_metro = st.selectbox(
        "광역자치단체 선택",
        options=metropolitan_govs
    )
    
    # 선택된 광역자치단체의 기초자치단체 목록
    basic_govs = sorted(df[
        (df['org_type'] == '지방자치단체') & 
        (df['parent_org'] == selected_metro)
    ]['organization'].unique())
    
    # 기초자치단체 선택 (선택사항)
    selected_basic = st.selectbox(
        "기초자치단체 선택 (선택사항)",
        options=["전체"] + basic_govs
    )
    
    # 선택된 기관의 데이터 필터링
    if selected_basic == "전체":
        filtered_df = df[
            (df['org_type'] == '지방자치단체') & 
            (df['parent_org'] == selected_metro)
        ]
        analysis_level = "metro"
    else:
        filtered_df = df[
            (df['org_type'] == '지방자치단체') & 
            (df['organization'] == selected_basic)
        ]
        analysis_level = "basic"
    
else:  # 교육행정기관
    # 시도교육청 목록
    edu_offices = sorted(df[
        (df['org_type'] == '교육행정기관') & 
        (df['parent_org'].notna())
    ]['parent_org'].unique())
    
    # 시도교육청 선택
    selected_edu = st.selectbox(
        "시도교육청 선택",
        options=edu_offices
    )
    
    # 선택된 시도교육청의 교육지원청 목록
    support_offices = sorted(df[
        (df['org_type'] == '교육행정기관') & 
        (df['parent_org'] == selected_edu)
    ]['organization'].unique())
    
    # 교육지원청 선택 (선택사항)
    selected_support = st.selectbox(
        "교육지원청 선택 (선택사항)",
        options=["전체"] + support_offices
    )
    
    # 선택된 기관의 데이터 필터링
    if selected_support == "전체":
        filtered_df = df[
            (df['org_type'] == '교육행정기관') & 
            (df['parent_org'] == selected_edu)
        ]
        analysis_level = "edu"
    else:
        filtered_df = df[
            (df['org_type'] == '교육행정기관') & 
            (df['organization'] == selected_support)
        ]
        analysis_level = "support"

# 1. 기관 개요
st.header("1. 기관 개요")

# 주요 지표 계산
total_budget = filtered_df['budget_amount'].sum()
total_projects = len(filtered_df)
avg_budget = total_budget / total_projects if total_projects > 0 else 0
total_orgs = filtered_df['organization'].nunique()

# 주요 지표 표시
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "총 예산 규모",
        f"₩{total_budget:,.0f}",
        help="전체 예산 규모"
    )

with col2:
    st.metric(
        "총 사업 수",
        f"{total_projects:,}개",
        help="전체 사업 건수"
    )

with col3:
    st.metric(
        "평균 사업 규모",
        f"₩{avg_budget:,.0f}",
        help="사업당 평균 예산"
    )

with col4:
    if analysis_level in ["metro", "edu"]:
        st.metric(
            "소속 기관 수",
            f"{total_orgs:,}개",
            help="소속된 기초/지원 기관 수"
        )
    else:
        st.metric(
            "소속 상급기관",
            selected_metro if org_type == "지방자치단체" else selected_edu,
            help="소속된 상급기관명"
        )

# 2. 예산 현황
st.header("2. 예산 현황")

# 사업 유형별 예산 분석
type_summary = filtered_df.groupby('project_type').agg({
    'budget_amount': ['sum', 'mean', 'count']
}).reset_index()

type_summary.columns = ['사업유형', '총예산액', '평균예산액', '사업수']

# 정렬 적용
if st.session_state.chart_settings['sort_by'] == '금액':
    type_summary = type_summary.sort_values('총예산액', ascending=False)
else:
    type_summary = type_summary.sort_values('사업수', ascending=False)

# 시각화
col1, col2 = st.columns(2)

with col1:
    # 예산 분포 도넛 차트
    fig_budget = PieChart.create_donut(
        df=type_summary,
        values='총예산액',
        names='사업유형',
        title='사업 유형별 예산 분포',
        color_set=st.session_state.chart_settings['color_set']
    )
    st.plotly_chart(fig_budget, use_container_width=True)

with col2:
    # 사업 수 분포 도넛 차트
    fig_projects = PieChart.create_donut(
        df=type_summary,
        values='사업수',
        names='사업유형',
        title='사업 유형별 사업 수 분포',
        color_set=st.session_state.chart_settings['color_set']
    )
    st.plotly_chart(fig_projects, use_container_width=True)

# 3. 예산 규모별 분석
st.header("3. 예산 규모별 분석")

# 예산 구간 정의
budget_ranges = [
    (0, 5000000, '500만원 미만'),
    (5000000, 10000000, '500만원~1천만원'),
    (10000000, 30000000, '1천만원~3천만원'),
    (30000000, 50000000, '3천만원~5천만원'),
    (50000000, 100000000, '5천만원~1억원'),
    (100000000, 300000000, '1억원~3억원'),
    (300000000, 500000000, '3억원~5억원'),
    (500000000, 1000000000, '5억원~10억원'),
    (1000000000, float('inf'), '10억원 이상')
]

# 예산 구간별 데이터 집계
budget_dist = []
for start, end, label in budget_ranges:
    count = len(filtered_df[(filtered_df['budget_amount'] >= start) & (filtered_df['budget_amount'] < end)])
    total = filtered_df[(filtered_df['budget_amount'] >= start) & (filtered_df['budget_amount'] < end)]['budget_amount'].sum()
    budget_dist.append({
        '예산 구간': label,
        '사업 수': count,
        '총 예산': total
    })

budget_dist_df = pd.DataFrame(budget_dist)

col1, col2 = st.columns(2)

with col1:
    # 구간별 사업 수 막대 그래프
    fig_count = BarChart.create_basic_bar(
        df=budget_dist_df,
        x='예산 구간',
        y='사업 수',
        title='예산 구간별 사업 수 분포',
        text=budget_dist_df['사업 수'].apply(lambda x: f'{x}개'),
        color_set=st.session_state.chart_settings['color_set']
    )
    st.plotly_chart(fig_count, use_container_width=True)

with col2:
    # 구간별 예산 비중 도넛 차트
    fig_budget_dist = PieChart.create_donut(
        df=budget_dist_df,
        values='총 예산',
        names='예산 구간',
        title='예산 구간별 예산 비중',
        color_set=st.session_state.chart_settings['color_set']
    )
    st.plotly_chart(fig_budget_dist, use_container_width=True)

# 4. 상세 데이터
st.header("4. 상세 데이터")

# 표시할 컬럼 설정
if analysis_level in ["metro", "edu"]:
    columns_to_show = {
        'organization': '기관명',
        'project_type': '사업유형',
        'project_detail': '사업내용',
        'budget_amount': '예산금액'
    }
else:
    columns_to_show = {
        'project_type': '사업유형',
        'project_detail': '사업내용',
        'budget_amount': '예산금액'
    }

# 데이터 테이블 표시
st.dataframe(
    filtered_df[columns_to_show.keys()].rename(columns=columns_to_show),
    column_config=TableStyles.get_column_config(columns_to_show),
    use_container_width=True,
    hide_index=True
)

# 데이터 다운로드 버튼
csv = filtered_df[columns_to_show.keys()].to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 데이터 다운로드",
    data=csv,
    file_name="institution_analysis.csv",
    mime="text/csv"
)
