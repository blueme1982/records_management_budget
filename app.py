import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import yaml
import hashlib
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="기록물관리 사업 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

# 비밀번호 해시 함수
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# 테스트용 해시값 출력
st.write("Test hash for 'admin':", hash_password('admin'))
st.write("Test hash for '123456':", hash_password('123456'))

# 로그인 검증 함수
def verify_login(username: str, password: str) -> bool:
    try:
        # 디버깅을 위한 정보 출력
        st.write("Available secrets:", st.secrets)
        st.write("Trying to login with username:", username)
        st.write("Input password hash:", hash_password(password))
        
        if "users" not in st.secrets:
            st.error("사용자 정보가 설정되지 않았습니다.")
            return False
            
        if username not in st.secrets.users:
            st.error("존재하지 않는 사용자입니다.")
            return False
            
        stored_hash = st.secrets.users[username]
        input_hash = hash_password(password)
        
        st.write("Stored hash:", stored_hash)
        st.write("Input hash:", input_hash)
        
        return stored_hash == input_hash
    except Exception as e:
        st.error(f"로그인 검증 중 오류 발생: {str(e)}")
        return False

# 로그인 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login_time' not in st.session_state:
    st.session_state.login_time = None
if 'username' not in st.session_state:
    st.session_state.username = None

# 로그아웃 함수
def logout():
    st.session_state.authenticated = False
    st.session_state.login_time = None
    st.session_state.username = None

# 세션 만료 체크
def check_session_expired():
    if st.session_state.login_time:
        # 12시간 후 세션 만료
        if datetime.now() - st.session_state.login_time > timedelta(hours=12):
            logout()
            st.warning("세션이 만료되었습니다. 다시 로그인해주세요.")
            return True
    return False

# 메인 화면
def main():
    st.title("📊 기록물관리 사업 분석 대시보드")
    st.markdown("---")
    
    st.markdown("""
    ### 👋 환영합니다!
    
    이 대시보드는 기록물관리 사업의 예산 집행 현황과 사업 유형별 분포를 분석하는 도구입니다.
    
    #### 📈 주요 기능
    
    1. **메인 대시보드**
       - 전체 예산 현황 및 주요 지표
       - 기관 유형별 예산 분포
       - 사업 유형별 분석
    
    2. **기관유형별 분석**
       - 지방자치단체/교육행정기관 구분 분석
       - 상급기관별 예산 운영 현황
       - 기관 유형간 비교 분석
    
    3. **사업유형별 분석**
       - 5대 사업 유형 분석
       - 예산 규모별 분포
       - 기관별 사업 유형 선호도
    
    4. **기관별 심층 분석**
       - 개별 기관 단위 분석
       - 계층적 구조 기반 분석
       - 예산 규모별 상세 분석
    
    #### 🔍 시작하기
    
    왼쪽 사이드바의 메뉴에서 원하는 분석 페이지를 선택하세요.
    각 페이지에서 다양한 차트와 데이터를 확인할 수 있습니다.
    """)

# 로그인 화면
def login_page():
    st.title("🔐 로그인")
    
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            if verify_login(username, password):
                st.session_state.authenticated = True
                st.session_state.login_time = datetime.now()
                st.session_state.username = username
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    
    st.markdown("---")
    st.markdown("""
    ### 📝 사용 안내
    
    - 처음 방문하시는 경우 관리자에게 계정을 요청하세요.
    - 비밀번호를 잊어버린 경우 관리자에게 문의하세요.
    - 로그인 세션은 12시간 동안 유지됩니다.
    """)

# 메인 앱 실행
if not st.session_state.authenticated:
    login_page()
else:
    if check_session_expired():
        login_page()
    else:
        # 로그아웃 버튼
        with st.sidebar:
            st.markdown(f"**👤 {st.session_state.username}** 님 환영합니다")
            if st.button("🚪 로그아웃"):
                logout()
                st.rerun()
        main() 