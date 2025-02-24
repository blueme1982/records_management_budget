# 기록물관리 사업 분석 대시보드 구현 가이드

## 1. 페이지 구조

```
src/
├── pages/
│   ├── 1_📊_메인대시보드.py
│   ├── 2_🗺️_지역별분석.py
│   ├── 3_📈_사업유형분석.py
│   └── 4_🏢_기관별심층분석.py
├── components/
│   ├── filters.py
│   ├── charts.py
│   └── maps.py
├── utils/
│   ├── budget_classifier.py
│   └── data_processor.py
└── Home.py
```

## 2. 페이지별 구현 상세

### 2.1 Home.py (메인 페이지)
- **레이아웃**: 사이드바 + 메인 컨텐츠
- **주요 기능**:
  - 전체 프로젝트 개요
  - 핵심 지표 요약
  - 최근 업데이트 정보
- **구현 컴포넌트**:
```python
# 예시 코드
st.set_page_config(layout="wide")
st.title("기록물관리 사업 분석 대시보드")

# 사이드바 구성
with st.sidebar:
    st.header("필터 옵션")
    selected_year = st.selectbox("년도", ["2025"])
    selected_region = st.multiselect("지역", regions)
    
# 메인 컨텐츠
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 사업 예산", "3.2조원", "12%")
```

### 2.2 1_📊_메인대시보드.py
- **주요 섹션**:
  1. 사업 기회 맵
  2. 핵심 지표
  3. 사업 유형별 분석
- **데이터 시각화**:
```python
# 지도 시각화
def create_opportunity_map():
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)
    # 지역별 마커 추가
    return m

# 핵심 지표 차트
def create_key_metrics():
    fig = px.pie(df, values='budget_amount', names='project_type')
    return fig
```

### 2.3 2_🗺️_지역별분석.py
- **주요 기능**:
  - 지역별 예산 분포
  - 기관 유형 비교
  - 상세 사업 목록
- **필터링 옵션**:
  - 지역 선택
  - 사업 유형
  - 예산 범위
- **차트 구성**:
  1. 지역별 예산 막대 차트
  2. 기관 유형 파이 차트
  3. 사업 목록 테이블

### 2.4 3_📈_사업유형분석.py
- **분석 항목**:
  1. 유형별 예산 규모
  2. 기관별 발주 현황
  3. 사업 상세 내용
- **인터랙티브 기능**:
  - 유형 선택에 따른 동적 차트
  - 드릴다운 분석
  - 상세 정보 모달

### 2.5 4_🏢_기관별심층분석.py
- **분석 기능**:
  - 기관별 예산 구조
  - 사업 이력 분석
  - 우선순위 평가
- **시각화 요소**:
  - 트리맵
  - 시계열 차트
  - 평가 매트릭스

## 3. 공통 컴포넌트

### 3.1 filters.py
```python
class FilterComponent:
    def __init__(self):
        self.regions = self.load_regions()
        self.project_types = self.load_project_types()
    
    def render_sidebar_filters(self):
        with st.sidebar:
            selected_regions = st.multiselect("지역 선택", self.regions)
            selected_types = st.multiselect("사업 유형", self.project_types)
            budget_range = st.slider("예산 범위", 0, 1000000000, (0, 1000000000))
        return selected_regions, selected_types, budget_range
```

### 3.2 charts.py
```python
class ChartComponents:
    @staticmethod
    def create_budget_distribution(df):
        fig = px.bar(df, x='region', y='budget_amount',
                    color='project_type',
                    title='지역별 예산 분포')
        return fig
    
    @staticmethod
    def create_project_type_pie(df):
        fig = px.pie(df, values='budget_amount',
                    names='project_type',
                    title='사업 유형별 분포')
        return fig
```

### 3.3 maps.py
```python
class MapComponents:
    @staticmethod
    def create_korea_map(df):
        m = folium.Map(location=[36.5, 127.5],
                      zoom_start=7)
        # 지역별 마커 및 팝업 추가
        return m
```

## 4. 데이터 처리

### 4.1 data_processor.py
```python
class DataProcessor:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.classifier = BudgetClassifier()
    
    def preprocess_data(self):
        # 데이터 전처리
        self.df['budget_amount'] = self.df['budget_amount'].str.replace(',', '').astype(float)
        
    def classify_projects(self):
        # 프로젝트 분류 적용
        classified_df = self.classifier.classify_budget_data(self.df)
        return classified_df
```

## 5. 성능 최적화

### 5.1 데이터 캐싱
```python
@st.cache_data
def load_data():
    processor = DataProcessor('assets/data/budget_2025.csv')
    return processor.get_processed_data()
```

### 5.2 컴포넌트 캐싱
```python
@st.cache_resource
def get_map_component():
    return MapComponents()
```

## 6. 배포 고려사항

### 6.1 환경 설정
- requirements.txt 구성
- 환경변수 관리
- 클라우드 배포 설정

### 6.2 성능 모니터링
- 페이지 로드 시간
- 메모리 사용량
- 에러 로깅 