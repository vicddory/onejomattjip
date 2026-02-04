# -*- coding: utf-8 -*-
# 실시간 데이터 사용 시 필요한 라이브러리:
# pip install streamlit plotly pandas yfinance

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# ========================================
# 페이지 설정 (최상단에 위치 필수)
# ========================================
st.set_page_config(
    page_title="커피 소싱 신호 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS: config.toml의 톤앤매너(Deep Emerald & Off-White) 적용
st.markdown("""
    <style>
        /* 1. 폰트 임포트 (Noto Sans KR) - Sans Serif 적용 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* 2. 전체 폰트 및 배경색 적용 (config.toml 일치) */
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', 'Inter', sans-serif !important;
            color: #333333;
        }
        
        /* 메인 배경색 강제 적용 */
        .stApp {
            background-color: #FAFAFA !important;
            background-image: none !important; /* 기존 그라데이션 제거 */
        }

        /* 3. 입력창 스타일 (Deep Emerald 포커스) */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stSelectbox > div > div > div {
            border-radius: 8px !important;
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
        }
        
        /* 입력창 포커스 시 색상 */
        .stTextInput > div > div > input:focus {
            border-color: #00695C !important;
            box-shadow: 0 0 0 1px #00695C !important;
        }

        /* 4. 버튼 스타일 */
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

        /* 5. 탭 스타일 */
        .stTabs [aria-selected="true"] {
            font-weight: 700 !important;
            color: #00695C !important;
            border-bottom-color: #00695C !important;
        }
        
        /* 6. 헤더 및 타이틀 스타일 (Deep Emerald) */
        h1, h2, h3, h4 {
            color: #333333 !important;
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        
        .main-title {
            font-family: 'Noto Sans KR', sans-serif; 
            color: #333333 !important; /* 기존 var(--primary-color)에서 변경 */
            font-size: 2.5rem; 
            font-weight: 700; 
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .section-header {
            border-bottom: 3px solid #00695C !important; /* 포인트 컬러 라인 */
        }
    </style>
""", unsafe_allow_html=True)


# ========================================
# 데이터 클래스
# ========================================
@dataclass
class MarketMetric:
    """시장 지표 데이터 클래스"""
    name: str
    price: float
    unit: str
    change: float
    change_pct: float

@dataclass
class ChartConfig:
    """차트 설정 데이터 클래스"""
    periods: int
    freq: str
    volatility: float

# ========================================
# 설정 및 상수
# ========================================
PERIOD_CONFIG = {
    '1D': ChartConfig(24, 'H', 0.3),
    '1W': ChartConfig(7, 'D', 0.8),
    '1M': ChartConfig(30, 'D', 1.2),
    '6M': ChartConfig(26, 'W', 2.5),
    '1Y': ChartConfig(52, 'W', 3.5),
    '3Y': ChartConfig(36, 'M', 5.0)
}

PERIOD_LABELS = {
    '1D': '24시간', '1W': '1주일', '1M': '1개월',
    '6M': '6개월', '1Y': '1년', '3Y': '3년'
}

# ========================================
# 유틸리티 함수
# ========================================
def render_html(html_content: str) -> None:
    """HTML을 Streamlit에서 안전하게 렌더링"""
    cleaned = re.sub(r'^```html\s*\n|^```\s*\n|\n```\s*$|```$', '', html_content, flags=re.MULTILINE).strip()
    (st.html if hasattr(st, 'html') else lambda x: st.markdown(x, unsafe_allow_html=True))(cleaned)

def get_trend_direction(change: float) -> Tuple[str, str]:
    """변동값에 따른 화살표와 CSS 클래스 반환"""
    return ("▲", "color-up") if change > 0 else ("▼", "color-down")

def calculate_y_range(series: pd.Series, padding: float = 0.05) -> Tuple[float, float]:
    """동적 Y축 범위 계산"""
    data_range = series.max() - series.min()
    padding_val = data_range * padding
    return (series.min() - padding_val, series.max() + padding_val)

# ========================================
# 데이터 생성 함수
# ========================================
@st.cache_data(ttl=300)
def get_dummy_market_data() -> Dict:
    """더미 시장 데이터 생성 (폴백용)"""
    return {
        'arabica': MarketMetric("ICE Arabica (NY)", 241.50, "¢/lb", -2.35, -0.96),
        'robusta': MarketMetric("London Robusta", 4820.00, "$/MT", 15.50, 0.32),
        'usd_krw': MarketMetric("USD/KRW Exchange Rate", 1382.50, "", 8.20, 0.60),
        'freight': MarketMetric("Shanghai Freight Index", 1458, "points", -23, -1.55),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')
    }

@st.cache_data(ttl=300)
def get_market_data_live() -> Dict:
    """
    실제 시장 데이터 로드 (Yahoo Finance)
    실패 시 더미 데이터로 자동 폴백
    """
    try:
        import yfinance as yf
        
        # Arabica 선물 데이터
        arabica_ticker = yf.Ticker("KC=F")
        arabica_data = arabica_ticker.history(period="5d")
        
        if len(arabica_data) >= 2:
            arabica_price = float(arabica_data['Close'].iloc[-1])
            arabica_prev = float(arabica_data['Close'].iloc[-2])
            arabica_change = arabica_price - arabica_prev
            arabica_change_pct = (arabica_change / arabica_prev) * 100
        else:
            raise ValueError("Arabica 데이터 부족")
        
        # USD/KRW 환율
        fx_ticker = yf.Ticker("KRW=X")
        fx_data = fx_ticker.history(period="5d")
        
        if len(fx_data) >= 2:
            fx_price = float(fx_data['Close'].iloc[-1])
            fx_prev = float(fx_data['Close'].iloc[-2])
            fx_change = fx_price - fx_prev
            fx_change_pct = (fx_change / fx_prev) * 100
        else:
            raise ValueError("환율 데이터 부족")
        
        # Robusta 추정치 (실제 API 없음)
        robusta_price = arabica_price * 0.55 * 50  # $/MT로 변환
        robusta_change = arabica_change * 0.5
        robusta_change_pct = arabica_change_pct * 0.8
        
        # Freight는 고정값 (실제 API 필요)
        freight_index = 1458
        freight_change = -23
        freight_change_pct = -1.55
        
        return {
            'arabica': MarketMetric("ICE Arabica (NY)", arabica_price, "¢/lb", 
                                   arabica_change, arabica_change_pct),
            'robusta': MarketMetric("London Robusta", robusta_price, "$/MT", 
                                   robusta_change, robusta_change_pct),
            'usd_krw': MarketMetric("USD/KRW Exchange Rate", fx_price, "", 
                                   fx_change, fx_change_pct),
            'freight': MarketMetric("Shanghai Freight Index", freight_index, "points", 
                                   freight_change, freight_change_pct),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S KST'),
            'data_source': '✅ Arabica: Live | ⚠️ Robusta: Estimated | ✅ USD/KRW: Live | ⚠️ Freight: Static'
        }
        
    except Exception as e:
        # 에러 발생 시 더미 데이터로 폴백
        print(f"⚠️ 실시간 데이터 로드 실패: {e}")
        dummy_data = get_dummy_market_data()
        dummy_data['data_source'] = '⚠️ 모든 데이터: Fallback (더미 데이터)'
        return dummy_data

def get_historical_data(period: str = '1M') -> pd.DataFrame:
    """
    기간별 히스토리 데이터 생성
    현실적인 시장 변동 패턴 적용
    """
    import numpy as np
    
    config = PERIOD_CONFIG[period]
    
    # 날짜 생성 (과거 → 현재 순서)
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=config.periods, freq=config.freq)
    
    # 기준 가격
    arabica_base = 245
    robusta_base = 4800
    
    # 현실적인 변동폭 설정 (기간별)
    if period == '1D':
        arabica_volatility = 0.5
        robusta_volatility = 15
    elif period == '1W':
        arabica_volatility = 1.0
        robusta_volatility = 25
    elif period == '1M':
        arabica_volatility = 2.0
        robusta_volatility = 40
    elif period == '6M':
        arabica_volatility = 5.0
        robusta_volatility = 80
    elif period == '1Y':
        arabica_volatility = 8.0
        robusta_volatility = 120
    else:  # 3Y
        arabica_volatility = 15.0
        robusta_volatility = 200
    
    # 랜덤 시드 고정 (재현성)
    np.random.seed(42)
    
    # 데이터 생성 (현실적인 랜덤 워크)
    arabica_prices = [arabica_base]
    robusta_prices = [robusta_base]
    
    for i in range(1, config.periods):
        # Arabica: 이전 가격 기준 작은 변동
        arabica_change = np.random.normal(0, arabica_volatility * 0.5)
        arabica_price = arabica_prices[-1] + arabica_change
        # 가격 범위 제한
        arabica_price = max(arabica_base * 0.85, min(arabica_base * 1.15, arabica_price))
        arabica_prices.append(arabica_price)
        
        # Robusta: 이전 가격 기준 작은 변동
        robusta_change = np.random.normal(0, robusta_volatility * 0.5)
        robusta_price = robusta_prices[-1] + robusta_change
        # 가격 범위 제한
        robusta_price = max(robusta_base * 0.85, min(robusta_base * 1.15, robusta_price))
        robusta_prices.append(robusta_price)
    
    # DataFrame 생성 (이미 날짜순 정렬됨)
    df = pd.DataFrame({
        'date': dates,
        'arabica': arabica_prices,
        'robusta': robusta_prices
    })
    
    # 명시적으로 날짜순 정렬
    df = df.sort_values('date').reset_index(drop=True)
    
    return df

