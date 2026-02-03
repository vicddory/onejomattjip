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
# 3. 사이드바 네비게이션
# ==========================================
def main():
    # 사이드바 스타일링
    st.sidebar.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #4B2C20 0%, #6F4E37 100%);
        }
        [data-testid="stSidebar"] * {
            color: #F4E8D8 !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            font-size: 1rem;
            padding: 8px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 로고 및 타이틀
    st.sidebar.markdown("# ☕ Coffee AX Hub")
    st.sidebar.markdown("##### 글로벌 커피 무역 인텔리전스")
    st.sidebar.divider()
    
    # 네비게이션 메뉴
    menu = st.sidebar.radio(
        "📍 Navigate to",
        [
            "🏠 Home (산지 지도)",
            "📊 Dashboard (시장 신호)",
            "🌿 Bean Analysis (품종 분석)",
            "🧮 Cost Calculator (원가 계산)",
            "📰 News (뉴스 인사이트)",
            "📈 Strategy (전략 분석)",
            "🇰🇷 Korean Market (국내 시장)"
        ],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    st.sidebar.caption("© 2026 무역 AX 마스터 1기")
    st.sidebar.caption("조성빈, 강정민 프로젝트")
    
    # ==========================================
    # 4. 페이지 라우팅
    # ==========================================
    if "Home" in menu:
        tab_landing.show()
    elif "Dashboard" in menu:
        tab1_dashboard.show()
    elif "Bean Analysis" in menu:
        tab2_coffeebeans.show()
    elif "Cost Calculator" in menu:
        tab3_costcal.show()
    elif "News" in menu:
        tab4_news.show()
    elif "Strategy" in menu:
        tab5_strategy.show()
    elif "Korean Market" in menu:
        tab6_korean_coffee.show()

if __name__ == "__main__":
    main()
