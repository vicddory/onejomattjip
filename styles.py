# -*- coding: utf-8 -*-
"""
================================================================================
📁 styles.py - 공통 CSS 스타일 관리
================================================================================
이 파일은 프로젝트 전체에서 사용되는 CSS 스타일을 한 곳에서 관리합니다.

💡 사용법:
    from styles import apply_global_styles
    apply_global_styles()  # main.py에서 1번만 호출하면 됩니다.
================================================================================
"""

import streamlit as st


def apply_global_styles():
    """
    전역 CSS 스타일을 적용합니다.
    main.py에서 st.set_page_config() 직후에 1번만 호출하세요.
    """
    st.markdown("""
    <style>
        /* ===========================================
           1. 폰트 설정 (Google Fonts)
           =========================================== */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* 전체 폰트 적용 */
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', 'Inter', sans-serif !important;
            color: #333333;
        }

        /* ===========================================
           2. 배경색 설정 (config.toml 보조)
           =========================================== */
        .stApp {
            background-color: #FAFAFA !important;
            background-image: none !important;
        }

        /* ===========================================
           3. 입력 요소 스타일
           =========================================== */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {
            border-radius: 8px !important;
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        /* 입력창 포커스 시 */
        .stTextInput > div > div > input:focus {
            border-color: #00695C !important;
            box-shadow: 0 0 0 1px #00695C !important;
        }

        /* ===========================================
           4. 버튼 스타일
           =========================================== */
        .stButton > button {
            border-radius: 8px !important;
            background-color: #FFFFFF;
            color: #333333;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            border-color: #00695C;
            color: #00695C;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* ===========================================
           5. 탭 스타일
        =========================================== */
        /* 1. 모든 탭의 기본 글자 크기 설정 */
        .stTabs [data-baseweb="tab"] p {
            font-size: 1.2rem !important;  /* 기존보다 크게 설정 (원하는 수치로 조절 가능) */
            font-weight: 500 !important;
        }

        /* 2. 선택된 탭의 스타일 강조 */
        .stTabs [aria-selected="true"] p {
            font-weight: 800 !important;   /* 선택된 탭은 더 두껍게 */
            color: #00695C !important;     /* 테마 색상 적용 */
        }

        /* 3. 선택된 탭 하단 라인 색상 */
        .stTabs [aria-selected="true"] {
            border-bottom-color: #00695C !important;
        }


        /* ===========================================
           6. 헤더 스타일
           =========================================== */
        h1, h2, h3, h4 {
            color: #333333 !important;
            font-family: 'Noto Sans KR', sans-serif !important;
        }

        /* ===========================================
           7. 메트릭 카드 스타일
           =========================================== */
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 14px !important;
        }

        /* ===========================================
           8. 커스텀 컴포넌트 스타일
           =========================================== */
        /* 메트릭 컨테이너 */
        .metric-container {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* 메트릭 박스 (환율, 시세 표시용) */
        .metric-box {
            flex: 1;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 6px 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .metric-label {
            color: #666;
            font-size: 11px;
            margin-bottom: 0px;
            font-weight: 500;
        }

        .metric-value {
            font-size: 18px;
            font-weight: 700;
            color: #333;
            line-height: 1.2;
        }

        /* 신호등 카드 */
        .signal-card {
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .traffic-light {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-right: 16px;
        }

        .signal-green { background-color: rgba(46, 125, 50, 0.15); }
        .signal-yellow { background-color: rgba(255, 193, 7, 0.15); }
        .signal-red { background-color: rgba(211, 47, 47, 0.15); }

        /* 변동 지시자 */
        .color-up { color: #D32F2F; }
        .color-down { color: #2E7D32; }

        /* 전략 카드 */
        .strategy-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #00695C;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        /* AI 박스 */
        .ai-box {
            background: linear-gradient(135deg, #F5F5F5 0%, #EEEEEE 100%);
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid #00695C;
            margin-top: 16px;
        }

        /* 규제 아이템 */
        .regulation-item {
            background-color: #FAFAFA;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #00695C;
        }

        /* ===========================================
           9. 사이드바 숨기기
           =========================================== */
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* ===========================================
           10. 정보 박스 스타일
           =========================================== */
        .rate-box {
            background-color: #E8F5E9;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            color: #2E7D32;
        }

        /* 패널 하이라이트 */
        .panel-highlight {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #E0E0E0;
        }
    </style>
    """, unsafe_allow_html=True)


def get_metric_html(label: str, value: str, delta: str = None, delta_color: str = "#2E7D32"):
    """
    커스텀 메트릭 HTML을 반환합니다.
    
    Args:
        label: 메트릭 라벨
        value: 메트릭 값
        delta: 변동값 (선택사항)
        delta_color: 변동값 색상
    
    Returns:
        HTML 문자열
    """
    delta_html = ""
    if delta:
        delta_html = f"""
        <div class="metric-delta" style="color: {delta_color};">
            <span class="delta-badge" style="background-color: {delta_color}15; padding: 2px 6px; border-radius: 4px;">
                {delta}
            </span>
        </div>
        """
    
    return f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """


def get_signal_card_html(emoji: str, title: str, description: str, detail: str):
    """
    신호등 스타일 카드 HTML을 반환합니다.
    
    Args:
        emoji: 신호 이모지 (🟢, 🟡, 🔴)
        title: 카드 제목
        description: 설명
        detail: 세부 정보
    """
    signal_class = {
        "🟢": "signal-green",
        "🟡": "signal-yellow",
        "🔴": "signal-red"
    }.get(emoji, "signal-green")
    
    return f"""
    <div class="signal-card">
        <div style="display: flex; align-items: center;">
            <div class="traffic-light {signal_class}">{emoji}</div>
            <div>
                <h3 style="margin: 0; color: #333333; font-size: 1.1rem;">{title}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #333333; font-size: 0.95rem; font-weight: 500;">{description}</p>
                <p style="margin: 0.25rem 0 0 0; color: #666; font-size: 0.85rem;">{detail}</p>
            </div>
        </div>
    </div>
    """
