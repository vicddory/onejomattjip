# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab1_sourcing.py - 커피 소싱 시그널 대시보드
================================================================================
실시간 시장 데이터와 알고리즘 기반 소싱 시그널을 제공합니다.
[버그 수정] HTML 렌더링 문제 해결 및 UI 개선
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple

# 경로 설정
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_RISK,
    PERIOD_LABELS
)


# ===========================================
# 데이터 클래스 정의
# ===========================================
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


# 기간별 설정
PERIOD_CONFIG = {
    '1D': ChartConfig(24, 'H', 0.3),
    '1W': ChartConfig(7, 'D', 0.8),
    '1M': ChartConfig(30, 'D', 1.2),
    '6M': ChartConfig(26, 'W', 2.5),
    '1Y': ChartConfig(52, 'W', 3.5),
    '3Y': ChartConfig(36, 'M', 5.0)
}


# ===========================================
# CSS 스타일 주입
# ===========================================
def inject_custom_css():
    """커스텀 CSS 스타일 주입"""
    st.markdown("""
    <style>
    .metric-card {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-label {
        margin: 0;
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #333;
        margin: 8px 0;
    }
    .metric-unit {
        font-size: 0.9rem;
        color: #999;
        font-weight: 400;
    }
    .metric-change {
        font-size: 0.9rem;
        font-weight: 600;
    }
    .color-up {
        color: #10B981;
    }
    .color-down {
        color: #EF4444;
    }
    .signal-card {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .signal-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    .signal-emoji {
        font-size: 28px;
        margin-right: 12px;
    }
    .signal-title {
        margin: 0;
        color: #333;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .signal-desc {
        margin: 8px 0 4px 0;
        color: #555;
        font-size: 0.95rem;
    }
    .signal-price {
        margin: 0;
        color: #666;
        font-size: 0.85rem;
    }
    .summary-box {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .signal-badge {
        background: #F5F5F5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .action-box {
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ===========================================
# 유틸리티 함수
# ===========================================
def get_trend_direction(change: float) -> Tuple[str, str]:
    """변동값에 따른 화살표와 CSS 클래스 반환"""
    return ("▲", "color-up") if change > 0 else ("▼", "color-down")


def calculate_y_range(series: pd.Series, padding: float = 0.05) -> Tuple[float, float]:
    """동적 Y축 범위 계산"""
    data_range = series.max() - series.min()
    padding_val = data_range * padding
    return (series.min() - padding_val, series.max() + padding_val)


# ===========================================
# 데이터 생성 함수
# ===========================================
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
        
        # Robusta 추정치
        robusta_price = arabica_price * 0.55 * 50
        robusta_change = arabica_change * 0.5
        robusta_change_pct = arabica_change_pct * 0.8
        
        # Freight 고정값
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
            'data_source': '✅ Live Data'
        }
        
    except Exception as e:
        dummy_data = get_dummy_market_data()
        dummy_data['data_source'] = '⚠️ Fallback Data'
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
    arabica_vol, robusta_vol = volatility_map.get(period, (2.0, 40))
    
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


# ===========================================
# 분석 함수
# ===========================================
def analyze_market_signal(change_pct: float) -> Tuple[str, str, str]:
    """시장 신호 분석"""
    if change_pct < -1.0:
        return "🟢", "GREEN", "매수 호기 - 가격 하락세"
    elif change_pct > 1.0:
        return "🔴", "RED", "주의 - 가격 급등"
    return "🟡", "YELLOW", "관망 - 변동성 제한적"


def generate_algorithmic_signal(market_data: Dict) -> Dict:
    """알고리즘 시그널 생성"""
    arabica = market_data['arabica']
    robusta = market_data['robusta']
    fx = market_data['usd_krw']
    freight = market_data['freight']
    
    # 점수 계산
    signal_score = 50
    logic_triggers = []
    
    # Arabica 가격 하락 → 매수 호기
    if arabica.change_pct < -1.0:
        signal_score += 15
        logic_triggers.append(f"Arabica 가격 {arabica.change_pct:.2f}% 하락 (매수 적기)")
    elif arabica.change_pct > 2.0:
        signal_score -= 15
        logic_triggers.append(f"Arabica 가격 {arabica.change_pct:.2f}% 급등 (신중)")
    
    # Robusta 가격
    if robusta.change_pct < -1.0:
        signal_score += 10
        logic_triggers.append(f"Robusta 가격 {robusta.change_pct:.2f}% 하락")
    elif robusta.change_pct > 2.0:
        signal_score -= 10
        logic_triggers.append(f"Robusta 가격 {robusta.change_pct:.2f}% 상승")
    
    # 환율 (원화 강세 = 유리)
    if fx.change_pct < -0.5:
        signal_score += 10
        logic_triggers.append(f"원화 강세 {fx.change_pct:.2f}% (수입 유리)")
    elif fx.change_pct > 1.0:
        signal_score -= 10
        logic_triggers.append(f"원화 약세 {fx.change_pct:.2f}% (비용 증가)")
    
    # 운임지수
    if freight.change_pct < -1.0:
        signal_score += 5
        logic_triggers.append(f"운임지수 {freight.change_pct:.2f}% 하락")
    elif freight.change_pct > 2.0:
        signal_score -= 5
        logic_triggers.append(f"운임지수 {freight.change_pct:.2f}% 상승")
    
    # 최종 신호 결정
    if signal_score >= 75:
        signal_status = "강력 매수"
        signal_emoji = "🟢🟢"
        market_context = "매우 유리한 시장 조건이 감지되었습니다."
        cpo_action = "즉시 소싱 계약 추진 권장. 현재 가격 수준에서 대량 매입을 고려하십시오."
    elif signal_score >= 60:
        signal_status = "매수"
        signal_emoji = "🟢"
        market_context = "양호한 시장 조건입니다."
        cpo_action = "1-2주 내 소싱 계약 체결을 권장합니다."
    elif signal_score >= 45:
        signal_status = "중립 관망"
        signal_emoji = "🟡"
        market_context = "시장이 균형 상태입니다."
        cpo_action = "추가 시장 변동을 모니터링하면서 단계적 접근을 권장합니다."
    elif signal_score >= 30:
        signal_status = "주의"
        signal_emoji = "🟠"
        market_context = "불리한 시장 조건이 예상됩니다."
        cpo_action = "소싱 결정을 1-2주 지연하거나 소량 계약만 진행하십시오."
    else:
        signal_status = "변동성 경고"
        signal_emoji = "🔴"
        market_context = "시장 변동성이 매우 높습니다."
        cpo_action = "소싱 결정을 보류하고 시장 안정화를 기다리십시오."
    
    if not logic_triggers:
        logic_triggers.append("현재 시장은 중립 상태입니다.")
    
    return {
        'signal_status': signal_status,
        'signal_emoji': signal_emoji,
        'signal_strength': signal_score,
        'logic_triggers': logic_triggers,
        'market_context': market_context,
        'cpo_action': cpo_action,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')
    }


# ===========================================
# UI 컴포넌트 (Streamlit Native)
# ===========================================
def render_metric_card(metric: MarketMetric):
    """메트릭 카드 렌더링 (Streamlit Native)"""
    arrow, color_class = get_trend_direction(metric.change)
    color = "#10B981" if color_class == "color-up" else "#EF4444"
    
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">{metric.name}</p>
        <div class="metric-value">
            {metric.price:.2f}
            <span class="metric-unit">{metric.unit}</span>
        </div>
        <div class="metric-change" style="color: {color};">
            {arrow} {abs(metric.change):.2f} ({abs(metric.change_pct):.2f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_card(emoji: str, title: str, desc: str, price_info: str):
    """신호등 카드 렌더링 (Streamlit Native)"""
    st.markdown(f"""
    <div class="signal-card">
        <div class="signal-header">
            <div class="signal-emoji">{emoji}</div>
            <div>
                <h4 class="signal-title">{title}</h4>
            </div>
        </div>
        <p class="signal-desc">{desc}</p>
        <p class="signal-price">{price_info}</p>
    </div>
    """, unsafe_allow_html=True)


def create_price_chart(df: pd.DataFrame, column: str, title: str, unit: str, 
                       color: str, period: str) -> go.Figure:
    """가격 차트 생성"""
    df = df.sort_values('date').reset_index(drop=True)
    y_range = calculate_y_range(df[column])
    
    max_idx = df[column].idxmax()
    min_idx = df[column].idxmin()
    
    fig = go.Figure()
    
    # 메인 라인
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[column],
        mode='lines',
        name=title,
        line=dict(color=color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba(0, 105, 92, 0.1)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>가격: %{y:.2f} ' + unit + '<extra></extra>'
    ))
    
    # 최고가/최저가 마커
    fig.add_trace(go.Scatter(
        x=[df.loc[max_idx, 'date']],
        y=[df.loc[max_idx, column]],
        mode='markers+text',
        marker=dict(color='#EF4444', size=12, symbol='triangle-up'),
        text=['최고가'],
        textposition='top center',
        name='최고가',
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=[df.loc[min_idx, 'date']],
        y=[df.loc[min_idx, column]],
        mode='markers+text',
        marker=dict(color='#10B981', size=12, symbol='triangle-down'),
        text=['최저가'],
        textposition='bottom center',
        name='최저가',
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(text=f'{title} 가격 추이 ({PERIOD_LABELS[period]})', x=0.5),
        xaxis=dict(title='날짜', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(title=f'가격 ({unit})', range=list(y_range)),
        plot_bgcolor='white',
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified'
    )
    
    return fig


# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """소싱 시그널 대시보드를 렌더링합니다."""
    
    # CSS 주입
    inject_custom_css()
    
    # 헤더
    st.markdown("<h1 style='text-align: center; color:#6F4E37;'>원두 시세 및 데이터</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")

    # 실제 데이터 로드
    market_data = get_market_data_live()
    
    
    # ===========================================
    # 섹션 1: Market Data Snapshot
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; color:#6F4E37;">시장 데이터 스냅샷</h3>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for col, key in zip(cols, ['arabica', 'robusta', 'usd_krw', 'freight']):
        with col:
            render_metric_card(market_data[key])
    
    # ===========================================
    # 섹션 2: 선물 가격 추세
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; margin-top: 2rem; color:#6F4E37;">선물 가격 추이</h3>', unsafe_allow_html=True)
    
    period = st.radio("기간 선택", options=['1D', '1W', '1M', '6M', '1Y', '3Y'],
                      index=2, horizontal=True, key="sourcing_period")
    
    hist_data = get_historical_data(period)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_arabica = create_price_chart(hist_data, 'arabica', 'Arabica', '¢/lb', COLOR_PRIMARY, period)
        st.plotly_chart(fig_arabica, use_container_width=True)
    
    with col2:
        fig_robusta = create_price_chart(hist_data, 'robusta', 'Robusta', '$/MT', COLOR_PRIMARY, period)
        st.plotly_chart(fig_robusta, use_container_width=True)
    
    # ===========================================
    # 섹션 3: 소싱 시그널
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; margin-top: 2rem; color:#6F4E37;">소싱 시그널 분석</h3>', unsafe_allow_html=True)
    
    signals = {
        'arabica': analyze_market_signal(market_data['arabica'].change_pct),
        'robusta': analyze_market_signal(market_data['robusta'].change_pct),
        'fx': analyze_market_signal(market_data['usd_krw'].change_pct),
        'freight': analyze_market_signal(market_data['freight'].change_pct)
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_signal_card(
            signals['arabica'][0], "Arabica 소싱", signals['arabica'][2],
            f"현재가 {market_data['arabica'].price:.2f} ¢/lb | 변동 {market_data['arabica'].change_pct:+.2f}%"
        )
        render_signal_card(
            signals['fx'][0], "환율 타이밍", signals['fx'][2],
            f"현재 ₩{market_data['usd_krw'].price:.2f}/$ | 변동 {market_data['usd_krw'].change_pct:+.2f}%"
        )
    
    with col2:
        render_signal_card(
            signals['robusta'][0], "Robusta 소싱", signals['robusta'][2],
            f"현재가 ${market_data['robusta'].price:.2f}/MT | 변동 {market_data['robusta'].change_pct:+.2f}%"
        )
        render_signal_card(
            signals['freight'][0], "물류 리스크", signals['freight'][2],
            f"SCFI 지수 {market_data['freight'].price:.0f} | 변동 {market_data['freight'].change_pct:+.2f}%"
        )
    
    # ===========================================
    # 섹션 4: Executive Summary
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; margin-top: 2rem; color:#6F4E37;">핵심 요약 및 실행 계획</h3>', unsafe_allow_html=True)
    
    algo_signal = generate_algorithmic_signal(market_data)
    
    signal_colors = {
        '강력 매수': '#10B981', '매수': '#34D399', '중립 관망': '#F59E0B',
        '주의': '#F97316', '변동성 경고': '#EF4444'
    }
    signal_color = signal_colors.get(algo_signal['signal_status'], '#6B7280')
    
    # Streamlit 네이티브 컴포넌트로 렌더링
    with st.container():
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 12px; border: 1px solid #E0E0E0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <h4 style="color: {COLOR_PRIMARY}; margin-top: 0;">시장 상황 분석</h4>
            <p style="color: #555; line-height: 1.6;">{algo_signal['market_context']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 시그널 배지
        st.markdown(f"""
        <div style="background: #F5F5F5; padding: 1rem; border-radius: 8px; border-left: 4px solid {signal_color}; margin: 1rem 0;">
            <strong style="font-size: 1.1rem;">시그널: {algo_signal['signal_emoji']} {algo_signal['signal_status']}</strong>
            <br>
            <span style="color: #666;">강도: {algo_signal['signal_strength']}/100</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 로직 트리거
        st.markdown(f"<h5 style='color: {COLOR_PRIMARY}; margin-top: 1.5rem; margin-bottom: 0.5rem;'>로직 트리거:</h5>", unsafe_allow_html=True)
        for trigger in algo_signal['logic_triggers']:
            # 이모티콘 제거 및 폰트 사이즈 키움 (1.1rem)
            st.markdown(f"- <span style='font-size: 1.1rem;'>{trigger}</span>", unsafe_allow_html=True)
        
        # CPO 실행 권고
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {signal_color}15 0%, {signal_color}08 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid {signal_color}; margin-top: 1.5rem;">
            <strong style="color: {signal_color}; font-size: 1.05rem;">💡 CPO 실행 권고사항:</strong>
            <br><br>
            <p style="margin: 0; color: #333; line-height: 1.6;">{algo_signal['cpo_action']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption(f"Last Updated: {market_data['last_updated']}")


if __name__ == "__main__":
    show()