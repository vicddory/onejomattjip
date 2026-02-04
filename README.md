# ☕ Coffee Trade Hub

> 글로벌 원두 무역 데이터 분석 및 시각화 플랫폼

무역 AX 마스터 1기 "원조맛집" 팀 프로젝트

---

## 📁 프로젝트 구조

```
coffee_trade_hub/
│
├── main.py                 # 🚀 메인 실행 파일 (Entry Point)
├── config.py               # ⚙️ API 키, 상수 설정
├── styles.py               # 🎨 전역 CSS 스타일
├── requirements.txt        # 📦 의존성 패키지 목록
│
├── .streamlit/
│   └── config.toml         # Streamlit 테마 설정
│
├── .env.example            # 환경변수 예시 (복사해서 .env로 사용)
│
├── data/
│   └── coffee_data.csv     # 한국 커피 수입 데이터
│
├── views/                  # 📄 각 화면(탭) 모듈
│   ├── __init__.py
│   ├── landing.py              # 🏠 홈 - 세계 산지 지도
│   ├── tab1_sourcing.py        # 📈 소싱 시그널 대시보드
│   ├── tab2_proposal.py        # 📝 제안서 생성기
│   ├── tab3_cost_calculator.py # 💰 원가 계산기
│   ├── tab4_news.py            # 📰 뉴스 인사이트
│   ├── tab5_trade_intel.py     # 📊 무역 인텔리전스
│   └── tab6_korean_market.py   # 🇰🇷 한국 시장 분석
│
└── utils/                  # 🔧 유틸리티 함수
    ├── __init__.py
    └── api_helpers.py          # API 호출 함수들
```

---

## 🚀 시작하기

### 1. 환경 설정

```bash
# 저장소 클론 또는 파일 다운로드 후
cd coffee_trade_hub

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 실제 API 키 입력
# - EXCHANGE_RATE: exchangerate-api.com
# - WEATHER_API_KEY: openweathermap.org
# - OPENAI_API_KEY: platform.openai.com
# - NAVER_CLIENT_ID/SECRET: developers.naver.com
```

### 3. 실행

```bash
streamlit run main.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📋 기능 설명

### 🏠 홈 (세계지도)
- 세계 커피 산지 대화형 지도
- 실시간 환율 및 커피 선물 시세
- 산지별 상세 정보 (HS코드, 필수 서류, 리드타임)

### 📈 소싱 시그널
- 시장 데이터 스냅샷 (Arabica, Robusta, 환율, 운임)
- 가격 추이 차트
- AI 기반 소싱 시그널 (신호등 시스템)
- CPO 실행 권고사항

### 📝 제안서 생성
- 산지/품종 선택
- 비용 자동 계산
- AI 전문가 의견 생성 (OpenAI)
- PDF/Excel 다운로드

### 💰 원가 계산기
- 인코텀즈별 비용 계산 (EXW, FOB, CFR, CIF, DDP)
- 관세/부가세 자동 산출
- Excel 결과 다운로드

### 📰 뉴스 인사이트
- Google RSS 해외 뉴스 수집
- 네이버 API 국내 뉴스 검색
- 감성 분석 및 워드클라우드
- 기사 자동 요약

### 📊 무역 인텔리전스
- 10개년 수입 통계 분석
- 관세 조회 시스템
- EUDR 컴플라이언스 분석
- AI 기반 공급망 리밸런싱 예측

### 🇰🇷 한국 시장 분석
- 연도별 수입량/수입액 추이
- 전년 대비 증가율 분석
- 주요 인사이트 메트릭

---

## 💡 개발자를 위한 팁

### 새 탭 추가하기

1. `views/` 폴더에 새 파일 생성 (예: `tab7_new_feature.py`)

```python
# views/tab7_new_feature.py
import streamlit as st

def show():
    """새 기능 페이지"""
    st.title("새로운 기능")
    st.write("내용 작성")
```

2. `main.py`의 `MENU_OPTIONS`에 추가:

```python
MENU_OPTIONS = {
    # ... 기존 메뉴들 ...
    "🆕 새 기능": "tab7_new_feature"
}
```

3. `render_selected_page()` 함수에 조건 추가:

```python
elif module_name == "tab7_new_feature":
    from views.tab7_new_feature import show
    show()
```

### 주의사항

- ⚠️ `st.set_page_config()`는 **main.py에서만** 호출하세요!
- ⚠️ 각 view 파일의 실행 코드는 반드시 `show()` 함수 안에 넣으세요.
- ⚠️ `.env` 파일은 절대 Git에 커밋하지 마세요.

---

## 👥 팀원

무역 AX 마스터 1기 "원조맛집" 팀

---

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
