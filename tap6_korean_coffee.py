import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 페이지 설정
st.set_page_config(page_title="커피 수입 데이터 분리 분석", layout="wide")

# 데이터 로드 및 전처리
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df.columns = ['연도', '수입량(톤)', '수입액(백만달러)']
        # 증가율 계산 (YoY)
        df['수입량 증가율(%)'] = df['수입량(톤)'].pct_change() * 100
        df['수입액 증가율(%)'] = df['수입액(백만달러)'].pct_change() * 100
        return df
    return None

df = load_data('coffee_data.csv')

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
    st.caption("작년보다 얼마나 늘었거나 줄었는지(%) 보여줍니다. (2018년 제외)")

    # 2019년부터 데이터 필터링 (NaN 제거)
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
            }).background_gradient(cmap='RdYlBu_r', axis=0), # 높을수록 붉은색
            use_container_width=True
        )