# ========================================
# 분석 함수
# ========================================
def analyze_market_signal(change_pct: float) -> Tuple[str, str, str]:
    """시장 신호 분석"""
    if change_pct < -1.0:
        return "🟢", "GREEN", "매수 호기 - 가격 하락세"
    elif change_pct > 1.0:
        return "🔴", "RED", "주의 - 가격 급등"
    return "🟡", "YELLOW", "관망 - 변동성 제한적"

def determine_market_structure(arabica_chg: float, robusta_chg: float) -> Tuple[str, str]:
    """시장 구조 판단"""
    if arabica_chg < 0 and robusta_chg < 0:
        return "재고 충분", "현물 매수 유리"
    elif arabica_chg > 2 or robusta_chg > 2:
        return "공급 긴축", "선물 헤지 권장"
    return "중립 시장", "분산 매수 전략"

def generate_algorithmic_signal(market_data: Dict) -> Dict:
    """
    API 기반 알고리즘 시그널 생성
    """
    arabica = market_data['arabica']
    robusta = market_data['robusta']
    fx = market_data['usd_krw']
    freight = market_data['freight']
    
    # 시그널 점수 계산 (0-100)
    signal_score = 50  # 중립에서 시작
    logic_triggers = []
    
    # 1. Arabica 가격 분석
    if arabica.change_pct < -1.5:
        signal_score += 20
        logic_triggers.append(f"아라비카 가격 {abs(arabica.change_pct):.2f}% 하락 → 매수 유리")
    elif arabica.change_pct > 1.5:
        signal_score -= 20
        logic_triggers.append(f"아라비카 가격 +{arabica.change_pct:.2f}% 상승 → 진입 시점 불리")
    
    # 2. Robusta 가격 분석
    if robusta.change_pct < -1.5:
        signal_score += 15
        logic_triggers.append(f"로부스타 가격 {abs(robusta.change_pct):.2f}% 하락 → 베트남 공급 안정")
    elif robusta.change_pct > 1.5:
        signal_score -= 15
        logic_triggers.append(f"로부스타 가격 +{robusta.change_pct:.2f}% 상승 → 공급 우려 감지")
    
    # 3. 환율 분석
    if fx.change_pct < -0.5:
        signal_score += 10
        logic_triggers.append(f"원화 강세 ({fx.change_pct:+.2f}%) → 구매력 향상")
    elif fx.change_pct > 0.8:
        signal_score -= 10
        logic_triggers.append(f"원화 약세 (+{fx.change_pct:.2f}%) → 수입 비용 증가")
    
    # 4. 물류 비용 분석
    if freight.change_pct < -2.0:
        signal_score += 10
        logic_triggers.append(f"운임 비용 {abs(freight.change_pct):.2f}% 하락 → 물류 이점 확보")
    elif freight.change_pct > 2.0:
        signal_score -= 10
        logic_triggers.append(f"운임 비용 +{freight.change_pct:.2f}% 상승 → 물류 부담 증가")
    
    # 5. 변동성 체크
    volatility_score = abs(arabica.change_pct) + abs(robusta.change_pct)
    if volatility_score > 3.0:
        logic_triggers.append(f"높은 변동성 감지 (합산: {volatility_score:.2f}%) → 리스크 상승")
    
    # 시그널 상태 결정
    if signal_score >= 75:
        signal_status = "강력 매수"
        signal_emoji = "🟢🟢"
        market_context = "매우 유리한 시장 조건이 감지되었습니다. 다수의 지표가 공격적 소싱을 지지합니다."
        cpo_action = "실행 권고: 장기 계약 체결. 정상 일정보다 3-6개월 앞당겨 매수 검토."
    elif signal_score >= 60:
        signal_status = "매수"
        signal_emoji = "🟢"
        market_context = "유리한 매수 시점이 확인되었습니다. 가격 추세와 펀더멘털이 조달을 지지합니다."
        cpo_action = "진행 권고: 정상~증량 구매. 현물 계약 확보."
    elif signal_score >= 40:
        signal_status = "중립 관망"
        signal_emoji = "🟡"
        market_context = "시장에 혼재된 신호가 나타납니다. 즉각적 행동의 명확한 이점이 없습니다."
        cpo_action = "모니터링: 표준 조달 일정 유지. 추세 변화 주시."
    elif signal_score >= 25:
        signal_status = "주의"
        signal_emoji = "🟠"
        market_context = "불리한 조건이 나타나고 있습니다. 가격 추세와 비용이 조달에 불리하게 작용 중입니다."
        cpo_action = "지연 권고: 구매 물량 축소. 단기 계약만 고려."
    else:
        signal_status = "변동성 경고"
        signal_emoji = "🔴"
        market_context = "높은 리스크 환경이 감지되었습니다. 시장에 다수의 불리한 요인이 존재합니다."
        cpo_action = "중단 권고: 비필수 조달 일시 중지. 기존 재고 관리에 집중."
    
    # 트리거가 없으면 기본 메시지
    if not logic_triggers:
        logic_triggers.append("시장 지표가 정상 범위 내 (±1% 임계값)")
    
    return {
        'signal_status': signal_status,
        'signal_emoji': signal_emoji,
        'signal_strength': signal_score,
        'logic_triggers': logic_triggers,
        'market_context': market_context,
        'cpo_action': cpo_action,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')
    }

