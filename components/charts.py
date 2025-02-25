import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Tuple, List
import streamlit as st

class StreamlitIntegration:
    """Streamlit 통합 기능을 담당하는 클래스"""
    
    @staticmethod
    def initialize_chart_settings():
        """차트 설정 초기화"""
        if 'chart_settings' not in st.session_state:
            st.session_state.chart_settings = {
                'color_set': 'primary',
                'sort_by': '금액',
                'height': 600
            }
    
    @staticmethod
    def add_chart_filters(df: pd.DataFrame, section_key: str = "") -> dict:
        """차트 필터링 옵션 추가"""
        # 차트 설정 초기화
        StreamlitIntegration.initialize_chart_settings()
        
        # 메인 대시보드의 첫 번째 섹션에서만 설정을 표시
        if section_key == "project_type":
            with st.sidebar:
                st.subheader("📊 차트 설정")
                
                # 색상 테마 선택
                st.session_state.chart_settings['color_set'] = st.selectbox(
                    "색상 테마",
                    options=['primary', 'pastel', 'sequential', 'categorical'],
                    key="global_color_set"
                )
                
                # 정렬 기준
                st.session_state.chart_settings['sort_by'] = st.radio(
                    "정렬 기준",
                    options=['금액', '사업수'],
                    key="global_sort_by"
                )
        
        return st.session_state.chart_settings

class ResponsiveLayout:
    """반응형 레이아웃을 담당하는 클래스"""
    
    @staticmethod
    def get_chart_layout(is_mobile: bool = False) -> dict:
        """화면 크기에 따른 레이아웃 설정"""
        base_layout = BaseChart.LAYOUT_DEFAULTS.copy()
        
        if is_mobile:
            base_layout.update({
                'height': 400,
                'margin': dict(t=60, l=50, r=30, b=50),
                'title': {
                    'font': {'size': 18},
                    'y': 0.95
                },
                'xaxis': {
                    **base_layout['xaxis'],
                    'tickangle': 45
                }
            })
        
        return base_layout

class ChartAnnotations:
    """차트 주석을 담당하는 클래스"""
    
    @staticmethod
    def add_summary_stats(fig: go.Figure, data: pd.Series, title: str = "") -> None:
        """차트에 요약 통계 추가"""
        stats_text = (
            f"{title}<br>"
            f"총계: ₩{data.sum():,.0f}<br>"
            f"평균: ₩{data.mean():,.0f}<br>"
            f"최대: ₩{data.max():,.0f}"
        )
        
        fig.add_annotation(
            text=stats_text,
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="left",
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="rgba(255,255,255,0.2)",
            font=dict(size=12, color="#F9FAFB")
        )

class EnhancedTooltips:
    """향상된 호버 템플릿을 담당하는 클래스"""
    
    @staticmethod
    def get_budget_tooltip() -> str:
        return (
            "<b>%{x}</b><br>" +
            "예산액: ₩%{y:,.0f}<br>" +
            "전체 대비: %{customdata[0]:.1f}%<br>" +
            "사업 수: %{customdata[1]}개<br>" +
            "<extra></extra>"
        )
    
    @staticmethod
    def get_project_tooltip() -> str:
        return (
            "<b>%{x}</b><br>" +
            "사업 수: %{y}개<br>" +
            "평균 예산: ₩%{customdata:,.0f}<br>" +
            "<extra></extra>"
        )

class MetricCards:
    """메트릭 카드를 담당하는 클래스"""
    
    @staticmethod
    def display_summary_metrics(df: pd.DataFrame) -> None:
        """주요 지표를 카드 형태로 표시"""
        cols = st.columns(4)
        
        with cols[0]:
            st.metric(
                "총 예산",
                f"₩{df['budget_amount'].sum():,.0f}",
                help="전체 사업의 총 예산 금액"
            )
        
        with cols[1]:
            st.metric(
                "평균 사업 규모",
                f"₩{df['budget_amount'].mean():,.0f}",
                help="사업당 평균 예산 금액"
            )
        
        with cols[2]:
            st.metric(
                "총 사업 수",
                f"{len(df):,}개",
                help="전체 사업 건수"
            )
        
        with cols[3]:
            st.metric(
                "최대 사업 규모",
                f"₩{df['budget_amount'].max():,.0f}",
                help="가장 큰 규모의 사업 예산"
            )

