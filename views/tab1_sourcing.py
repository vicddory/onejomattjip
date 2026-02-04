# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab1_sourcing.py - 커피 소싱 시그널 대시보드
================================================================================
실시간 시장 데이터와 알고리즘 기반 소싱 시그널을 제공합니다.

💡 이 파일의 역할:
- 시장 데이터 스냅샷 (Arabica, Robusta, 환율, 운임)
- 선물 가격 추이 차트
- 소싱 시그널 (신호등 시스템)
- CPO 실행 권고사항
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re

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
# 유틸리티 함수
# ===========================================
def render_html(html_content: str) -> None:
    """HTML을 Streamlit에서 안전하게 렌더링"""
    cleaned = re.sub(r'^```html\s*\n|^```\s*\n|\n```\s*$|```$', '', html_content, flags=re.MULTILINE).strip()
    st.markdown(cleaned, unsafe_allow_html=True)


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
    """API 기반 알고리즘 시그널 생성"""
    arabica = market_data['arabica']
    robusta = market_data['robusta']
    fx = market_data['usd_krw']
    freight = market_data['freight']
    
    signal_score = 50
    logic_triggers = []
    
    # Arabica 분석
    if arabica.change_pct < -1.5:
        signal_score += 20
        logic_triggers.append(f"아라비카 가격 {abs(arabica.change_pct):.2f}% 하락 → 매수 유리")
    elif arabica.change_pct > 1.5:
        signal_score -= 20
        logic_triggers.append(f"아라비카 가격 +{arabica.change_pct:.2f}% 상승 → 진입 시점 불리")
    
    # Robusta 분석
    if robusta.change_pct < -1.5:
        signal_score += 15
        logic_triggers.append(f"로부스타 가격 {abs(robusta.change_pct):.2f}% 하락 → 베트남 공급 안정")
    elif robusta.change_pct > 1.5:
        signal_score -= 15
        logic_triggers.append(f"로부스타 가격 +{robusta.change_pct:.2f}% 상승 → 공급 우려 감지")
    
    # 환율 분석
    if fx.change_pct < -0.5:
        signal_score += 10
        logic_triggers.append(f"원화 강세 ({fx.change_pct:+.2f}%) → 구매력 향상")
    elif fx.change_pct > 0.8:
        signal_score -= 10
        logic_triggers.append(f"원화 약세 (+{fx.change_pct:.2f}%) → 수입 비용 증가")
    
    # 물류 분석
    if freight.change_pct < -2.0:
        signal_score += 10
        logic_triggers.append(f"운임 비용 {abs(freight.change_pct):.2f}% 하락 → 물류 이점 확보")
    elif freight.change_pct > 2.0:
        signal_score -= 10
        logic_triggers.append(f"운임 비용 +{freight.change_pct:.2f}% 상승 → 물류 부담 증가")
    
    # 시그널 상태 결정
    if signal_score >= 75:
        signal_status = "강력 매수"
        signal_emoji = "🟢🟢"
        market_context = "매우 유리한 시장 조건이 감지되었습니다."
        cpo_action = "실행 권고: 장기 계약 체결. 정상 일정보다 3-6개월 앞당겨 매수 검토."
    elif signal_score >= 60:
        signal_status = "매수"
        signal_emoji = "🟢"
        market_context = "유리한 매수 시점이 확인되었습니다."
        cpo_action = "진행 권고: 정상~증량 구매. 현물 계약 확보."
    elif signal_score >= 40:
        signal_status = "중립 관망"
        signal_emoji = "🟡"
        market_context = "시장에 혼재된 신호가 나타납니다."
        cpo_action = "모니터링: 표준 조달 일정 유지. 추세 변화 주시."
    elif signal_score >= 25:
        signal_status = "주의"
        signal_emoji = "🟠"
        market_context = "불리한 조건이 나타나고 있습니다."
        cpo_action = "지연 권고: 구매 물량 축소. 단기 계약만 고려."
    else:
        signal_status = "변동성 경고"
        signal_emoji = "🔴"
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


