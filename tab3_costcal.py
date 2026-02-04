import streamlit as st
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import urllib3
import io 

# SSL 경고 메시지 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. 환경변수 및 기본 설정
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="원두 수입 원가 계산기", layout="wide")

# --- 🎨 UI/UX 디자인 (색상은 config.toml에서 제어, 여기서는 형태만 잡음) ---
st.markdown("""
    <style>
        /* 1. 폰트 임포트 (Noto Sans KR) */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

        /* 2. 전체 폰트 적용 */
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif !important;
        }

        /* 3. 입력창 둥근 모서리 및 쉐도우 (색상은 config.toml을 따름) */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input, 
        .stSelectbox > div > div > div {
            border-radius: 8px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        /* 4. 버튼 둥근 모서리 및 그림자 */
        .stButton > button {
            border-radius: 8px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            font-weight: 600 !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }

        /* 5. 탭 스타일 (선택된 탭 텍스트 굵게) */
        .stTabs [aria-selected="true"] {
            font-weight: 700 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>원두 수입 원가 계산기</h1>", unsafe_allow_html=True)
st.divider()

# --- 🛠️ 환율 API 호출 함수 (User-Agent 포함) ---
def get_current_exchange_rate():
    api_key = os.getenv("EXCHANGE_RATE")
    if not api_key:
        return None, "❌ .env 파일에서 'EXCHANGE_RATE' 키를 찾을 수 없습니다."

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    # [중요] 봇 차단 방지용 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            if "conversion_rates" in data and "KRW" in data["conversion_rates"]:
                return data["conversion_rates"]["KRW"], "✅ 실시간 환율을 성공적으로 불러왔습니다."
            else:
                return None, "⚠️ 응답은 받았으나 KRW 환율 정보가 없습니다."
        else:
            return None, f"⚠️ API 서버 오류 (코드: {response.status_code})"
    except Exception as e:
        return None, f"❌ 연결 오류: {str(e)}"

# ------------------------------------------------

# 2. 사이드바: 환율 설정
with st.sidebar:
    st.header("환율 설정")
    
    # [핵심 로직] 환율 기준(Source)을 추적하기 위한 세션 상태 초기화
    if 'exchange_source' not in st.session_state:
        st.session_state['exchange_source'] = 'manual' # 기본값은 수동

    tab1, tab2 = st.tabs(["오늘의 환율", "수동 입력"])
    
    # 탭 1: API 연동
    with tab1:
        if st.button("실시간 환율 가져오기 🔄"):
            with st.spinner("환율 서버에 접속 중입니다..."):
                rate, msg = get_current_exchange_rate()
                if rate:
                    st.success(msg)
                    st.session_state['api_rate'] = rate
                    # [중요] API 버튼을 누르면 계산 기준을 'api'로 변경
                    st.session_state['exchange_source'] = 'api'
                else:
                    st.error(msg)
        
        # API 환율이 있으면 표시
        if 'api_rate' in st.session_state:
            st.metric("API 수신 환율", f"{st.session_state['api_rate']:,.2f} 원")

    # 탭 2: 수동 입력
    with tab2:
        # [중요] 수동 입력값이 변경되면 실행될 함수
        def set_manual_mode():
            st.session_state['exchange_source'] = 'manual'

        manual_rate = st.number_input(
            "직접 입력하기", 
            value=1400.0, 
            format="%.2f",
            on_change=set_manual_mode # 값이 바뀌면 'manual' 모드로 전환
        )

    # 최종 환율 결정 로직
    # 소스가 'api'이고, 실제로 api 값이 있을 때만 API 환율 적용
    if st.session_state['exchange_source'] == 'api' and 'api_rate' in st.session_state:
        exchange_rate = st.session_state['api_rate']
    else:
        # 그 외(기본 상태이거나, 수동 입력을 건드렸을 때)는 수동 값 적용
        exchange_rate = manual_rate

    st.divider()
    # 현재 어떤 환율이 적용되는지 명확히 표시
    st.markdown(f"**현재 적용 환율:**\n# **{exchange_rate:,.2f} 원/USD**")


# 3. 메인 입력 섹션
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. 계약 조건")
    incoterm = st.selectbox(
        "인코텀즈 선택",
        ["EXW (공장인도)", "FOB (본선인도)", "CFR (운임포함)", "CIF (운임보험료포함)", "DDP (관세지급인도)"]
    )
    selected_code = incoterm.split()[0]

with col2:
    st.subheader("2. 비용 데이터")
    
    # ① 물품대금 (항상 표시) - 소수점 2자리
    p_value = st.number_input("① 물품대금 (Price, USD)", min_value=0.0, value=0.0, format="%.2f")

    # ② 국제운송비 (조건부 표시) - 소수점 2자리
    f_value = 0.0
    if selected_code in ["EXW", "FOB"]:
        f_value = st.number_input("② 국제운송비 (Freight, USD)", min_value=0.0, value=0.0, format="%.2f")
    else:
        st.info(f"💡 {selected_code} 조건은 운임이 물품대금에 포함되어 있습니다.")
    
    # ③ 보험료 (조건부 표시) - 원화는 정수형(%d)
    i_value_krw = 0.0
    if selected_code in ["EXW", "FOB", "CFR"]:
        label = "③ 보험료 (Insurance, KRW)"
        if selected_code == "CFR":
            label += " (선택: 0 가능)"
        i_value_krw = st.number_input(label, min_value=0, value=0, step=1000, format="%d")
    else:
        st.info(f"💡 {selected_code} 조건은 보험료가 물품대금에 포함되어 있습니다.")

    c1, c2 = st.columns(2)
    with c1:
        duty_rate = st.number_input("④ 관세율 (%)", value=0.0, step=0.1, format="%.2f")
    with c2:
        local_cost = st.number_input("⑤ 국내 발생비용 (KRW)", value=0, step=10000, format="%d")

# 4. 계산 및 결과 출력
if st.button("계산 결과 보기", type="primary", use_container_width=True):
    
    # --- 계산 로직 ---
    usd_portion = p_value + f_value
    base_krw = usd_portion * exchange_rate
    cif_krw = base_krw + i_value_krw
    cif_usd_ref = cif_krw / exchange_rate if exchange_rate > 0 else 0

    duty_amt = cif_krw * (duty_rate / 100)
    vat_amt = 0 if duty_rate == 0 else (cif_krw + duty_amt) * 0.1
    
    if selected_code == "DDP":
        total_krw = (p_value * exchange_rate) + local_cost
        duty_amt = 0 
        vat_amt = 0 
        cif_krw = base_krw 
    else:
        total_krw = cif_krw + duty_amt + vat_amt + local_cost

    # --- 결과 화면 ---
    st.divider()
    st.subheader(f"[{selected_code}] 최종 원가 분석")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("총 필요 자금", f"{int(total_krw):,} 원", delta="Total Cost")
    k2.metric("예상 세금 (관세+부가세)", f"{int(duty_amt + vat_amt):,} 원")
    k3.metric("과세가격 (CIF)", f"{int(cif_krw):,} 원", help="관세청 신고 기준 가격")

    st.caption(f"※ 적용 환율: {exchange_rate:,.2f} 원/USD | 보험료는 원화({int(i_value_krw):,}원) 그대로 합산되었습니다.")
    
    df = pd.DataFrame({
        "항목": ["물품대금(Price)", "국제운송비(Freight)", "보험료(Insurance)", "과세가격(CIF)", "관세(Duty)", "부가세(VAT)", "국내비용(Local)"],
        "외화 (USD)": [
            f"${p_value:,.2f}",
            f"${f_value:,.2f}" if f_value > 0 else "-",
            "-", 
            f"${cif_usd_ref:,.2f} (참고)",
            "-", "-", "-"
        ],
        "원화 (KRW)": [
            f"{int(p_value * exchange_rate):,}원",
            f"{int(f_value * exchange_rate):,}원" if f_value > 0 else "-",
            f"{int(i_value_krw):,}원" if i_value_krw > 0 else "-", 
            f"🔴 {int(cif_krw):,}원",
            f"{int(duty_amt):,}원",
            f"{int(vat_amt):,}원",
            f"{int(local_cost):,}원"
        ]
    })
    st.table(df)

    # ═══════════════════════════════════════════════════════════
    # 🎨 프로페셔널 엑셀 다운로드
    # ═══════════════════════════════════════════════════════════
    
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('최종원가분석')
        
        # ═══════════════════════════════════════════════════════════
        # 🎨 고급 스타일 포맷 정의
        # ═══════════════════════════════════════════════════════════
        
        # 📋 제목 스타일 (큰 제목)
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#1F4788',
            'align': 'left',
            'valign': 'vcenter',
            'bottom': 2,
            'bottom_color': '#1F4788'
        })
        
        # 📊 서브타이틀 (인코텀즈, 환율 정보)
        subtitle_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#666666',
            'align': 'left',
            'italic': True
        })
        
        # 📌 헤더 스타일 (그라데이션 효과)
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#1F4788',
            'border': 1,
            'border_color': '#FFFFFF',
            'text_wrap': True
        })
        
        # 💰 항목명 스타일 (좌측 컬럼)
        item_format = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#E8EFF7',
            'border': 1,
            'border_color': '#CCCCCC',
            'left': 2,
            'left_color': '#1F4788'
        })
        
        # 📝 일반 데이터 스타일
        data_format = workbook.add_format({
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#DDDDDD'
        })
        
        # 🔴 강조 데이터 (CIF 과세가격)
        highlight_format = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': '#C0504D',
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFF2CC',
            'border': 1,
            'border_color': '#DDDDDD'
        })
        
        # 🎯 최종 합계 스타일
        total_label_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#1F4788',
            'border': 2,
            'left': 3,
            'left_color': '#1F4788'
        })
        
        total_value_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': '#1F4788',
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#D9E9FF',
            'border': 2,
            'num_format': '#,##0 "원"'
        })
        
        # ═══════════════════════════════════════════════════════════
        # 📝 문서 작성
        # ═══════════════════════════════════════════════════════════
        
        # 열 너비 설정
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 22)
        
        current_row = 0
        
        # 1️⃣ 제목 섹션
        worksheet.merge_range(current_row, 0, current_row, 2, 
                            f'☕ 원두 수입 원가 계산 결과', title_format)
        current_row += 1
        
        worksheet.merge_range(current_row, 0, current_row, 2, 
                            f'인코텀즈: {selected_code} | 환율: {exchange_rate:,.2f} 원/USD | 작성일: 2026-02-02', 
                            subtitle_format)
        current_row += 2
        
        # 2️⃣ 테이블 헤더
        worksheet.write(current_row, 0, '항목', header_format)
        worksheet.write(current_row, 1, '외화 (USD)', header_format)
        worksheet.write(current_row, 2, '원화 (KRW)', header_format)
        worksheet.set_row(current_row, 25)  # 헤더 행 높이
        current_row += 1
        
        # 3️⃣ 데이터 행 작성
        for idx, row in df.iterrows():
            # 항목명
            worksheet.write(current_row, 0, row['항목'], item_format)
            
            # USD 값
            worksheet.write(current_row, 1, row['외화 (USD)'], data_format)
            
            # KRW 값 (CIF는 강조)
            if '🔴' in str(row['원화 (KRW)']):
                clean_value = str(row['원화 (KRW)']).replace('🔴 ', '')
                worksheet.write(current_row, 2, clean_value, highlight_format)
            else:
                worksheet.write(current_row, 2, row['원화 (KRW)'], data_format)
            
            worksheet.set_row(current_row, 22)  # 데이터 행 높이
            current_row += 1
        
        # 빈 행 추가
        current_row += 1
        
        # 4️⃣ 최종 합계 섹션
        worksheet.merge_range(current_row, 0, current_row, 1, 
                            '💵 총 필요 자금 (Total Cost)', total_label_format)
        worksheet.write(current_row, 2, int(total_krw), total_value_format)
        worksheet.set_row(current_row, 28)
        current_row += 1
        
        # 5️⃣ 추가 정보 (작은 글씨로)
        worksheet.merge_range(current_row, 0, current_row, 2, 
                            f'※ 세금 합계: {int(duty_amt + vat_amt):,}원 (관세 {int(duty_amt):,}원 + 부가세 {int(vat_amt):,}원)', 
                            subtitle_format)
        current_row += 1
        
        worksheet.merge_range(current_row, 0, current_row, 2, 
                            f'※ 보험료는 원화({int(i_value_krw):,}원) 기준으로 합산되었습니다.', 
                            subtitle_format)

    output.seek(0)

    st.download_button(
        label="엑셀 파일 다운로드",
        data=output,
        file_name="Import_Cost_Professional.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
