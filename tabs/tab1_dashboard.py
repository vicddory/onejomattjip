# -*- coding: utf-8 -*-
"""
Tab 1: Dashboard - 커피 소싱 신호 대시보드
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import numpy as np
import re
from dataclasses import dataclass
from typing import Dict, Tuple

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
    """실제 시장 데이터 로드 (Yahoo Finance)"""
    try:
        import yfinance as yf
        
        arabica_ticker = yf.Ticker("KC=F")
        arabica_data = arabica_ticker.history(period="5d")
        
        if len(arabica_data) >= 2:
            arabica_price = float(arabica_data['Close'].iloc[-1])
            arabica_prev = float(arabica_data['Close'].iloc[-2])
            arabica_change = arabica_price - arabica_prev
            arabica_change_pct = (arabica_change / arabica_prev) * 100
        else:
            raise ValueError("Arabica 데이터 부족")
        
        fx_ticker = yf.Ticker("KRW=X")
        fx_data = fx_ticker.history(period="5d")
        
        if len(fx_data) >= 2:
            fx_price = float(fx_data['Close'].iloc[-1])
            fx_prev = float(fx_data['Close'].iloc[-2])
            fx_change = fx_price - fx_prev
            fx_change_pct = (fx_change / fx_prev) * 100
        else:
            raise ValueError("환율 데이터 부족")
        
        robusta_price = arabica_price * 0.55 * 50
        robusta_change = arabica_change * 0.5
        robusta_change_pct = arabica_change_pct * 0.8
        
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
        dummy_data = get_dummy_market_data()
        dummy_data['data_source'] = '⚠️ 모든 데이터: Fallback (더미 데이터)'
        return dummy_data

def get_historical_data(period: str = '1M') -> pd.DataFrame:
    """기간별 히스토리 데이터 생성"""
    config = PERIOD_CONFIG[period]
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=config.periods, freq=config.freq)
    
    arabica_base = 245
    robusta_base = 4800
    
    volatility_map = {
        '1D': (0.5, 15), '1W': (1.0, 25), '1M': (2.0, 40),
        '6M': (5.0, 80), '1Y': (8.0, 120), '3Y': (15.0, 200)
    }
    arabica_vol, robusta_vol = volatility_map[period]
    
    np.random.seed(42)
    
    arabica_prices = [arabica_base]
    robusta_prices = [robusta_base]
    
    for i in range(1, config.periods):
        arabica_change = np.random.normal(0, arabica_vol * 0.5)
        arabica_price = arabica_prices[-1] + arabica_change
        arabica_price = max(arabica_base * 0.85, min(arabica_base * 1.15, arabica_price))
        arabica_prices.append(arabica_price)
        
        robusta_change = np.random.normal(0, robusta_vol * 0.5)
        robusta_price = robusta_prices[-1] + robusta_change
        robusta_price = max(robusta_base * 0.85, min(robusta_base * 1.15, robusta_price))
        robusta_prices.append(robusta_price)
    
    df = pd.DataFrame({
        'date': dates,
        'arabica': arabica_prices,
        'robusta': robusta_prices
    })
    
    return df.sort_values('date').reset_index(drop=True)

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

def generate_algorithmic_signal(market_data: Dict) -> Dict:
    """API 기반 알고리즘 시그널 생성"""
    arabica = market_data['arabica']
    robusta = market_data['robusta']
    fx = market_data['usd_krw']
    freight = market_data['freight']
    
    signal_score = 50
    logic_triggers = []
    
    if arabica.change_pct < -1.5:
        signal_score += 20
        logic_triggers.append(f"아라비카 가격 {abs(arabica.change_pct):.2f}% 하락 → 매수 유리")
    elif arabica.change_pct > 1.5:
        signal_score -= 20
        logic_triggers.append(f"아라비카 가격 +{arabica.change_pct:.2f}% 상승 → 진입 시점 불리")
    
    if robusta.change_pct < -1.5:
        signal_score += 15
        logic_triggers.append(f"로부스타 가격 {abs(robusta.change_pct):.2f}% 하락 → 베트남 공급 안정")
    elif robusta.change_pct > 1.5:
        signal_score -= 15
        logic_triggers.append(f"로부스타 가격 +{robusta.change_pct:.2f}% 상승 → 공급 우려 감지")
    
    if fx.change_pct < -0.5:
        signal_score += 10
        logic_triggers.append(f"원화 강세 ({fx.change_pct:+.2f}%) → 구매력 향상")
    elif fx.change_pct > 0.8:
        signal_score -= 10
        logic_triggers.append(f"원화 약세 (+{fx.change_pct:.2f}%) → 수입 비용 증가")
    
    if freight.change_pct < -2.0:
        signal_score += 10
        logic_triggers.append(f"운임 비용 {abs(freight.change_pct):.2f}% 하락 → 물류 이점 확보")
    elif freight.change_pct > 2.0:
        signal_score -= 10
        logic_triggers.append(f"운임 비용 +{freight.change_pct:.2f}% 상승 → 물류 부담 증가")
    
    if signal_score >= 75:
        signal_status, signal_emoji = "강력 매수", "🟢🟢"
        market_context = "매우 유리한 시장 조건이 감지되었습니다."
        cpo_action = "실행 권고: 장기 계약 체결."
    elif signal_score >= 60:
        signal_status, signal_emoji = "매수", "🟢"
        market_context = "유리한 매수 시점이 확인되었습니다."
        cpo_action = "진행 권고: 정상~증량 구매."
    elif signal_score >= 40:
        signal_status, signal_emoji = "중립 관망", "🟡"
        market_context = "시장에 혼재된 신호가 나타납니다."
        cpo_action = "모니터링: 표준 조달 일정 유지."
    elif signal_score >= 25:
        signal_status, signal_emoji = "주의", "🟠"
        market_context = "불리한 조건이 나타나고 있습니다."
        cpo_action = "지연 권고: 구매 물량 축소."
    else:
        signal_status, signal_emoji = "변동성 경고", "🔴"
        market_context = "높은 리스크 환경이 감지되었습니다."
        cpo_action = "중단 권고: 비필수 조달 일시 중지."
    
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
# UI 컴포넌트 생성 함수
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
                <h3 style="margin: 0; color: #4B2C20; font-family: Inter;">{title}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #8B5A3C; font-size: 0.95rem;">{desc}</p>
                <p style="margin: 0.25rem 0 0 0; color: #666; font-size: 0.85rem;">{price_info}</p>
            </div>
        </div>
    </div>
    '''

def create_price_chart(df: pd.DataFrame, column: str, title: str, unit: str, 
                       color: str, period: str) -> go.Figure:
    """가격 차트 생성"""
    df = df.sort_values('date').reset_index(drop=True)
    y_range = calculate_y_range(df[column])
    max_idx = df[column].idxmax()
    min_idx = df[column].idxmin()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df[column], mode='lines', name=title,
        line=dict(color=color, width=3, shape='linear'),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color[i:i+2], 16) for i in (1, 3, 5)) + [0.1])}',
        hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>가격: %{y:.2f} ' + unit + '<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[df.loc[max_idx, 'date']], y=[df.loc[max_idx, column]],
        mode='markers',
        marker=dict(color='#EF4444', size=12, symbol='triangle-up', line=dict(color='white', width=2)),
        name='최고가', showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=[df.loc[min_idx, 'date']], y=[df.loc[min_idx, column]],
        mode='markers',
        marker=dict(color='#10B981', size=12, symbol='triangle-down', line=dict(color='white', width=2)),
        name='최저가', showlegend=False
    ))
    
    fig.update_layout(
        title=dict(text=f'{title} 가격 추이 ({PERIOD_LABELS[period]})', font=dict(size=16, color='#4B2C20')),
        xaxis=dict(title='날짜', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(title=f'가격 ({unit})', range=[y_range[0], y_range[1]], tickformat='.2f'),
        plot_bgcolor='rgba(244, 232, 216, 0.3)',
        paper_bgcolor='rgba(255, 255, 255, 0.9)',
        height=400, showlegend=False, margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig

def create_stats_box(series: pd.Series) -> str:
    """통계 정보 박스 HTML 생성"""
    stats = {
        '최고가': (series.max(), '#D32F2F'),
        '평균가': (series.mean(), '#4B2C20'),
        '최저가': (series.min(), '#388E3C'),
        '변동폭': (series.max() - series.min(), '#4B2C20')
    }
    
    stats_html = ''.join([
        f'''<div style="text-align: center;">
            <div style="font-size: 0.75rem; color: #8B5A3C;">{label}</div>
            <div style="font-size: 1rem; font-weight: 600; color: {color};">{value:.2f}</div>
        </div>'''
        for label, (value, color) in stats.items()
    ])
    
    return f'''
    <div style="display: flex; justify-content: space-around; padding: 0.5rem; 
                background: rgba(255,255,255,0.7); border-radius: 8px; margin-top: -0.5rem;">
        {stats_html}
    </div>
    '''

# ========================================
# CSS 로드
# ========================================
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * { font-family: 'Inter', -apple-system, sans-serif; }
        h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
        
        :root {
            --coffee-dark: #4B2C20; --coffee-medium: #8B5A3C;
            --coffee-light: #C4A27E; --coffee-cream: #F4E8D8;
        }
        
        .main-title {
            font-family: 'Playfair Display', serif; color: var(--coffee-dark);
            font-size: 3rem; font-weight: 700; text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            font-family: 'Inter', sans-serif; color: var(--coffee-medium);
            text-align: center; font-size: 1.1rem; margin-bottom: 2rem;
        }
        
        .metric-container {
            background: #FFFFFF; padding: 0; border-radius: 12px;
            border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem; overflow: hidden;
        }
        
        .metric-header { padding: 1rem 1.5rem 0.5rem 1.5rem; border-bottom: 1px solid #F3F4F6; }
        .metric-title { font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 1.2px; margin: 0; }
        .metric-body { padding: 1.5rem; background: #FFFFFF; }
        .metric-price { font-size: 2.5rem; font-weight: 700; color: #111827; margin: 0.5rem 0; }
        .metric-unit { font-size: 0.9rem; color: #9CA3AF; margin-left: 0.25rem; }
        .metric-change-wrapper { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.75rem; }
        .change-arrow { font-size: 1.5rem; font-weight: bold; }
        .change-text { font-size: 1rem; font-weight: 600; }
        .color-up { color: #EF4444; }
        .color-down { color: #10B981; }
        
        .signal-card {
            background: #FFFFFF; padding: 1.5rem; border-radius: 12px;
            border: 1px solid #E5E7EB; margin-bottom: 1rem;
        }
        
        .traffic-light {
            width: 60px; height: 60px; border-radius: 50%;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 1.8rem; margin-right: 1rem;
        }
        
        .signal-green { background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.25)); }
        .signal-yellow { background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.25)); }
        .signal-red { background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.25)); }
        
        .section-header {
            font-family: 'Playfair Display', serif; color: var(--coffee-dark);
            font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem; border-bottom: 3px solid var(--coffee-medium);
        }
        
        .timestamp { text-align: center; color: var(--coffee-medium); font-size: 0.85rem; font-style: italic; margin-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ========================================
# 메인 show 함수
# ========================================
def show():
    """Dashboard를 렌더링하는 메인 함수"""
    load_css()
    
    st.markdown('<h1 class="main-title">☕ Coffee Sourcing Signal Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">실시간 커피 원두 시장 분석 및 매수 신호 시스템</p>', unsafe_allow_html=True)
    
    market_data = get_market_data_live()
    
    if 'data_source' in market_data:
        st.info(f"📡 데이터 소스: {market_data['data_source']}")
    
    # 섹션 1: Market Data Snapshot
    st.markdown('<h2 class="section-header">📊 Market Data Snapshot</h2>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for col, key in zip(cols, ['arabica', 'robusta', 'usd_krw', 'freight']):
        with col:
            render_html(create_metric_card(market_data[key]))
    
    # 섹션 2: 선물 가격 추세
    st.markdown('<h2 class="section-header">📈 Futures Price Trends</h2>', unsafe_allow_html=True)
    
    period = st.radio("기간 선택", options=['1D', '1W', '1M', '6M', '1Y', '3Y'],
                     index=2, horizontal=True, label_visibility="collapsed")
    
    hist_data = get_historical_data(period)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_arabica = create_price_chart(hist_data, 'arabica', 'Arabica', '¢/lb', '#8B5A3C', period)
        st.plotly_chart(fig_arabica, use_container_width=True)
        render_html(create_stats_box(hist_data['arabica']))
    
    with col2:
        fig_robusta = create_price_chart(hist_data, 'robusta', 'Robusta', '$/MT', '#C4A27E', period)
        st.plotly_chart(fig_robusta, use_container_width=True)
        render_html(create_stats_box(hist_data['robusta']))
    
    # 섹션 3: Traffic Light 분석
    st.markdown('<h2 class="section-header">🚦 Sourcing Signal Analysis</h2>', unsafe_allow_html=True)
    
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
    
    # 섹션 4: Executive Summary
    st.markdown('<h2 class="section-header">💼 Executive Summary & Action Plan</h2>', unsafe_allow_html=True)
    
    algo_signal = generate_algorithmic_signal(market_data)
    
    signal_colors = {
        '강력 매수': '#10B981', '매수': '#34D399', '중립 관망': '#F59E0B',
        '주의': '#F97316', '변동성 경고': '#EF4444'
    }
    signal_color = signal_colors.get(algo_signal['signal_status'], '#6B7280')
    
    triggers_html = ''.join([
        f'<li style="margin-bottom: 0.5rem; color: #4B5563;">{trigger}</li>'
        for trigger in algo_signal['logic_triggers']
    ])
    
    summary_html = f'''
    <div class="metric-container" style="padding: 2rem; background: white;">
        <div style="margin-bottom: 2rem;">
            <h3 style="color: #4B2C20; margin-top: 0;">📊 시장 상황 분석</h3>
            <p style="color: #374151; font-size: 1.05rem; line-height: 1.8;">{algo_signal['market_context']}</p>
        </div>
        
        <div style="background: #1F2937; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {signal_color};">
            <div style="font-size: 0.75rem; color: #9CA3AF;">시스템 상태 @ {algo_signal['timestamp']}</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #10B981;">{algo_signal['signal_emoji']} 신호: {algo_signal['signal_status']}</div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #60A5FA;">신호 강도: {algo_signal['signal_strength']}/100</div>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: #1F2937;">로직 트리거 조건:</h4>
            <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8;">{triggers_html}</ul>
        </div>
        
        <div style="background: {signal_color}15; padding: 1.5rem; border-radius: 12px; border-left: 5px solid {signal_color};">
            <h3 style="color: #4B2C20; margin-top: 0;">🎯 CPO 실행 권고사항</h3>
            <p style="color: #111827; font-size: 1.1rem; font-weight: 600;">{algo_signal['cpo_action']}</p>
        </div>
    </div>
    '''
    
    render_html(summary_html)
    
    st.markdown(f'<p class="timestamp">📅 Last Updated: {market_data["last_updated"]}</p>', unsafe_allow_html=True)
