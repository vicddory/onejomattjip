# 필수 라이브러리 설치: pip install streamlit pandas plotly openai python-dotenv

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# --- 0. 환경 변수 로드 (API Key) ---
load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

# --- 1. Page Config (최상단에 단 한 번만) ---
st.set_page_config(page_title="Coffee Trade Intelligence Hub", layout="wide")

# --- 2. 통합 컬러 테마 ---
COLOR_DEEP_COFFEE = "#4B2C20"
COLOR_ROAST = "#6F4E37"
COLOR_BG = "#FAF7F2"
COLOR_SAFE = "#2E7D32"
COLOR_WARNING = "#F9A825"
COLOR_RISK = "#D32F2F"
COLOR_FUTURE_GOLD = "#D4AF37"
COLOR_STABLE_GRAY = "#7F8C8D"

COFFEE_PALETTE = [
    "#3C2A21", "#4B3228", "#5C4033", "#6F4E37", "#8B5E3C",
    "#A67B5B", "#BC9A7A", "#D4B996", "#E6CCB2", "#F5EBE0"
]

# --- 3. 통합 CSS 스타일 ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; }}
    .main-title {{
        color: {COLOR_DEEP_COFFEE};
        font-family: 'Playfair Display', serif;
        font-weight: 800;
        text-align: left;
        margin-bottom: 0px;
    }}
    div[data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid #E0D7D0;
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 2px 2px 10px rgba(75, 44, 32, 0.05);
    }}
    .strategy-card {{
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #333;
        height: 100%;
    }}
    .report-card {{ 
        background-color: white; 
        padding: 25px; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
    }}
    .regulation-item {{ 
        padding: 12px; 
        border-left: 5px solid {COLOR_DEEP_COFFEE}; 
        background-color: #FDFBFA; 
        margin-bottom: 10px; 
        border-radius: 0 8px 8px 0; 
    }}
    .ai-box {{ 
        background-color: #F0F4F8; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px dashed #4B2C20; 
        margin-top: 20px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    }}
    .strategy-container {{ 
        background-color: white; 
        padding: 30px; 
        border-radius: 20px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
    }}
    h1, h2, h3 {{ color: {COLOR_DEEP_COFFEE} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. 데이터 로드 함수 (FAQ1,2.py) ---
@st.cache_data
def load_all_combined_data():
    # [데이터 A] 10개년 수입 실측 데이터
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

    # [데이터 B] 관세 데이터
    dummy_tariff = [
        ["남미", "과테말라", 901.11, "생두", 2, "미체결", 0, 0, "🌟 한-중미 FTA 협상 중! 현재 할당관세 0% 적용됩니다."],
        ["남미", "온두라스", 901.11, "생두", 2, "0", 0, 0, "✅ 한-중미 FTA 체결국입니다."],
        ["남미", "코스타리카", 901.11, "생두", 2, "0", 0, 0, "✅ 한-중미 FTA 체결국입니다."],
        ["남미", "콜롬비아", 901.11, "생두", 2, "0", 0, 0, "✅ 한-콜롬비아 FTA 적용!"],
        ["남미", "페루", 901.11, "생두", 2, "0", 0, 0, "✅ 한-페루 FTA 적용!"],
        ["남미", "브라질", 901.11, "생두", 2, "미체결", 0, 0, "🌟 현재 할당관세 0% 수입 가능!"],
        ["아프리카", "케냐", 901.11, "생두", 2, "미체결", 0, 0, "🌟 프리미엄 산지! 할당관세 혜택."],
        ["아프리카", "에티오피아", 901.11, "생두", 2, "0", 0, 0, "🕊️ 최빈개발국 특례 0%."],
        ["아시아", "베트남", 901.11, "생두", 2, "0", 0, 0, "✅ 한-아세안 FTA."],
        ["아시아", "인도네시아", 901.11, "생두", 2, "0", 0, 0, "✅ 한-아세안 FTA 및 CEPA."]
    ]
    df_tariff = pd.DataFrame(dummy_tariff, columns=["대륙", "국가", "HSCode", "품목", "기본세율", "FTA세율", "할당관세", "최종세율", "비고"])
    
    return df_import, df_tariff

# --- 5. 규제 데이터베이스 (FAQ3.py) ---
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

# --- 6. OpenAI 분석 함수 (FAQ3.py) ---
@st.cache_data(show_spinner=False) 
def get_ai_compliance_summary(country):
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

# --- 7. OpenAI 기반 기후 트렌드 분석 (FAQ4.py) ---
@st.cache_data(show_spinner=False)
def get_ai_rebalancing_data():
    if not api_key: 
        return None
    
    client = OpenAI(api_key=api_key)
    
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

# --- 8. 데이터 시뮬레이션 엔진 (FAQ4.py) ---
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

# --- 9. 데이터 로드 ---
df_import, df_tariff = load_all_combined_data()
df_reg = get_regulation_db()

# --- 10. 헤더 ---
st.markdown('<p class="main-title">☕ COFFEE TRADE INTELLIGENCE HUB</p>', unsafe_allow_html=True)
st.markdown(f"<p style='color:{COLOR_ROAST}; font-size:1.1rem; margin-bottom:20px;'>실시간 관세율 분석 | 글로벌 컴플라이언스 | AI 공급망 최적화</p>", unsafe_allow_html=True)

# --- 11. 전역 사이드바 (Tab 1, 2에서만 사용) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=80)
    st.title("Trade Intel")
    st.write("---")
    
    st.markdown("#### 📊 수입 통계 필터")
    year_opts = ["10개년 평균"] + sorted(df_import[df_import['Year'] != "10개년 평균"]['Year'].unique().tolist(), reverse=True)
    selected_year = st.selectbox("📅 분석 연도 선택", options=year_opts, index=0)
    selected_region = st.multiselect("📍 대륙 선택", ["남미", "아시아", "아프리카"], default=["남미", "아시아", "아프리카"])

# --- 12. 메인 탭 구성 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 수입 통계 분석", 
    "🔍 관세 조회 시스템", 
    "🛡️ 통합 컴플라이언스", 
    "🌍 공급망 리밸런싱"
])