class BaseChart:
    """차트 기본 설정을 담당하는 기본 클래스"""
    
    COLORS = {
        'primary': ['#4C9AFF', '#FF991F', '#36B37E', '#FF5630', '#8777D9'],
        'pastel': ['#B3D4FF', '#FFE0BD', '#ABF5D1', '#FFD5D2', '#DFD8FD'],
        'sequential': ['#0052CC', '#0065FF', '#2684FF', '#4C9AFF', '#B3D4FF'],
        'diverging': ['#FF5630', '#FF7452', '#FF8F73', '#36B37E', '#57D9A3'],
        'categorical': ['#00B8D9', '#36B37E', '#6554C0', '#FF5630', '#FFAB00']
    }
    
    LAYOUT_DEFAULTS = {
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'family': 'Pretendard, sans-serif',
            'color': '#E5E7EB',
            'size': 13
        },
        'title': {
            'font': {
                'size': 24,
                'color': '#F9FAFB',
                'family': 'Pretendard, sans-serif'
            },
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            'pad': {'b': 20}
        },
        'margin': dict(t=80, l=80, r=40, b=60),
        'xaxis': {
            'gridcolor': 'rgba(107,114,128,0.2)',
            'zerolinecolor': 'rgba(107,114,128,0.2)',
            'tickfont': {'color': '#E5E7EB', 'size': 12},
            'title_font': {'color': '#F9FAFB', 'size': 14},
            'tickangle': 30,
            'showgrid': True,
            'showline': True,
            'linecolor': 'rgba(107,114,128,0.2)',
            'linewidth': 1
        },
        'yaxis': {
            'gridcolor': 'rgba(107,114,128,0.2)',
            'zerolinecolor': 'rgba(107,114,128,0.2)',
            'tickfont': {'color': '#E5E7EB', 'size': 12},
            'title_font': {'color': '#F9FAFB', 'size': 14},
            'showgrid': True,
            'showline': True,
            'linecolor': 'rgba(107,114,128,0.2)',
            'linewidth': 1
        }
    }

    @staticmethod
    def get_hover_template(mode: str = 'default') -> str:
        """호버 템플릿을 반환합니다."""
        templates = {
            'default': "<b>%{x}</b><br>%{y}<extra></extra>",
            'budget': "<b>%{x}</b><br>예산액: ₩%{y:,.0f}<extra></extra>",
            'count': "<b>%{x}</b><br>사업 수: %{y}개<extra></extra>",
            'percent': "<b>%{label}</b><br>값: %{value:,.0f}<br>비중: %{percent}<extra></extra>"
        }
        return templates.get(mode, templates['default'])

    @staticmethod
    def get_hover_label() -> dict:
        """호버 레이블 스타일을 반환합니다."""
        return dict(
            bgcolor='rgba(31,41,55,0.95)',
            bordercolor='rgba(107,114,128,0.2)',
            font=dict(
                family='Pretendard',
                size=14,
                color='#F9FAFB'
            )
        )

