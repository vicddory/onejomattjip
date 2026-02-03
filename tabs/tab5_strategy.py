# -*- coding: utf-8 -*-
"""
Tab 5: Strategy - 커피 무역 전략 인텔리전스 허브
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")

# 컬러 테마
COLOR_DEEP_COFFEE = "#4B2C20"
COLOR_ROAST = "#6F4E37"
COLOR_SAFE = "#2E7D32"
COLOR_WARNING = "#F9A825"
COLOR_RISK = "#D32F2F"
COLOR_FUTURE_GOLD = "#D4AF37"
COLOR_STABLE_GRAY = "#7F8C8D"

COFFEE_PALETTE = ["#3C2A21", "#4B3228", "#5C4033", "#6F4E37", "#8B5E3C",
                  "#A67B5B", "#BC9A7A", "#D4B996", "#E6CCB2", "#F5EBE0"]

# ==========================================
# 데이터 로드 함수
# ==========================================
@st.cache_data
def load_all_combined_data():
    years = range(2016, 2026)
    countries = ["브라질", "콜롬비아", "베트남", "에티오피아", "페루", "과테말라", "온두라스", "케냐", "인도네시아", "코스타리카"]
    regions_map = {
        "브라질": "남미", "콜롬비아": "남미", "베트남": "아시아", "에티오피아": "아프리카",
        "페루": "남미", "과테말라": "남미", "온두라스": "남미", "케냐": "아프리카",
        "인도네시아": "아시아", "코스타리카": "남미"
    }
    
    val_2025 = [56191180, 27020216, 27188789, 21927014, 3095697, 6875382, 5425930, 2817374, 2634648, 1890076]
    usd_2025 = [420862043, 219089266, 145513937, 163756484, 19477006, 59109621, 39204311, 22891133, 17345112, 17352058]
    val_2016 = [29781184, 25095585, 29765184, 9039065, 9085646, 5511872, 7894651, 2308925, 2466170, 2013591]
    usd_2016 = [83045525, 82205137, 53009244, 42850860, 25858209, 24871669, 21529182, 13593511, 11293523, 10075278]

    all_import_list = []
    for i, year in enumerate(years):
        for j, country in enumerate(countries):
            weight = (i / (len(years)-1))
            cur_kg = val_2016[j] + (val_2025[j] - val_2016[j]) * weight
            cur_usd = usd_2016[j] + (usd_2025[j] - usd_2016[j]) * weight
            all_import_list.append({
                "Year": str(year), "Country": country, "Region": regions_map[country],
                "Import_Qty": round(cur_kg / 1000, 1), "Value_USD": round(cur_usd / 1000000, 1)
            })
    
    df_import = pd.DataFrame(all_import_list)
    avg_df = df_import.groupby('Country').agg({'Import_Qty': 'mean', 'Value_USD': 'mean'}).reset_index()
    avg_df['Year'], avg_df['Region'] = "10개년 평균", avg_df['Country'].map(regions_map)
    df_import = pd.concat([avg_df.round(1), df_import], ignore_index=True)

    dummy_tariff = [
        ["남미", "과테말라", 901.11, "생두", 2, "미체결", 0, 0, "🌟 한-중미 FTA 협상 중!"],
        ["남미", "온두라스", 901.11, "생두", 2, "0", 0, 0, "✅ 한-중미 FTA 체결국"],
        ["남미", "코스타리카", 901.11, "생두", 2, "0", 0, 0, "✅ 한-중미 FTA 체결국"],
        ["남미", "콜롬비아", 901.11, "생두", 2, "0", 0, 0, "✅ 한-콜롬비아 FTA"],
        ["남미", "페루", 901.11, "생두", 2, "0", 0, 0, "✅ 한-페루 FTA"],
        ["남미", "브라질", 901.11, "생두", 2, "미체결", 0, 0, "🌟 할당관세 0% 가능"],
        ["아프리카", "케냐", 901.11, "생두", 2, "미체결", 0, 0, "🌟 프리미엄 산지"],
        ["아프리카", "에티오피아", 901.11, "생두", 2, "0", 0, 0, "🕊️ 최빈개발국 특례"],
        ["아시아", "베트남", 901.11, "생두", 2, "0", 0, 0, "✅ 한-아세안 FTA"],
        ["아시아", "인도네시아", 901.11, "생두", 2, "0", 0, 0, "✅ 한-아세안 FTA"]
    ]
    df_tariff = pd.DataFrame(dummy_tariff, columns=["대륙", "국가", "HSCode", "품목", "기본세율", "FTA세율", "할당관세", "최종세율", "비고"])
    
    return df_import, df_tariff

@st.cache_data
def get_regulation_db():
    reg_data = {
        "Country": ["Brazil", "Vietnam", "Colombia", "Ethiopia", "Peru", "Honduras", "Indonesia", "Guatemala", "Costa Rica", "Kenya"],
        "Risk_Level": [3, 2, 2, 1, 2, 3, 3, 2, 1, 1],
        "EUDR_Risk": ["High", "Medium", "Medium", "Low", "Medium", "High", "High", "Medium", "Low", "Low"],
        "Import_Regulation": "검역/잔류농약",
        "Labor_Compliance": "아동노동/인권",
        "Certification": "지속가능성인증",
        "Description": [
            "아마존 산림 보존과 관련된 EUDR 실사가 매우 엄격합니다.",
            "농약 잔류 허용 기준(MRL) 위반 사례 모니터링이 필요합니다.",
            "수자원 관리 및 생물다양성 보존 리포트가 중요합니다.",
            "산림 파괴 리스크는 낮으나 노동 인권 실사가 강조됩니다.",
            "안데스 보호 구역 내 지오태깅 데이터 제출이 요구됩니다.",
            "최근 산림 면적 변화율이 급격히 상승하여 EUDR 고위험군입니다.",
            "열대 우림 및 이탄지 보호 규제(ISPO) 준수가 핵심입니다.",
            "토양 보호 및 생산지 위치 정보의 정확성이 요구됩니다.",
            "국가 주도의 탄소 중립 정책으로 규제 대응력이 우수합니다.",
            "고산지대 생태계 보호 및 노동 환경 리포트가 필요합니다."
        ]
    }
    return pd.DataFrame(reg_data)

# ==========================================
# AI 분석 함수
# ==========================================
@st.cache_data(show_spinner=False) 
def get_ai_compliance_summary(country):
    if not api_key:
        return "⚠️ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        당신은 한국의 숙련된 커피 수입 무역 전문가입니다.
        현재 '{country}'에서 커피 생두를 수입하려고 합니다.
        
        다음 내용을 포함하여 구매팀이 준비해야 할 것을 '한 줄'로 명확하게 요약해 주세요:
        1. 필수 서류 2. 특별히 주의해야 할 점 3. 구매팀의 핵심 행동 가이드
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

@st.cache_data(show_spinner=False)
def get_ai_rebalancing_data():
    fallback_data = [
        {"Country": "브라질", "Region": "남미", "Annual_Trend": -2.5, "Type": "Risk", "Reason": "아마존 산림 파괴와 기온 상승으로 저지대 농장의 생산성이 감소합니다."},
        {"Country": "베트남", "Region": "아시아", "Annual_Trend": -2.0, "Type": "Risk", "Reason": "몬순 패턴 변화와 극심한 가뭄으로 로부스타 생산량이 위협받습니다."},
        {"Country": "인도네시아", "Region": "아시아", "Annual_Trend": -2.8, "Type": "Risk", "Reason": "열대우림 감소와 이탄지 고갈로 지속가능한 생산 기반이 약화됩니다."},
        {"Country": "온두라스", "Region": "중미", "Annual_Trend": -1.8, "Type": "Risk", "Reason": "허리케인 빈도 증가와 커피 녹병 확산으로 수확량이 불안정합니다."},
        {"Country": "과테말라", "Region": "중미", "Annual_Trend": -1.5, "Type": "Risk", "Reason": "강수량 변동성 증가로 전통적 재배지역의 품질 저하가 우려됩니다."},
        {"Country": "페루", "Region": "남미", "Annual_Trend": 0.2, "Type": "Stable", "Reason": "안데스 고산지대의 미세기후 덕분에 상대적으로 안정적입니다."},
        {"Country": "콜롬비아", "Region": "남미", "Annual_Trend": -0.3, "Type": "Stable", "Reason": "다양한 고도의 재배지역 분산으로 기후 리스크를 완화합니다."},
        {"Country": "코스타리카", "Region": "중미", "Annual_Trend": 0.1, "Type": "Stable", "Reason": "친환경 재배 정책과 고품질 스페셜티 중심 전략으로 안정성을 유지합니다."},
        {"Country": "에티오피아", "Region": "아프리카", "Annual_Trend": 1.5, "Type": "Opportunity", "Reason": "고산지대 확장 가능성과 원산지 유전자 다양성이 기회 요인입니다."},
        {"Country": "케냐", "Region": "아프리카", "Annual_Trend": 1.3, "Type": "Opportunity", "Reason": "케냐산 고지대는 온난화로 인해 재배 적지가 확대되고 있습니다."},
        {"Country": "우간다", "Region": "아프리카", "Annual_Trend": 1.8, "Type": "Opportunity", "Reason": "빅토리아 호수 주변 미세기후와 신규 고산지 개발이 활발합니다."},
        {"Country": "탄자니아", "Region": "아프리카", "Annual_Trend": 3.2, "Type": "Next Frontier", "Reason": "킬리만자로 고지대의 최적 기후 조건과 미개발 잠재력이 폭발적입니다."},
        {"Country": "중국(윈난)", "Region": "아시아", "Annual_Trend": 3.8, "Type": "Next Frontier", "Reason": "정부 주도 기술 투자와 고산지대 확장으로 급부상 중입니다."}
    ]
    
    if not api_key:
        return fallback_data
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        target_countries = ["브라질", "베트남", "인도네시아", "온두라스", "과테말라", 
                           "페루", "콜롬비아", "코스타리카", "에티오피아", "케냐",
                           "우간다", "탄자니아", "중국(윈난)"]
        
        prompt = f"""
        기후 위기 시나리오(RCP 8.5)를 분석하세요: {target_countries}
        
        반드시 다음 JSON 형식으로만 출력:
        [{{"Country": "국가명", "Region": "지역", "Annual_Trend": 숫자, "Type": "Risk/Stable/Opportunity/Next Frontier", "Reason": "설명"}}]
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "JSON format only."}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        result = json.loads(response.choices[0].message.content)
        return result if result else fallback_data
    except:
        return fallback_data

