# -*- coding: utf-8 -*-
"""
☕ Coffee AX Master Hub - 통합 메인 애플리케이션
===================================================
팀 프로젝트 통합본 (2026-02-03)
- 조성빈, 강정민 팀
"""

import streamlit as st

# ==========================================
# 1. 페이지 설정 (반드시 최상단, 단 한 번만!)
# ==========================================
st.set_page_config(
    page_title="☕ Coffee AX Master Hub",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 각 탭 모듈 임포트
# ==========================================
from tabs import (
    tab_landing,
    tab1_dashboard,
    tab2_coffeebeans,
    tab3_costcal,
    tab4_news,
    tab5_strategy,
    tab6_korean_coffee
)

# ==========================================
# 3. 세션 상태 초기화
# ==========================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# ==========================================
# 4. 네비게이션 헬퍼 함수
# ==========================================
def go_home():
    st.session_state.current_page = 'Home'

def go_to(page_name):
    st.session_state.current_page = page_name

# ==========================================
# 5. 홈 버튼 (사이드바 공통)
# ==========================================
def render_home_button():
    """각 탭의 사이드바 최상단에 홈 버튼 표시"""
    with st.sidebar:
        st.markdown("### ☕ Coffee AX Hub")
        if st.button("🏠 메인으로 돌아가기", use_container_width=True, type="primary"):
            go_home()
            st.rerun()
        st.markdown("---")

# ==========================================
# 6. 메인 라우팅
# ==========================================
def main():
    current = st.session_state.current_page
    
    if current == 'Home':
        show_home_page()
    elif current == 'Landing':
        render_home_button()
        tab_landing.show()
    elif current == 'Dashboard':
        render_home_button()
        tab1_dashboard.show()
    elif current == 'BeanAnalysis':
        render_home_button()
        tab2_coffeebeans.show()
    elif current == 'CostCalculator':
        render_home_button()
        tab3_costcal.show()
    elif current == 'News':
        render_home_button()
        tab4_news.show()
    elif current == 'Strategy':
        render_home_button()
        tab5_strategy.show()
    elif current == 'KoreanMarket':
        render_home_button()
        tab6_korean_coffee.show()

# ==========================================
# 7. 홈 페이지 (카드 그리드 네비게이션)
# ==========================================
def show_home_page():
    # CSS 스타일
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #4B2C20 0%, #6F4E37 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .nav-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid transparent;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nav-card:hover {
        border-color: #6F4E37;
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .nav-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .nav-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #4B2C20;
        margin-bottom: 0.5rem;
    }
    .nav-desc {
        font-size: 0.9rem;
        color: #666;
        line-height: 1.4;
    }
    .team-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #888;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>☕ Coffee AX Master Hub</h1>
        <p>글로벌 커피 무역 인텔리전스 플랫폼</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 네비게이션 카드 데이터
    nav_items = [
        {
            "icon": "🌍",
            "title": "산지 지도",
            "desc": "글로벌 커피 산지 지도와 실시간 환율 분석",
            "page": "Landing"
        },
        {
            "icon": "📊",
            "title": "시장 대시보드",
            "desc": "아라비카/로부스타 선물 가격 및 매수 신호",
            "page": "Dashboard"
        },
        {
            "icon": "🌿",
            "title": "원두 분석",
            "desc": "품종별 특성 분석 및 AI 제안서 생성",
            "page": "BeanAnalysis"
        },
        {
            "icon": "🧮",
            "title": "원가 계산기",
            "desc": "인코텀즈별 수입 원가 계산",
            "page": "CostCalculator"
        },
        {
            "icon": "📰",
            "title": "뉴스 인사이트",
            "desc": "글로벌/국내 커피 뉴스 수집 및 분석",
            "page": "News"
        },
        {
            "icon": "📈",
            "title": "전략 분석",
            "desc": "FTA, 관세, 기후 리밸런싱 전략",
            "page": "Strategy"
        },
        {
            "icon": "🇰🇷",
            "title": "국내 시장",
            "desc": "한국 커피 수입 트렌드 분석",
            "page": "KoreanMarket"
        }
    ]
    
    # 카드 그리드 렌더링 (3열 + 3열 + 1열)
    # 첫 번째 행 (3개)
    cols1 = st.columns(3)
    for i, item in enumerate(nav_items[:3]):
        with cols1[i]:
            st.markdown(f"""
            <div class="nav-card">
                <div class="nav-icon">{item['icon']}</div>
                <div class="nav-title">{item['title']}</div>
                <div class="nav-desc">{item['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{item['icon']} {item['title']} 바로가기", key=f"nav_{item['page']}", use_container_width=True):
                go_to(item['page'])
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 두 번째 행 (3개)
    cols2 = st.columns(3)
    for i, item in enumerate(nav_items[3:6]):
        with cols2[i]:
            st.markdown(f"""
            <div class="nav-card">
                <div class="nav-icon">{item['icon']}</div>
                <div class="nav-title">{item['title']}</div>
                <div class="nav-desc">{item['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{item['icon']} {item['title']} 바로가기", key=f"nav_{item['page']}", use_container_width=True):
                go_to(item['page'])
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 세 번째 행 (1개 - 가운데 정렬)
    cols3 = st.columns([1, 1, 1])
    with cols3[1]:
        item = nav_items[6]
        st.markdown(f"""
        <div class="nav-card">
            <div class="nav-icon">{item['icon']}</div>
            <div class="nav-title">{item['title']}</div>
            <div class="nav-desc">{item['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{item['icon']} {item['title']} 바로가기", key=f"nav_{item['page']}", use_container_width=True):
            go_to(item['page'])
            st.rerun()
    
    # 팀 정보 푸터
    st.markdown("""
    <div class="team-footer">
        <p>© 2026 무역 AX 마스터 1기 | 조성빈, 강정민 프로젝트</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
