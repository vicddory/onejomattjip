# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab6_korean_market.py - 대한민국 커피 수입 데이터 분석
================================================================================
한국 커피 시장의 수입량과 수입액 트렌드를 분석합니다.
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path


# ===========================================
# 데이터 로드 함수
# ===========================================
@st.cache_data
def load_data():
    """coffee_data.csv 로드 및 전처리"""
    possible_paths = [
        Path(__file__).parent.parent / 'data' / 'coffee_data.csv',
        'data/coffee_data.csv',
        './data/coffee_data.csv',
        'coffee_data.csv',
    ]
    
    df = None
    for file_path in possible_paths:
        try:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                break
        except:
            continue
    
    if df is None:
        df = pd.DataFrame({
            'year': [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'import_volume': [158385, 167654, 176648, 189502, 205065, 192623, 215838, 215792],
            'import_value': [637, 662, 738, 916, 1305, 1111, 1378, 1861]
        })
    
    df.columns = ['연도', '수입량(톤)', '수입액(백만달러)']
    df['수입량 증가율(%)'] = df['수입량(톤)'].pct_change() * 100
    df['수입액 증가율(%)'] = df['수입액(백만달러)'].pct_change() * 100
    return df


# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """한국 커피 시장 페이지를 렌더링합니다."""
    
    df = load_data()
    
    # st.title("국내 원두 수입 동향")  <-- 이건 지우고

    # 요래 바꾸면 가운데로 딱 옵니데이
    st.markdown("<h1 style='text-align: center;'>국내 원두 수입 동향</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    
    # 1. 수입 규모 분석
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; color:#6F4E37;">수입 규모 (수입량 & 수입액)</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(" ")
        # 별표(**) 빼고 HTML <b> 태그로 깔끔하게 굵게 맹글었심더
        st.markdown("<b>연도별 수입량 (톤)</b>", unsafe_allow_html=True)
        fig_vol = px.bar(df, x='연도', y='수입량(톤)', text='수입량(톤)', color_discrete_sequence=['#8D6E63'])
        fig_vol.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_vol.update_layout(yaxis_showgrid=False)
        st.plotly_chart(fig_vol, use_container_width=True)

    with col2:
        st.markdown(" ")
        # 여기도 별표 싹 걷어내고 볼드체 딱 적용했습니데이
        st.markdown("<b>연도별 수입액 (백만달러)</b>", unsafe_allow_html=True)
        fig_val = px.bar(df, x='연도', y='수입액(백만달러)', text='수입액(백만달러)', color_discrete_sequence=['#D4AC0D'])
        fig_val.update_traces(texttemplate='$%{text:,}', textposition='outside')
        fig_val.update_layout(yaxis_showgrid=False)
        st.plotly_chart(fig_val, use_container_width=True)

    with st.expander(" 수입 규모 데이터 상세 보기"):
        # 1. 먼저 보여줄 컬럼만 딱 떼서 변수에 담고 (copy() 써야 원본 안 다칩니데이)
        display_df = df[['연도', '수입량(톤)', '수입액(백만달러)']].copy()
        
        # 2. 인덱스를 1씩 싹 다 올려줍니다
        display_df.index = display_df.index + 1
        
        # 3. 그 다음에 출력하면 1번부터 깔끔하게 나옵니데이!
        st.dataframe(display_df, use_container_width=True)

    st.markdown("---")

    # 2. 증가율 분석
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; color:#6F4E37;">전년 대비 증가율 (변동 추이)</h3>', unsafe_allow_html=True)
    
    chart_df = df.dropna(subset=['수입량 증가율(%)', '수입액 증가율(%)'])

    fig_rate = go.Figure()
    
    fig_rate.add_trace(go.Scatter(
        x=chart_df['연도'], y=chart_df['수입량 증가율(%)'],
        mode='lines+markers+text', name='수입량 증가율',
        text=[f"{v:.1f}%" for v in chart_df['수입량 증가율(%)']],
        textposition="top center", line=dict(color='gray', width=2, dash='dot')
    ))

    fig_rate.add_trace(go.Scatter(
        x=chart_df['연도'], y=chart_df['수입액 증가율(%)'],
        mode='lines+markers+text', name='수입액 증가율',
        text=[f"{v:.1f}%" for v in chart_df['수입액 증가율(%)']],
        textposition="bottom center", line=dict(color='#8D6E63', width=3)
    ))

    fig_rate.add_hline(y=0, line_width=1, line_dash="solid", line_color="black")
    fig_rate.update_layout(
        title=" 수입량 vs 수입액 증가율 비교",
        yaxis_title="증가율 (%)", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_rate, use_container_width=True)

    with st.expander("증가율 데이터 상세 보기"):
        st.dataframe(chart_df[['연도', '수입량 증가율(%)', '수입액 증가율(%)']], use_container_width=True)
    
    st.markdown("---")

    # 3. 주요 인사이트
    st.markdown('<h3 style="border-bottom: 3px solid #00695C; padding-bottom: 8px; color:#6F4E37;">주요 인사이트</h3>', unsafe_allow_html=True)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 데이터 계산
    vol_change = ((latest['수입량(톤)'] - prev['수입량(톤)']) / prev['수입량(톤)']) * 100
    val_change = ((latest['수입액(백만달러)'] - prev['수입액(백만달러)']) / prev['수입액(백만달러)']) * 100
    avg_price = (latest['수입액(백만달러)'] * 1000000) / (latest['수입량(톤)'] * 1000)
    
    # 카드 HTML 생성 헬퍼 함수
    def create_card(title, value, delta_text, delta_color):
        return f"""
        <div style="
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            padding: 20px;
            background-color: #FFFFFF;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        ">
            <div style="color: #757575; font-size: 14px; margin-bottom: 5px;">{title}</div>
            <div style="color: #212121; font-size: 28px; font-weight: 700; margin-bottom: 8px;">{value}</div>
            <div style="color: {delta_color}; font-size: 14px; font-weight: 500;">{delta_text}</div>
        </div>
        """

    col1, col2, col3 = st.columns(3)
    
    with col1:
        color = "#D32F2F" if vol_change < 0 else "#388E3C" # 하락이면 빨강, 상승이면 초록
        arrow = "▼" if vol_change < 0 else "▲"
        st.markdown(create_card(
            f"{int(latest['연도'])}년 수입량",
            f"{int(latest['수입량(톤)']):,} 톤",
            f"{arrow} {abs(vol_change):.1f}%",
            color
        ), unsafe_allow_html=True)
    
    with col2:
        color = "#D32F2F" if val_change < 0 else "#388E3C"
        arrow = "▼" if val_change < 0 else "▲"
        st.markdown(create_card(
            f"{int(latest['연도'])}년 수입액",
            f"${int(latest['수입액(백만달러)']):,}M",
            f"{arrow} {abs(val_change):.1f}%",
            color
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_card(
            "평균 kg당 수입가격",
            f"${avg_price:.2f}/kg",
            "↑ FOB 기준",
            "#388E3C"
        ), unsafe_allow_html=True)
    
    # 노란색 -> 초록색 그라데이션 스타일로 변경 (요청하신 대로 적용!)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #388E3C15 0%, #388E3C08 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid #388E3C; margin-top: 1.5rem;">
        <h4 style="margin-top: 0; color: #388E3C;"> 데이터 해석</h4>
        <ul style="color: #333;">
            <li><b>수입량</b>: 물리적으로 얼마나 많은 커피가 들어왔는지 (수요 추세)</li>
            <li><b>수입액</b>: 얼마를 지불했는지 (가격 변동 + 수량 변동 복합)</li>
            <li><b>증가율 격차</b>: 수입액 증가율 > 수입량 증가율 → 국제 커피 가격 상승 시그널</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show()