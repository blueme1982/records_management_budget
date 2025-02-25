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
    page_title="사업 유형별 분석",
    page_icon="📈",
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
        key="project_color_set"
    )
    
    # 정렬 기준
    st.session_state.chart_settings['sort_by'] = st.radio(
        "정렬 기준",
        options=['금액', '사업수'],
        key="project_sort_by"
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
st.title("📈 사업 유형별 분석")
st.markdown("---")

# 1. 사업 유형 개요
st.header("1. 사업 유형 개요")

# 핵심 지표 계산
total_types = df['project_type'].nunique()
total_budget = df['budget_amount'].sum()
avg_project = df['budget_amount'].mean()
total_projects = len(df)

# 핵심 지표 표시
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "총 사업 유형 수",
        f"{total_types:,}개",
        help="전체 사업 유형의 수"
    )

with col2:
    st.metric(
        "전체 예산 규모",
        f"₩{total_budget:,.1f}",
        help="전체 사업의 총 예산 규모"
    )

with col3:
    st.metric(
        "평균 사업 규모",
        f"₩{avg_project:,.1f}",
        help="사업당 평균 예산 규모"
    )

with col4:
    st.metric(
        "총 사업 건수",
        f"{total_projects:,}개",
        help="전체 사업 건수"
    )

# 사업 유형별 총괄 현황
type_summary = df.groupby('project_type').agg({
    'budget_amount': ['sum', 'mean', 'count'],
    'organization': 'nunique',
    'parent_org': lambda x: x.value_counts().index[0]
}).reset_index()

type_summary.columns = [
    '사업유형', '총예산액', '평균예산액', '사업수', '수행기관수', '주요수행기관'
]

# 정렬 적용
if st.session_state.chart_settings['sort_by'] == '금액':
    type_summary = type_summary.sort_values('총예산액', ascending=False)
else:
    type_summary = type_summary.sort_values('사업수', ascending=False)

# 데이터 테이블 표시
st.markdown("##### 사업 유형별 총괄 현황")
st.dataframe(
    type_summary,
    column_config=TableStyles.get_column_config({
        "사업유형": "사업 유형",
        "총예산액": "총 예산액",
        "평균예산액": "평균 예산액",
        "사업수": "사업 수",
        "수행기관수": "수행 기관 수",
        "주요수행기관": "주요 수행 기관"
    }),
    use_container_width=True,
    hide_index=True
)

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
    fig_budget.update_layout(height=720)
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
    fig_projects.update_layout(height=720)
    st.plotly_chart(fig_projects, use_container_width=True)

st.markdown("---")

# 2. 사업 유형별 분석
st.header("2. 사업 유형별 분석")

# 탭 생성
budget_tab, org_tab = st.tabs(["예산 분석", "기관 분석"])

with budget_tab:
    st.subheader("예산 분석")
    
    # 예산 규모 시각화
    st.markdown("##### 사업 유형별 예산 규모")
    fig_budget_scale = BarChart.create_basic_bar(
        df=type_summary,
        x='사업유형',
        y='총예산액',
        title='사업 유형별 총 예산액',
        text=type_summary['총예산액'].apply(lambda x: f'₩{x:,.1f}'),
        color_set=st.session_state.chart_settings['color_set'],
        hover_mode='budget'
    )
    fig_budget_scale.update_layout(height=720)
    st.plotly_chart(fig_budget_scale, use_container_width=True)
    
    # 예산 규모별 분포
    st.markdown("##### 예산 규모별 분포")
    
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
    
    # 각 사업 유형별로 예산 구간 분포 계산
    budget_dist = []
    for type_name in type_summary['사업유형']:
        type_data = df[df['project_type'] == type_name]
        for start, end, label in budget_ranges:
            count = len(type_data[(type_data['budget_amount'] >= start) & (type_data['budget_amount'] < end)])
            budget_dist.append({
                '사업유형': type_name,
                '예산구간': label,
                '사업수': count
            })
    
    budget_dist_df = pd.DataFrame(budget_dist)
    
    # 히트맵 생성
    fig_budget_dist = px.density_heatmap(
        budget_dist_df,
        x='사업유형',
        y='예산구간',
        z='사업수',
        title='사업 유형별 예산 규모 분포',
        color_continuous_scale='RdYlBu_r',
        labels={'사업수': '사업 수'}
    )
    
    # 레이아웃 설정
    fig_budget_dist.update_layout(
        dict(
            height=720,
            font_family="Pretendard",
            xaxis=dict(tickangle=45)
        )
    )
    
    st.plotly_chart(fig_budget_dist, use_container_width=True)

