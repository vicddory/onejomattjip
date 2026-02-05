# -*- coding: utf-8 -*-
"""
================================================================================
📁 utils/api_helpers.py - API 호출 관련 유틸리티 함수
================================================================================
환율, 날씨, 주식 시세 등 외부 API 호출 함수들을 모아놓은 파일입니다.

💡 팁:
- 모든 API 함수는 오류 발생 시 기본값을 반환하도록 설계되어 있습니다.
- 캐싱을 통해 불필요한 API 호출을 줄입니다.
================================================================================
"""

import requests
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from config import EXCHANGE_API_KEY, WEATHER_API_KEY, COLOR_PRIMARY


# ===========================================
# 1. 환율 관련 함수
# ===========================================

def get_exchange_rate() -> float:
    """
    USD/KRW 실시간 환율을 가져옵니다.
    
    Returns:
        float: 환율 (실패 시 기본값 1445.0)
    """
    try:
        if not EXCHANGE_API_KEY:
            return 1445.0
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
        res = requests.get(url, timeout=10).json()
        return res['conversion_rates']['KRW']
    except Exception:
        return 1445.0


def get_exchange_rate_with_status():
    """
    환율을 가져오고 상태 메시지도 함께 반환합니다.
    
    Returns:
        tuple: (환율 또는 None, 상태 메시지)
    """
    try:
        if not EXCHANGE_API_KEY:
            return None, "❌ .env 파일에서 'EXCHANGE_RATE' 키를 찾을 수 없습니다."
        
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if "conversion_rates" in data and "KRW" in data["conversion_rates"]:
                return data["conversion_rates"]["KRW"], "✅ 실시간 환율을 성공적으로 불러왔습니다."
            return None, "⚠️ 응답은 받았으나 KRW 환율 정보가 없습니다."
        return None, f"⚠️ API 서버 오류 (코드: {response.status_code})"
    except Exception as e:
        return None, f"❌ 연결 오류: {str(e)}"


def get_current_local_rate(currency_code: str):
    """
    특정 통화의 USD 대비 환율을 Yahoo Finance에서 가져옵니다.
    
    Args:
        currency_code: 통화 코드 (예: "ETB", "BRL")
    
    Returns:
        float 또는 None
    """
    try:
        ticker = f"{currency_code}=X" if currency_code != "USD" else "USDKRW=X"
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        return None
    except Exception:
        return None


# ===========================================
# 2. 시장 데이터 함수
# ===========================================

@st.cache_data(ttl=300)
def get_market_data(ticker: str):
    """
    Yahoo Finance에서 시장 데이터를 가져옵니다.
    
    Args:
        ticker: Yahoo Finance 티커 (예: "KC=F" for Coffee)
    
    Returns:
        tuple: (현재가, 변동률%)
    """
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if not df.empty and len(df) >= 2:
            curr = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            change = ((curr - prev) / prev) * 100
            return round(curr, 2), round(change, 2)
        return 0.0, 0.0
    except Exception:
        return 0.0, 0.0


def get_history_rate(currency_code: str, period: str):
    """
    환율 히스토리 차트를 생성합니다.
    
    Args:
        currency_code: 통화 코드
        period: 기간 ("1y", "5y", "10y", "max")
    
    Returns:
        plotly Figure 또는 None
    """
    try:
        ticker = f"{currency_code}=X" if currency_code != "USD" else "USDKRW=X"
        df = yf.Ticker(ticker).history(period=period)
        if df.empty:
            return None
        
        fig = go.Figure(data=[
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                line=dict(color=COLOR_PRIMARY)
            )
        ])
        fig.update_layout(
            title=f"{currency_code} / USD History ({period.upper()})",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10),
            template="plotly_white"
        )
        return fig
    except Exception:
        return None


# ===========================================
# 3. 날씨 API 함수
# ===========================================

def get_country_weather(city_name: str):
    """
    OpenWeatherMap API를 사용하여 도시 날씨를 가져옵니다.
    
    Args:
        city_name: 도시 이름 (영문)
    
    Returns:
        dict: {'temp': 온도, 'desc_ko': 한글 설명, 'desc_en': 영문 설명}
    """
    try:
        if not WEATHER_API_KEY:
            return {'temp': 0, 'desc_ko': "API키 없음", 'desc_en': "No API Key"}
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=en"
        res = requests.get(url, timeout=10).json()
        
        if res.get('cod') != 200:
            return {'temp': 0, 'desc_ko': "정보 없음", 'desc_en': "No Info"}
        
        desc_en = res['weather'][0]['description']
        temp = res['main']['temp']
        
        # 영문 → 한글 변환
        weather_map = {
            'clear sky': '맑음',
            'few clouds': '구름 조금',
            'scattered clouds': '구름 낌',
            'broken clouds': '구름 많음',
            'overcast clouds': '흐림',
            'light rain': '약한 비',
            'moderate rain': '비',
            'heavy intensity rain': '강한 비',
            'thunderstorm': '뇌우',
            'snow': '눈',
            'mist': '안개',
            'haze': '연무'
        }
        desc_ko = weather_map.get(desc_en, desc_en)
        
        return {'temp': temp, 'desc_ko': desc_ko, 'desc_en': desc_en}
    except Exception:
        return {'temp': 0, 'desc_ko': "수신 불가", 'desc_en': "Error"}
