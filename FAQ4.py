# 필수 라이브러리: pip install streamlit pandas plotly openai python-dotenv

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# --- 1. 환경 설정 및 컬러 테마 ---
load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

COLOR_DEEP_COFFEE = "#4B2C20" 
COLOR_PAPER_BG = "#FAF7F2"     
COLOR_FUTURE_GOLD = "#D4AF37"  
COLOR_SAFE_GREEN = "#2E7D32"   
COLOR_RISK_RED = "#D32F2F"     
COLOR_STABLE_GRAY = "#7F8C8D"  

st.set_page_config(page_title="AI Supply Chain Rebalancing", layout="wide")

# 전문적인 커스텀 CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_PAPER_BG}; }}
    .strategy-container {{ background-color: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
    h1, h2, h3 {{ color: {COLOR_DEEP_COFFEE} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 2. OpenAI 기반 기후 트렌드 분석 (13개국) ---
@st.cache_data(show_spinner=False)
def get_ai_rebalancing_data():
    if not api_key: return None
    client = OpenAI(api_key=api_key)
    
    # 13개국 설정 (기존 10국 + 신규 3국)
    target_countries = [
        "브라질", "베트남", "인도네시아", "온두라스", "과테말라", 
        "페루", "콜롬비아", "코스타리카", "에티오피아", "케냐",
        "우간다", "탄자니아", "중국(윈난)"
    ]
    
    prompt = f"""
    당신은 기후 위기 시나리오(RCP 8.5)를 분석하는 데이터 과학자입니다. 
    다음 13개국의 2050년까지 커피 생산성 변화를 분석하세요: {target_countries}
    
    [결과 가이드라인]
    1. 브라질, 베트남, 인도네시아, 온두라스, 과테말라: Risk (연간 -1.5% ~ -3.5%)
    2. 페루, 콜롬비아, 코스타리카: Stable (연간 -0.5% ~ +0.5%)
    3. 에티오피아, 케냐, 우간다: Opportunity (연간 +1.0% ~ +2.0%)
    4. 탄자니아, 중국(윈난): Next Frontier (연간 +2.5% ~ +4.5%)
    
    반드시 다음 JSON 형식으로만 출력하세요:
    [
        {{"Country": "국가명", "Region": "지역", "Annual_Trend": 숫자, "Type": "Risk/Stable/Opportunity/Next Frontier", "Reason": "설명"}}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "JSON format only."}, {"role": "user", "content": prompt}],
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

# --- 3. 데이터 시뮬레이션 엔진 ---
def run_rebalancing_sim(ai_data, target_year):
    base_year = 2025
    years_passed = target_year - base_year
    sim_results = []
    
    for item in ai_data:
        # 복리 계산을 통한 미래 영향도 산출
        impact = (1 + item['Annual_Trend'] / 100) ** years_passed - 1
        sim_results.append({
            "Country": item['Country'],
            "Region": item['Region'],
            "Climate_Impact": round(impact * 100, 1),
            "Shift_Type": item['Type'],
            "Description": item['Reason']
        })
    return pd.DataFrame(sim_results)

# --- 4. 메인 UI 구성 ---
st.markdown(f"<h1 style='text-align: left;'>🌎 AI 기반 지정학적 공급망 리밸런싱</h1>", unsafe_allow_html=True)
st.caption("OpenAI RCP 8.5 시나리오 분석: 2025년 대비 미래 산지 생산성 변화 예측")

# 데이터 로드
if 'rebalance_db' not in st.session_state:
    with st.spinner("🤖 AI가 글로벌 기후 시나리오를 시뮬레이션 중입니다..."):
        raw_ai = get_ai_rebalancing_data()
        if raw_ai: st.session_state['rebalance_db'] = raw_ai

if 'rebalance_db' in st.session_state:
    # [A] Time Machine 슬라이더
    st.write("")
    st.markdown("### 📅 예측 시점 설정 (Time Machine)")
    selected_year = st.slider("연도를 조절하여 공급망의 구조적 변화를 추적하세요", 2025, 2050, 2050, step=1)
    
    # 해당 연도의 데이터 계산
    df_re = run_rebalancing_sim(st.session_state['rebalance_db'], selected_year)

    # [B] 메인 그래프
    st.subheader(f"📈 {selected_year}년 국가별 생산성 변동률 예측")
    
    fig = px.bar(
        df_re.sort_values("Climate_Impact"), 
        x="Country", y="Climate_Impact", color="Shift_Type",
        color_discrete_map={
            "Risk": COLOR_RISK_RED, 
            "Opportunity": COLOR_SAFE_GREEN, 
            "Next Frontier": COLOR_FUTURE_GOLD, 
            "Stable": COLOR_STABLE_GRAY
        },
        labels={"Climate_Impact": "예상 생산량 변화 (%)"},
        text_auto='.1f'
    )
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")

    # [C] 전략 분석 & 액션 가이드 (시각적 균형 최적화 버전)
    col_sel, col_val = st.columns([1, 1.4])

    with col_sel:
        st.markdown(f"### 🎯 {selected_year} 전략 국가 심층 분석")
        target = st.selectbox("리포트를 확인할 국가를 선택하세요", df_re['Country'].tolist(), index=12)
        c_info = df_re[df_re['Country'] == target].iloc[0]
        
        status_theme = {
            "Next Frontier": COLOR_FUTURE_GOLD, "Risk": COLOR_RISK_RED,
            "Opportunity": COLOR_SAFE_GREEN, "Stable": COLOR_STABLE_GRAY
        }.get(c_info['Shift_Type'], COLOR_DEEP_COFFEE)
        
        st.markdown(f"""
            <div style="background-color: white; padding: 24px; border-radius: 12px; border-top: 10px solid {status_theme}; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 315px; display: flex; flex-direction: column; justify-content: center;">
                <p style="color: #666; font-size: 0.85rem; margin-bottom: 2px; letter-spacing: 1px;">STRATEGIC REPORT ({selected_year})</p>
                <h2 style="margin: 0 0 10px 0; color:{COLOR_DEEP_COFFEE}; font-size: 1.8rem; line-height: 1.2;">{target}</h2>
                <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                    <span style="background-color: {status_theme}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; font-weight: bold;">{c_info['Shift_Type']}</span>
                    <span style="background-color: #F8F9FA; color: {COLOR_DEEP_COFFEE}; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; border: 1px solid #EEE;">{c_info['Region']}</span>
                </div>
                <p style="font-size: 1.1rem; font-weight: bold; color: {status_theme}; margin-bottom: 8px;">누적 생산성 변동: {c_info['Climate_Impact']}%</p>
                <hr style="border: 0; border-top: 1px solid #EEE; margin: 10px 0;">
                <p style="line-height: 1.5; color: #444; font-size: 0.95rem; margin: 0;">{c_info['Description']}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_val:
        st.markdown(f"### 🚀 리밸런싱 액션 가이드")
        
        # 줄바꿈 문제 해결 및 균형 맞춘 디자인
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="background-color: #F0F4F0; padding: 18px; border-radius: 10px; border-left: 5px solid {COLOR_SAFE_GREEN};">
                    <p style="margin:0; font-weight:bold; color:{COLOR_SAFE_GREEN}; font-size: 1rem;">🛡️ 아프리카 공급망 거점 강화 (Tanzania & Uganda)</p>
                    <p style="margin: 4px 0 0 0; font-size: 0.9rem; line-height: 1.4;">동아프리카 고산지대는 기후 변화의 최대 수혜지로 부상합니다.<br>현지 농장 선점 및 선제적 파트너십 구축이 시급합니다.</p>
                </div>
                <div style="background-color: #FFF9E6; padding: 18px; border-radius: 10px; border-left: 5px solid {COLOR_FUTURE_GOLD};">
                    <p style="margin:0; font-weight:bold; color:{COLOR_FUTURE_GOLD}; font-size: 1rem;">⚡ 동아시아 물류 허브 선점 (China Yunnan)</p>
                    <p style="margin: 4px 0 0 0; font-size: 0.9rem; line-height: 1.4;">지리적 이점과 탄소 규제 대응을 위해 중국 윈난 산지를<br>'차세대 전략 엔진'으로 격상하여 운용하십시오.</p>
                </div>
                <div style="background-color: #F8F9FA; padding: 18px; border-radius: 10px; border-left: 5px solid {COLOR_STABLE_GRAY};">
                    <p style="margin:0; font-weight:bold; color:{COLOR_STABLE_GRAY}; font-size: 1rem;">📉 고위험 산지 의존도 분산 전략</p>
                    <p style="margin: 4px 0 0 0; font-size: 0.9rem; line-height: 1.4;">기온 상승 직격탄을 받는 저지대 의존도를 <b>{selected_year}년까지 점진적 축소</b>하고<br>안정적 고산지 포트폴리오로 재편하십시오.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.caption(f"© 2026 무역 AX 마스터 1기 | Data Source: OpenAI Scenario Engine (Based on IPCC AR6) | Current View: {selected_year}")