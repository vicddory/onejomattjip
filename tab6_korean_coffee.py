# -*- coding: utf-8 -*-
"""
Tab 6: Korean Coffee Market - 대한민국 커피 수입 데이터 분석
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

# ==========================================
# 데이터 로드 함수
# ==========================================
@st.cache_data
def load_data():
    """coffee_data.csv 로드 및 전처리"""
    # 여러 경로에서 파일 찾기
    possible_paths = [
        'data/coffee_data.csv',
        './data/coffee_data.csv',
        '../data/coffee_data.csv',
        'coffee_data.csv',
        Path(__file__).parent.parent / 'data' / 'coffee_data.csv'
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
        # 기본 데이터 (파일 없을 경우)
        df = pd.DataFrame({
            'year': [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'import_volume': [158385, 167654, 176648, 189502, 205065, 192623, 215838, 215792],
            'import_value': [637, 662, 738, 916, 1305, 1111, 1378, 1861]
        })
    
    df.columns = ['연도', '수입량(톤)', '수입액(백만달러)']
    df['수입량 증가율(%)'] = df['수입량(톤)'].pct_change() * 100
    df['수입액 증가율(%)'] = df['수입액(백만달러)'].pct_change() * 100
    return df

# ==========================================
# 메인 show 함수
# ==========================================
def show():
    """Korean Market 페이지를 렌더링하는 메인 함수"""
    
    df = load_data()
    
    if df is not None:
        st.title("☕ 대한민국 커피 수입 : 규모와 속도 분리 분석")
        st.markdown("---")

        # ==========================================
        # 1. 수입 규모 분석 (Absolute Value)
        # ==========================================
        st.subheader("1️⃣ 수입 규모 (수입량 & 수입액)")
        st.caption("연도별 실제 수입된 물량과 금액의 크기입니다.")

        col1, col2 = st.columns(2)

        # [왼쪽] 수입량 그래프
        with col1:
            st.markdown("**📦 연도별 수입량 (톤)**")
            fig_vol = px.bar(df, x='연도', y='수입량(톤)', 
                             text='수입량(톤)', color_discrete_sequence=['#8D6E63'])
            fig_vol.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_vol.update_layout(yaxis_showgrid=False)
            st.plotly_chart(fig_vol, use_container_width=True)

        # [오른쪽] 수입액 그래프
        with col2:
            st.markdown("**💰 연도별 수입액 (백만달러)**")
            fig_val = px.bar(df, x='연도', y='수입액(백만달러)', 
                             text='수입액(백만달러)', color_discrete_sequence=['#D4AC0D'])
            fig_val.update_traces(texttemplate='$%{text:,}', textposition='outside')
            fig_val.update_layout(yaxis_showgrid=False)
            st.plotly_chart(fig_val, use_container_width=True)

        # [데이터 표 - 규모]
        with st.expander("🔽 수입 규모 데이터 상세 보기"):
            st.dataframe(
                df[['연도', '수입량(톤)', '수입액(백만달러)']].style.format({
                    '수입량(톤)': '{:,.0f}', 
                    '수입액(백만달러)': '${:,.0f}'
                }), 
                use_container_width=True
            )

        st.markdown("---")

        # ==========================================
        # 2. 증가율 분석 (Growth Rate)
        # ==========================================
        st.subheader("2️⃣ 전년 대비 증가율 (변동 추이)")
        st.caption("작년보다 얼마나 늘었거나 줄었는지(%) 보여줍니다. (첫 해 제외)")

        # 첫 해(NaN) 제외 데이터 필터링
        chart_df = df.dropna(subset=['수입량 증가율(%)', '수입액 증가율(%)'])

        # 증가율 꺾은선 그래프 통합
        fig_rate = go.Figure()
        
        # 수입량 증가율 선
        fig_rate.add_trace(go.Scatter(
            x=chart_df['연도'], y=chart_df['수입량 증가율(%)'],
            mode='lines+markers+text',
            name='수입량 증가율',
            text=[f"{v:.1f}%" for v in chart_df['수입량 증가율(%)']],
            textposition="top center",
            line=dict(color='gray', width=2, dash='dot')
        ))

        # 수입액 증가율 선
        fig_rate.add_trace(go.Scatter(
            x=chart_df['연도'], y=chart_df['수입액 증가율(%)'],
            mode='lines+markers+text',
            name='수입액 증가율',
            text=[f"{v:.1f}%" for v in chart_df['수입액 증가율(%)']],
            textposition="bottom center",
            line=dict(color='red', width=3)
        ))

        # 0% 기준선 추가 (증가/감소 구분)
        fig_rate.add_hline(y=0, line_width=1, line_dash="solid", line_color="black")

        fig_rate.update_layout(
            title="📈 수입량 vs 수입액 증가율 비교",
            yaxis_title="증가율 (%)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rate, use_container_width=True)

        # [데이터 표 - 증가율]
        with st.expander("🔽 증가율 데이터 상세 보기"):
            st.dataframe(
                chart_df[['연도', '수입량 증가율(%)', '수입액 증가율(%)']].style.format({
                    '수입량 증가율(%)': '{:+.1f}%', 
                    '수입액 증가율(%)': '{:+.1f}%'
                }).background_gradient(cmap='RdYlBu_r', axis=0),
                use_container_width=True
            )
        
        # ==========================================
        # 3. 주요 인사이트
        # ==========================================
        st.markdown("---")
        st.subheader("3️⃣ 주요 인사이트")
        
        # 최신 연도 데이터
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            vol_change = ((latest['수입량(톤)'] - prev['수입량(톤)']) / prev['수입량(톤)']) * 100
            st.metric(
                f"{int(latest['연도'])}년 수입량",
                f"{int(latest['수입량(톤)']):,} 톤",
                f"{vol_change:+.1f}% vs {int(prev['연도'])}년"
            )
        
        with col2:
            val_change = ((latest['수입액(백만달러)'] - prev['수입액(백만달러)']) / prev['수입액(백만달러)']) * 100
            st.metric(
                f"{int(latest['연도'])}년 수입액",
                f"${int(latest['수입액(백만달러)']):,}M",
                f"{val_change:+.1f}% vs {int(prev['연도'])}년"
            )
        
        with col3:
            avg_price = (latest['수입액(백만달러)'] * 1000000) / (latest['수입량(톤)'] * 1000)
            st.metric(
                "평균 kg당 수입가격",
                f"${avg_price:.2f}/kg",
                "FOB 기준 추정"
            )
        
        # 분석 코멘트
        st.markdown("""
        <div style="background-color: #FFF8E1; padding: 20px; border-radius: 10px; border-left: 5px solid #FFC107; margin-top: 20px;">
            <h4 style="margin-top: 0; color: #6F4E37;">📊 데이터 해석</h4>
            <ul style="color: #333;">
                <li><b>수입량</b>: 물리적으로 얼마나 많은 커피가 들어왔는지 (수요 추세)</li>
                <li><b>수입액</b>: 얼마를 지불했는지 (가격 변동 + 수량 변동 복합)</li>
                <li><b>증가율 격차</b>: 수입액 증가율 > 수입량 증가율 → 국제 커피 가격 상승 시그널</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ 데이터를 불러올 수 없습니다. coffee_data.csv 파일을 확인해주세요.")