with org_tab:
    st.subheader("기관 분석")
    
    # 기관 유형별 사업 유형 선호도
    st.markdown("##### 기관 유형별 사업 유형 선호도")
    
    # 기관 유형별 사업 유형 집계
    org_type_pref = df.groupby(['org_type', 'project_type']).size().reset_index(name='count')
    org_type_pref = org_type_pref.pivot(
        index='org_type',
        columns='project_type',
        values='count'
    ).fillna(0)
    
    # 히트맵 생성
    fig_org_pref = px.imshow(
        org_type_pref,
        title='기관 유형별 사업 유형 선호도',
        color_continuous_scale='viridis',
        aspect='auto'
    )
    
    # 레이아웃 설정
    fig_org_pref.update_layout(
        dict(
            height=720,
            xaxis_title="사업 유형",
            yaxis_title="기관 유형",
            font=dict(family="Pretendard")
        )
    )
    
    st.plotly_chart(fig_org_pref, use_container_width=True)
    
    # 지역별 사업 유형 분포
    st.markdown("##### 지역별 사업 유형 분포")
    
    # 지역별 주력 사업 유형 파악
    region_type_pref = df.groupby(['region', 'project_type'])['budget_amount'].sum().reset_index()
    region_type_pref = region_type_pref.pivot(
        index='region',
        columns='project_type',
        values='budget_amount'
    ).fillna(0)
    
    # 버블 차트 데이터 준비
    bubble_data = []
    for region in region_type_pref.index:
        for proj_type in region_type_pref.columns:
            budget = region_type_pref.loc[region, proj_type]
            if budget > 0:
                bubble_data.append({
                    '지역': region,
                    '사업유형': proj_type,
                    '예산액': budget
                })
    
    bubble_df = pd.DataFrame(bubble_data)
    
    # 버블 차트 생성
    fig_region_dist = px.scatter(
        bubble_df,
        x='지역',
        y='사업유형',
        size='예산액',
        title='지역별 사업 유형 분포',
        color='사업유형',
        color_discrete_sequence=BarChart.COLORS[st.session_state.chart_settings['color_set']]
    )
    
    # 레이아웃 설정
    fig_region_dist.update_layout(
        height=720,
        xaxis_title="지역",
        yaxis_title="사업 유형",
        font=dict(family="Pretendard"),
        showlegend=True
    )
    
    st.plotly_chart(fig_region_dist, use_container_width=True)

st.markdown("---")

# 3. 사업 유형 비교 분석
st.header("3. 사업 유형 비교 분석")

# 탭 생성
type_compare_tab, org_compare_tab = st.tabs(["유형간 비교", "기관 유형별 비교"])

