# 필수 라이브러리 설치: pip install streamlit pandas plotly openai python-dotenv

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from openai import OpenAI

# --- 0. 환경 변수 로드 (API Key) ---
load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

# --- 1. 디자인 및 컬러 설정 ---
COLOR_DEEP_COFFEE = "#4B2C20"
COLOR_SAFE = "#2E7D32"
COLOR_WARNING = "#F9A825"
COLOR_RISK = "#D32F2F"

st.set_page_config(page_title="Coffee Import Compliance", layout="wide")

st.markdown(f"""
    <style>
    .report-card {{ background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px; }}
    .regulation-item {{ padding: 12px; border-left: 5px solid {COLOR_DEEP_COFFEE}; background-color: #FDFBFA; margin-bottom: 10px; border-radius: 0 8px 8px 0; }}
    .ai-box {{ background-color: #F0F4F8; padding: 20px; border-radius: 12px; border: 1px dashed #4B2C20; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 통합 규제 데이터베이스 ---
@st.cache_data
def get_regulation_db():
    reg_data = {
        "Country": ["Brazil", "Vietnam", "Colombia", "Ethiopia", "Peru", "Honduras", "Indonesia", "Guatemala", "Costa Rica", "Kenya"],
        "Risk_Level": [3, 2, 2, 1, 2, 3, 3, 2, 1, 1], # 3: High, 2: Medium, 1: Low
        "EUDR_Risk": ["High", "Medium", "Medium", "Low", "Medium", "High", "High", "Medium", "Low", "Low"],
        "Import_Regulation": "검역/잔류농약",
        "Labor_Compliance": "아동노동/인권",
        "Certification": "지속가능성인증",
        "Description": [
            "아마존 산림 보존과 관련된 EUDR 실사가 매우 엄격하며, 대규모 농장의 탄소 배출권 관리가 필수적입니다.",
            "농약 잔류 허용 기준(MRL) 위반 사례 모니터링이 필요하며, 수입 전 정밀 검역이 권장됩니다.",
            "수자원 관리 및 생물다양성 보존 리포트가 중요하며, 고품질 스페셜티 인증 비중이 높습니다.",
            "산림 파괴 리스크는 낮으나 공급망 내 노동 인권 및 공정무역 준수 여부 실사가 강조됩니다.",
            "안데스 보호 구역 내 경작 여부 확인을 위한 정밀 지오태깅(Geo-tagging) 데이터 제출이 요구됩니다.",
            "최근 산림 면적 변화율이 급격히 상승하여 EUDR 고위험군으로 분류, 강력한 실사가 수반됩니다.",
            "열대 우림 및 이탄지 보호 규제(ISPO) 준수가 핵심이며, 공급망 투명성 확보가 시급합니다.",
            "토양 보호 및 생산지 위치 정보의 정확성이 요구되며 산림 인접 농장에 대한 주의가 필요합니다.",
            "국가 주도의 탄소 중립 정책으로 규제 대응력이 우수하며 안정적인 공급망을 유지하고 있습니다.",
            "고산지대 생태계 보호 및 노동 환경에 대한 포괄적인 컴플라이언스 리포트가 필요합니다."
        ]
    }
    return pd.DataFrame(reg_data)

df_reg = get_regulation_db()

# --- 3. OpenAI 분석 함수 (캐싱 적용: 중요!) ---
# @st.cache_data를 써야 같은 나라를 다시 클릭했을 때 돈이 안 나가고 속도가 빠름
@st.cache_data(show_spinner=False) 
def get_ai_summary(country):
    if not api_key:
        return "⚠️ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        당신은 한국의 숙련된 커피 수입 무역 전문가입니다.
        현재 '{country}'에서 커피 생두를 수입하려고 합니다.
        
        다음 내용을 포함하여 구매팀이 준비해야 할 것을 '한 줄'로 명확하게 요약해 주세요:
        1. 필수 서류 (원산지 증명서, 검역증 등)
        2. 특별히 주의해야 할 점 (잔류농약, EUDR 등)
        3. 구매팀의 핵심 행동 가이드
        
        답변 형식 예시: "필수 서류로 [서류명]을 준비하고, [주의사항]에 유의하여 [행동] 하십시오."
        말투는 정중하고 전문적으로 하세요.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "핵심만 간결하게 요약하는 무역 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"분석 중 오류 발생: {str(e)}"

# --- 4. UI 구성 ---
st.markdown(f"<h1 style='color: {COLOR_DEEP_COFFEE};'>🛰️ 커피 생두 수입 통합 컴플라이언스 분석</h1>", unsafe_allow_html=True)

with st.container():
    st.info("""
        **안내:** 본 시스템은 **환경(EUDR)**, **식품안전(검역)**, **노동(인권)** 등 커피 수입 시 필수적으로 검토해야 할 
        글로벌 규제 리스크를 국가별로 정밀 분석하여 제공합니다.
    """)

st.write("")
col_input, col_info = st.columns([1, 1.8])

with col_input:
    st.markdown("#### 🌍 분석 국가 선택")
    
    # 정렬 및 선택 로직
    sort_option = st.radio("목록 정렬", ["이름순", "위험도순"], horizontal=True)
    
    if sort_option == "이름순":
        display_df = df_reg.sort_values("Country")
    else:
        display_df = df_reg.sort_values("Risk_Level", ascending=False)
        
    target_country = st.selectbox(
        "상세 리스크를 확인할 국가를 선택하세요",
        options=display_df['Country'].tolist(),
        index=0
    )
    
    country_info = df_reg[df_reg['Country'] == target_country].iloc[0]
    risk = country_info['EUDR_Risk']
    risk_color = COLOR_RISK if risk == "High" else (COLOR_WARNING if risk == "Medium" else COLOR_SAFE)
    
    st.markdown(f"""
        <div style="background-color:white; padding:30px; border-radius:12px; border-top: 10px solid {risk_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <p style="margin-bottom:5px; color:#666; font-weight:600;">통합 수입 리스크 등급</p>
            <h2 style="color:{risk_color}; margin-top:0; font-size:2.5rem;">{risk} Risk</h2>
            <hr style="margin: 20px 0;">
            <p style="font-size:1.1rem; color:#333; line-height:1.6;">{country_info['Description']}</p>
        </div>
    """, unsafe_allow_html=True)

with col_info:
    st.markdown(f"#### 📜 {target_country} 수입 컴플라이언스 체크리스트")
    
    # 필수 규제 항목 시각화
    checks = [
        ("환경 리스크", country_info['EUDR_Risk'], "EUDR 산림파괴 방지 규제 대응 상태"),
        ("식품 안전", "준수 필요", f"한국 관세청 {country_info['Import_Regulation']} 기준"),
        ("공급망 실사", "분석 대상", f"{country_info['Labor_Compliance']} 리포트 제출 의무"),
        ("인증 현황", "확인 필요", f"글로벌 {country_info['Certification']} 보유 상태")
    ]
    
    for title, status, desc in checks:
        st.markdown(f"""
            <div class="regulation-item">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; font-size:1.1rem; color:{COLOR_DEEP_COFFEE};">{title}</span>
                    <span style="background-color:{COLOR_DEEP_COFFEE}; color:white; padding:2px 10px; border-radius:15px; font-size:0.8rem;">{status}</span>
                </div>
                <div style="color:#666; font-size:0.9rem; margin-top:5px;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # --- [수정된 부분] 버튼 없이 자동 실행되는 AI 어드바이저 ---
    st.write("")
    
    # AI 박스 디자인
    ai_box_container = st.empty() # 자리를 미리 잡아둠
    
    # 스피너(로딩바)가 돌면서 자동으로 데이터를 가져옵니다.
    with st.spinner(f"🤖 AI가 {target_country} 수입 전략을 분석 중입니다..."):
        ai_advice = get_ai_summary(target_country)
    
    st.markdown(f"""
        <div class="ai-box">
            <div style="display:flex; align-items:center; margin-bottom:10px;">
                <span style="font-size:1.5rem; margin-right:10px;">🤖</span>
                <span style="font-weight:bold; color:{COLOR_DEEP_COFFEE}; font-size:1.1rem;">AI 수입 전략 어드바이저</span>
            </div>
            <p style="color:#333; line-height:1.6; margin:0; font-weight:500;">{ai_advice}</p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")
st.caption("© 2026 무역 AX 마스터 1기 원조 | 본 분석 결과는 글로벌 무역 규제 동향에 기반한 시뮬레이션 데이터입니다.")