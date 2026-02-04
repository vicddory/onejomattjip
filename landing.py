import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import requests
import yfinance as yf
from dotenv import load_dotenv
import plotly.graph_objects as go
from folium.plugins import BeautifyIcon

# 0. 환경 설정
load_dotenv()
EXCHANGE_API_KEY = os.getenv("EXCHANGE_RATE")

# ==========================================
# 1. 지원 함수 (API 및 데이터 로직)
# ==========================================

def get_exchange_rate():
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
        res = requests.get(url).json()
        return res['conversion_rates']['KRW']
    except: return 1445.0

def get_current_local_rate(currency_code):
    try:
        ticker = f"{currency_code}=X" if currency_code != "USD" else "USDKRW=X"
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        return None
    except: return None

def get_market_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty:
            curr = df['Close'].iloc[-1]
            change = ((curr - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            return round(curr, 2), round(change, 2)
        return 0.0, 0.0
    except: return 0.0, 0.0

def get_history_rate(currency_code, period):
    try:
        ticker = f"{currency_code}=X" if currency_code != "USD" else "USDKRW=X"
        df = yf.Ticker(ticker).history(period=period)
        if df.empty: return None
        
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='#00695C'))])
        fig.update_layout(
            title=f"{currency_code} / USD History ({period.upper()})",
            height=300, margin=dict(l=10, r=10, t=40, b=10),
            template="plotly_white"
        )
        return fig
    except: return None