with type_compare_tab:
    # 비교할 사업 유형 선택
    selected_types = st.multiselect(
        "비교할 사업 유형 선택 (2~3개 권장)",
        options=type_summary['사업유형'].tolist(),
        default=type_summary['사업유형'].tolist()[:2]
    )
    
    if len(selected_types) > 1:
        # 선택된 사업 유형 데이터 필터링
        compare_type_df = type_summary[type_summary['사업유형'].isin(selected_types)].copy()
        
        # 1. 예산 규모 비교
        st.markdown("##### 예산 규모 비교")
        fig_budget_compare = BarChart.create_basic_bar(
            df=compare_type_df,
            x='사업유형',
            y='총예산액',
            title='사업 유형별 예산 규모 비교',
            text=compare_type_df['총예산액'].apply(lambda x: f'₩{x:,.1f}'),
            color_set=st.session_state.chart_settings['color_set'],
            hover_mode='budget'
        )
        fig_budget_compare.update_layout(height=720)
        st.plotly_chart(fig_budget_compare, use_container_width=True)
        
        # 2. 사업 현황 비교
        st.markdown("##### 사업 현황 비교")
        col1, col2 = st.columns(2)
        
        with col1:
            # 평균 사업 규모 비교
            fig_avg_compare = BarChart.create_basic_bar(
                df=compare_type_df,
                x='사업유형',
                y='평균예산액',
                title='평균 사업 규모 비교',
                text=compare_type_df['평균예산액'].apply(lambda x: f'₩{x:,.1f}'),
                color_set=st.session_state.chart_settings['color_set']
            )
            fig_avg_compare.update_layout(height=720)
            st.plotly_chart(fig_avg_compare, use_container_width=True)
        
        with col2:
            # 수행 기관 수 비교
            fig_org_compare = BarChart.create_basic_bar(
                df=compare_type_df,
                x='사업유형',
                y='수행기관수',
                title='수행 기관 수 비교',
                text=compare_type_df['수행기관수'].apply(lambda x: f'{x}개'),
                color_set=st.session_state.chart_settings['color_set']
            )
            fig_org_compare.update_layout(height=720)
            st.plotly_chart(fig_org_compare, use_container_width=True)
        
        # 3. 상세 비교 테이블
        st.markdown("##### 상세 비교")
        st.dataframe(
            compare_type_df,
            column_config=TableStyles.get_column_config({
                "사업유형": "사업 유형",
                "총예산액": "총 예산액",
                "평균예산액": "평균 예산액",
                "사업수": "사업 수",
                "수행기관수": "수행 기관 수",
                "주요수행기관": "주요 수행 기관"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("비교 분석을 위해 2개 이상의 사업 유형을 선택해주세요.")

with org_compare_tab:
    # 기관 유형별 사업 유형 비교
    org_type_summary = df.groupby(['org_type', 'project_type']).agg({
        'budget_amount': ['sum', 'count'],
        'organization': 'nunique'
    }).reset_index()
    
    org_type_summary.columns = [
        '기관유형', '사업유형', '총예산액', '사업수', '수행기관수'
    ]
    
    # 1. 예산 비중 비교
    st.markdown("##### 기관 유형별 사업 유형 예산 비중")
    
    # 기관 유형별 전체 예산
    org_total_budget = org_type_summary.groupby('기관유형')['총예산액'].sum().reset_index()
    org_type_summary = org_type_summary.merge(
        org_total_budget,
        on='기관유형',
        suffixes=('', '_total')
    )
    org_type_summary['예산비중'] = (org_type_summary['총예산액'] / org_type_summary['총예산액_total'] * 100).round(1)
    
    # 히트맵 생성
    budget_ratio_pivot = org_type_summary.pivot(
        index='기관유형',
        columns='사업유형',
        values='예산비중'
    ).fillna(0)
    
    fig_budget_ratio = px.imshow(
        budget_ratio_pivot,
        title='기관 유형별 사업 유형 예산 비중 (%)',
        color_continuous_scale='viridis',
        aspect='auto'
    )
    
    # 레이아웃 설정
    fig_budget_ratio.update_layout(
        dict(
            height=720,
            xaxis_title="사업 유형",
            yaxis_title="기관 유형",
            font=dict(family="Pretendard")
        )
    )
    
    st.plotly_chart(fig_budget_ratio, use_container_width=True)
    
    # 2. 상세 비교 테이블
    st.markdown("##### 기관 유형별 사업 유형 상세 비교")
    st.dataframe(
        org_type_summary.drop('총예산액_total', axis=1),
        column_config=TableStyles.get_column_config({
            "기관유형": "기관 유형",
            "사업유형": "사업 유형",
            "총예산액": "총 예산액",
            "사업수": "사업 수",
            "수행기관수": "수행 기관 수",
            "예산비중": "예산 비중(%)"
        }),
        use_container_width=True,
        hide_index=True
    )
