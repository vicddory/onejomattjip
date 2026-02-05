# -*- coding: utf-8 -*-
"""
================================================================================
📁 main.py - Coffee Trade Hub 메인 애플리케이션
================================================================================

🚀 실행 방법:
    streamlit run main.py
    jhhh

📌 이 파일이 하는 일:
    1. Streamlit 페이지 설정 (st.set_page_config) - 반드시 최상단에 1번만!
    2. 전역 CSS 스타일 적용
    3. 사이드바 네비게이션 메뉴 생성
    4. 선택된 메뉴에 따라 해당 탭(view) 모듈의 show() 함수 호출

💡 구조 설명:
    - views/ 폴더 안의 각 파일은 하나의 화면(탭)을 담당합니다.
    - 각 파일에는 show() 함수가 있어서, 여기서 호출하면 화면이 표시됩니다.
    - 새로운 탭을 추가하고 싶으면:
        1. views/ 폴더에 새 파일 생성 (예: tab7_new_feature.py)
        2. 그 파일에 def show(): 함수 작성
        3. 이 파일의 MENU_OPTIONS에 추가
        4. render_selected_page() 함수에 조건 추가

================================================================================
"""

import streamlit as st

# ===========================================
# 1. 페이지 설정 (반드시 최상단에!)
# ===========================================
# ⚠️ 중요: st.set_page_config()는 전체 앱에서 단 1번만, 가장 먼저 호출해야 합니다!
# 다른 파일(views/*.py)에서는 절대 호출하지 마세요.

st.set_page_config(
    page_title="COFFEE TRADE HUB",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===========================================
# 2. 전역 스타일 적용
# ===========================================
from styles import apply_global_styles
apply_global_styles()

# ===========================================
# 3. 메뉴 옵션 정의
# ===========================================
# 각 메뉴 항목: (표시 이름, 아이콘, 모듈 이름)
MENU_OPTIONS = {
    "홈": "landing",
    "원두 데이터": "tab1_sourcing",
    "제안서 생성기": "tab2_proposal",
    "원가 계산기": "tab3_cost_calculator",
    "뉴스 큐레이션": "tab4_news",
    "무역 인사이트": "tab5_trade_intel",
    "한국 시장 분석": "tab6_korean_market"
}

# ===========================================
# 4. 상단 네비게이션
# ===========================================
# 로고/타이틀 헤더
# 로고/타이틀 헤더
st.markdown("""
<style>
    .main-title {
        color: #00695C !important;
        margin: 0 !important;
        font-size: 3.0rem !important;
    }
</style>
<div style="display: flex; align-items: center; justify-content: center; padding: 10px 0 5px 0;">
    <h2 class="main-title">COFFEE TRADE HUB</h2>
    
</div>
""", unsafe_allow_html=True)
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")

# 수평 메뉴
menu_keys = list(MENU_OPTIONS.keys())
menu_cols = st.columns(len(menu_keys))

if "selected_menu_index" not in st.session_state:
    st.session_state.selected_menu_index = 0

for i, (col, key) in enumerate(zip(menu_cols, menu_keys)):
    with col:
        is_active = (i == st.session_state.selected_menu_index)
        btn_type = "primary" if is_active else "secondary"
        if st.button(key, key=f"nav_{i}", use_container_width=True, type=btn_type):
            st.session_state.selected_menu_index = i
            st.rerun()

selected_menu = menu_keys[st.session_state.selected_menu_index]

st.markdown('<hr style="border-top: 1px solid #E0E0E0; margin: 5px 0 15px 0;">', unsafe_allow_html=True)


# ===========================================
# 5. 선택된 페이지 렌더링
# ===========================================
def render_selected_page(menu_key: str):
    """
    선택된 메뉴에 해당하는 페이지를 렌더링합니다.
    
    💡 새 탭을 추가하려면:
        1. views/ 폴더에 새 파일 추가
        2. MENU_OPTIONS 딕셔너리에 메뉴 추가
        3. 아래 if-elif 체인에 조건 추가
    """
    module_name = MENU_OPTIONS[menu_key]
    
    # 각 모듈 동적 import 및 show() 호출
    # (지연 로딩으로 초기 로드 시간 단축)
    
    if module_name == "landing":
        from views.landing import show
        show()
        
    elif module_name == "tab1_sourcing":
        from views.tab1_sourcing import show
        show()
        
    elif module_name == "tab2_proposal":
        from views.tab2_proposal import show
        show()
        
    elif module_name == "tab3_cost_calculator":
        from views.tab3_cost_calculator import show
        show()
        
    elif module_name == "tab4_news":
        from views.tab4_news import show
        show()
        
    elif module_name == "tab5_trade_intel":
        from views.tab5_trade_intel import show
        show()
        
    elif module_name == "tab6_korean_market":
        from views.tab6_korean_market import show
        show()
        
    else:
        st.error(f"알 수 없는 메뉴: {module_name}")


# ===========================================
# 6. 메인 실행
# ===========================================
if __name__ == "__main__":
    render_selected_page(selected_menu)