def get_coffee_data():
    bold_docs = ["<b>B/L (Bill of Lading / 선하증권)</b>", "<b>Commercial Invoice (상업송장)</b>", 
                 "<b>Packing List (포장명세서)</b>", "<b>Phytosanitary Certificate (식물검역증)</b>"]
    return {
        "에티오피아": {"currency": "ETB", "lat": 9.145, "lon": 40.4897, "port": "Djibouti", "hs_code": "0901.11-0000", "lead_time": "45-60 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "화사한 꽃향기와 세련된 산미 / Floral & Bright Acidity"},
        "브라질": {"currency": "BRL", "lat": -14.235, "lon": -51.9253, "port": "Santos", "hs_code": "0901.11-0000", "lead_time": "40-55 Days", "docs": bold_docs, "desc": "고소함과 우수한 밸런스 / Nutty & Well-balanced"},
        "베트남": {"currency": "VND", "lat": 14.0583, "lon": 108.2772, "port": "Ho Chi Minh", "hs_code": "0901.11-0000", "lead_time": "15-25 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "강한 바디감과 구수한 맛 / Bold Body & Roasted Flavor"},
        "콜롬비아": {"currency": "COP", "lat": 4.5709, "lon": -74.2973, "port": "Buenaventura", "hs_code": "0901.11-0000", "lead_time": "35-50 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "부드러운 마일드 커피의 대명사 / Classic Mild Coffee"},
        "과테말라": {"currency": "GTQ", "lat": 15.7835, "lon": -90.2308, "port": "Puerto Barrios", "hs_code": "0901.11-0000", "lead_time": "30-45 Days", "docs": bold_docs, "desc": "스모키한 향과 초콜릿 풍미 / Smoky & Chocolate Flavor"},
        "케냐": {"currency": "KES", "lat": -1.2921, "lon": 36.8219, "port": "Mombasa", "hs_code": "0901.11-0000", "lead_time": "45-60 Days", "docs": bold_docs, "desc": "강렬한 산미와 와인 같은 후미 / Intense Acidity & Winey"},
        "코스타리카": {"currency": "CRC", "lat": 9.7489, "lon": -83.7534, "port": "Limon", "hs_code": "0901.11-0000", "lead_time": "35-50 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "섬세하고 우아한 향미 / Delicate & Elegant Flavor"},
        "페루": {"currency": "PEN", "lat": -9.19, "lon": -75.0152, "port": "Callao", "hs_code": "0901.11-0000", "lead_time": "40-55 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "부드러운 단맛과 유기농 품질 / Mild Sweetness & Organic"},
        "인도네시아": {"currency": "IDR", "lat": -0.7893, "lon": 113.9213, "port": "Jakarta", "hs_code": "0901.11-0000", "lead_time": "20-35 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "묵직한 바디와 독특한 흙내음 / Heavy Body & Earthy Flavor"},
        "온두라스": {"currency": "HNL", "lat": 15.2, "lon": -86.2419, "port": "Puerto Cortes", "hs_code": "0901.11-0000", "lead_time": "35-50 Days", "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"], "desc": "부드러운 단맛과 가성비 / Mild Sweetness & Cost-effective"}
    }

# ==========================================
# 2. UI 레이아웃
# ==========================================

st.set_page_config(layout="wide", page_title="Coffee AX Master Hub")

# CSS: 스타일 보강
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input, 
    .stSelectbox > div > div > div {
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton > button {
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .stTabs [aria-selected="true"] {
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px !important; 
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important; 
    }
</style>
""", unsafe_allow_html=True)

data = get_coffee_data()
current_krw_rate = get_exchange_rate()
coffee_p, coffee_c = get_market_data("KC=F")

st.markdown("<h1 style='text-align: center;'>글로벌 원두 무역 대시보드</h1>", unsafe_allow_html=True)
st.markdown('<hr style="border-top: 2px solid #00695C; margin: 30px 0;">', unsafe_allow_html=True)

col_map, col_info = st.columns([1.5, 1])

with col_map:
    # 1. 변수 설정
    usd_arrow = "↑"
    usd_color = "#2E7D32" # 초록
    usd_bg = "#E8F5E9"

    if coffee_c < 0:
        ice_color = "#D32F2F" # 빨강
        ice_bg = "#FFEBEE"
        ice_arrow = "▼"
    else:
        ice_color = "#2E7D32" # 초록
        ice_bg = "#E8F5E9"
        ice_arrow = "▲"

    # 2. HTML 렌더링
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
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.metric-label {{
    color: #666;
    font-size: 11px;
    margin-bottom: 0px;
    font-weight: 500;
}}
.metric-value {{
    font-size: 18px;
    font-weight: 700;
    color: #333;
    line-height: 1.2;
}}
.metric-delta {{
    font-size: 10px;
    font-weight: 500;
    margin-top: 2px;
}}
.delta-badge {{
    padding: 1px 4px; 
    border-radius: 3px;
}}
</style>
<div class="metric-container">
    <div class="metric-box">
        <div class="metric-label">USD / KRW (오늘의 환율)</div>
        <div class="metric-value">{current_krw_rate:,.1f} 원</div>
        <div class="metric-delta" style="color: {usd_color};">
            <span class="delta-badge" style="background-color: {usd_bg};">
                {usd_arrow} Real-time
            </span>
        </div>
    </div>
    <div class="metric-box">
        <div class="metric-label">ICE Arabica (NY) / 커피 시세</div>
        <div class="metric-value">${coffee_p:,.2f}</div>
        <div class="metric-delta" style="color: {ice_color};">
            <span class="delta-badge" style="background-color: {ice_bg};">
                {ice_arrow} {coffee_c:+.2f}%
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #8B5A2B;'>세계 원두 산지 지도</h3>", unsafe_allow_html=True)
    
    # 3. 지도 생성
    m = folium.Map(
        location=[15, 10], 
        zoom_start=2, 
        tiles="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        min_zoom=2
    )

    for name, info in data.items():
        icon = BeautifyIcon(
            icon="coffee",
            icon_shape="marker",
            background_color="#00695C",
            text_color="white",
            border_color="#00695C",
            inner_icon_style="font-size: 11px; margin-left: 3px; margin-top: 2px;"
        )
        
        popup_content = folium.Popup(name, max_width=300, min_width=100)
        
        folium.Marker(
            location=[info["lat"], info["lon"]], 
            popup=popup_content, 
            icon=icon
        ).add_to(m)
        
    map_data = st_folium(m, width="100%", height=900)

with col_info:
    selected_country = map_data.get("last_object_clicked_popup")
    
    if selected_country:
        info = data[selected_country]
        st.markdown(f'<div class="panel-highlight">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #8B5A2B;'> {selected_country}</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
**• 특징:**

{info['desc']}
""", unsafe_allow_html=True)

        details = pd.DataFrame({
            "Trade Item / 항목": ["HS Code / 세번부호", "Loading Port / 선적항", "Lead Time / 리드타임"],
            "Details / 상세내용": [info['hs_code'], info['port'], info['lead_time']]
        })
        st.table(details)
        
        st.write("**• 환율 변동 내역:**")
        
        local_rate = get_current_local_rate(info['currency'])
        if local_rate:
            st.markdown(f"""
<div class="rate-box">
    현재 실시간 환율: 1 달러 = {local_rate:,} {info['currency']}
</div>
""", unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns([1, 5])
        with c1:
            st.markdown("**• 기간 선택:**")
        
        with c2:
            selected_period = st.radio(
                "",
                ["1y", "5y", "10y", "max"],
                horizontal=True
            )

        fig = get_history_rate(info['currency'], selected_period)
        if fig: st.plotly_chart(fig, use_container_width=True)
        
        st.write("**• 필수 서류:**")
        
        # [수정] 표(Table) 형태로 변경
        clean_docs = [doc.replace("<b>", "").replace("</b>", "") for doc in info['docs']]
        docs_df = pd.DataFrame({
            "Required Documents / 필수 서류": clean_docs
        })
        st.table(docs_df)
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("지도에서 생산국 핀을 클릭하세요.")