import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import warnings

# 경고 메시지 필터링
warnings.filterwarnings('ignore', category=SyntaxWarning)

# 페이지 설정
st.set_page_config(
    page_title="기록물관리 예산 현황 대시보드",
    page_icon="📊",
    layout="wide"
)

# 한국 지역 중심 좌표 데이터
KOREA_REGIONS = {
    "서울": {"lat": 37.5665, "lon": 126.9780},
    "부산": {"lat": 35.1796, "lon": 129.0756},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "인천": {"lat": 37.4563, "lon": 126.7052},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "대전": {"lat": 36.3504, "lon": 127.3845},
    "울산": {"lat": 35.5384, "lon": 129.3114},
    "세종": {"lat": 36.4800, "lon": 127.2890},
    "경기": {"lat": 37.4138, "lon": 127.5183},
    "강원": {"lat": 37.8228, "lon": 128.1555},
    "충북": {"lat": 36.6356, "lon": 127.4914},
    "충남": {"lat": 36.6588, "lon": 126.6728},
    "전북": {"lat": 35.8203, "lon": 127.1088},
    "전남": {"lat": 34.8160, "lon": 126.4629},
    "경북": {"lat": 36.4919, "lon": 128.8889},
    "경남": {"lat": 35.4606, "lon": 128.2132},
    "제주": {"lat": 33.4996, "lon": 126.5312}
}

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('data/budget_2025.csv')
    # 금액 컬럼의 쉼표 제거 후 숫자로 변환
    df['금액'] = df['금액'].str.replace(',', '').astype(float)
    return df

# 지도 시각화 함수
def create_map_visualization(df):
    # 지역별 예산 합계 계산
    region_budget = df.groupby('지역')['금액'].sum().reset_index()
    
    # 위도, 경도 데이터 추가
    region_budget['lat'] = region_budget['지역'].map(lambda x: KOREA_REGIONS[x]['lat'])
    region_budget['lon'] = region_budget['지역'].map(lambda x: KOREA_REGIONS[x]['lon'])
    
    # 버블 맵 생성
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lon=region_budget['lon'],
        lat=region_budget['lat'],
        text=region_budget.apply(lambda x: f"{x['지역']}: {x['금액']:,.0f}원", axis=1),
        marker=dict(
            size=region_budget['금액'] / region_budget['금액'].max() * 50,
            color=region_budget['금액'],
            colorscale='Viridis',
            showscale=True,
            colorbar_title="예산 규모"
        ),
        mode='markers+text',
        textposition="top center",
        name='예산 규모'
    ))
    
    fig.update_layout(
        title='지역별 예산 분포',
        geo=dict(
            scope='asia',
            center=dict(lon=127.5, lat=36),
            projection_scale=20,
            showland=True,
            showcoastlines=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        ),
        height=600
    )
    
    return fig

# 메인 앱
def main():
    st.title("2025년도 기록물관리 예산 현황 대시보드")
    
    # 데이터 로드
    try:
        df = load_data()
        st.success("데이터 로드 완료!")
        
        # 사이드바 - 필터링 옵션
        st.sidebar.header("필터 옵션")
        
        # 지역 선택
        regions = ['전체'] + sorted(df['지역'].unique().tolist())
        selected_region = st.sidebar.selectbox('지역 선택', regions)
        
        # 예산 범위 선택
        min_budget = float(df['금액'].min())
        max_budget = float(df['금액'].max())
        budget_range = st.sidebar.slider(
            '예산 범위 (원)',
            min_value=min_budget,
            max_value=max_budget,
            value=(min_budget, max_budget),
            format="%,.0f"
        )
        
        # 데이터 필터링
        mask = (df['금액'] >= budget_range[0]) & (df['금액'] <= budget_range[1])
        if selected_region != '전체':
            mask &= (df['지역'] == selected_region)
        df_filtered = df[mask]
            
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_budget = df_filtered['금액'].sum()
            st.metric("총 예산", f"{total_budget:,.0f}원")
            
        with col2:
            avg_budget = df_filtered['금액'].mean()
            st.metric("평균 예산", f"{avg_budget:,.0f}원")
            
        with col3:
            org_count = df_filtered['기관'].nunique()
            st.metric("기관 수", f"{org_count}개")
            
        with col4:
            project_count = len(df_filtered)
            st.metric("사업 건수", f"{project_count}건")

        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(["지도", "예산 분포", "사업 유형 분석", "상세 데이터"])
        
        with tab1:
            # 지도 시각화
            st.plotly_chart(create_map_visualization(df_filtered), use_container_width=True)
            
            # 지역별 통계 테이블
            st.subheader("지역별 예산 통계")
            region_stats = df_filtered.groupby('지역').agg({
                '금액': ['sum', 'mean', 'count']
            }).round(0)
            region_stats.columns = ['총예산', '평균예산', '사업수']
            st.dataframe(
                region_stats,
                column_config={
                    "총예산": st.column_config.NumberColumn(format="₩%d"),
                    "평균예산": st.column_config.NumberColumn(format="₩%d"),
                }
            )
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # 지역별 예산 분포 (파이 차트)
                st.subheader("지역별 예산 분포")
                fig_region = px.pie(
                    df_filtered.groupby('지역')['금액'].sum().reset_index(),
                    values='금액',
                    names='지역',
                    hole=0.4
                )
                st.plotly_chart(fig_region)
            
            with col2:
                # 기관별 예산 TOP 10 (수평 막대 차트)
                st.subheader("기관별 예산 TOP 10")
                fig_org = px.bar(
                    df_filtered.groupby('기관')['금액'].sum()
                             .sort_values(ascending=True)
                             .tail(10)
                             .reset_index(),
                    x='금액',
                    y='기관',
                    orientation='h'
                )
                st.plotly_chart(fig_org)

        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # 항목별 예산 분포
                st.subheader("항목별 예산 분포")
                fig_category = px.treemap(
                    df_filtered,
                    path=['항목1', '항목2'],
                    values='금액'
                )
                st.plotly_chart(fig_category)
            
            with col2:
                # 예산 규모별 분포 (히스토그램)
                st.subheader("예산 규모별 분포")
                fig_hist = px.histogram(
                    df_filtered,
                    x='금액',
                    nbins=30,
                    title="예산 규모별 사업 수",
                    marginal="box"  # 박스플롯 추가
                )
                st.plotly_chart(fig_hist)

        with tab4:
            # 상세 데이터 테이블
            st.subheader("상세 데이터")
            
            # 검색 필터
            search_term = st.text_input("사업명 검색", "")
            
            if search_term:
                filtered_df = df_filtered[
                    df_filtered['상세'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_df = df_filtered
            
            st.dataframe(
                filtered_df,
                column_config={
                    "금액": st.column_config.NumberColumn(
                        "금액",
                        format="₩%d"
                    ),
                    "예산서 사이트": st.column_config.LinkColumn("예산서 링크")
                }
            )
            
            # 데이터 다운로드 버튼
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "CSV 다운로드",
                csv,
                "budget_data.csv",
                "text/csv",
                key='download-csv'
            )
        
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 