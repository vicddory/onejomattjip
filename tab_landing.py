# -*- coding: utf-8 -*-
"""
Tab: Landing Page - 글로벌 커피 산지 지도 대시보드
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import requests
import yfinance as yf
from dotenv import load_dotenv
import plotly.graph_objects as go

# 환경 변수 로드
load_dotenv()

# ==========================================
# 지원 함수 (API 및 데이터 로직)
# ==========================================

def get_exchange_rate():
    """실시간 USD/KRW 환율 (국내 정산용)"""
    try:
        api_key = os.getenv("EXCHANGE_RATE")
        if not api_key:
            return 1445.0
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        res = requests.get(url, timeout=10).json()
        return res['conversion_rates']['KRW']
    except:
        return 1445.0

def get_current_local_rate(currency_code):
    """선택된 국가의 USD 대비 현재 환율"""
    try:
        ticker = f"{currency_code}=X" if currency_code != "USD" else "USDKRW=X"
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        return None
    except:
        return None

def get_market_data(ticker):
    """ICE Arabica 선물 시세"""
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty:
            curr = df['Close'].iloc[-1]
            change = ((curr - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            return round(curr, 2), round(change, 2)
        return 0.0, 0.0
    except:
        return 0.0, 0.0

def get_history_rate(currency_code, period):
    """국가별 환율 추이 그래프 (1y, 5y, 10y, max)"""
    try:
        ticker = f"{currency_code}=X" if currency_code != "USD" else "USDKRW=X"
        df = yf.Ticker(ticker).history(period=period)
        if df.empty:
            return None
        
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='#1f77b4'))])
        fig.update_layout(
            title=f"{currency_code} / USD History ({period.upper()})",
            height=300, margin=dict(l=10, r=10, t=40, b=10),
            template="plotly_white"
        )
        return fig
    except:
        return None

def get_coffee_data():
    """무역 실무 데이터 (한영 병기 및 서류 목록 진하게)"""
    bold_docs = [
        "<b>B/L (Bill of Lading / 선하증권)</b>", 
        "<b>Commercial Invoice (상업송장)</b>", 
        "<b>Packing List (포장명세서)</b>", 
        "<b>Phytosanitary Certificate (식물검역증)</b>"
    ]
    
    return {
        "Ethiopia (에티오피아)": {"currency": "ETB", "lat": 9.145, "lon": 40.4897, "port": "Djibouti", "hs_code": "0901.11-0000", "lead_time": "45-60 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "화사한 꽃향기와 세련된 산미 / Floral & Bright Acidity"},
        "Brazil (브라질)": {"currency": "BRL", "lat": -14.235, "lon": -51.9253, "port": "Santos", "hs_code": "0901.11-0000", "lead_time": "40-55 Days", "docs": bold_docs, "desc": "고소함과 우수한 밸런스 / Nutty & Well-balanced"},
        "Vietnam (베트남)": {"currency": "VND", "lat": 14.0583, "lon": 108.2772, "port": "Ho Chi Minh", "hs_code": "0901.11-0000", "lead_time": "15-25 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "강한 바디감과 구수한 맛 / Bold Body & Roasted Flavor"},
        "Colombia (콜롬비아)": {"currency": "COP", "lat": 4.5709, "lon": -74.2973, "port": "Buenaventura", "hs_code": "0901.11-0000", "lead_time": "35-50 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "부드러운 마일드 커피의 대명사 / Classic Mild Coffee"},
        "Guatemala (과테말라)": {"currency": "GTQ", "lat": 15.7835, "lon": -90.2308, "port": "Puerto Barrios", "hs_code": "0901.11-0000", "lead_time": "30-45 Days", "docs": bold_docs, "desc": "스모키한 향과 초콜릿 풍미 / Smoky & Chocolate Flavor"},
        "Kenya (케냐)": {"currency": "KES", "lat": -1.2921, "lon": 36.8219, "port": "Mombasa", "hs_code": "0901.11-0000", "lead_time": "45-60 Days", "docs": bold_docs, "desc": "강렬한 산미와 와인 같은 후미 / Intense Acidity & Winey"},
        "Costa Rica (코스타리카)": {"currency": "CRC", "lat": 9.7489, "lon": -83.7534, "port": "Limon", "hs_code": "0901.11-0000", "lead_time": "35-50 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "섬세하고 우아한 향미 / Delicate & Elegant Flavor"},
        "Peru (페루)": {"currency": "PEN", "lat": -9.19, "lon": -75.0152, "port": "Callao", "hs_code": "0901.11-0000", "lead_time": "40-55 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "부드러운 단맛과 유기농 품질 / Mild Sweetness & Organic"},
        "Indonesia (인도네시아)": {"currency": "IDR", "lat": -0.7893, "lon": 113.9213, "port": "Jakarta", "hs_code": "0901.11-0000", "lead_time": "20-35 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "묵직한 바디와 독특한 흙내음 / Heavy Body & Earthy Flavor"},
        "Honduras (온두라스)": {"currency": "HNL", "lat": 15.2, "lon": -86.2419, "port": "Puerto Cortes", "hs_code": "0901.11-0000", "lead_time": "35-50 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "부드러운 단맛과 가성비 / Mild Sweetness & Cost-effective"}
    }

# ==========================================
# 메인 show 함수
# ==========================================
def show():
    """Landing Page를 렌더링하는 메인 함수"""
    
    # CSS 스타일
    st.markdown("""
        <style>
        .panel-highlight {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #1f77b4;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }
        .rate-box {
            background-color: #f1f3f5;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 15px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    data = get_coffee_data()
    current_krw_rate = get_exchange_rate()
    coffee_p, coffee_c = get_market_data("KC=F")
    
    st.title("☕ Global Coffee Trade Dashboard")
    st.caption("조성빈, 강정민 프로젝트 - 한영 병기 및 실시간 환율 분석기")
    
    # 상단 지표
    m1, m2 = st.columns(2)
    m1.metric("USD / KRW (오늘의 환율)", f"{current_krw_rate:,.1f} 원", "Real-time")
    m2.metric("ICE Arabica (NY) / 커피 시세", f"${coffee_p:,.2f}", f"{coffee_c:+.2f}%")
    
    st.divider()
    
    col_map, col_info = st.columns([1.5, 1])
    
    with col_map:
        st.subheader("📍 World Coffee Origin Map (산지 지도)")
        m = folium.Map(location=[15, 10], zoom_start=2, tiles="CartoDB Voyager", min_zoom=2)
        for name, info in data.items():
            folium.Marker(
                location=[info["lat"], info["lon"]], 
                popup=name, 
                icon=folium.Icon(color="darkblue", icon="coffee", prefix="fa")
            ).add_to(m)
        map_data = st_folium(m, width="100%", height=600)
    
    with col_info:
        selected_country = map_data.get("last_object_clicked_popup") if map_data else None
        
        if selected_country and selected_country in data:
            info = data[selected_country]
            st.markdown('<div class="panel-highlight">', unsafe_allow_html=True)
            st.subheader(f"📑 {selected_country} Panel")
            
            st.write(f"ℹ️ **Description / 특징:** {info['desc']}")
            
            # 무역 상세 표 (한영 병기)
            details = pd.DataFrame({
                "Trade Item / 항목": ["HS Code / 세번부호", "Loading Port / 선적항", "Lead Time / 리드타임"],
                "Details / 상세내용": [info['hs_code'], info['port'], info['lead_time']]
            })
            st.table(details)
            
            st.write("📈 **Exchange Rate History / 환율 분석**")
            
            # 실시간 현지 환율 표시
            local_rate = get_current_local_rate(info['currency'])
            if local_rate:
                st.markdown(f"""
                    <div class="rate-box">
                        Current Exchange Rate: 1 USD = {local_rate:,} {info['currency']}<br>
                        (현재 실시간 환율: 1 달러 = {local_rate:,} {info['currency']})
                    </div>
                """, unsafe_allow_html=True)
            
            # 기간 선택 버튼
            selected_period = st.radio("Select Period / 기간 선택", ["1y", "5y", "10y", "max"], horizontal=True)
            
            fig = get_history_rate(info['currency'], selected_period)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            st.write("📋 **Required Documents / 필수 서류**")
            for doc in info['docs']:
                st.markdown(f"- {doc}", unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("지도에서 생산국 핀을 클릭하세요. (Click a country on the map)")
