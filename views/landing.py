# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/landing.py - 메인 랜딩 페이지 (홈)
================================================================================
세계 커피 산지 지도와 실시간 시세를 보여주는 메인 화면입니다.

💡 이 파일의 역할:
- 대화형 세계 지도 표시 (Folium)
- 실시간 환율 및 커피 시세 표시
- 산지 클릭 시 상세 정보 표시
================================================================================
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import BeautifyIcon

# 상대 경로 import (패키지 구조)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_coffee_origins, COLOR_PRIMARY, COLOR_SECONDARY
from utils import get_exchange_rate, get_market_data, get_current_local_rate, get_history_rate


def show():
    """
    랜딩 페이지를 렌더링하는 메인 함수입니다.
    main.py에서 이 함수를 호출하여 화면을 표시합니다.
    """
    # ===========================================
    # 1. 데이터 로드
    # ===========================================
    data = get_coffee_origins()
    current_krw_rate = get_exchange_rate()
    coffee_p, coffee_c = get_market_data("KC=F")
    
    # ===========================================
    # 2. 페이지 헤더
    # ===========================================
    st.markdown("<h1 style='text-align: center;'>글로벌 원두 무역 대시보드</h1>", unsafe_allow_html=True)
    st.markdown('<hr style="border-top: 2px solid #00695C; margin: 30px 0;">', unsafe_allow_html=True)
    
    # ===========================================
    # 3. 메인 레이아웃 (지도 | 정보 패널)
    # ===========================================
    col_map, col_info = st.columns([1.5, 1])
    
    with col_map:
        # -----------------------------------------
        # 3-1. 상단 메트릭 (환율, 커피 시세)
        # -----------------------------------------
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

        st.markdown(f"""
        <style>
        .metric-container {{
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .metric-box {{
            flex: 1;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 6px 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        .metric-label {{
            color: #666;
            font-size: 11px;
            font-weight: 500;
        }}
        .metric-value {{
            font-size: 18px;
            font-weight: 700;
            color: #333;
        }}
        .delta-badge {{
            padding: 1px 4px;
            border-radius: 3px;
            font-size: 10px;
        }}
        </style>
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-label">USD / KRW (오늘의 환율)</div>
                <div class="metric-value">{current_krw_rate:,.1f} 원</div>
                <div style="color: {usd_color}; font-size: 10px;">
                    <span class="delta-badge" style="background-color: {usd_bg};">
                        {usd_arrow} Real-time
                    </span>
                </div>
            </div>
            <div class="metric-box">
                <div class="metric-label">ICE Arabica (NY) / 커피 시세</div>
                <div class="metric-value">${coffee_p:,.2f}</div>
                <div style="color: {ice_color}; font-size: 10px;">
                    <span class="delta-badge" style="background-color: {ice_bg};">
                        {ice_arrow} {coffee_c:+.2f}%
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='color: {COLOR_SECONDARY};'>세계 원두 산지 지도</h3>", unsafe_allow_html=True)
        
        # -----------------------------------------
        # 3-2. Folium 지도 생성
        # -----------------------------------------
        m = folium.Map(
            location=[15, 10],
            zoom_start=2,
            tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
            attr='&copy; OpenStreetMap &copy; CARTO',
            min_zoom=2
        )

        # 각 산지에 마커 추가
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

        # 지도 렌더링
        map_data = st_folium(m, width="100%", height=900)
    
    # -----------------------------------------
    # 3-3. 정보 패널 (산지 상세 정보)
    # -----------------------------------------
    with col_info:
        selected_country = map_data.get("last_object_clicked_popup")
        
        if selected_country and selected_country in data:
            info = data[selected_country]
            
            st.markdown(f"<h3 style='color: {COLOR_SECONDARY};'> {selected_country}</h3>", unsafe_allow_html=True)
            
            # 특징
            st.markdown(f"""
**• 특징:**

{info['desc']}
""", unsafe_allow_html=True)

            # 무역 정보 테이블
            details = pd.DataFrame({
                "Trade Item / 항목": ["HS Code / 세번부호", "Loading Port / 선적항", "Lead Time / 리드타임"],
                "Details / 상세내용": [info['hs_code'], info['port'], info['lead_time']]
            })
            st.table(details)
            
            # 환율 정보
            st.write("**• 환율 변동 내역:**")
            local_rate = get_current_local_rate(info['currency'])
            if local_rate:
                st.markdown(f"""
<div style="background-color: #E8F5E9; padding: 12px; border-radius: 8px; text-align: center; font-weight: 600; color: #2E7D32;">
    현재 실시간 환율: 1 달러 = {local_rate:,} {info['currency']}
</div>
""", unsafe_allow_html=True)
            
            # 기간 선택 및 차트
            st.write("")
            c1, c2 = st.columns([1, 5])
            with c1:
                st.markdown("**• 기간 선택:**")
            with c2:
                selected_period = st.radio(
                    "",
                    ["1y", "5y", "10y", "max"],
                    horizontal=True,
                    key="landing_period"
                )

            fig = get_history_rate(info['currency'], selected_period)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # 필수 서류 테이블
            st.write("**• 필수 서류:**")
            clean_docs = [doc.replace("<b>", "").replace("</b>", "") for doc in info['docs']]
            docs_df = pd.DataFrame({
                "Required Documents / 필수 서류": clean_docs
            })
            st.table(docs_df)
            
        else:
            st.info("👆 지도에서 생산국 핀을 클릭하세요.")


# 모듈 직접 실행 시 (테스트용)
if __name__ == "__main__":
    show()
