# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab5_trade_intel.py - 원두 무역 인사이트 허브
================================================================================
수입 통계, 관세 조회, 컴플라이언스, 공급망 리밸런싱 기능 제공
================================================================================
"""


import streamlit as st
import pandas as pd
import plotly.express as px
import json


# 경로 설정
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from config import OPENAI_API_KEY, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_RISK, COLOR_SUCCESS, COLOR_WARNING, COFFEE_PALETTE




# ===========================================
# 색상 상수
# ===========================================
COLOR_DEEP_COFFEE = "#362419"
COLOR_FUTURE_GOLD = "#FFD700"
COLOR_STABLE_GRAY = "#757575"




# ===========================================
# 데이터 로드 함수
# ===========================================
@st.cache_data
def load_import_data():
    """10개년 수입 데이터 생성"""
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
   
    # 10개년 평균 추가
    avg_df = df_import.groupby('Country').agg({'Import_Qty': 'mean', 'Value_USD': 'mean'}).reset_index()
    avg_df['Year'] = "10개년 평균"
    avg_df['Region'] = avg_df['Country'].map(regions_map)
    df_import = pd.concat([avg_df.round(1), df_import], ignore_index=True)
   
    return df_import




@st.cache_data
def load_tariff_data():
    """관세 데이터"""
    dummy_tariff = [
        ["남미", "과테말라", 901.11, "생두", 2, "미체결", 0, 0, " 한-중미 FTA 협상 중! 현재 할당관세 0%"],
        ["남미", "온두라스", 901.11, "생두", 2, "0", 0, 0, " 한-중미 FTA 체결국"],
        ["남미", "코스타리카", 901.11, "생두", 2, "0", 0, 0, " 한-중미 FTA 체결국"],
        ["남미", "콜롬비아", 901.11, "생두", 2, "0", 0, 0, " 한-콜롬비아 FTA"],
        ["남미", "페루", 901.11, "생두", 2, "0", 0, 0, " 한-페루 FTA"],
        ["남미", "브라질", 901.11, "생두", 2, "미체결", 0, 0, " 현재 할당관세 0%"],
        ["아프리카", "케냐", 901.11, "생두", 2, "미체결", 0, 0, " 프리미엄 산지! 할당관세 혜택"],
        ["아프리카", "에티오피아", 901.11, "생두", 2, "0", 0, 0, " 최빈개발국 특례 0%"],
        ["아시아", "베트남", 901.11, "생두", 2, "0", 0, 0, " 한-아세안 FTA"],
        ["아시아", "인도네시아", 901.11, "생두", 2, "0", 0, 0, " 한-아세안 FTA 및 CEPA"]
    ]
    return pd.DataFrame(dummy_tariff, columns=["대륙", "국가", "HSCode", "품목", "기본세율", "FTA세율", "할당관세", "최종세율", "비고"])




@st.cache_data
def get_regulation_db():
    """규제 데이터베이스"""
    return pd.DataFrame({
        "Country": ["브라질", "베트남", "콜롬비아", "에티오피아", "페루", "온두라스", "인도네시아", "과테말라", "코스타리카", "케냐"],
        "Risk_Level": [3, 2, 2, 1, 2, 3, 3, 2, 1, 1],
        "EUDR_Risk": ["High", "Medium", "Medium", "Low", "Medium", "High", "High", "Medium", "Low", "Low"],
        "Import_Regulation": "검역/잔류농약",
        "Labor_Compliance": "아동노동/인권",
        "Certification": "지속가능성인증",
        "Description": [
            "아마존 산림 보존 관련 EUDR 실사가 매우 엄격합니다.",
            "농약 잔류 허용 기준(MRL) 위반 사례 모니터링이 필요합니다.",
            "수자원 관리 및 생물다양성 보존 리포트가 중요합니다.",
            "산림 파괴 리스크는 낮으나 공정무역 준수 실사가 강조됩니다.",
            "안데스 보호 구역 내 경작 여부 확인이 필요합니다.",
            "최근 산림 면적 변화율이 급격히 상승했습니다.",
            "열대 우림 및 이탄지 보호 규제(ISPO) 준수가 핵심입니다.",
            "토양 보호 및 생산지 위치 정보의 정확성이 요구됩니다.",
            "국가 주도 탄소 중립 정책으로 규제 대응력이 우수합니다.",
            "고산지대 생태계 보호 및 노동 환경 컴플라이언스가 필요합니다."
        ]
    })




# ===========================================
# AI 분석 함수
# ===========================================
@st.cache_data(show_spinner=False)
def get_ai_compliance_summary(country):
    """AI 컴플라이언스 분석"""
    if not OPENAI_API_KEY:
        return "⚠️ API 키가 설정되지 않았습니다."
   
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
       
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "커피 수입 무역 전문가입니다. 한 줄로 답변하세요."},
                {"role": "user", "content": f"'{country}'에서 커피 수입 시 필수 서류와 주의사항을 요약해주세요."}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"분석 오류: {str(e)}"




@st.cache_data(show_spinner=False)
def get_rebalancing_data():
    """기후 리밸런싱 데이터"""
    return [
        {"Country": "브라질", "Region": "남미", "Annual_Trend": -2.5, "Type": "Risk", "Reason": "아마존 산림 파괴와 기온 상승"},
        {"Country": "베트남", "Region": "아시아", "Annual_Trend": -2.0, "Type": "Risk", "Reason": "몬순 패턴 변화와 가뭄"},
        {"Country": "인도네시아", "Region": "아시아", "Annual_Trend": -2.8, "Type": "Risk", "Reason": "열대우림 감소와 이탄지 고갈"},
        {"Country": "페루", "Region": "남미", "Annual_Trend": 0.2, "Type": "Stable", "Reason": "안데스 고산지대 안정적 생산"},
        {"Country": "콜롬비아", "Region": "남미", "Annual_Trend": -0.3, "Type": "Stable", "Reason": "다양한 고도 재배지역"},
        {"Country": "에티오피아", "Region": "아프리카", "Annual_Trend": 1.5, "Type": "Opportunity", "Reason": "고산지대 확장 가능성"},
        {"Country": "케냐", "Region": "아프리카", "Annual_Trend": 1.3, "Type": "Opportunity", "Reason": "온난화로 재배 적지 확대"},
        {"Country": "탄자니아", "Region": "아프리카", "Annual_Trend": 3.2, "Type": "Next Frontier", "Reason": "킬리만자로 고지대 최적 조건"},
        {"Country": "중국(윈난)", "Region": "아시아", "Annual_Trend": 3.8, "Type": "Next Frontier", "Reason": "정부 주도 기술 투자"}
    ]




def run_rebalancing_sim(ai_data, target_year):
    """리밸런싱 시뮬레이션"""
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




# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """무역 인사이트 페이지를 렌더링합니다."""
   
    # 데이터 로드
    df_import = load_import_data()
    df_tariff = load_tariff_data()
    df_reg = get_regulation_db()
   
    st.markdown("<h1 style='text-align: center;'>원두 무역 인사이트</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
   
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([" 수입 통계", " 관세 조회", " 컴플라이언스", " 공급망 리밸런싱"])
   
    # ===========================================
    # TAB 1: 수입 통계 분석
    # ===========================================
    with tab1:
        f_col1, f_col2 = st.columns(2)
       
        with f_col1:
            year_opts = ["10개년 평균"] + sorted([y for y in df_import['Year'].unique() if y != "10개년 평균"], reverse=True)
            selected_year = st.selectbox(" 분석 연도", options=year_opts, key="intel_year")
           
        with f_col2:
            selected_region = st.multiselect(" 대륙", ["남미", "아시아", "아프리카"], default=["남미", "아시아", "아프리카"], key="intel_region")
       
        st.divider()
       
        f_import = df_import[(df_import['Year'] == selected_year) & (df_import['Region'].isin(selected_region))]
       
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 수입량", f"{f_import['Import_Qty'].sum():,.1f} ton")
        m2.metric("주요 수입국", f_import.sort_values("Import_Qty", ascending=False).iloc[0]['Country'] if not f_import.empty else "-")
        m3.metric("총 수입액", f"${f_import['Value_USD'].sum():,.1f}M")
        m4.metric("분석 국가", f"{len(f_import)}개국")


        st.divider()
       
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown(f"""
                <h3 style='color:{COLOR_SECONDARY}; font-size: 30px; font-weight: 600; margin-bottom: -10px;'>
                    {selected_year} 국가별 수입 비중
                </h3>
            """, unsafe_allow_html=True)
            st.markdown(" ")


            fig = px.pie(f_import, values='Import_Qty', names='Country', hole=0.6, color_discrete_sequence=COFFEE_PALETTE)
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(margin=dict(t=20, b=20, l=0, r=0), legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig, use_container_width=True)


        with c2:
            st.markdown(f"""
                <h3 style='color:{COLOR_SECONDARY}; font-size: 30px; font-weight: 600; margin-bottom: -10px;'>
                    {selected_year} 실측 데이터
                </h3>
            """, unsafe_allow_html=True)
            st.markdown(" ")


            st.dataframe(
                f_import[['Country', 'Import_Qty', 'Value_USD', 'Region']].sort_values("Import_Qty", ascending=False),
                column_config={
                    "Import_Qty": st.column_config.ProgressColumn("수입량(ton)", format="%.1f", min_value=0, max_value=60000),
                    "Value_USD": st.column_config.NumberColumn("금액($M)", format="$%.1f")
                },
                hide_index=True, use_container_width=True
            )


    # ===========================================
    # TAB 2: 관세 조회
    # ===========================================
    with tab2:
        st.markdown("###  공급망 권고안")
       
        sl, sr = st.columns(2)
        with sl:
            st.success("""
            **안정적 파트너 (FTA 그룹)**
           
            온두라스, 코스타리카, 콜롬비아, 페루, 에티오피아, 베트남, 인도네시아
           
            관세 0%가 영구적으로 보장되어 장기 계약에 최적입니다.
            """)
        with sr:
            st.warning("""
            **기회 포착 파트너 (할당관세 그룹)**
           
            과테말라, 브라질, 케냐
           
            한시적 할당관세 0% 혜택 기간 내 물량 선점이 유리합니다.
            """)




        st.markdown(" ")


       
   
        st.markdown(f"""
            <h3 style='color:{COLOR_SECONDARY}; font-size: 30px; font-weight: 600; margin-bottom: -10px;'>
                전체 국가 관세 현황
            </h3>
        """, unsafe_allow_html=True)




        st.markdown('<hr style="border-top: 2px solid #00695C; margin: 1px 0;">', unsafe_allow_html=True)


        st.markdown(" ")






        k1, k2, k3, k4 = st.columns(4)
        k1.metric("분석 국가", f"{len(df_tariff)}개국")
        k2.metric("FTA 체결국", f"{len(df_tariff[df_tariff['FTA세율'] != '미체결'])}개")
        k3.metric("평균 최종세율", f"{df_tariff['최종세율'].mean():.1f}%")
        k4.metric("최고 기본세율", f"{df_tariff['기본세율'].max()}%")


        st.dataframe(df_tariff, use_container_width=True, hide_index=True)


    # ===========================================
    # TAB 3: 컴플라이언스
    # ===========================================
        st.markdown(" ")


    with tab3:
        st.info("환경(EUDR), 식품안전(검역), 노동(인권) 등 필수 규제 리스크를 분석합니다.")


        col_input, col_info = st.columns([1, 1.8])


        with col_input:
           
            st.markdown(f"""
            <h3 style='color:{COLOR_SECONDARY}; font-size: 30px; font-weight: 600; margin-bottom: -10px;'>
                분석 국가 선택
            </h3>
            """, unsafe_allow_html=True)


            st.markdown(" ")
            st.markdown(" ")


            sort_option = st.radio("목록 정렬", ["이름순", "위험도순"], horizontal=True, key="comp_sort")
           
            display_df = df_reg.sort_values("Country" if sort_option == "이름순" else "Risk_Level", ascending=(sort_option == "이름순") if sort_option == "이름순" else False)


            st.markdown(" ")


            target_country = st.selectbox("상세 리스크 확인", options=display_df['Country'].tolist(), key="comp_country")
           
            st.markdown(" ")
            st.markdown(" ")


            country_info = df_reg[df_reg['Country'] == target_country].iloc[0]
            risk = country_info['EUDR_Risk']
            risk_color = COLOR_RISK if risk == "High" else (COLOR_WARNING if risk == "Medium" else COLOR_SUCCESS)
           
            st.markdown(f"""
            <div style="background-color:white; padding:20px; border-radius:12px; border-top: 8px solid {risk_color};">
                <h3 style="color:{risk_color}; margin-top:0;">{risk} Risk</h3>
                <p>{country_info['Description']}</p>
            </div>
            """, unsafe_allow_html=True)


        with col_info:
           
            st.markdown(f"""
            <h3 style='color:{COLOR_SECONDARY}; font-size: 30px; font-weight: 600; margin-bottom: -10px;'>
                {target_country} 체크리스트
            </h3>
            """, unsafe_allow_html=True)


            st.markdown(" ")
            st.markdown(" ")


            checks = [
                ("환경 리스크", country_info['EUDR_Risk'], "EUDR 산림파괴 방지 규제"),
                ("식품 안전", "준수 필요", f"한국 관세청 {country_info['Import_Regulation']} 기준"),
                ("공급망 실사", "분석 대상", f"{country_info['Labor_Compliance']} 리포트"),
                ("인증 현황", "확인 필요", f"글로벌 {country_info['Certification']} 보유 상태")
            ]
           
            for title, status, desc in checks:
                st.markdown(f"""
                <div style="background-color:#FAFAFA; padding:12px; border-radius:8px; margin-bottom:8px; border-left: 4px solid {COLOR_PRIMARY};">
                    <strong>{title}</strong> - {status}<br>
                    <small style="color:#666;">{desc}</small>
                </div>
                """, unsafe_allow_html=True)
           
            with st.spinner(f" AI가 {target_country} 분석 중..."):
                ai_advice = get_ai_compliance_summary(target_country)
           
            st.markdown(f"""
            <div style="background:#F5F5F5; padding:20px; border-radius:12px; border-left:5px solid {COLOR_PRIMARY}; margin-top:16px;">
                <strong> AI 수입 전략 어드바이저</strong><br>
                {ai_advice}
            </div>
            """, unsafe_allow_html=True)


    # ===========================================
    # TAB 4: 공급망 리밸런싱
    # ===========================================
    with tab4:




        raw_data = get_rebalancing_data()
       
        st.markdown("###  예측 시점 설정")
        selected_year = st.slider("연도 조절", 2025, 2050, 2050, key="rebal_year")
       
        df_re = run_rebalancing_sim(raw_data, selected_year)


        st.markdown(" ")


        st.subheader(f" {selected_year}년 국가별 생산성 변동률 예측")
       
        fig = px.bar(
            df_re.sort_values("Climate_Impact"),
            x="Country", y="Climate_Impact", color="Shift_Type",
            color_discrete_map={"Risk": COLOR_RISK, "Opportunity": COLOR_SUCCESS, "Next Frontier": COLOR_FUTURE_GOLD, "Stable": COLOR_STABLE_GRAY},
            labels={"Climate_Impact": "예상 생산량 변화 (%)"},
            text_auto='.1f'
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)


        st.divider()
       
        col_sel, col_val = st.columns([1, 1.4])


        with col_sel:
            st.markdown(f"###  {selected_year} 전략 국가 분석")
            target = st.selectbox("국가 선택", df_re['Country'].tolist(), key="rebal_country")
            c_info = df_re[df_re['Country'] == target].iloc[0]
           
            status_theme = {"Next Frontier": COLOR_FUTURE_GOLD, "Risk": COLOR_RISK, "Opportunity": COLOR_SUCCESS, "Stable": COLOR_STABLE_GRAY}.get(c_info['Shift_Type'], COLOR_DEEP_COFFEE)
           
            st.markdown(f"""
            <div style="background:white; padding:24px; border-radius:12px; border-top:8px solid {status_theme};">
                <h3 style="margin:0;">{target}</h3>
                <span style="background:{status_theme}; color:white; padding:4px 12px; border-radius:15px;">{c_info['Shift_Type']}</span>
                <p style="margin-top:16px;"><b>누적 생산성 변동:</b> {c_info['Climate_Impact']}%</p>
                <p>{c_info['Description']}</p>
            </div>
            """, unsafe_allow_html=True)


        with col_val:
            st.markdown("###  리밸런싱 액션 가이드")
           
            st.success("""
            **아프리카 공급망 거점 강화**
           
            탄자니아 & 우간다 - 동아프리카 고산지대는 기후 변화의 최대 수혜지입니다.
            현지 농장 선점 및 선제적 파트너십 구축이 시급합니다.
            """)
           
            st.warning("""
            **동아시아 물류 허브 선점**
           
            중국 윈난 - 지리적 이점과 탄소 규제 대응을 위해 '차세대 전략 엔진'으로 격상하십시오.
            """)
           
            st.info(f"""
            **고위험 산지 의존도 분산**
           
            기온 상승 직격탄을 받는 저지대 의존도를 {selected_year}년까지 점진적 축소하고
            안정적 고산지 포트폴리오로 재편하십시오.
            """)




if __name__ == "__main__":
    show()