# =============================================================================
# TAB 1: 수입 통계 분석 (FAQ1,2.py의 첫 번째 탭)
# =============================================================================
with tab1:
    f_import = df_import[(df_import['Year'] == selected_year) & (df_import['Region'].isin(selected_region))]
    st.write("")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 수입량", f"{f_import['Import_Qty'].sum():,.1f} ton")
    m2.metric("주요 수입국", f_import.sort_values("Import_Qty", ascending=False).iloc[0]['Country'] if not f_import.empty else "-")
    m3.metric("총 수입액", f"${f_import['Value_USD'].sum():,.1f}M")
    m4.metric("분석 국가", f"{len(f_import)}개국")

    st.write("---")
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"#### 🌍 {selected_year} 국가별 커피 생두 수입 비중")
        fig = px.pie(f_import, values='Import_Qty', names='Country', hole=0.6, color_discrete_sequence=COFFEE_PALETTE)
        fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig.update_layout(margin=dict(t=20, b=20, l=0, r=0), legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(f"#### 📊 {selected_year} 실측 데이터")
        st.dataframe(f_import[['Country', 'Import_Qty', 'Value_USD', 'Region']].sort_values("Import_Qty", ascending=False),
                     column_config={"Import_Qty": st.column_config.ProgressColumn("수입량(ton)", format="%.1f", min_value=0, max_value=60000),
                                    "Value_USD": st.column_config.NumberColumn("금액($M)", format="$%.1f")},
                     hide_index=True, use_container_width=True)

# =============================================================================
# TAB 2: 관세 조회 시스템 (FAQ1,2.py의 두 번째 탭)
# =============================================================================
with tab2:
    f_tariff = df_tariff[df_tariff['대륙'].isin(selected_region)] if selected_region else df_tariff
    
    st.write("")

    st.markdown("### 🔍 공급망 권고안")
    sl, sr = st.columns(2)
    with sl:
        st.markdown(f"""
            <div class="strategy-card" style="background-color:#F0F4F0; border-top: 6px solid #2E7D32;">
                <h4 style="color:#2E7D32; margin-top:0;">🛡️ 안정적 파트너 (FTA 그룹)</h4>
                <p style="font-size:0.9rem; color:#555;"><b>해당 국가:</b> 온두라스, 코스타리카, 콜롬비아, 페루, 에티오피아, 베트남, 인도네시아</p>
                <p style="line-height:1.7; font-size:1.05rem;">
                    이 국가들은 <b>무역 협정(FTA)</b> 또는 <b>특혜 관세</b>가 확정되어 있습니다. 국제 정세가 변해도 <b>관세 0%가 영구적으로 보장</b>되므로, 원가 변동 폭이 적은 <span style="color:#2E7D32; font-weight:700;">장기 계약 및 주력 산지</span>로 운용하기에 최적입니다.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with sr:
        st.markdown(f"""
            <div class="strategy-card" style="background-color:#FFF8F0; border-top: 6px solid #EF6C00;">
                <h4 style="color:#EF6C00; margin-top:0;">⚡ 기회 포착 파트너 (할당관세 그룹)</h4>
                <p style="font-size:0.9rem; color:#555;"><b>해당 국가:</b> 과테말라, 브라질, 케냐</p>
                <p style="line-height:1.7; font-size:1.05rem;">
                    해당 산지는 원래 2%의 관세가 부과되나, 현재 <b>정부의 한시적 할당관세 0%</b> 혜택을 받고 있습니다. 정책 유효 기간 내에 <span style="color:#EF6C00; font-weight:700;">최대한의 물량을 선점</span>하는 전략이 유리하며, 추후 관세 복귀에 대비한 원가 시나리오를 미리 준비해야 합니다.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("분석 국가", f"{len(f_tariff)}개국")
    k2.metric("FTA 체결국", f"{len(f_tariff[f_tariff['FTA세율'] != '미체결'])}개")
    k3.metric("평균 최종세율", f"{f_tariff['최종세율'].mean():.1f}%")
    k4.metric("최고 기본세율", f"{f_tariff['기본세율'].max()}%")

    st.write("")
    st.markdown(f"#### 📋 {', '.join(selected_region) if selected_region else '전체'} 국가 관세 세부 현황")
    st.dataframe(f_tariff.style.background_gradient(subset=['최종세율'], cmap='YlOrBr').format({'최종세율': '{:.1f}%', '기본세율': '{:.1f}%'}),
                 use_container_width=True, hide_index=True)

# =============================================================================
# TAB 3: 통합 컴플라이언스 (FAQ3.py 전체)
# =============================================================================
with tab3:
    st.markdown(f"<h2 style='color: {COLOR_DEEP_COFFEE};'>🛡️ 커피 생두 수입 통합 컴플라이언스 분석</h2>", unsafe_allow_html=True)

    with st.container():
        st.info("""
            **안내:** 본 시스템은 **환경(EUDR)**, **식품안전(검역)**, **노동(인권)** 등 커피 수입 시 필수적으로 검토해야 할 
            글로벌 규제 리스크를 국가별로 정밀 분석하여 제공합니다.
        """)

    st.write("")
    col_input, col_info = st.columns([1, 1.8])

    with col_input:
        st.markdown("#### 🌍 분석 국가 선택")
        
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
        
        st.write("")
        
        with st.spinner(f"🤖 AI가 {target_country} 수입 전략을 분석 중입니다..."):
            ai_advice = get_ai_compliance_summary(target_country)
        
        st.markdown(f"""
            <div class="ai-box">
                <div style="display:flex; align-items:center; margin-bottom:10px;">
                    <span style="font-size:1.5rem; margin-right:10px;">🤖</span>
                    <span style="font-weight:bold; color:{COLOR_DEEP_COFFEE}; font-size:1.1rem;">AI 수입 전략 어드바이저</span>
                </div>
                <p style="color:#333; line-height:1.6; margin:0; font-weight:500;">{ai_advice}</p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: 공급망 리밸런싱 (FAQ4.py 전체)
# =============================================================================
with tab4:
    st.markdown(f"<h2 style='text-align: left;'>🌍 AI 기반 지정학적 공급망 리밸런싱</h2>", unsafe_allow_html=True)
    st.caption("OpenAI RCP 8.5 시나리오 분석: 2025년 대비 미래 산지 생산성 변화 예측")

    # 데이터 로드
    if 'rebalance_db' not in st.session_state:
        with st.spinner("🤖 AI가 글로벌 기후 시나리오를 시뮬레이션 중입니다..."):
            raw_ai = get_ai_rebalancing_data()
            if raw_ai: 
                st.session_state['rebalance_db'] = raw_ai

    if 'rebalance_db' in st.session_state:
        st.write("")
        st.markdown("### 📅 예측 시점 설정 (Time Machine)")
        selected_year_tab4 = st.slider("연도를 조절하여 공급망의 구조적 변화를 추적하세요", 2025, 2050, 2050, step=1)
        
        df_re = run_rebalancing_sim(st.session_state['rebalance_db'], selected_year_tab4)

        st.subheader(f"📈 {selected_year_tab4}년 국가별 생산성 변동률 예측")
        
        fig = px.bar(
            df_re.sort_values("Climate_Impact"), 
            x="Country", y="Climate_Impact", color="Shift_Type",
            color_discrete_map={
                "Risk": COLOR_RISK, 
                "Opportunity": COLOR_SAFE, 
                "Next Frontier": COLOR_FUTURE_GOLD, 
                "Stable": COLOR_STABLE_GRAY
            },
            labels={"Climate_Impact": "예상 생산량 변화 (%)"},
            text_auto='.1f'
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

        st.write("---")

        col_sel, col_val = st.columns([1, 1.4])

        with col_sel:
            st.markdown(f"### 🎯 {selected_year_tab4} 전략 국가 심층 분석")
            target = st.selectbox("리포트를 확인할 국가를 선택하세요", df_re['Country'].tolist(), index=12)
            c_info = df_re[df_re['Country'] == target].iloc[0]
            
            status_theme = {
                "Next Frontier": COLOR_FUTURE_GOLD, "Risk": COLOR_RISK,
                "Opportunity": COLOR_SAFE, "Stable": COLOR_STABLE_GRAY
            }.get(c_info['Shift_Type'], COLOR_DEEP_COFFEE)
            
            st.markdown(f"""
                <div style="background-color: white; padding: 24px; border-radius: 12px; border-top: 10px solid {status_theme}; 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 315px; display: flex; flex-direction: column; justify-content: center;">
                    <p style="color: #666; font-size: 0.85rem; margin-bottom: 2px; letter-spacing: 1px;">STRATEGIC REPORT ({selected_year_tab4})</p>
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
            
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="background-color: #F0F4F0; padding: 18px; border-radius: 10px; border-left: 5px solid {COLOR_SAFE};">
                        <p style="margin:0; font-weight:bold; color:{COLOR_SAFE}; font-size: 1rem;">🛡️ 아프리카 공급망 거점 강화 (Tanzania & Uganda)</p>
                        <p style="margin: 4px 0 0 0; font-size: 0.9rem; line-height: 1.4;">동아프리카 고산지대는 기후 변화의 최대 수혜지로 부상합니다.<br>현지 농장 선점 및 선제적 파트너십 구축이 시급합니다.</p>
                    </div>
                    <div style="background-color: #FFF9E6; padding: 18px; border-radius: 10px; border-left: 5px solid {COLOR_FUTURE_GOLD};">
                        <p style="margin:0; font-weight:bold; color:{COLOR_FUTURE_GOLD}; font-size: 1rem;">⚡ 동아시아 물류 허브 선점 (China Yunnan)</p>
                        <p style="margin: 4px 0 0 0; font-size: 0.9rem; line-height: 1.4;">지리적 이점과 탄소 규제 대응을 위해 중국 윈난 산지를<br>'차세대 전략 엔진'으로 격상하여 운용하십시오.</p>
                    </div>
                    <div style="background-color: #F8F9FA; padding: 18px; border-radius: 10px; border-left: 5px solid {COLOR_STABLE_GRAY};">
                        <p style="margin:0; font-weight:bold; color:{COLOR_STABLE_GRAY}; font-size: 1rem;">📉 고위험 산지 의존도 분산 전략</p>
                        <p style="margin: 4px 0 0 0; font-size: 0.9rem; line-height: 1.4;">기온 상승 직격탄을 받는 저지대 의존도를 <b>{selected_year_tab4}년까지 점진적 축소</b>하고<br>안정적 고산지 포트폴리오로 재편하십시오.</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.caption("© 2026 무역 AX 마스터 1기 원조맛집 | Data: 관세청 10개년 실측 통계 + OpenAI Scenario Engine")
