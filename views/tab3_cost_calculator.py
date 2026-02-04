# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab3_cost_calculator.py - 원두 수입 원가 계산기
================================================================================
인코텀즈별 비용 계산 및 세금 산출 기능을 제공합니다.
[리팩토링] 사이드바 제거, 환율 설정을 메인 화면 상단으로 이동
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
    st.markdown("<h1 style='text-align: center; color:#6F4E37;'>☕ 원두 수입 원가 계산기</h1>", unsafe_allow_html=True)
    st.divider()

    # ===========================================
    # 환율 설정 섹션 (메인 화면 상단)
    # ===========================================
    
    # 세션 상태 초기화
    if 'cost_exchange_source' not in st.session_state:
        st.session_state['cost_exchange_source'] = 'manual'
    if 'cost_api_rate' not in st.session_state:
        st.session_state['cost_api_rate'] = None
    if 'cost_manual_rate' not in st.session_state:
        st.session_state['cost_manual_rate'] = 1400.0
        
    # 2개 컬럼으로 배치
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("##### 🌐 실시간 환율 정보")
        
        # 현재 적용된 환율 표시
        if st.session_state['cost_exchange_source'] == 'api' and st.session_state['cost_api_rate']:
            exchange_rate = st.session_state['cost_api_rate']
            rate_label = "🟢 API 환율"
        else:
            exchange_rate = st.session_state['cost_manual_rate']
            rate_label = "🔵 수동 환율"
        
        st.metric(
            label="현재 시장 환율 (USD)",
            value=f"{exchange_rate:,.2f} 원",
            delta=rate_label
        )
        
        # 실시간 환율 가져오기 버튼
        if st.button("🔄 실시간 환율 갱신", use_container_width=True, type="primary", key="cost_rate_btn"):
            with st.spinner("환율 서버 접속 중..."):
                rate, msg = get_exchange_rate_with_status()
                if rate:
                    st.session_state['cost_api_rate'] = rate
                    st.session_state['cost_exchange_source'] = 'api'
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    with col2:
        st.markdown("##### ✏️ 환율 수동 설정")
        
        # 환율 수동 입력
        manual_rate = st.number_input(
            "적용 환율 (원/달러)",
            min_value=100.0,
            max_value=10000.0,
            value=st.session_state['cost_manual_rate'],
            step=10.0,
            format="%.2f",
            key="manual_rate_input",
            help="계산에 사용할 환율을 직접 입력하세요"
        )
        
        # 수동 입력 적용 버튼
        if st.button("✅ 적용", use_container_width=True, type="primary", key="apply_manual_rate"):
            st.session_state['cost_manual_rate'] = manual_rate
            st.session_state['cost_exchange_source'] = 'manual'
            st.success(f"수동 환율 적용: {manual_rate:,.2f} 원/USD")
            st.rerun()
    
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
            st.info(f"💡 {selected_code} 조건은 운임이 물품대금에 포함되어 있습니다.")
        
        # ③ 보험료 (조건부)
        i_value_krw = 0.0
        if selected_code in ["EXW", "FOB", "CFR"]:
            label = "③ 보험료 (Insurance, KRW)"
            if selected_code == "CFR":
                label += " (선택: 0 가능)"
            i_value_krw = st.number_input(label, min_value=0, value=0, step=1000, format="%d", key="cost_insurance")
        else:
            st.info(f"💡 {selected_code} 조건은 보험료가 물품대금에 포함되어 있습니다.")

        c1, c2 = st.columns(2)
        with c1:
            duty_rate = st.number_input("④ 관세율 (%)", value=0.0, step=0.1, format="%.2f", key="cost_duty")
        with c2:
            local_cost = st.number_input("⑤ 국내 발생비용 (KRW)", value=0, step=10000, format="%d", key="cost_local")

    # ===========================================
    # 계산 및 결과
    # ===========================================
    if st.button("💰 계산 결과 보기", type="primary", use_container_width=True, key="cost_calc_btn"):
        
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
        st.subheader(f"📊 [{selected_code}] 최종 원가 분석")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("💵 총 필요 자금", f"{int(total_krw):,} 원", delta="Total Cost")
        k2.metric("💸 예상 세금 (관세+부가세)", f"{int(duty_amt + vat_amt):,} 원")
        k3.metric("📦 과세가격 (CIF)", f"{int(cif_krw):,} 원", help="관세청 신고 기준 가격")

        st.caption(f"※ 적용 환율: {exchange_rate:,.2f} 원/USD | 보험료는 원화({int(i_value_krw):,}원) 그대로 합산")
        
        # 결과 테이블
        st.markdown("### 📋 상세 비용 분석표")
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
        st.markdown("### 📥 결과 다운로드")
        
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('최종원가분석')
            
            # 스타일 정의
            title_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'font_color': '#6F4E37',
                'align': 'left', 'valign': 'vcenter', 'bottom': 2
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
            worksheet.merge_range(row, 0, row, 2, f'☕ 원두 수입 원가 계산 결과', title_format)
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
            worksheet.write(row, 0, '💵 총 필요 자금', header_format)
            worksheet.write(row, 2, f"{int(total_krw):,}원", total_format)
            
            row += 1
            worksheet.write(row, 0, '💸 예상 세금', header_format)
            worksheet.write(row, 2, f"{int(duty_amt + vat_amt):,}원", total_format)

        output.seek(0)

        download_col1, download_col2 = st.columns(2)
        with download_col1:
            st.download_button(
                label="📄 엑셀 파일 다운로드",
                data=output,
                file_name=f"Import_Cost_Analysis_{selected_code}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="cost_excel_dl"
            )


if __name__ == "__main__":
    show()