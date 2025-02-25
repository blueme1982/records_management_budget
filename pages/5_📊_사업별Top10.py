import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from components.charts import (
    StreamlitIntegration, TableStyles,
    BarChart
)

# 페이지 설정
st.set_page_config(
    page_title="사업별 Top 10",
    page_icon="📊",
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
        key="top10_color_set"
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
st.title("📊 사업별 Top 10 기관")
st.markdown("---")

# 사업 유형 순서 정의
project_types = [
    '전자화 사업',
    '기록물관리',
    '특수사업',
    '시스템 관리',
    '보존관리'
]

# 탭 생성
tabs = st.tabs([f"📈 {project_type}" for project_type in project_types])

# 각 탭에 대한 내용 생성
for tab, project_type in zip(tabs, project_types):
    with tab:
        # 해당 사업 유형의 기관별 총 예산 계산
        top10_orgs = df[df['project_type'] == project_type].groupby('organization').agg({
            'budget_amount': 'sum',
            'org_type': 'first',
            'parent_org': 'first',
            'project_detail': lambda x: ', '.join(set(x))  # 중복 제거하여 모든 프로젝트 상세 내용 결합
        }).reset_index()
        
        # 예산액 기준 상위 10개 기관 선택
        top10_orgs = top10_orgs.nlargest(10, 'budget_amount')
        
        # 기관명에 상급기관 정보 추가
        top10_orgs['organization_full'] = top10_orgs.apply(
            lambda x: f"{x['organization']} ({x['parent_org']})" if pd.notna(x['parent_org']) else x['organization'],
            axis=1
        )
        
        # 1. 주요 지표
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_budget = top10_orgs['budget_amount'].sum()
            st.metric(
                "Top 10 총 예산",
                f"₩{total_budget:,.0f}",
                help="상위 10개 기관의 총 예산 규모"
            )
            
        with col2:
            avg_budget = total_budget / len(top10_orgs)
            st.metric(
                "Top 10 평균 예산",
                f"₩{avg_budget:,.0f}",
                help="상위 10개 기관의 평균 예산 규모"
            )
            
        with col3:
            max_budget = top10_orgs['budget_amount'].max()
            st.metric(
                "최고 예산",
                f"₩{max_budget:,.0f}",
                help="1위 기관의 예산 규모"
            )
        
        st.markdown("---")
        
        # 2. 막대 그래프
        st.subheader("📊 예산 규모 순위")
        
        fig = BarChart.create_basic_bar(
            df=top10_orgs,
            x='organization_full',
            y='budget_amount',
            title=f'{project_type} 예산 규모 상위 10개 기관',
            text=top10_orgs['budget_amount'].apply(lambda x: f'₩{x:,.0f}'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='budget'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. 상세 데이터 테이블
        st.subheader("📋 상세 현황")
        
        # 테이블용 데이터 준비
        table_data = top10_orgs.copy()
        table_data['순위'] = range(1, len(table_data) + 1)
        table_data = table_data[[
            '순위', 'organization', 'parent_org', 'org_type', 'project_detail', 'budget_amount'
        ]].rename(columns={
            'organization': '기관명',
            'parent_org': '상급기관',
            'org_type': '기관유형',
            'project_detail': '사업내용',
            'budget_amount': '예산액'
        })
        
        # 테이블 표시
        st.dataframe(
            table_data,
            column_config=TableStyles.get_column_config({
                "순위": "순위",
                "기관명": "기관명",
                "상급기관": "상급기관",
                "기관유형": "기관 유형",
                "사업내용": "사업 내용",
                "예산액": "예산액"
            }),
            use_container_width=True,
            hide_index=True
        )

# 페이지 하단에 설명 추가
st.markdown("---")
st.markdown("""
### 📝 참고사항

- 각 사업 유형별로 예산 규모가 가장 큰 상위 10개 기관을 보여줍니다.
- 기관명 옆의 괄호는 해당 기관의 상급기관을 나타냅니다.
- 광역자치단체의 경우 상급기관 정보가 표시되지 않습니다.
- 예산액은 해당 사업 유형에 대한 기관의 총 예산을 의미합니다.
""")

# 페이지 하단에 업데이트 정보 추가
st.caption("마지막 업데이트: 2024-02-21") 