# ========================================
# UI 컴포넌트 생성 함수 (HTML/CSS 수정됨)
# ========================================
def create_metric_card(metric: MarketMetric) -> str:
    """메트릭 카드 HTML 생성"""
    arrow, color_class = get_trend_direction(metric.change)
    
    return f'''
    <div class="metric-container">
        <div class="metric-header">
            <p class="metric-title">{metric.name}</p>
        </div>
        <div class="metric-body">
            <div class="metric-price">
                {metric.price:.2f}
                <span class="metric-unit">{metric.unit}</span>
            </div>
            <div class="metric-change-wrapper">
                <span class="change-arrow {color_class}">{arrow}</span>
                <span class="change-text {color_class}">
                    {abs(metric.change):.2f} ({abs(metric.change_pct):.2f}%)
                </span>
            </div>
        </div>
    </div>
    '''

def create_signal_card(emoji: str, title: str, desc: str, price_info: str) -> str:
    """신호등 카드 HTML 생성"""
    signal_color = {"🟢": "green", "🟡": "yellow", "🔴": "red"}[emoji]
    
    return f'''
    <div class="signal-card">
        <div style="display: flex; align-items: center;">
            <div class="traffic-light signal-{signal_color}">{emoji}</div>
            <div>
                <h3 style="margin: 0; color: #333333; font-family: 'Noto Sans KR', sans-serif; font-size: 1.1rem;">{title}</h3>
                
                <p style="margin: 0.5rem 0 0 0; color: #333333; font-size: 0.95rem; font-weight: 500;">{desc}</p>
                <p style="margin: 0.25rem 0 0 0; color: #666; font-size: 0.85rem;">{price_info}</p>
            </div>
        </div>
    </div>
    '''

