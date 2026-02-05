# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab3_cost_calculator.py - 원두 수입 원가 계산기
================================================================================
인코텀즈별 비용 계산 및 세금 산출 기능을 제공합니다.
[Fix] NameError 해결: 계산 로직에서 exchange_rate 변수 정의 추가
================================================================================
"""


import streamlit as st
import pandas as pd
import io


# 경로 설정
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utils import get_exchange_rate_with_status




def show():
    """원가 계산기를 렌더링합니다."""
   
    # 페이지 타이틀
    st.markdown("<h1 style='text-align: center; color:#6F4E37;'>원두 수입 원가 계산기</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")


    # ===========================================
    # 환율 설정 섹션 (메인 화면 상단) - 최종 슬림형 (한 줄 통합)
    # ===========================================
   
    # 세션 상태 초기화
    if 'cost_exchange_source' not in st.session_state:
        st.session_state['cost_exchange_source'] = 'manual'
    if 'cost_api_rate' not in st.session_state:
        st.session_state['cost_api_rate'] = None
    if 'cost_manual_rate' not in st.session_state:
        st.session_state['cost_manual_rate'] = 1400.0


    # API 환율 자동 로드
    if st.session_state['cost_api_rate'] is None:
        with st.spinner("최신 환율 정보를 가져오는 중..."):
            fetched_rate, _ = get_exchange_rate_with_status()
            if fetched_rate:
                st.session_state['cost_api_rate'] = fetched_rate


    # [상단 박스] 버튼 인라인 배치 (높이 120px)
    BOX_HEIGHT = 120
    col1, col2 = st.columns([1, 1], gap="medium")
   
    # 1. 왼쪽: 실시간 환율
    with col1:
        with st.container(border=True, height=BOX_HEIGHT):
            st.markdown("##### 오늘의 환율")
            display_rate = st.session_state['cost_api_rate'] if st.session_state['cost_api_rate'] else 0.0
           
            c_val, c_btn = st.columns([3, 1], vertical_alignment="bottom")
            with c_val:
                st.metric(label="USD 기준", value=f"{display_rate:,.2f} 원", label_visibility="collapsed")
            with c_btn:
                if st.button("갱신 →", use_container_width=True, key="cost_rate_btn"):
                    rate, msg = get_exchange_rate_with_status()
                    if rate:
                        st.session_state['cost_api_rate'] = rate
                        st.session_state['cost_exchange_source'] = 'api'
                        st.rerun()


    # 2. 오른쪽: 수동 설정
    with col2:
        with st.container(border=True, height=BOX_HEIGHT):
            st.markdown("##### 환율 수동 설정")
           
            c_input, c_btn = st.columns([3, 1], vertical_alignment="bottom")
            with c_input:
                manual_rate = st.number_input(
                    "수동 환율",
                    value=st.session_state['cost_manual_rate'],
                    step=10.0, format="%.2f",
                    key="manual_rate_input",
                    label_visibility="collapsed"
                )
            with c_btn:
                if st.button("적용 →", use_container_width=True, key="apply_manual_rate"):
                    st.session_state['cost_manual_rate'] = manual_rate
                    st.session_state['cost_exchange_source'] = 'manual'
                    st.rerun()


    # 3. [하단 정보] 최종 디자인 (연한 녹색 박스 + 중앙 정렬)
    st.write("") # 상단 박스와의 간격 확보


    # 데이터 결정 로직 (이 값이 최종적으로 계산에 쓰임)
    if st.session_state['cost_exchange_source'] == 'api' and st.session_state['cost_api_rate']:
        final_applied_rate = st.session_state['cost_api_rate']
    else:
        final_applied_rate = st.session_state['cost_manual_rate']


    # CSS 스타일링: 연한 녹색 배경(#E0F2F1), 중앙 정렬, 라운딩 처리
    st.markdown(f"""
        <div style='
            background-color: #E0F2F1;
            border: 1px solid #B2DFDB;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            margin-top: 5px;
        '>
            <span style='color: #424242; font-size: 15px; font-weight: 500;'>현재 적용 환율:</span>
            <span style='color: #00695C; font-size: 18px; font-weight: 800; margin-left: 8px;'>
                {final_applied_rate:,.2f} 원/USD
            </span>
        </div>
    """, unsafe_allow_html=True)
   
    st.divider()


    # ===========================================
    # 메인 입력 섹션
    # ===========================================
    col1, col2 = st.columns([1, 2])


    with col1:
        st.subheader("1. 계약 조건")
        incoterm = st.selectbox(
            "인코텀즈 선택",
            ["EXW (공장인도)", "FOB (본선인도)", "CFR (운임포함)", "CIF (운임보험료포함)", "DDP (관세지급인도)"],
            key="cost_incoterm"
        )
        selected_code = incoterm.split()[0]
       


    with col2:
        st.subheader("2. 비용 데이터")
       
        # ① 물품대금
        p_value = st.number_input("① 물품대금 (Price, USD)", min_value=0.0, value=0.0, format="%.2f", key="cost_price")


        # ② 국제운송비 (조건부)
        f_value = 0.0
        if selected_code in ["EXW", "FOB"]:
            f_value = st.number_input("② 국제운송비 (Freight, USD)", min_value=0.0, value=0.0, format="%.2f", key="cost_freight")
        else:
            st.info(f"{selected_code} 조건은 운임이 물품대금에 포함되어 있습니다.")
       
        # ③ 보험료 (조건부)
        i_value_krw = 0.0
        if selected_code in ["EXW", "FOB", "CFR"]:
            label = "③ 보험료 (Insurance, KRW)"
            if selected_code == "CFR":
                label += " (선택: 0 가능)"
            i_value_krw = st.number_input(label, min_value=0, value=0, step=1000, format="%d", key="cost_insurance")
        else:
            st.info(f"{selected_code} 조건은 보험료가 물품대금에 포함되어 있습니다.")


        c1, c2 = st.columns(2)
        with c1:
            duty_rate = st.number_input("④ 관세율 (%)", value=0.0, step=0.1, format="%.2f", key="cost_duty")
        with c2:
            local_cost = st.number_input("⑤ 국내 발생비용 (KRW)", value=0, step=10000, format="%d", key="cost_local")


    # ===========================================
    # 계산 및 결과
    # ===========================================
    if st.button("계산 결과 보기", use_container_width=True, key="cost_calc_btn"):
       
        # [Fix] 계산 로직에 사용할 변수 정의 (위에서 결정된 final_applied_rate를 할당)
        exchange_rate = final_applied_rate


        # 계산 로직
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


        # 결과 화면
        st.divider()
        st.subheader(f"[{selected_code}] 최종 원가 분석")
       


        k1, k2, k3 = st.columns(3)
        k1.metric("총 필요 자금", f"{int(total_krw):,} 원", delta="Total Cost")
        k2.metric("예상 세금 (관세+부가세)", f"{int(duty_amt + vat_amt):,} 원")
        k3.metric("과세가격 (CIF)", f"{int(cif_krw):,} 원", help="관세청 신고 기준 가격")


        st.caption(f"※ 적용 환율: {exchange_rate:,.2f} 원/USD | 보험료는 원화({int(i_value_krw):,}원) 그대로 합산")
       
        # 결과 테이블
        st.markdown("### 상세 비용 분석표")
        st.markdown('<div style="width: 100%; height: 3px; background-color: #00695C; margin-top: 5px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)


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


# ===========================================
        # 엑셀 다운로드
        # ===========================================
        st.divider()
        st.markdown("### 결과 다운로드")
       
        output = io.BytesIO()


        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('최종원가분석')
           
            # [수정] 스타일 정의: 타이틀을 검정색(#000000) 및 중앙 정렬(center)로 변경
            title_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'font_color': '#333333',
                'align': 'center', 'valign': 'vcenter', 'bottom': 2
            })
           
            header_format = workbook.add_format({
                'bold': True, 'font_size': 11, 'font_color': 'white',
                'align': 'center', 'fg_color': '#00695C', 'border': 1
            })
           
            data_format = workbook.add_format({
                'font_size': 10, 'align': 'right', 'border': 1
            })
           
            total_format = workbook.add_format({
                'bold': True, 'font_size': 12, 'font_color': '#00695C',
                'align': 'right', 'bg_color': '#E8F5E9', 'border': 2
            })
           
            # 열 너비 설정
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 22)
            worksheet.set_column('C:C', 22)
           
            # 제목
            row = 0
            worksheet.merge_range(row, 0, row, 2, f'원두 수입 원가 계산 결과', title_format)
            row += 2
           
            # 계산 정보
            info_format = workbook.add_format({'font_size': 10, 'align': 'left'})
            worksheet.write(row, 0, f'인코텀즈: {selected_code}', info_format)
            row += 1
            worksheet.write(row, 0, f'적용 환율: {exchange_rate:,.2f} 원/USD', info_format)
            row += 2
           
            # 헤더
            worksheet.write(row, 0, '항목', header_format)
            worksheet.write(row, 1, '외화 (USD)', header_format)
            worksheet.write(row, 2, '원화 (KRW)', header_format)
            row += 1
           
            # 데이터
            for idx, r in df.iterrows():
                worksheet.write(row, 0, r['항목'], data_format)
                worksheet.write(row, 1, r['외화 (USD)'], data_format)
                clean_val = str(r['원화 (KRW)']).replace('🔴 ', '')
                worksheet.write(row, 2, clean_val, data_format)
                row += 1
           
            row += 1
            worksheet.write(row, 0, '총 필요 자금', header_format)
            worksheet.write(row, 2, f"{int(total_krw):,}원", total_format)
           
            row += 1
            worksheet.write(row, 0, '예상 세금', header_format)
            worksheet.write(row, 2, f"{int(duty_amt + vat_amt):,}원", total_format)


        output.seek(0)




        # ----------------------------------------------------------------------
        # [스타일 보정] 다운로드 버튼을 '계산 결과 보기' 버튼과 똑같이 만들기 위한 CSS
        # ----------------------------------------------------------------------
        st.markdown("""
            <style>
            /* 다운로드 버튼에 마우스를 올렸을 때(Hover) 테두리와 글자를 초록색(#00695C)으로 변경 */
            div[data-testid="stDownloadButton"] > button:hover {
                border-color: #00695C !important;
                color: #00695C !important;
                background-color: transparent !important;
            }
            /* 버튼의 가로 너비 꽉 차게, 기본 텍스트 색상 설정 */
            div[data-testid="stDownloadButton"] > button {
                width: 100%;
                border-color: rgba(49, 51, 63, 0.2);
            }
            </style>
        """, unsafe_allow_html=True)


        # 엑셀 다운로드 버튼 생성 (type="primary" 제거 -> 기본 흰색 배경 유지)
        st.download_button(
            label="엑셀 파일 다운로드 →",
            data=output,
            file_name=f"Import_Cost_Analysis_{selected_code}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,  # 계산 버튼과 동일하게 가로 꽉 채움
            key="cost_excel_dl"
        )


if __name__ == "__main__":
    show()

