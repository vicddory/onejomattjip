# pip install streamlit pandas folium streamlit-folium plotly

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import BeautifyIcon

# 상대 경로 import (패키지 구조) - 기존 코드 유지
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 외부 모듈 임포트 (기존 코드 유지)
try:
    from config import get_coffee_origins, COLOR_PRIMARY, COLOR_SECONDARY
    from utils import get_exchange_rate, get_market_data, get_current_local_rate, get_history_rate
except ImportError:
    # 더미 데이터 및 설정 (Import 실패 시 대비)
    COLOR_PRIMARY = "#4B2C20"
    COLOR_SECONDARY = "#6F4E37"
    def get_coffee_origins():
        return {
            "에티오피아": {"lat": 9.145, "lon": 40.4896, "desc": "커피의 고향", "hs_code": "0901.11", "port": "Djibouti", "lead_time": "45 days", "currency": "ETB", "docs": ["B/L", "Invoice"]}
        }
    def get_exchange_rate(): return 1350.0
    def get_market_data(ticker): return 250.0, 1.5
    def get_current_local_rate(curr): return 56.0
    def get_history_rate(curr, p): return None

def show():
    """
    랜딩 페이지를 렌더링하는 메인 함수입니다.
    """
    # ===========================================
    # 1. 데이터 로드
    # ===========================================
    try:
        data = get_coffee_origins()
        current_krw_rate = get_exchange_rate()
        coffee_p, coffee_c = get_market_data("KC=F")
    except Exception:
        st.error("데이터를 불러오는 중 에러가 발생했습니다.")
        return

    # ===========================================
    # 2. 페이지 헤더
    # ===========================================
    st.markdown("<h1 style='text-align: center;'>세계 원두 산지</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    
    # ===========================================
    # 3. 상단 메트릭
    # ===========================================
    usd_arrow = "↔"
    usd_color = "#2E7D32"
    usd_bg = "#E8F5E9"

    if coffee_c < 0:
        ice_color = "#D32F2F"
        ice_bg = "#FFEBEE"
        ice_arrow = "▼"
    else:
        ice_color = "#2E7D32"
        ice_bg = "#E8F5E9"
        ice_arrow = "▲"

    # [수정됨] CSS 스타일 정의 (박스 디자인 및 안내창 스타일)
    st.markdown(f"""
    <style>
    .metric-box {{
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 10px 15px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        height: 100%; /* 높이 채우기 */
    }}
    .metric-label {{
        color: #666;
        font-size: 11px;
        font-weight: 500;
        margin-bottom: 4px;
    }}
    .metric-value {{
        font-size: 18px;
        font-weight: 700;
        color: #333;
        margin-bottom: 4px;
    }}
    .delta-badge {{
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 10px;
    }}
    /* 안내창 디자인 유지 */
    .empty-state-card {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 600px;
        text-align: center;
        padding: 40px;
        margin-top: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # [수정됨] st.columns를 사용하여 두 박스를 물리적으로 분리
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">USD / KRW (오늘의 환율)</div>
            <div class="metric-value">{current_krw_rate:,.1f} 원</div>
            <div style="color: {usd_color}; font-size: 10px;">
                <span class="delta-badge" style="background-color: {usd_bg};">
                    {usd_arrow} Real-time
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">ICE Arabica (NY) / 커피 시세</div>
            <div class="metric-value">${coffee_p:,.2f}</div>
            <div style="color: {ice_color}; font-size: 10px;">
                <span class="delta-badge" style="background-color: {ice_bg};">
                    {ice_arrow} {coffee_c:+.2f}%
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ===========================================
    # 4. 메인 레이아웃 (지도 | 정보 패널)
    # ===========================================
    col_map, col_info = st.columns([1.5, 1])
    
    with col_map:
        st.markdown(f"<h3 style='color: {COLOR_SECONDARY}; margin-top: 0;'>세계 원두 산지 지도</h3>", unsafe_allow_html=True)

        m = folium.Map(
            location=[15, 10],
            zoom_start=2,
            tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
            attr='&copy; OpenStreetMap &copy; CARTO',
            min_zoom=2
        )

        for name, info in data.items():
            icon = BeautifyIcon(
                icon="coffee",
                icon_shape="marker",
                background_color=COLOR_PRIMARY,
                text_color="white",
                border_color=COLOR_PRIMARY,
                inner_icon_style="font-size: 11px; margin-left: 3px; margin-top: 2px;"
            )
            popup_content = folium.Popup(name, max_width=300, min_width=100)
            folium.Marker(
                location=[info["lat"], info["lon"]],
                popup=popup_content,
                icon=icon
            ).add_to(m)

        # [수정됨] 높이를 900 -> 700으로 조정하여 우측 정보창 끝부분과 얼추 맞춤
        map_data = st_folium(m, width="100%", height=700)
    
    with col_info:
        selected_country = map_data.get("last_object_clicked_popup")
        
        if selected_country and selected_country in data:
            info = data[selected_country]
            st.markdown(f"<h3 style='color: {COLOR_SECONDARY}; margin-top: 0;'> {selected_country}</h3>", unsafe_allow_html=True)
            st.markdown(f"**• 특징:**\n\n{info['desc']}", unsafe_allow_html=True)

            details = pd.DataFrame({
                "Trade Item / 항목": ["HS Code / 세번부호", "Loading Port / 선적항", "Lead Time / 리드타임"],
                "Details / 상세내용": [info['hs_code'], info['port'], info['lead_time']]
            })
            details.index = details.index + 1
            st.table(details)
            
            st.write("**• 환율 변동 내역:**")
            local_rate = get_current_local_rate(info['currency'])
            if local_rate:
                st.markdown(f"""
                <div style="background-color: #E8F5E9; padding: 12px; border-radius: 8px; text-align: center; font-weight: 600; color: #2E7D32;">
                    현재 실시간 환율: 1 달러 = {local_rate:,} {info['currency']}
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")
            c1, c2 = st.columns([4, 6])
            with c1: st.markdown("**• 기간 선택:**")
            with c2:
                selected_period = st.radio("", ["1y", "5y", "10y", "max"], horizontal=True, key="landing_period")

            fig = get_history_rate(info['currency'], selected_period)
            if fig: st.plotly_chart(fig, use_container_width=True)
            
            st.write("**• 필수 서류:**")
            clean_docs = [doc.replace("<b>", "").replace("</b>", "") for doc in info['docs']]
            docs_df = pd.DataFrame({"Required Documents / 필수 서류": clean_docs})
            docs_df.index = docs_df.index + 1
            st.table(docs_df)
            
        else:
            # [수정 사항 반영] 손가락 아이콘을 텍스트 위 중앙에 배치
            st.markdown("""
            <div class="empty-state-card">
                <div style="font-size: 60px; line-height: 1; margin-bottom: 20px;">👆</div>
                <div style="font-size: 20px; font-weight: 700; color: #9E9E9E; margin-bottom: 10px;">
                    좌측 지도에서<br>원하는 산지의 핀을 클릭해주세요.
                </div>
                <div style="font-size: 14px; color: #BDBDBD;">
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()