# ===========================================
# UI 컴포넌트
# ===========================================
def create_metric_card(metric: MarketMetric) -> str:
    """메트릭 카드 HTML 생성"""
    arrow, color_class = get_trend_direction(metric.change)
    
    return f'''
    <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 16px; margin-bottom: 8px;">
        <p style="margin: 0; color: #666; font-size: 0.9rem;">{metric.name}</p>
        <div style="font-size: 1.5rem; font-weight: 700; color: #333;">
            {metric.price:.2f}
            <span style="font-size: 0.9rem; color: #999;">{metric.unit}</span>
        </div>
        <div class="{color_class}" style="font-size: 0.9rem;">
            {arrow} {abs(metric.change):.2f} ({abs(metric.change_pct):.2f}%)
        </div>
    </div>
    '''


def create_signal_card(emoji: str, title: str, desc: str, price_info: str) -> str:
    """신호등 카드 HTML 생성"""
    signal_color = {"🟢": "green", "🟡": "yellow", "🔴": "red"}[emoji]
    
    return f'''
    <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 24px; margin-right: 16px;">{emoji}</div>
            <div>
                <h4 style="margin: 0; color: #333;">{title}</h4>
                <p style="margin: 0.5rem 0 0 0; color: #333;">{desc}</p>
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
        mode='markers',
        marker=dict(color='#EF4444', size=12, symbol='triangle-up'),
        name='최고가',
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=[df.loc[min_idx, 'date']],
        y=[df.loc[min_idx, column]],
        mode='markers',
        marker=dict(color='#10B981', size=12, symbol='triangle-down'),
        name='최저가',
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(text=f'{title} 가격 추이 ({PERIOD_LABELS[period]})', x=0.5),
        xaxis=dict(title='날짜', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(title=f'가격 ({unit})', range=list(y_range)),
        plot_bgcolor='white',
        height=350,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """소싱 시그널 대시보드를 렌더링합니다."""
    
    # 헤더
    st.markdown("<h1 style='text-align: center;'>커피 소싱 시그널 대시보드</h1>", unsafe_allow_html=True)
    st.divider()

    # 실제 데이터 로드
    market_data = get_market_data_live()
    
    # ===========================================
    # 섹션 1: Market Data Snapshot
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px;">시장 데이터 스냅샷</h3>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for col, key in zip(cols, ['arabica', 'robusta', 'usd_krw', 'freight']):
        with col:
            render_html(create_metric_card(market_data[key]))
    
    # ===========================================
    # 섹션 2: 선물 가격 추세
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; margin-top: 2rem;">선물 가격 추이</h3>', unsafe_allow_html=True)
    
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
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; margin-top: 2rem;">소싱 시그널 분석</h3>', unsafe_allow_html=True)
    
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
    
    # ===========================================
    # 섹션 4: Executive Summary
    # ===========================================
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; margin-top: 2rem;">핵심 요약 및 실행 계획</h3>', unsafe_allow_html=True)
    
    algo_signal = generate_algorithmic_signal(market_data)
    
    signal_colors = {
        '강력 매수': '#10B981', '매수': '#34D399', '중립 관망': '#F59E0B',
        '주의': '#F97316', '변동성 경고': '#EF4444'
    }
    signal_color = signal_colors.get(algo_signal['signal_status'], '#6B7280')
    
    triggers_html = ''.join([f'<li>{t}</li>' for t in algo_signal['logic_triggers']])
    
    st.markdown(f"""
    <div style="background: white; padding: 2rem; border-radius: 12px; border: 1px solid #E0E0E0;">
        <h4 style="color: {COLOR_PRIMARY};">시장 상황 분석</h4>
        <p>{algo_signal['market_context']}</p>
        
        <div style="background: #F5F5F5; padding: 1rem; border-radius: 8px; border-left: 4px solid {signal_color}; margin: 1rem 0;">
            <strong>시그널: {algo_signal['signal_emoji']} {algo_signal['signal_status']}</strong>
            <br>강도: {algo_signal['signal_strength']}/100
        </div>
        
        <h5>로직 트리거:</h5>
        <ul>{triggers_html}</ul>
        
        <div style="background: linear-gradient(135deg, {signal_color}15 0%, {signal_color}08 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid {signal_color};">
            <strong>CPO 실행 권고사항:</strong><br>
            {algo_signal['cpo_action']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Last Updated: {market_data['last_updated']}")


if __name__ == "__main__":
    show()