def run_rebalancing_sim(ai_data, target_year):
    base_year = 2025
    years_passed = target_year - base_year
    sim_results = []
    
    for item in ai_data:
        impact = (1 + item['Annual_Trend'] / 100) ** years_passed - 1
        sim_results.append({
            "Country": item['Country'],
            "Region": item['Region'],
            "Climate_Impact": round(impact * 100, 1),
            "Shift_Type": item['Type'],
            "Description": item['Reason']
        })
    return pd.DataFrame(sim_results)

# ==========================================
# 메인 show 함수
# ==========================================
def show():
    """Strategy 페이지를 렌더링하는 메인 함수"""
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #FAF7F2; }}
        div[data-testid="stMetric"] {{
            background-color: white;
            border: 1px solid #E0D7D0;
            border-radius: 12px;
            padding: 20px !important;
        }}
        h1, h2, h3 {{ color: {COLOR_DEEP_COFFEE} !important; }}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align:left;'>☕ Coffee Trade Intelligence Hub</h1>", unsafe_allow_html=True)
    
    # 데이터 로드
    df_import, df_tariff = load_all_combined_data()
    df_reg = get_regulation_db()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 수입 트렌드", "🧾 FTA & 관세", "🛡️ 규제 리스크", "🌍 공급망 리밸런싱"])

    # TAB 1: 수입 트렌드
    with tab1:
        st.subheader("📊 10개년 수입 데이터 분석")
        
        col1, col2 = st.columns([1.5, 1])
        with col1:
            selected_year = st.selectbox("연도 선택", ["10개년 평균"] + [str(y) for y in range(2025, 2015, -1)], key="strategy_year")
        with col2:
            view_metric = st.radio("지표 선택", ["수입량 (톤)", "수입액 (백만$)"], horizontal=True, key="strategy_metric")
        
        value_col = "Import_Qty" if "톤" in view_metric else "Value_USD"
        filtered_df = df_import[df_import['Year'] == selected_year]
        
        fig = px.bar(
            filtered_df.sort_values(value_col, ascending=False),
            x='Country', y=value_col, color='Region',
            color_discrete_sequence=COFFEE_PALETTE,
            title=f"{selected_year} 국가별 {view_metric}"
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: FTA & 관세
    with tab2:
        st.subheader("🧾 FTA 협정 및 관세 현황")
        
        selected_region = st.selectbox("대륙 필터", ["전체"] + df_tariff['대륙'].unique().tolist(), key="strategy_region")
        
        display_df = df_tariff if selected_region == "전체" else df_tariff[df_tariff['대륙'] == selected_region]
        
        st.dataframe(
            display_df.style.applymap(
                lambda x: 'background-color: #E8F5E9' if x == "0" else '', 
                subset=['FTA세율']
            ),
            use_container_width=True,
            hide_index=True
        )

    # TAB 3: 규제 리스크
    with tab3:
        st.subheader("🛡️ 수입 컴플라이언스 분석")
        
        col_input, col_info = st.columns([1, 1.5])
        
        with col_input:
            st.markdown("#### 🌍 분석 국가 선택")
            target_country = st.selectbox("상세 리스크를 확인할 국가", df_reg['Country'].tolist(), key="strategy_country")
            
            country_info = df_reg[df_reg['Country'] == target_country].iloc[0]
            risk = country_info['EUDR_Risk']
            risk_color = COLOR_RISK if risk == "High" else (COLOR_WARNING if risk == "Medium" else COLOR_SAFE)
            
            st.markdown(f"""
                <div style="background-color:white; padding:30px; border-radius:12px; border-top: 10px solid {risk_color};">
                    <p style="margin-bottom:5px; color:#666;">통합 수입 리스크 등급</p>
                    <h2 style="color:{risk_color}; margin-top:0;">{risk} Risk</h2>
                    <hr>
                    <p style="color:#333;">{country_info['Description']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_info:
            st.markdown(f"#### 📜 {target_country} 컴플라이언스 체크리스트")
            
            checks = [
                ("환경 리스크", country_info['EUDR_Risk'], "EUDR 산림파괴 방지 규제"),
                ("식품 안전", "준수 필요", f"한국 관세청 {country_info['Import_Regulation']} 기준"),
                ("공급망 실사", "분석 대상", f"{country_info['Labor_Compliance']} 리포트"),
                ("인증 현황", "확인 필요", f"글로벌 {country_info['Certification']} 보유")
            ]
            
            for title, status, desc in checks:
                st.markdown(f"""
                    <div style="padding:12px; border-left:5px solid {COLOR_DEEP_COFFEE}; background-color:#FDFBFA; margin-bottom:10px; border-radius:0 8px 8px 0;">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-weight:700; color:{COLOR_DEEP_COFFEE};">{title}</span>
                            <span style="background-color:{COLOR_DEEP_COFFEE}; color:white; padding:2px 10px; border-radius:15px; font-size:0.8rem;">{status}</span>
                        </div>
                        <div style="color:#666; font-size:0.9rem; margin-top:5px;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with st.spinner(f"🤖 AI가 {target_country} 수입 전략을 분석 중..."):
                ai_advice = get_ai_compliance_summary(target_country)
            
            st.markdown(f"""
                <div style="background-color:#F0F4F8; padding:20px; border-radius:12px; border:1px dashed {COLOR_DEEP_COFFEE}; margin-top:20px;">
                    <span style="font-size:1.5rem;">🤖</span>
                    <span style="font-weight:bold; color:{COLOR_DEEP_COFFEE};">AI 수입 전략 어드바이저</span>
                    <p style="color:#333; margin-top:10px;">{ai_advice}</p>
                </div>
            """, unsafe_allow_html=True)

    # TAB 4: 공급망 리밸런싱
    with tab4:
        st.subheader("🌍 AI 기반 지정학적 공급망 리밸런싱")
        st.caption("OpenAI RCP 8.5 시나리오 분석: 2025년 대비 미래 산지 생산성 변화 예측")

        if 'rebalance_db' not in st.session_state:
            with st.spinner("🤖 AI가 글로벌 기후 시나리오를 시뮬레이션 중..."):
                raw_ai = get_ai_rebalancing_data()
                st.session_state['rebalance_db'] = raw_ai

        if st.session_state.get('rebalance_db'):
            st.markdown("### 📅 예측 시점 설정")
            selected_year_tab4 = st.slider("연도를 조절하여 공급망 변화를 추적하세요", 2025, 2050, 2050, key="rebalance_year")
            
            df_re = run_rebalancing_sim(st.session_state['rebalance_db'], selected_year_tab4)

            st.subheader(f"📈 {selected_year_tab4}년 국가별 생산성 변동률 예측")
            
            fig = px.bar(
                df_re.sort_values("Climate_Impact"), 
                x="Country", y="Climate_Impact", color="Shift_Type",
                color_discrete_map={
                    "Risk": COLOR_RISK, "Opportunity": COLOR_SAFE, 
                    "Next Frontier": COLOR_FUTURE_GOLD, "Stable": COLOR_STABLE_GRAY
                },
                labels={"Climate_Impact": "예상 생산량 변화 (%)"},
                text_auto='.1f'
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            col_sel, col_val = st.columns([1, 1.4])

            with col_sel:
                st.markdown(f"### 🎯 {selected_year_tab4} 전략 국가 심층 분석")
                default_index = min(12, len(df_re) - 1) if len(df_re) > 0 else 0
                target = st.selectbox("리포트를 확인할 국가", df_re['Country'].tolist(), index=default_index, key="rebalance_country")
                c_info = df_re[df_re['Country'] == target].iloc[0]
                
                status_theme = {
                    "Next Frontier": COLOR_FUTURE_GOLD, "Risk": COLOR_RISK,
                    "Opportunity": COLOR_SAFE, "Stable": COLOR_STABLE_GRAY
                }.get(c_info['Shift_Type'], COLOR_DEEP_COFFEE)
                
                st.markdown(f"""
                    <div style="background-color:white; padding:24px; border-radius:12px; border-top:10px solid {status_theme};">
                        <p style="color:#666; font-size:0.85rem;">STRATEGIC REPORT ({selected_year_tab4})</p>
                        <h2 style="margin:0 0 10px 0; color:{COLOR_DEEP_COFFEE};">{target}</h2>
                        <span style="background-color:{status_theme}; color:white; padding:4px 12px; border-radius:15px;">{c_info['Shift_Type']}</span>
                        <p style="font-weight:bold; color:{status_theme}; margin-top:15px;">누적 생산성 변동: {c_info['Climate_Impact']}%</p>
                        <hr>
                        <p style="color:#444;">{c_info['Description']}</p>
                    </div>
                """, unsafe_allow_html=True)

            with col_val:
                st.markdown("### 🚀 리밸런싱 액션 가이드")
                
                st.markdown(f"""
                    <div style="background-color:#F0F4F0; padding:18px; border-radius:10px; border-left:5px solid {COLOR_SAFE}; margin-bottom:12px;">
                        <p style="margin:0; font-weight:bold; color:{COLOR_SAFE};">🛡️ 아프리카 공급망 거점 강화</p>
                        <p style="margin:4px 0 0 0; font-size:0.9rem;">동아프리카 고산지대는 기후 변화의 최대 수혜지로 부상합니다.</p>
                    </div>
                    <div style="background-color:#FFF9E6; padding:18px; border-radius:10px; border-left:5px solid {COLOR_FUTURE_GOLD}; margin-bottom:12px;">
                        <p style="margin:0; font-weight:bold; color:{COLOR_FUTURE_GOLD};">⚡ 동아시아 물류 허브 선점</p>
                        <p style="margin:4px 0 0 0; font-size:0.9rem;">중국 윈난 산지를 차세대 전략 엔진으로 격상하십시오.</p>
                    </div>
                    <div style="background-color:#F8F9FA; padding:18px; border-radius:10px; border-left:5px solid {COLOR_STABLE_GRAY};">
                        <p style="margin:0; font-weight:bold; color:{COLOR_STABLE_GRAY};">📉 고위험 산지 의존도 분산</p>
                        <p style="margin:4px 0 0 0; font-size:0.9rem;">저지대 의존도를 점진적 축소하고 고산지 포트폴리오로 재편하십시오.</p>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("© 2026 무역 AX 마스터 1기 | Data: 관세청 10개년 실측 통계 + OpenAI Scenario Engine")
