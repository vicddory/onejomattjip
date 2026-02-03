# -*- coding: utf-8 -*-
"""
Tab 3: Cost Calculator - 원두 수입 원가 계산기
"""

import streamlit as st
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import urllib3
import io

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

def get_current_exchange_rate():
    api_key = os.getenv("EXCHANGE_RATE")
    if not api_key:
        return None, "❌ .env 파일에서 'EXCHANGE_RATE' 키를 찾을 수 없습니다."

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            if "conversion_rates" in data and "KRW" in data["conversion_rates"]:
                return data["conversion_rates"]["KRW"], "✅ 실시간 환율을 성공적으로 불러왔습니다."
        return None, "⚠️ API 서버 오류"
    except Exception as e:
        return None, f"❌ 연결 오류: {str(e)}"

def show():
    """Cost Calculator 페이지를 렌더링하는 메인 함수"""
    
    st.title("🚢 원두 수입 원가 계산기")
    st.markdown("### 인코텀즈를 선택해주세요. 상세 내용은 자동으로 안내됩니다.")
    st.divider()

    # 사이드바: 환율 설정
    with st.sidebar:
        st.header("💰 환율 설정")
        
        if 'exchange_source_tab3' not in st.session_state:
            st.session_state['exchange_source_tab3'] = 'manual'

        tab1, tab2 = st.tabs(["📡 오늘의 환율", "✍️ 수동 입력"])
        
        with tab1:
            if st.button("실시간 환율 가져오기 🔄", key="tab3_rate_btn"):
                with st.spinner("환율 서버에 접속 중입니다..."):
                    rate, msg = get_current_exchange_rate()
                    if rate:
                        st.success(msg)
                        st.session_state['api_rate_tab3'] = rate
                        st.session_state['exchange_source_tab3'] = 'api'
                    else:
                        st.error(msg)
            
            if 'api_rate_tab3' in st.session_state:
                st.metric("API 수신 환율", f"{st.session_state['api_rate_tab3']:,.2f} 원")

        with tab2:
            def set_manual_mode():
                st.session_state['exchange_source_tab3'] = 'manual'

            manual_rate = st.number_input(
                "직접 입력하기", 
                value=1400.0, 
                format="%.2f",
                on_change=set_manual_mode,
                key="tab3_manual_rate"
            )

        if st.session_state['exchange_source_tab3'] == 'api' and 'api_rate_tab3' in st.session_state:
            exchange_rate = st.session_state['api_rate_tab3']
        else:
            exchange_rate = manual_rate

        st.divider()
        st.markdown(f"**현재 적용 환율:**\n# **{exchange_rate:,.2f} 원/USD**")

    # 메인 입력 섹션
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("1. 계약 조건")
        incoterm = st.selectbox(
            "인코텀즈 선택",
            ["EXW (공장인도)", "FOB (본선인도)", "CFR (운임포함)", "CIF (운임보험료포함)", "DDP (관세지급인도)"],
            key="tab3_incoterm"
        )
        selected_code = incoterm.split()[0]

    with col2:
        st.subheader("2. 비용 데이터")
        
        p_value = st.number_input("① 물품대금 (Price, USD)", min_value=0.0, value=0.0, format="%.2f", key="tab3_price")

        f_value = 0.0
        if selected_code in ["EXW", "FOB"]:
            f_value = st.number_input("② 국제운송비 (Freight, USD)", min_value=0.0, value=0.0, format="%.2f", key="tab3_freight")
        else:
            st.info(f"💡 {selected_code} 조건은 운임이 물품대금에 포함되어 있습니다.")
        
        i_value_krw = 0.0
        if selected_code in ["EXW", "FOB", "CFR"]:
            label = "③ 보험료 (Insurance, KRW)"
            if selected_code == "CFR":
                label += " (선택: 0 가능)"
            i_value_krw = st.number_input(label, min_value=0, value=0, step=1000, format="%d", key="tab3_insurance")
        else:
            st.info(f"💡 {selected_code} 조건은 보험료가 물품대금에 포함되어 있습니다.")

        c1, c2 = st.columns(2)
        with c1:
            duty_rate = st.number_input("④ 관세율 (%)", value=0.0, step=0.1, format="%.2f", key="tab3_duty")
        with c2:
            local_cost = st.number_input("⑤ 국내 발생비용 (KRW)", value=0, step=10000, format="%d", key="tab3_local")

    # 계산 및 결과 출력
    if st.button("🧮 계산 결과 보기", type="primary", use_container_width=True, key="tab3_calc_btn"):
        
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

        st.divider()
        st.subheader(f"📊 [{selected_code}] 최종 원가 분석")
        
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

        # 엑셀 다운로드
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('최종원가분석')
            
            title_format = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#1F4788'})
            header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4788', 'border': 1})
            data_format = workbook.add_format({'align': 'right', 'border': 1})
            total_format = workbook.add_format({'bold': True, 'font_size': 12, 'bg_color': '#D9E9FF', 'border': 2, 'num_format': '#,##0 "원"'})
            
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:C', 22)
            
            row = 0
            worksheet.merge_range(row, 0, row, 2, f'☕ 원두 수입 원가 계산 결과', title_format)
            row += 2
            
            worksheet.write(row, 0, '항목', header_format)
            worksheet.write(row, 1, '외화 (USD)', header_format)
            worksheet.write(row, 2, '원화 (KRW)', header_format)
            row += 1
            
            for idx, r in df.iterrows():
                worksheet.write(row, 0, r['항목'], data_format)
                worksheet.write(row, 1, r['외화 (USD)'], data_format)
                krw_val = str(r['원화 (KRW)']).replace('🔴 ', '')
                worksheet.write(row, 2, krw_val, data_format)
                row += 1
            
            row += 1
            worksheet.merge_range(row, 0, row, 1, '💵 총 필요 자금', header_format)
            worksheet.write(row, 2, int(total_krw), total_format)

        output.seek(0)

        st.download_button(
            label="📥 엑셀 파일 다운로드",
            data=output,
            file_name="Import_Cost_Analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="tab3_excel_dl"
        )
