import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from components.charts import (
    StreamlitIntegration, OrganizationCharts,
    TableStyles, BarChart, PieChart
)

def get_top_project_type_by_budget(data: pd.DataFrame) -> str:
    """예산액 기준으로 가장 큰 비중을 차지하는 사업 유형을 반환합니다."""
    type_budget = data.groupby('project_type')['budget_amount'].sum()
    return type_budget.idxmax() if not type_budget.empty else "N/A"

# 페이지 설정
st.set_page_config(
    page_title="기관유형별 분석",
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
        key="org_color_set"
    )
    
    # 정렬 기준
    st.session_state.chart_settings['sort_by'] = st.radio(
        "정렬 기준",
        options=['금액', '사업수'],
        key="org_sort_by"
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
            
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        st.stop()

df = load_data()

# 제목
st.title("🏢 기관유형별 분석")
st.markdown("---")

# 1. 기관 유형 개요
st.header("1. 기관 유형 개요")

# 기관 유형별 주요 지표 계산
org_type_summary = df.groupby('org_type').agg({
    'budget_amount': ['sum', 'mean', 'count'],
    'organization': 'nunique',
    'project_type': lambda x: x.value_counts().index[0]
}).reset_index()

org_type_summary.columns = [
    '기관유형', '총예산액', '평균예산액', '사업수', '기관수', '주요사업유형'
]

# 주요 지표 표시
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orgs = org_type_summary['기관수'].sum()
    st.metric(
        "총 기관 수",
        f"{total_orgs:,}개",
        help="전체 참여 기관 수"
    )

with col2:
    total_budget = org_type_summary['총예산액'].sum()
    st.metric(
        "총 예산 규모",
        f"₩{total_budget:,.0f}",
        help="전체 기관의 총 예산 규모"
    )

with col3:
    avg_budget = total_budget / total_orgs
    st.metric(
        "기관당 평균 예산",
        f"₩{avg_budget:,.0f}",
        help="기관당 평균 예산 규모"
    )

with col4:
    total_projects = org_type_summary['사업수'].sum()
    st.metric(
        "총 사업 수",
        f"{total_projects:,}개",
        help="전체 사업 건수"
    )

# 기관 유형별 현황 테이블
st.markdown("##### 기관 유형별 총괄 현황")
st.dataframe(
    org_type_summary,
    column_config=TableStyles.get_column_config({
        "기관유형": "기관 유형",
        "총예산액": "총 예산액",
        "평균예산액": "평균 예산액",
        "사업수": "사업 수",
        "기관수": "기관 수",
        "주요사업유형": "주요 사업 유형"
    }),
    use_container_width=True,
    hide_index=True
)

# 기관 유형별 분포 시각화
col1, col2 = st.columns(2)

with col1:
    # 예산 분포 도넛 차트
    fig_budget = PieChart.create_donut(
        df=org_type_summary,
        values='총예산액',
        names='기관유형',
        title='기관 유형별 예산 분포',
        color_set=st.session_state.chart_settings['color_set']
    )
    st.plotly_chart(fig_budget, use_container_width=True)

with col2:
    # 사업 수 분포 도넛 차트
    fig_projects = PieChart.create_donut(
        df=org_type_summary,
        values='사업수',
        names='기관유형',
        title='기관 유형별 사업 수 분포',
        color_set=st.session_state.chart_settings['color_set']
    )
    st.plotly_chart(fig_projects, use_container_width=True)

st.markdown("---")

# 2. 지방자치단체 분석
st.header("2. 상급기관별 분석")

# 2.1 전체 현황
st.subheader("2.1 상급기관 전체 현황")

# 탭 생성
gov_tab_all, edu_tab_all = st.tabs(["광역자치단체 현황", "시도교육청 현황"])

with gov_tab_all:
    # 광역자치단체 데이터 필터링
    local_gov_df = df[df['org_type'] == '지방자치단체'].copy()

    # 광역별 예산 및 사업 현황
    gov_summary = local_gov_df.groupby('parent_org').agg({
        'budget_amount': ['sum', 'mean', 'count'],
        'project_type': lambda x: get_top_project_type_by_budget(pd.DataFrame({'project_type': x, 'budget_amount': local_gov_df.loc[x.index, 'budget_amount']}))
    }).reset_index()

    gov_summary.columns = ['광역자치단체', '총예산액', '평균예산액', '사업수', '주요사업유형']

    # 주요사업유형에 예산 비중 추가
    for idx, row in gov_summary.iterrows():
        org_data = local_gov_df[local_gov_df['parent_org'] == row['광역자치단체']]
        type_budget = org_data[org_data['project_type'] == row['주요사업유형']]['budget_amount'].sum()
        total_budget = org_data['budget_amount'].sum()
        budget_ratio = (type_budget / total_budget * 100) if total_budget > 0 else 0
        gov_summary.at[idx, '주요사업유형'] = f"{row['주요사업유형']} ({budget_ratio:.1f}%)"

    # 데이터 테이블 표시
    st.markdown("##### 광역자치단체별 상세 현황")
    st.dataframe(
        gov_summary,
        column_config=TableStyles.get_column_config({
            "광역자치단체": "광역자치단체",
            "총예산액": "총 예산액",
            "평균예산액": "평균 예산액",
            "사업수": "사업 수",
            "주요사업유형": "주요 사업 유형"
        }),
        use_container_width=True,
        hide_index=True
    )

    # 시각화
    col1, col2 = st.columns(2)

    with col1:
        # 예산 규모 막대 그래프
        fig_budget = BarChart.create_basic_bar(
            df=gov_summary,
            x='광역자치단체',
            y='총예산액',
            title='광역자치단체별 예산 규모',
            text=gov_summary['총예산액'].apply(lambda x: f'₩{x:,.0f}'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='budget'
        )
        st.plotly_chart(fig_budget, use_container_width=True)

    with col2:
        # 사업 수 막대 그래프
        fig_projects = BarChart.create_basic_bar(
            df=gov_summary,
            x='광역자치단체',
            y='사업수',
            title='광역자치단체별 사업 수',
            text=gov_summary['사업수'].apply(lambda x: f'{x}개'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='count'
        )
        st.plotly_chart(fig_projects, use_container_width=True)

with edu_tab_all:
    # 교육청 데이터 준비
    edu_df = df[df['org_type'] == '교육행정기관'].copy()
    
    # 교육청별 예산 및 사업 현황
    edu_summary = edu_df.groupby('parent_org').agg({
        'budget_amount': ['sum', 'mean', 'count'],
        'project_type': lambda x: get_top_project_type_by_budget(pd.DataFrame({'project_type': x, 'budget_amount': edu_df.loc[x.index, 'budget_amount']}))
    }).reset_index()
    
    edu_summary.columns = ['교육청', '총예산액', '평균예산액', '사업수', '주요사업유형']
    
    # 주요사업유형에 예산 비중 추가
    for idx, row in edu_summary.iterrows():
        org_data = edu_df[edu_df['parent_org'] == row['교육청']]
        type_budget = org_data[org_data['project_type'] == row['주요사업유형']]['budget_amount'].sum()
        total_budget = org_data['budget_amount'].sum()
        budget_ratio = (type_budget / total_budget * 100) if total_budget > 0 else 0
        edu_summary.at[idx, '주요사업유형'] = f"{row['주요사업유형']} ({budget_ratio:.1f}%)"

    # 데이터 테이블 표시
    st.markdown("##### 시도교육청별 상세 현황")
    st.dataframe(
        edu_summary,
        column_config=TableStyles.get_column_config({
            "교육청": "시도교육청",
            "총예산액": "총 예산액",
            "평균예산액": "평균 예산액",
            "사업수": "사업 수",
            "주요사업유형": "주요 사업 유형"
        }),
        use_container_width=True,
        hide_index=True
    )

    # 시각화
    col1, col2 = st.columns(2)

    with col1:
        # 예산 규모 막대 그래프
        fig_budget = BarChart.create_basic_bar(
            df=edu_summary,
            x='교육청',
            y='총예산액',
            title='시도교육청별 예산 규모',
            text=edu_summary['총예산액'].apply(lambda x: f'₩{x:,.0f}'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='budget'
        )
        st.plotly_chart(fig_budget, use_container_width=True)

    with col2:
        # 사업 수 막대 그래프
        fig_projects = BarChart.create_basic_bar(
            df=edu_summary,
            x='교육청',
            y='사업수',
            title='시도교육청별 사업 수',
            text=edu_summary['사업수'].apply(lambda x: f'{x}개'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='count'
        )
        st.plotly_chart(fig_projects, use_container_width=True)

# 2.2 기관간 비교 분석
st.subheader("2.2 상급기관간 비교 분석")

# 광역자치단체 목록
metropolitan_govs = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시',
    '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
    '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도',
    '전라남도', '경상북도', '경상남도', '제주특별자치도'
]

# 탭 생성
gov_tab, edu_tab = st.tabs(["광역자치단체 비교", "시도교육청 비교"])

with gov_tab:
    # 비교할 광역자치단체 선택
    selected_govs = st.multiselect(
        "비교할 광역자치단체 선택 (2~4개 권장)",
        options=metropolitan_govs,
        default=metropolitan_govs[:3]  # 기본값으로 처음 3개 선택
    )
    
    if len(selected_govs) > 1:
        # 선택된 광역자치단체 데이터 필터링
        compare_gov_df = gov_summary[gov_summary['광역자치단체'].isin(selected_govs)].copy()
        
        # 1. 예산 규모 비교
        st.markdown("##### 예산 규모 비교")
        fig_budget_compare = BarChart.create_basic_bar(
            df=compare_gov_df,
            x='광역자치단체',
            y='총예산액',
            title='광역자치단체별 예산 규모 비교',
            text=compare_gov_df['총예산액'].apply(lambda x: f'₩{x:,.0f}'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='budget'
        )
        st.plotly_chart(fig_budget_compare, use_container_width=True)
        
        # 2. 사업 현황 비교
        st.markdown("##### 사업 현황 비교")
        col1, col2 = st.columns(2)
        
        with col1:
            # 평균 사업 규모 비교
            fig_avg_compare = BarChart.create_basic_bar(
                df=compare_gov_df,
                x='광역자치단체',
                y='평균예산액',
                title='평균 사업 규모 비교',
                text=compare_gov_df['평균예산액'].apply(lambda x: f'₩{x:,.0f}'),
                color_set=st.session_state.chart_settings['color_set']
            )
            st.plotly_chart(fig_avg_compare, use_container_width=True)
        
        with col2:
            # 사업 수 비교
            fig_count_compare = BarChart.create_basic_bar(
                df=compare_gov_df,
                x='광역자치단체',
                y='사업수',
                title='총 사업 수 비교',
                text=compare_gov_df['사업수'].apply(lambda x: f'{x}개'),
                color_set=st.session_state.chart_settings['color_set'],
                hover_mode='count'
            )
            st.plotly_chart(fig_count_compare, use_container_width=True)
        
        # 3. 상세 비교 테이블
        st.markdown("##### 상세 비교")
        st.dataframe(
            compare_gov_df,
            column_config=TableStyles.get_column_config({
                "광역자치단체": "광역자치단체",
                "총예산액": "총 예산액",
                "평균예산액": "평균 예산액",
                "사업수": "사업 수",
                "주요사업유형": "주요 사업 유형"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("비교 분석을 위해 2개 이상의 광역자치단체를 선택해주세요.")

with edu_tab:
    # 비교할 교육청 선택
    selected_edus = st.multiselect(
        "비교할 시도교육청 선택 (2~4개 권장)",
        options=edu_summary['교육청'].tolist(),
        default=edu_summary['교육청'].tolist()[:3]  # 기본값으로 처음 3개 선택
    )
    
    if len(selected_edus) > 1:
        # 선택된 교육청 데이터 필터링
        compare_edu_df = edu_summary[edu_summary['교육청'].isin(selected_edus)].copy()
        
        # 1. 예산 규모 비교
        st.markdown("##### 예산 규모 비교")
        fig_budget_compare = BarChart.create_basic_bar(
            df=compare_edu_df,
            x='교육청',
            y='총예산액',
            title='시도교육청별 예산 규모 비교',
            text=compare_edu_df['총예산액'].apply(lambda x: f'₩{x:,.0f}'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='budget'
        )
        st.plotly_chart(fig_budget_compare, use_container_width=True)
        
        # 2. 사업 현황 비교
        st.markdown("##### 사업 현황 비교")
        col1, col2 = st.columns(2)
        
        with col1:
            # 평균 사업 규모 비교
            fig_avg_compare = BarChart.create_basic_bar(
                df=compare_edu_df,
                x='교육청',
                y='평균예산액',
                title='평균 사업 규모 비교',
                text=compare_edu_df['평균예산액'].apply(lambda x: f'₩{x:,.0f}'),
                color_set=st.session_state.chart_settings['color_set']
            )
            st.plotly_chart(fig_avg_compare, use_container_width=True)
        
        with col2:
            # 사업 수 비교
            fig_count_compare = BarChart.create_basic_bar(
                df=compare_edu_df,
                x='교육청',
                y='사업수',
                title='총 사업 수 비교',
                text=compare_edu_df['사업수'].apply(lambda x: f'{x}개'),
                color_set=st.session_state.chart_settings['color_set'],
                hover_mode='count'
            )
            st.plotly_chart(fig_count_compare, use_container_width=True)
        
        # 3. 상세 비교 테이블
        st.markdown("##### 상세 비교")
        st.dataframe(
            compare_edu_df,
            column_config=TableStyles.get_column_config({
                "교육청": "시도교육청",
                "총예산액": "총 예산액",
                "평균예산액": "평균 예산액",
                "사업수": "사업 수",
                "주요사업유형": "주요 사업 유형"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("비교 분석을 위해 2개 이상의 시도교육청을 선택해주세요.")