def create_price_chart(df: pd.DataFrame, column: str, title: str, unit: str, 
                       color: str, period: str) -> go.Figure:
    """
    가격 차트 생성 (config.toml 스타일 적용)
    """
    # 날짜순 정렬 확인
    df = df.sort_values('date').reset_index(drop=True)
    
    # Y축 범위 계산
    y_range = calculate_y_range(df[column])
    
    # 최고가/최저가 인덱스
    max_idx = df[column].idxmax()
    min_idx = df[column].idxmin()
    
    # Figure 생성
    fig = go.Figure()
    
    # 메인 라인
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[column],
        mode='lines',
        name=title,
        line=dict(
            color=color, # 인자로 받은 색상 사용
            width=3,
            shape='linear',
            smoothing=0
        ),
        fill='tozeroy',
        # 채우기 색상: 투명도 조절
        fillcolor=f'rgba{tuple(list(int(color[i:i+2], 16) for i in (1, 3, 5)) + [0.1])}',
        hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>가격: %{y:.2f} ' + unit + '<extra></extra>'
    ))
    
    # 최고가 마커
    fig.add_trace(go.Scatter(
        x=[df.loc[max_idx, 'date']],
        y=[df.loc[max_idx, column]],
        mode='markers',
        marker=dict(
            color='#EF4444',
            size=12,
            symbol='triangle-up',
            line=dict(color='white', width=2)
        ),
        name='최고가',
        hovertemplate=f'최고가: %{{y:.2f}} {unit}<extra></extra>',
        showlegend=False
    ))
    
    # 최저가 마커
    fig.add_trace(go.Scatter(
        x=[df.loc[min_idx, 'date']],
        y=[df.loc[min_idx, column]],
        mode='markers',
        marker=dict(
            color='#10B981',
            size=12,
            symbol='triangle-down',
            line=dict(color='white', width=2)
        ),
        name='최저가',
        hovertemplate=f'최저가: %{{y:.2f}} {unit}<extra></extra>',
        showlegend=False
    ))
    
    # 레이아웃 설정 (배경색 및 폰트 config.toml과 일치)
    fig.update_layout(
        title=dict(
            text=f'{title} 가격 추이 ({PERIOD_LABELS[period]})',
            font=dict(size=16, color='#333333', family='Noto Sans KR'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='날짜',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False
        ),
        yaxis=dict(
            title=f'가격 ({unit})',
            range=[y_range[0], y_range[1]],
            tickformat='.2f',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False
        ),
        # 배경색: config.toml의 backgroundColor (#FAFAFA)
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Noto Sans KR', color='#333333'),
        hovermode='x unified',
        height=400,
        showlegend=False,
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig

def create_stats_box(series: pd.Series) -> str:
    """통계 정보 박스 HTML 생성"""
    stats = {
        '최고가': (series.max(), '#D32F2F'),
        '평균가': (series.mean(), '#333333'), # 갈색 -> 짙은 회색
        '최저가': (series.min(), '#388E3C'),
        '변동폭': (series.max() - series.min(), '#333333')
    }
    
    stats_html = ''.join([
        f'''<div style="text-align: center;">
            <div style="font-size: 0.75rem; color: #666;">{label}</div>
            <div style="font-size: 1rem; font-weight: 600; color: {color};">{value:.2f}</div>
        </div>'''
        for label, (value, color) in stats.items()
    ])
    
    return f'''
    <div style="display: flex; justify-content: space-around; padding: 0.5rem; 
                background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; margin-top: -0.5rem;">
        {stats_html}
    </div>
    '''

# ========================================
# CSS (축약 버전 - 주요 변수 재정의)
# ========================================
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * { font-family: 'Noto Sans KR', sans-serif; }
        
        :root {
            --primary-color: #00695C;
            --text-color: #333333;
            --bg-color: #FAFAFA;
        }
        
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
        
        /* 메인 컨텐츠 영역 */
        section.main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .main-title {
            font-family: 'Noto Sans KR', sans-serif; 
            color: var(--primary-color);
            font-size: 2.5rem; font-weight: 700; text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .metric-container {
            background: #FFFFFF; padding: 0; border-radius: 12px;
            border: 1px solid #E0E0E0; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem; overflow: hidden; transition: all 0.2s ease;
        }
        
        .metric-container:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-color: var(--primary-color);
        }
        
        .metric-header {
            padding: 1rem 1.5rem 0.5rem 1.5rem;
            border-bottom: 1px solid #F5F5F5;
        }
        
        .metric-title {
            font-family: 'Noto Sans KR', sans-serif; font-size: 0.8rem;
            color: #757575; text-transform: uppercase;
            letter-spacing: 1px; font-weight: 600; margin: 0;
        }
        
        .metric-body { padding: 1.5rem; background: #FFFFFF; }
        
        .metric-price {
            font-family: 'Noto Sans KR', sans-serif; font-size: 2.2rem;
            font-weight: 700; color: #333333; margin: 0.5rem 0; line-height: 1.2;
        }
        
        .metric-unit { font-size: 0.9rem; color: #9E9E9E; margin-left: 0.25rem; }
        
        .metric-change-wrapper {
            display: flex; align-items: center; gap: 0.5rem; margin-top: 0.75rem;
        }
        
        .change-arrow { font-size: 1.2rem; font-weight: bold; line-height: 1; }
        .change-text { font-family: 'Noto Sans KR', sans-serif; font-size: 1rem; font-weight: 600; }
        
        .color-up { color: #EF4444; }
        .color-down { color: #10B981; }
        
        .signal-card {
            background: #FFFFFF; padding: 1.5rem; border-radius: 12px;
            border: 1px solid #E0E0E0; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem; transition: all 0.2s ease;
        }
        
        .signal-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-color: var(--primary-color);
        }
        
        .traffic-light {
            width: 50px; height: 50px; border-radius: 50%;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 1.5rem; margin-right: 1rem; position: relative;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .signal-green { background: rgba(16, 185, 129, 0.15); border: 2px solid rgba(16, 185, 129, 0.4); }
        .signal-yellow { background: rgba(245, 158, 11, 0.15); border: 2px solid rgba(245, 158, 11, 0.4); }
        .signal-red { background: rgba(239, 68, 68, 0.15); border: 2px solid rgba(239, 68, 68, 0.4); }
        
        .section-header {
            font-family: 'Noto Sans KR', sans-serif; color: #333333;
            font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem; border-bottom: 3px solid var(--primary-color);
        }
        
        .timestamp {
            text-align: center; color: #9E9E9E;
            font-size: 0.85rem; margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ========================================
# 메인 대시보드
# ========================================
def main():
    # CSS 로드
    load_css()
    
    # 헤더
    st.markdown("<h1 style='text-align: center;'>커피 소싱 신호 대시보드</h1>", unsafe_allow_html=True)
    st.divider()

    # 실제 데이터 로드 (자동 폴백)
    market_data = get_market_data_live()
    
    # ========================================
    # 섹션 1: Market Data Snapshot
    # ========================================
    st.markdown('<h3 class="section-header" style="font-size: 1.4rem;">시장 데이터 스냅샷</h3>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for col, key in zip(cols, ['arabica', 'robusta', 'usd_krw', 'freight']):
        with col:
            render_html(create_metric_card(market_data[key]))
    
    # ========================================
    # 섹션 2: 선물 가격 추세
    # ========================================
    st.markdown('<h3 class="section-header" style="font-size: 1.4rem;">선물 가격 추이</h3>', unsafe_allow_html=True)
    
    # 기간 선택
    period = st.radio("기간 선택", options=['1D', '1W', '1M', '6M', '1Y', '3Y'],
                      index=2, horizontal=True, label_visibility="collapsed")
    
    hist_data = get_historical_data(period)
    
    col1, col2 = st.columns(2)
    
   # [수정 전] st.plotly_chart(fig_arabica, use_container_width=True)
    # [수정 후] use_container_width=True 를 width="stretch" 로 변경
    
    with col1:
        fig_arabica = create_price_chart(hist_data, 'arabica', 'Arabica', '¢/lb', '#00695C', period)
        st.plotly_chart(fig_arabica, width="stretch") # 수정됨
        render_html(create_stats_box(hist_data['arabica']))
    
    with col2:
        fig_robusta = create_price_chart(hist_data, 'robusta', 'Robusta', '$/MT', '#00695C', period)
        st.plotly_chart(fig_robusta, width="stretch") # 수정됨
        render_html(create_stats_box(hist_data['robusta']))
    
    # ========================================
    # 섹션 3: Traffic Light 분석
    # ========================================
    st.markdown('<h3 class="section-header" style="font-size: 1.4rem;">소싱 시그널 분석</h3>', unsafe_allow_html=True)
    
    # 신호 생성
    signals = {
        'arabica': analyze_market_signal(market_data['arabica'].change_pct),
        'robusta': analyze_market_signal(market_data['robusta'].change_pct),
        'fx': analyze_market_signal(market_data['usd_krw'].change_pct),
        'freight': analyze_market_signal(market_data['freight'].change_pct)
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_html(create_signal_card(
            signals['arabica'][0], "Arabica 소싱", signals['arabica'][2],
            f"현재가 {market_data['arabica'].price:.2f} ¢/lb | 변동 {market_data['arabica'].change_pct:+.2f}%"
        ))
        render_html(create_signal_card(
            signals['fx'][0], "환율 타이밍", signals['fx'][2],
            f"현재 ₩{market_data['usd_krw'].price:.2f}/$ | 변동 {market_data['usd_krw'].change_pct:+.2f}%"
        ))
    
    with col2:
        render_html(create_signal_card(
            signals['robusta'][0], "Robusta 소싱", signals['robusta'][2],
            f"현재가 ${market_data['robusta'].price:.2f}/MT | 변동 {market_data['robusta'].change_pct:+.2f}%"
        ))
        render_html(create_signal_card(
            signals['freight'][0], "물류 리스크", signals['freight'][2],
            f"SCFI 지수 {market_data['freight'].price:.0f} | 변동 {market_data['freight'].change_pct:+.2f}%"
        ))
    
    # ========================================
    # 섹션 4: Executive Summary & Action Plan
    # ========================================
    st.markdown('<h3 class="section-header" style="font-size: 1.4rem;">핵심 요약 및 실행 계획</h3>', unsafe_allow_html=True)
    
    # 알고리즘 시그널 생성
    algo_signal = generate_algorithmic_signal(market_data)
    
    # 시그널 상태에 따른 색상 결정
    signal_colors = {
        '강력 매수': '#10B981',
        '매수': '#34D399',
        '중립 관망': '#F59E0B',
        '주의': '#F97316',
        '변동성 경고': '#EF4444'
    }
    signal_color = signal_colors.get(algo_signal['signal_status'], '#6B7280')
    
    # Logic Triggers HTML 생성
    triggers_html = ''.join([
        f'<li style="margin-bottom: 0.5rem; color: #333333;">{trigger}</li>'
        for trigger in algo_signal['logic_triggers']
    ])
    
    # Summary HTML 스타일 수정 (배경색 흰색, 텍스트 짙은 회색/Emerald)
    summary_html = f'''
    <div class="metric-container" style="padding: 2rem; background: white; border: 1px solid #E0E0E0;">
        
        <div style="margin-bottom: 2rem;">
            <h3 style="color: #00695C; margin-top: 0; font-family: 'Noto Sans KR', sans-serif; 
                       font-weight: 700; font-size: 1.3rem; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;"></span> 시장 상황 분석
            </h3>
            <p style="color: #333333; font-size: 1.05rem; line-height: 1.8; 
                      font-family: 'Noto Sans KR', sans-serif; margin: 0;">
                {algo_signal['market_context']}
            </p>
        </div>
        
        <div style="background: #FAFAFA;
                   padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
                   border: 2px solid {signal_color};">
            
            <h3 style="color: #00695C; margin-top: 0; font-family: 'Noto Sans KR', sans-serif; 
                       font-weight: 700; font-size: 1.1rem; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;"></span> API 알고리즘 시그널
            </h3>
            
            <div style="background: #263238; padding: 1rem; border-radius: 8px; 
                        font-family: 'Courier New', monospace; color: #10B981; 
                        margin-bottom: 1rem; border-left: 4px solid {signal_color};">
                <div style="font-size: 0.75rem; color: #B0BEC5; margin-bottom: 0.25rem;">
                    시스템 상태 @ {algo_signal['timestamp']}
                </div>
                <div style="font-size: 1.2rem; font-weight: bold; letter-spacing: 2px;">
                    {algo_signal['signal_emoji']} 신호: {algo_signal['signal_status']}
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #80CBC4;">
                    신호 강도: {algo_signal['signal_strength']}/100
                    <span style="display: inline-block; width: 100px; height: 8px; background: #37474F; 
                                 border-radius: 4px; margin-left: 10px; position: relative; top: 2px;">
                        <span style="display: block; width: {algo_signal['signal_strength']}%; height: 100%; 
                                     background: {signal_color}; border-radius: 4px;"></span>
                    </span>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <h4 style="color: #333333; font-family: 'Noto Sans KR', sans-serif; font-size: 1rem; 
                           font-weight: 600; margin-bottom: 0.75rem;">
                    로직 트리거 조건:
                </h4>
                <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8; 
                           font-family: 'Noto Sans KR', sans-serif; font-size: 0.95rem;">
                    {triggers_html}
                </ul>
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, {signal_color}15 0%, {signal_color}08 100%);
                   padding: 1.5rem; border-radius: 12px; border-left: 5px solid {signal_color};">
            <h3 style="color: #00695C; margin-top: 0; font-family: 'Noto Sans KR', sans-serif; 
                       font-weight: 700; font-size: 1.1rem; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;"></span> CPO 실행 권고사항
            </h3>
            <p style="color: #333333; font-size: 1.0rem; line-height: 1.8; 
                      font-family: 'Noto Sans KR', sans-serif; font-weight: 600; margin: 0;">
                {algo_signal['cpo_action']}
            </p>
        </div>
        
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #EEEEEE; 
                   text-align: center; font-size: 0.85rem; color: #9E9E9E; 
                   font-family: 'Noto Sans KR', sans-serif;">
            알고리즘 버전: v2.0.3-alpha | 데이터 소스: 다중 거래소 API 통합
        </div>
    </div>
    '''
    
    render_html(summary_html)
    
    # 타임스탬프
    st.markdown(f'<p class="timestamp">Last Updated: {market_data["last_updated"]}</p>', 
                unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("### 대시보드 설정")
        st.info("샘플 데이터로 구동 중입니다. 실제 배포 시 API 연동이 필요합니다.")
        
        st.markdown("---")
        st.markdown("### 📚 데이터 출처")
        st.markdown("""
        - **Arabica**: ICE Futures US (KC)
        - **Robusta**: ICE Futures Europe (RM)
        - **환율**: 실시간 외환시세
        - **물류**: Shanghai Containerized Freight Index
        """)
        
        st.markdown("---")
        if st.button("데이터 업데이트", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    main()