class BarChart(BaseChart):
    """막대 그래프 관련 기능을 담당하는 클래스"""
    
    @staticmethod
    def create_basic_bar(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str,
        color_set: str = 'primary',
        text: pd.Series = None,
        hover_mode: str = 'default',
        hovertext: pd.Series = None,
        **kwargs
    ) -> go.Figure:
        """기본 막대 그래프를 생성합니다."""
        fig = go.Figure()
        
        # 단일 색상 또는 색상 배열 결정
        colors = BaseChart.COLORS[color_set]
        if isinstance(colors, list):
            if len(df) <= len(colors):
                colors = colors[:len(df)]
            else:
                colors = colors * (len(df) // len(colors) + 1)
                colors = colors[:len(df)]
        
        # 호버 템플릿 설정
        if hovertext is not None:
            hovertemplate = "%{hovertext}<extra></extra>"
        else:
            if hover_mode == 'budget':
                customdata = list(zip(
                    (df[y] / df[y].sum() * 100).round(1),
                    df.get('사업수', [0] * len(df))
                ))
                hovertemplate = EnhancedTooltips.get_budget_tooltip()
            elif hover_mode == 'count':
                avg_budget = df.get('예산액', df[y] * 0).div(df[y])
                customdata = avg_budget
                hovertemplate = EnhancedTooltips.get_project_tooltip()
            else:
                customdata = None
                hovertemplate = BaseChart.get_hover_template(hover_mode)
        
        # 데이터 추가
        fig.add_trace(go.Bar(
            x=df[x],
            y=df[y],
            text=text if text is not None else df[y],
            textposition='outside',
            marker=dict(
                color=colors,
                opacity=0.85,
                line=dict(
                    color='rgba(255,255,255,0.2)',
                    width=1
                )
            ),
            textfont=dict(
                family='Pretendard',
                color='#F9FAFB',
                size=13
            ),
            customdata=None if hovertext is not None else customdata,
            hovertemplate=hovertemplate,
            hovertext=hovertext
        ))
        
        # 레이아웃 설정
        layout = {
            **BaseChart.LAYOUT_DEFAULTS,
            'title_text': title,
            'xaxis_title': kwargs.get('xaxis_title', ''),
            'yaxis_title': kwargs.get('yaxis_title', ''),
            'height': kwargs.get('height', 400),
            'showlegend': kwargs.get('showlegend', False),
            'hoverlabel': BaseChart.get_hover_label()
        }
        
        # 모바일 대응
        if kwargs.get('is_mobile', False):
            layout.update(ResponsiveLayout.get_chart_layout(is_mobile=True))
        
        fig.update_layout(**layout)
        
        # 요약 통계 추가
        if kwargs.get('show_stats', False):
            ChartAnnotations.add_summary_stats(fig, df[y], title)
        
        return fig

class PieChart(BaseChart):
    """파이/도넛 차트 관련 기능을 담당하는 클래스"""
    
    @staticmethod
    def create_donut(
        df: pd.DataFrame,
        values: str,
        names: str,
        title: str,
        color_set: str = 'primary',
        **kwargs
    ) -> go.Figure:
        """도넛 차트를 생성합니다."""
        fig = go.Figure()
        
        # 색상 배열 준비
        colors = BaseChart.COLORS[color_set]
        if len(df) > len(colors):
            colors = colors * (len(df) // len(colors) + 1)
        colors = colors[:len(df)]
        
        # 데이터 추가
        fig.add_trace(go.Pie(
            values=df[values],
            labels=df[names],
            hole=kwargs.get('hole', 0.7),
            textinfo=kwargs.get('textinfo', 'label+percent'),
            textposition='outside',
            marker=dict(
                colors=colors,
                line=dict(
                    color='rgba(255,255,255,0.2)',
                    width=1.5
                )
            ),
            textfont=dict(
                family='Pretendard',
                color='#F9FAFB',
                size=13
            ),
            pull=kwargs.get('pull', [0.02] * len(df)),
            hovertemplate=kwargs.get('hovertemplate', BaseChart.get_hover_template('percent'))
        ))
        
        # 중앙 텍스트 계산
        if kwargs.get('show_total', True) and values in df.columns:
            total_value = df[values].sum()
            if '원' in str(df[values].iloc[0]):
                center_text = f'총계<br><b>₩{total_value:,.0f}</b>'
            else:
                center_text = f'총계<br><b>{total_value:,.0f}</b>'
        else:
            center_text = kwargs.get('center_text', '')
        
        # 레이아웃 설정
        layout = {
            **BaseChart.LAYOUT_DEFAULTS,
            'title_text': title,
            'height': kwargs.get('height', 450),
            'showlegend': kwargs.get('showlegend', True),
            'legend': dict(
                font=dict(
                    family='Pretendard',
                    color='#E5E7EB',
                    size=12
                ),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(107,114,128,0.2)',
                borderwidth=1
            ),
            'hoverlabel': BaseChart.get_hover_label(),
            'annotations': [
                dict(
                    text=center_text,
                    x=0.5,
                    y=0.5,
                    font=dict(
                        family='Pretendard',
                        size=16,
                        color='#F9FAFB'
                    ),
                    showarrow=False,
                    align='center'
                )
            ]
        }
        
        # 모바일 대응
        if kwargs.get('is_mobile', False):
            layout.update(ResponsiveLayout.get_chart_layout(is_mobile=True))
        
        fig.update_layout(**layout)
        
        return fig

class ProjectTypeCharts:
    """사업 유형 분석을 위한 차트 생성을 담당하는 클래스"""
    
    @staticmethod
    def create_summary(df: pd.DataFrame, type_mapping: Dict[str, str]) -> Tuple[pd.DataFrame, go.Figure, go.Figure, go.Figure]:
        """사업 유형별 분석을 위한 차트들을 생성합니다."""
        
        # 데이터 전처리
        valid_df = df[
            (df['project_type'].isin(type_mapping.keys())) &
            (df['budget_amount'] > 0)
        ].copy()
        
        valid_df['사업유형'] = valid_df['project_type'].map(type_mapping)
        
        # 사업 유형별 집계
        type_summary = valid_df.groupby('사업유형').agg({
            'budget_amount': 'sum',
            'project_type': 'count'
        }).reset_index()
        
        type_summary.columns = ['사업유형', '총예산액', '사업수']
        total_budget = type_summary['총예산액'].sum()
        type_summary['예산비중'] = (type_summary['총예산액'] / total_budget * 100).round(1)
        
        # 차트 설정 가져오기
        filters = StreamlitIntegration.add_chart_filters(valid_df, "project_type")
        
        # 정렬 적용
        if filters['sort_by'] == '금액':
            type_summary = type_summary.sort_values('총예산액', ascending=False)
        else:
            type_summary = type_summary.sort_values('사업수', ascending=False)
        
        # 1. 예산 금액 막대 그래프
        fig_budget = BarChart.create_basic_bar(
            df=type_summary,
            x='사업유형',
            y='총예산액',
            title='사업 유형별 예산 금액',
            text=type_summary['총예산액'].apply(lambda x: f'₩{x:,.0f}'),
            yaxis_title='예산액(원)',
            color_set=filters['color_set'],
            height=filters['height'],
            hovertemplate="<b>%{x}</b><br>예산액: ₩%{y:,.0f}<extra></extra>"
        )
        
        # 2. 예산 비중 도넛 차트
        fig_ratio = PieChart.create_donut(
            df=type_summary,
            values='총예산액',
            names='사업유형',
            title='사업 유형별 예산 비중',
            color_set=filters['color_set'],
            height=filters['height'],
            hovertemplate="<b>%{label}</b><br>예산액: ₩%{value:,.0f}<br>비중: %{percent}<extra></extra>"
        )
        
        # 3. 사업 수 막대 그래프
        fig_count = BarChart.create_basic_bar(
            df=type_summary,
            x='사업유형',
            y='사업수',
            title='사업 유형별 사업 수',
            text=type_summary['사업수'].apply(lambda x: f'{x}개'),
            yaxis_title='사업 수(개)',
            color_set=filters['color_set'],
            height=filters['height'],
            hovertemplate="<b>%{x}</b><br>사업 수: %{y}개<extra></extra>"
        )
        
        return type_summary, fig_budget, fig_ratio, fig_count

class BudgetRangeCharts:
    """예산 규모별 분석을 위한 차트 생성을 담당하는 클래스"""
    
    @staticmethod
    def create_summary(df: pd.DataFrame, ranges: List[Tuple[int, int, str]]) -> Tuple[pd.DataFrame, go.Figure, go.Figure]:
        """예산 규모별 분석을 위한 차트들을 생성합니다."""
        
        # 예산 구간별 데이터 집계
        budget_dist = []
        for start, end, label in ranges:
            filtered_df = df[(df['budget_amount'] >= start) & (df['budget_amount'] < end)]
            count = len(filtered_df)
            total = filtered_df['budget_amount'].sum()
            avg = total / count if count > 0 else 0
            budget_dist.append({
                '예산 구간': label,
                '사업 수': count,
                '총 예산': total,
                '평균 예산': avg
            })
        
        budget_dist_df = pd.DataFrame(budget_dist)
        
        # 차트 설정 가져오기
        filters = StreamlitIntegration.add_chart_filters(df, "budget_range")
        
        # 1. 사업 수 분포 도넛 차트
        fig_count = PieChart.create_donut(
            df=budget_dist_df,
            values='사업 수',
            names='예산 구간',
            title='예산 구간별 사업 수 분포',
            color_set=filters['color_set'],
            height=filters['height'],
            show_total=True
        )
        
        # 2. 총 예산 분포 도넛 차트
        fig_amount = PieChart.create_donut(
            df=budget_dist_df,
            values='총 예산',
            names='예산 구간',
            title='예산 구간별 총 예산 분포',
            color_set=filters['color_set'],
            height=filters['height'],
            show_total=True
        )
        
        return budget_dist_df, fig_count, fig_amount

class OrganizationCharts:
    """기관 유형별 분석을 위한 차트 생성을 담당하는 클래스"""
    
    @staticmethod
    def create_gov_summary(
        df: pd.DataFrame,
        gov_list: List[str]
    ) -> Tuple[pd.DataFrame, go.Figure, go.Figure]:
        """광역자치단체 분석을 위한 차트들을 생성합니다."""
        
        # 데이터 필터링
        local_gov_df = df[
            (df['org_type'] == '지방자치단체') & 
            (df['budget_amount'] > 0)
        ].copy()
        
        # 광역자치단체별 예산 및 사업 수 집계
        gov_summary = local_gov_df.groupby('parent_org').agg({
            'budget_amount': 'sum',
            'project_detail': 'count'
        }).reset_index()
        
        gov_summary.columns = ['지역', '예산액', '사업수']
        
        # 광역자치단체 목록에 있는 데이터만 필터링
        gov_summary = gov_summary[gov_summary['지역'].isin(gov_list)]
        
        # 광역자치단체 순서대로 정렬
        gov_summary['지역'] = pd.Categorical(
            gov_summary['지역'],
            categories=gov_list,
            ordered=True
        )
        gov_summary = gov_summary.sort_values('지역')
        
        # 차트 설정 가져오기
        filters = StreamlitIntegration.add_chart_filters(df, "organization_gov")
        
        # 1. 예산 규모 막대 그래프
        fig_budget = BarChart.create_basic_bar(
            df=gov_summary,
            x='지역',
            y='예산액',
            title='광역자치단체별 예산 규모',
            text=gov_summary['예산액'].apply(lambda x: f'₩{x:,.0f}'),
            yaxis_title='예산액(원)',
            height=filters['height'],
            color_set=filters['color_set'],
            hover_mode='budget'
        )
        
        # 2. 사업 수 막대 그래프
        fig_projects = BarChart.create_basic_bar(
            df=gov_summary,
            x='지역',
            y='사업수',
            title='광역자치단체별 사업 수',
            text=gov_summary['사업수'].apply(lambda x: f'{x}개'),
            yaxis_title='사업 수(개)',
            height=filters['height'],
            color_set=filters['color_set'],
            hover_mode='count'
        )
        
        return gov_summary, fig_budget, fig_projects
    
    @staticmethod
    def create_edu_summary(
        df: pd.DataFrame,
        edu_list: List[str]
    ) -> Tuple[pd.DataFrame, go.Figure, go.Figure]:
        """시도교육청 분석을 위한 차트들을 생성합니다."""
        
        # 데이터 필터링
        edu_df = df[
            (df['org_type'] == '교육행정기관') & 
            (df['budget_amount'] > 0)
        ].copy()
        
        # 교육청별 예산 및 사업 수 집계
        edu_summary = edu_df.groupby('parent_org').agg({
            'budget_amount': 'sum',
            'project_detail': 'count'
        }).reset_index()
        
        edu_summary.columns = ['교육청', '예산액', '사업수']
        
        # 교육청 목록에 있는 데이터만 필터링
        edu_summary = edu_summary[edu_summary['교육청'].isin(edu_list)]
        
        # 교육청 순서대로 정렬
        edu_summary['교육청'] = pd.Categorical(
            edu_summary['교육청'],
            categories=edu_list,
            ordered=True
        )
        edu_summary = edu_summary.sort_values('교육청')
        
        # 차트 설정 가져오기
        filters = StreamlitIntegration.add_chart_filters(df, "organization_edu")
        
        # 1. 예산 규모 막대 그래프
        fig_budget = BarChart.create_basic_bar(
            df=edu_summary,
            x='교육청',
            y='예산액',
            title='시도교육청별 예산 규모',
            text=edu_summary['예산액'].apply(lambda x: f'₩{x:,.0f}'),
            yaxis_title='예산액(원)',
            height=filters['height'],
            color_set=filters['color_set'],
            hover_mode='budget'
        )
        
        # 2. 사업 수 막대 그래프
        fig_projects = BarChart.create_basic_bar(
            df=edu_summary,
            x='교육청',
            y='사업수',
            title='시도교육청별 사업 수',
            text=edu_summary['사업수'].apply(lambda x: f'{x}개'),
            yaxis_title='사업 수(개)',
            height=filters['height'],
            color_set=filters['color_set'],
            hover_mode='count'
        )
        
        return edu_summary, fig_budget, fig_projects

class TableStyles:
    """데이터 테이블 스타일을 담당하는 클래스"""
    
    @staticmethod
    def get_column_config(columns: Dict[str, str]) -> Dict:
        """데이터 테이블의 컬럼 설정을 반환합니다."""
        config = {}
        for col, label in columns.items():
            base_config = {
                'help': f"{label} 정보입니다.",
                'width': 'medium'
            }
            
            if '금액' in label or '예산' in label:
                config[col] = st.column_config.NumberColumn(
                    label,
                    format="₩%d",
                    help=f"{label} 정보입니다. 금액은 원 단위로 표시됩니다.",
                    step=1000000,  # 백만 원 단위로 조정 가능
                    min_value=0
                )
            elif '수' in label:
                config[col] = st.column_config.NumberColumn(
                    label,
                    format="%d개",
                    help=f"{label} 정보입니다. 개수로 표시됩니다.",
                    min_value=0
                )
            elif '비중' in label or '비율' in label:
                config[col] = st.column_config.NumberColumn(
                    label,
                    format="%.1f%%",
                    help=f"{label} 정보입니다. 전체 대비 비율로 표시됩니다.",
                    min_value=0,
                    max_value=100
                )
            elif '평균' in label:
                config[col] = st.column_config.NumberColumn(
                    label,
                    format="₩%d",
                    help=f"{label} 정보입니다. 평균 금액은 원 단위로 표시됩니다.",
                    min_value=0
                )
            else:
                config[col] = st.column_config.TextColumn(
                    label,
                    help=f"{label} 정보입니다.",
                    width='medium'
                )
        
        return config 