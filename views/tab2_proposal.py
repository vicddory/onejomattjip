# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab2_proposal.py - 커피 무역 제안서 생성기
================================================================================
[리팩토링 v2] 핵심 컨트롤 패널 강조, 직관적인 워크플로우
================================================================================
"""

import streamlit as st
import os
from datetime import datetime
from io import BytesIO

# PDF 라이브러리
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Excel 라이브러리
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# 경로 설정
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENAI_API_KEY
from utils import get_exchange_rate_with_status, get_country_weather


# ===========================================
# 폰트 설정 (PDF용)
# ===========================================
KOREAN_FONT = 'Helvetica'
USE_KOREAN_FONT = False

def register_korean_font():
    global KOREAN_FONT, USE_KOREAN_FONT
    font_candidates = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        'C:/Windows/Fonts/malgun.ttf',
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('KoreanFont', path))
                KOREAN_FONT = 'KoreanFont'
                USE_KOREAN_FONT = True
                return
            except:
                continue

register_korean_font()


# ===========================================
# 커피 품종 데이터
# ===========================================
def get_coffee_varieties():
    return {
        "에티오피아": {
            "port": "Djibouti", "port_en": "Djibouti Port", "country_en": "Ethiopia",
            "varieties": {
                "Gesha (게이샤)": {"price": 12.5, "desc": "자스민 향과 독보적인 산미", "desc_en": "Jasmine aroma"},
                "Yirgacheffe (예가체프)": {"price": 6.8, "desc": "꽃향기와 밝은 산미", "desc_en": "Floral aroma"},
                "Sidamo (시다모)": {"price": 5.8, "desc": "풍부한 과일 향", "desc_en": "Fruity aroma"}
            }
        },
        "브라질": {
            "port": "Santos", "port_en": "Santos Port", "country_en": "Brazil",
            "varieties": {
                "Bourbon (버번)": {"price": 5.2, "desc": "뛰어난 단맛과 밸런스", "desc_en": "Excellent sweetness"},
                "Catuai (카투아이)": {"price": 4.5, "desc": "가벼운 바디감", "desc_en": "Light body"},
                "Mundo Novo (문도노보)": {"price": 4.2, "desc": "밸런스 잡힌 맛", "desc_en": "Well-balanced"}
            }
        },
        "콜롬비아": {
            "port": "Buenaventura", "port_en": "Buenaventura Port", "country_en": "Colombia",
            "varieties": {
                "Typica (티피카)": {"price": 6.5, "desc": "깔끔한 향미와 단맛", "desc_en": "Clean flavor"},
                "Caturra (카투라)": {"price": 5.2, "desc": "풍부한 산미", "desc_en": "Rich acidity"},
                "Castillo (카스티요)": {"price": 5.0, "desc": "부드러운 베리류 향미", "desc_en": "Smooth berry notes"}
            }
        },
        "베트남": {
            "port": "Ho Chi Minh", "port_en": "Ho Chi Minh Port", "country_en": "Vietnam",
            "varieties": {
                "Robusta (로부스타)": {"price": 3.2, "desc": "강한 바디감", "desc_en": "Strong body"},
                "Catimor (카티모르)": {"price": 3.8, "desc": "산미와 쓴맛의 밸런스", "desc_en": "Balanced"},
                "Excelsa (엑셀사)": {"price": 4.2, "desc": "독특한 과일 향", "desc_en": "Unique fruity aroma"}
            }
        }
    }


# ===========================================
# AI 전문가 분석 함수
# ===========================================
def get_ai_advice(context_data, lang_code):
    if not OPENAI_API_KEY:
        return "⚠️ .env 파일에 OPENAI_API_KEY가 설정되지 않았습니다."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        target_lang = "Korean" if lang_code == 'ko' else "English"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a coffee trade expert. Respond in {target_lang} in 2-3 sentences."},
                {"role": "user", "content": f"Analyze this trade: {context_data['country_en']}, {context_data['variety_en']}, {context_data['quantity_ton']} ton"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 분석 오류: {str(e)}"


# ===========================================
# PDF/Excel 생성 함수
# ===========================================
def create_pdf_proposal(data, lang='ko'):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    font_name = KOREAN_FONT if USE_KOREAN_FONT else 'Helvetica'
    
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName=font_name, fontSize=20)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName=font_name, fontSize=11)
    
    story = []
    title = "수입 의사결정 제안서" if lang == 'ko' else "Coffee Import Proposal"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Date: {data['date']}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"산지: {data['country']} ({data['port']})", normal_style))
    story.append(Paragraph(f"품종: {data['variety']}", normal_style))
    story.append(Paragraph(f"수량: {data['quantity_ton']} ton", normal_style))
    story.append(Paragraph(f"총액: ${data['total_usd']} ({data['total_krw']} KRW)", normal_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("전문가 의견:", normal_style))
    story.append(Paragraph(data['ai_opinion'], normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def create_excel_proposal(data, lang='ko'):
    buffer = BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Proposal"
    
    ws['A1'] = "수입 의사결정 제안서" if lang == 'ko' else "Coffee Import Proposal"
    ws['A1'].font = Font(size=16, bold=True)
    
    ws['A3'] = "Date"
    ws['B3'] = data['date']
    ws['A4'] = "산지"
    ws['B4'] = f"{data['country']} ({data['port']})"
    ws['A5'] = "품종"
    ws['B5'] = data['variety']
    ws['A6'] = "수량"
    ws['B6'] = f"{data['quantity_ton']} ton"
    ws['A7'] = "총액"
    ws['B7'] = f"${data['total_usd']} ({data['total_krw']} KRW)"
    
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 40
    
    wb.save(buffer)
    buffer.seek(0)
    return buffer


# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """무역 제안서 생성기를 렌더링합니다."""
    
    data = get_coffee_varieties()
    
    # 세션 상태 초기화
    if 'exchange_source' not in st.session_state:
        st.session_state['exchange_source'] = 'manual'
    if 'api_rate' not in st.session_state:
        st.session_state['api_rate'] = None
    if 'proposal_manual_rate' not in st.session_state:
        st.session_state['proposal_manual_rate'] = 1450.0
    
    # 페이지 타이틀
    st.markdown("<h1 style='text-align:center; color:#6F4E37;'>☕ 커피 무역 대시보드</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ===========================================
    # 컨트롤 영역
    # ===========================================
    
    # 3개 컬럼으로 배치
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("##### 💱 실시간 환율 정보")
        
        # 현재 적용된 환율 표시
        if st.session_state['exchange_source'] == 'api' and st.session_state['api_rate']:
            exchange_rate = st.session_state['api_rate']
            rate_label = "🟢 API 환율"
        else:
            exchange_rate = st.session_state['proposal_manual_rate']
            rate_label = "🔵 수동 환율"
        
        st.info(f"**1 USD = {exchange_rate:,.2f} KRW**")
        st.caption(rate_label)
        
        # 실시간 환율 가져오기 버튼
        if st.button("🔄 환율 갱신", use_container_width=True, key="proposal_rate_btn", type="primary"):
            with st.spinner("환율 정보를 가져오는 중..."):
                rate, msg = get_exchange_rate_with_status()
                if rate:
                    st.session_state['api_rate'] = rate
                    st.session_state['exchange_source'] = 'api'
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    with col2:
        st.markdown("##### ✏️ 환율 수동 조정")
        
        # 환율 수동 입력
        manual_rate = st.number_input(
            "직접 입력 (KRW)",
            min_value=100.0,
            max_value=10000.0,
            value=st.session_state['proposal_manual_rate'],
            step=10.0,
            format="%.2f",
            key="manual_rate_input",
            help="원하는 환율을 직접 입력하세요"
        )
        
        # 수동 입력 적용 버튼
        if st.button("✅ 적용", use_container_width=True, key="apply_manual_rate", type="primary"):
            st.session_state['proposal_manual_rate'] = manual_rate
            st.session_state['exchange_source'] = 'manual'
            st.success(f"수동 환율 적용: {manual_rate:,.2f} 원")
            st.rerun()
    
    with col3:
        st.markdown("##### 🌍 국가 선택")
        
        # 국가 선택
        sorted_countries = sorted(list(data.keys()))
        
        # 국가별 국기 이모지 매핑
        country_flags = {
            "에티오피아": "🇪🇹",
            "브라질": "🇧🇷",
            "콜롬비아": "🇨🇴",
            "베트남": "🇻🇳"
        }
        
        country_options = [f"{country_flags.get(c, '🌍')} {c}" for c in sorted_countries]
        selected_display = st.selectbox(
            "산지 국가",
            country_options,
            key="proposal_country_display",
            help="제안서를 작성할 국가를 선택하세요"
        )
        
        # 실제 국가명 추출 (이모지 제거)
        selected_country = selected_display.split(" ", 1)[1]
    
    st.markdown("---")
    
    # ===========================================
    # 정보 및 실행 영역
    # ===========================================
    country_info = data[selected_country]
    weather_data = get_country_weather(country_info['port'])
    
    # 산지 정보 (날씨, 항구)
    st.subheader(f"📍 산지 정보 - {selected_country}")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.metric("🏙️ 항구", country_info['port'])
    with info_col2:
        st.metric("🌡️ 현지 기온", f"{weather_data['temp']}°C")
    with info_col3:
        st.metric("🌤️ 날씨", weather_data['desc_ko'])
    
    st.divider()
    
    # 품종 및 물량 선택
    col_variety, col_quantity = st.columns(2)
    
    with col_variety:
        st.markdown("### 🫘 품종 선택")
        selected_v = st.radio(
            "커피 품종",
            list(country_info['varieties'].keys()),
            key="proposal_variety",
            label_visibility="collapsed"
        )
        v_info = country_info['varieties'][selected_v]
        st.success(f"✨ 특징: {v_info['desc']}")
        st.info(f"💰 단가: ${v_info['price']:.2f}/kg")
    
    with col_quantity:
        st.markdown("### 📦 수입 물량")
        qty = st.number_input(
            "수입 물량 (Ton)",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            key="proposal_qty"
        )
        
        # 비용 계산
        price = v_info['price']
        total_usd = qty * 1000 * price
        total_krw = total_usd * exchange_rate
        
        st.metric("총 중량", f"{qty * 1000:,.0f} kg")
        st.metric("총액 (USD)", f"${total_usd:,.2f}")
        st.metric("총액 (KRW)", f"{int(total_krw):,} 원")
    
    st.divider()
    
    # ===========================================
    # AI 제안서 생성 버튼 (크게)
    # ===========================================
    st.markdown("### 🤖 AI 제안서 생성")
    
    lang_choice = st.radio(
        "문서 언어",
        ["한국어 (Korean)", "English"],
        horizontal=True,
        key="proposal_lang"
    )
    lang_code = 'ko' if "한국어" in lang_choice else 'en'
    
    # AI 생성 버튼
    if 'generated_proposal' not in st.session_state:
        st.session_state['generated_proposal'] = None
    
    if st.button("✨ AI 제안서 생성하기", use_container_width=True, type="primary", key="generate_proposal_btn"):
        with st.spinner("AI가 제안서를 생성하는 중..."):
            weather_str = f"{weather_data['temp']}°C, {weather_data['desc_ko']}"
            
            prop_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'country': selected_country,
                'country_en': country_info['country_en'],
                'port': country_info['port'],
                'port_en': country_info['port_en'],
                'variety': selected_v,
                'variety_en': selected_v.split('(')[0].strip(),
                'exchange_rate': f"{exchange_rate:,.1f}",
                'unit_price': f"{price:,.2f}",
                'quantity_ton': f"{qty:,.1f}",
                'total_usd': f"{total_usd:,.2f}",
                'total_krw': f"{int(total_krw):,}",
                'weather_en': weather_str,
                'ai_opinion': ""
            }
            
            # AI 의견 생성
            ai_advice = get_ai_advice(prop_data, lang_code)
            if not ai_advice or "⚠️" in ai_advice:
                ai_advice = f"본 제안서는 실시간 시세와 환율 기반입니다. 현지 날씨({weather_str})를 고려하여 신속한 의사결정을 권장합니다."
            
            prop_data['ai_opinion'] = ai_advice
            st.session_state['generated_proposal'] = prop_data
            st.success("✅ 제안서 생성 완료!")
    
    # ===========================================
    # 결과물 영역
    # ===========================================
    if st.session_state['generated_proposal']:
        st.divider()
        st.markdown("### 📄 제안서 미리보기")
        
        prop_data = st.session_state['generated_proposal']
        
        # 종이 문서 느낌의 카드 UI
        st.markdown(f"""
        <div style="background-color: white; padding: 40px; border-radius: 10px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 1px solid #ddd;">
            <h2 style="text-align: center; color: #6F4E37; margin-bottom: 30px;">
                {"☕ 수입 의사결정 제안서" if lang_code == 'ko' else "☕ Coffee Import Proposal"}
            </h2>
            <hr style="border: 1px solid #6F4E37; margin-bottom: 30px;">
            
            <div style="margin-bottom: 20px;">
                <p style="margin: 10px 0;"><strong>📅 작성일:</strong> {prop_data['date']}</p>
                <p style="margin: 10px 0;"><strong>🌍 산지:</strong> {prop_data['country']} ({prop_data['port']})</p>
                <p style="margin: 10px 0;"><strong>🫘 품종:</strong> {prop_data['variety']}</p>
                <p style="margin: 10px 0;"><strong>📦 수량:</strong> {prop_data['quantity_ton']} ton</p>
                <p style="margin: 10px 0;"><strong>💰 단가:</strong> ${prop_data['unit_price']}/kg</p>
                <p style="margin: 10px 0;"><strong>💵 총액 (USD):</strong> ${prop_data['total_usd']}</p>
                <p style="margin: 10px 0;"><strong>💴 총액 (KRW):</strong> {prop_data['total_krw']} 원</p>
                <p style="margin: 10px 0;"><strong>💱 적용 환율:</strong> {prop_data['exchange_rate']} KRW/USD</p>
            </div>
            
            <hr style="border: 1px dashed #ccc; margin: 30px 0;">
            
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; 
                        border-left: 5px solid #6F4E37;">
                <h4 style="color: #6F4E37; margin-top: 0;">🤖 AI 전문가 의견</h4>
                <p style="line-height: 1.8; color: #333;">{prop_data['ai_opinion']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # 다운로드 버튼
        st.markdown("### 📥 다운로드")
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            pdf_file = create_pdf_proposal(prop_data, lang=lang_code)
            st.download_button(
                "📄 PDF 다운로드",
                pdf_file,
                f"Proposal_{prop_data['country_en']}_{prop_data['date']}.pdf",
                "application/pdf",
                use_container_width=True,
                key="dl_pdf"
            )
        
        with download_col2:
            excel_file = create_excel_proposal(prop_data, lang=lang_code)
            st.download_button(
                "📊 Excel 다운로드",
                excel_file,
                f"Proposal_{prop_data['country_en']}_{prop_data['date']}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_excel"
            )


if __name__ == "__main__":
    show()