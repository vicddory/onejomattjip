# -*- coding: utf-8 -*-
"""
================================================================================
📁 config.py - 전역 설정 및 상수 관리
================================================================================
이 파일은 프로젝트 전체에서 사용되는 API 키, 색상 상수, 데이터 설정 등을
한 곳에서 관리합니다.

💡 팁:
- .env 파일에 실제 API 키를 저장하고 이 파일에서 불러옵니다.
- 색상을 변경하고 싶으면 이 파일의 COLOR_ 변수들만 수정하면 됩니다.
================================================================================
"""

import os
from dotenv import load_dotenv

# ===========================================
# 1. 환경 변수 로드 (.env 파일에서 API 키 불러오기)
# ===========================================
# .env 파일이 프로젝트 루트에 있어야 합니다.
# 예시 .env 파일 내용:
#   EXCHANGE_RATE=your_api_key_here
#   WEATHER_API_KEY=your_api_key_here
#   OPENAI_API_KEY=your_api_key_here

load_dotenv()

# API 키들 (없으면 None 반환)
EXCHANGE_API_KEY = os.getenv("EXCHANGE_RATE")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 네이버 API (tab4에서 사용) - 직접 입력 필요
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "네이버 API ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "네이버 API 비밀번호")

# ===========================================
# 2. 색상 상수 (앱 전체 테마)
# ===========================================
# 메인 브랜드 컬러
COLOR_PRIMARY = "#00695C"       # Deep Emerald (메인 포인트 컬러)
COLOR_SECONDARY = "#6F4E37"     # Coffee Brown (보조 포인트)
COLOR_BACKGROUND = "#FAFAFA"    # Off-White (배경색)

# 커피 관련 색상
COLOR_ROAST = "#4B2E2A"         # 진한 로스팅 색
COLOR_DEEP_COFFEE = "#362419"   # 더 진한 커피색

# 시그널/상태 색상
COLOR_SUCCESS = "#2E7D32"       # 초록 (성공/긍정)
COLOR_SAFE = "#388E3C"          # 안전 (초록)
COLOR_WARNING = "#F57C00"       # 경고 (주황)
COLOR_RISK = "#D32F2F"          # 위험 (빨강)
COLOR_NEUTRAL = "#757575"       # 중립 (회색)
COLOR_FUTURE_GOLD = "#FFD700"   # 미래/기회 (골드)

# 차트용 커피 팔레트 (10색)
COFFEE_PALETTE = [
    "#4B2E2A", "#6F4E37", "#A67B5B", "#D2B48C", "#E0C097",
    "#8D6E63", "#5D4037", "#3E2723", "#795548", "#A1887F"
]

# ===========================================
# 3. 기간 설정 (차트용)
# ===========================================
PERIOD_LABELS = {
    '1D': '24시간',
    '1W': '1주일',
    '1M': '1개월',
    '6M': '6개월',
    '1Y': '1년',
    '3Y': '3년'
}

# ===========================================
# 4. 커피 산지 기본 데이터
# ===========================================
def get_coffee_origins():
    """
    전 세계 커피 산지 기본 정보를 반환합니다.
    landing 페이지와 다른 탭에서 공통으로 사용됩니다.
    """
    bold_docs = [
        "<b>B/L (Bill of Lading / 선하증권)</b>",
        "<b>Commercial Invoice (상업송장)</b>",
        "<b>Packing List (포장명세서)</b>",
        "<b>Phytosanitary Certificate (식물검역증)</b>"
    ]
    
    return {
        "에티오피아": {
            "currency": "ETB", "lat": 9.145, "lon": 40.4897,
            "port": "Djibouti", "port_en": "Djibouti Port", "country_en": "Ethiopia",
            "hs_code": "0901.11-0000", "lead_time": "45-60 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "화사한 꽃향기와 세련된 산미 / Floral & Bright Acidity"
        },
        "브라질": {
            "currency": "BRL", "lat": -14.235, "lon": -51.9253,
            "port": "Santos", "port_en": "Santos Port", "country_en": "Brazil",
            "hs_code": "0901.11-0000", "lead_time": "40-55 Days",
            "docs": bold_docs,
            "desc": "고소함과 우수한 밸런스 / Nutty & Well-balanced"
        },
        "베트남": {
            "currency": "VND", "lat": 14.0583, "lon": 108.2772,
            "port": "Ho Chi Minh", "port_en": "Ho Chi Minh Port", "country_en": "Vietnam",
            "hs_code": "0901.11-0000", "lead_time": "15-25 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "강한 바디감과 구수한 맛 / Bold Body & Roasted Flavor"
        },
        "콜롬비아": {
            "currency": "COP", "lat": 4.5709, "lon": -74.2973,
            "port": "Buenaventura", "port_en": "Buenaventura Port", "country_en": "Colombia",
            "hs_code": "0901.11-0000", "lead_time": "35-50 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "부드러운 마일드 커피의 대명사 / Classic Mild Coffee"
        },
        "과테말라": {
            "currency": "GTQ", "lat": 15.7835, "lon": -90.2308,
            "port": "Puerto Barrios", "port_en": "Puerto Barrios Port", "country_en": "Guatemala",
            "hs_code": "0901.11-0000", "lead_time": "30-45 Days",
            "docs": bold_docs,
            "desc": "스모키한 향과 초콜릿 풍미 / Smoky & Chocolate Flavor"
        },
        "케냐": {
            "currency": "KES", "lat": -1.2921, "lon": 36.8219,
            "port": "Mombasa", "port_en": "Mombasa Port", "country_en": "Kenya",
            "hs_code": "0901.11-0000", "lead_time": "45-60 Days",
            "docs": bold_docs,
            "desc": "강렬한 산미와 와인 같은 후미 / Intense Acidity & Winey"
        },
        "코스타리카": {
            "currency": "CRC", "lat": 9.7489, "lon": -83.7534,
            "port": "Limon", "port_en": "Limon Port", "country_en": "Costa Rica",
            "hs_code": "0901.11-0000", "lead_time": "35-50 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "섬세하고 우아한 향미 / Delicate & Elegant Flavor"
        },
        "페루": {
            "currency": "PEN", "lat": -9.19, "lon": -75.0152,
            "port": "Callao", "port_en": "Callao Port", "country_en": "Peru",
            "hs_code": "0901.11-0000", "lead_time": "40-55 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "부드러운 단맛과 유기농 품질 / Mild Sweetness & Organic"
        },
        "인도네시아": {
            "currency": "IDR", "lat": -0.7893, "lon": 113.9213,
            "port": "Jakarta", "port_en": "Jakarta Port", "country_en": "Indonesia",
            "hs_code": "0901.11-0000", "lead_time": "20-35 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "묵직한 바디와 독특한 흙내음 / Heavy Body & Earthy Flavor"
        },
        "온두라스": {
            "currency": "HNL", "lat": 15.2, "lon": -86.2419,
            "port": "Puerto Cortes", "port_en": "Puerto Cortes Port", "country_en": "Honduras",
            "hs_code": "0901.11-0000", "lead_time": "35-50 Days",
            "docs": bold_docs + ["<b>C/O (Certificate of Origin / 원산지증명서)</b>"],
            "desc": "부드러운 단맛과 가성비 / Mild Sweetness & Cost-effective"
        }
    }


# ===========================================
# 5. 앱 메타데이터
# ===========================================
APP_TITLE = "Coffee Trade Hub"
APP_ICON = "☕"
APP_LAYOUT = "wide"
