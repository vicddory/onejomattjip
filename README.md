# ☕ Coffee Trade Hub

> **글로벌 원두 무역을 위한 올인원 데이터 분석 플랫폼**

무역 AX 마스터 1기 **"원조맛집"** 팀 프로젝트

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-Educational-green)

---

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [프로젝트 구조](#-프로젝트-구조)
- [시작하기](#-시작하기)
- [API 키 설정](#-api-키-설정)
- [기능 상세](#-기능-상세)
- [개발자 가이드](#-개발자-가이드)
- [기술 스택](#-기술-스택)
- [팀 정보](#-팀-정보)

---

## 🎯 프로젝트 소개

**Coffee Trade Hub**는 커피 무역 실무자를 위한 종합 데이터 분석 플랫폼입니다.

실시간 시세 모니터링부터 AI 기반 제안서 생성까지, 원두 수입에 필요한 모든 정보와 도구를 하나의 대시보드에서 제공합니다.

### 핵심 가치

| 🌍 글로벌 데이터 | 💰 비용 최적화 | 🤖 AI 인사이트 | 📊 시각화 |
|:---:|:---:|:---:|:---:|
| 10개 주요 산지 실시간 정보 | 인코텀즈별 원가 계산 | GPT 기반 시장 분석 | 대화형 차트 & 지도 |

---

## ✨ 주요 기능

### 🗺️ 세계 원두 산지 지도
- 10개 주요 커피 산지 대화형 지도
- 실시간 USD/KRW 환율 및 ICE Arabica 선물 시세
- 산지별 HS코드, 선적항, 리드타임, 필수 서류 정보

### 📈 소싱 시그널 대시보드
- 시장 데이터 스냅샷 (Arabica, Robusta, 환율, 운임지수)
- 기간별 선물 가격 추이 차트 (1일~3년)
- 신호등 시스템 기반 소싱 시그널
- AI 알고리즘 기반 CPO 실행 권고사항

### 📝 AI 제안서 생성기
- 산지/품종 선택 기반 자동 비용 산출
- OpenAI GPT를 활용한 전문가 의견 생성
- PDF/Excel 형식 다운로드 지원
- 실시간 날씨 및 환율 정보 연동

### 💰 수입 원가 계산기
- 5가지 인코텀즈 지원 (EXW, FOB, CFR, CIF, DDP)
- 관세 및 부가세 자동 계산
- 실시간/수동 환율 설정
- Excel 결과 리포트 다운로드

### 📰 뉴스 큐레이션
- Google RSS 기반 글로벌 커피 뉴스
- 네이버 API 국내 뉴스 검색
- TextBlob 감성 분석 및 워드클라우드
- newspaper3k 기사 자동 요약

### 📊 무역 인텔리전스
- 10개년 국가별 수입 통계 분석
- HS코드 기반 관세 조회 시스템
- EUDR 컴플라이언스 분석
- AI 기반 공급망 리밸런싱 시뮬레이션

### 🇰🇷 한국 시장 분석
- 연도별 수입량/수입액 트렌드
- 전년 대비 증가율 비교 분석
- 주요 인사이트 메트릭 카드

---

## 📁 프로젝트 구조

```
coffee_trade_hub/
│
├── main.py                     # 🚀 메인 실행 파일 (Entry Point)
├── config.py                   # ⚙️ API 키, 색상 상수, 산지 데이터
├── styles.py                   # 🎨 전역 CSS 스타일
├── requirements.txt            # 📦 의존성 패키지 목록
│
├── .streamlit/
│   └── config.toml             # Streamlit 테마 설정
│
├── .env.example                # 환경변수 예시 파일
├── .gitignore                  # Git 제외 파일 목록
│
├── data/
│   └── coffee_data.csv         # 한국 커피 수입 통계 데이터
│
├── views/                      # 📄 각 화면(탭) 모듈
│   ├── __init__.py
│   ├── landing.py              # 🏠 홈 - 세계 산지 지도
│   ├── tab1_sourcing.py        # 📈 소싱 시그널 대시보드
│   ├── tab2_proposal.py        # 📝 제안서 생성기
│   ├── tab3_cost_calculator.py # 💰 원가 계산기
│   ├── tab4_news.py            # 📰 뉴스 큐레이션
│   ├── tab5_trade_intel.py     # 📊 무역 인텔리전스
│   └── tab6_korean_market.py   # 🇰🇷 한국 시장 분석
│
└── utils/                      # 🔧 유틸리티 함수
    ├── __init__.py
    └── api_helpers.py          # API 호출 함수 (환율, 날씨, 시세)
```

---

## 🚀 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/your-repo/coffee_trade_hub.git
cd coffee_trade_hub
```

### 2. 가상환경 설정 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 실제 API 키 입력
```

### 5. 앱 실행

```bash
streamlit run main.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 🔑 API 키 설정

`.env` 파일에 다음 API 키들을 설정하세요:

| API | 용도 | 발급처 |
|-----|------|--------|
| `EXCHANGE_RATE` | 실시간 환율 | [exchangerate-api.com](https://www.exchangerate-api.com/) |
| `WEATHER_API_KEY` | 산지 날씨 정보 | [openweathermap.org](https://openweathermap.org/api) |
| `OPENAI_API_KEY` | AI 분석 및 제안서 생성 | [platform.openai.com](https://platform.openai.com/api-keys) |
| `NAVER_CLIENT_ID` | 국내 뉴스 검색 | [developers.naver.com](https://developers.naver.com/) |
| `NAVER_CLIENT_SECRET` | 국내 뉴스 검색 | [developers.naver.com](https://developers.naver.com/) |

```env
# .env 파일 예시
EXCHANGE_RATE=your_api_key_here
WEATHER_API_KEY=your_api_key_here
OPENAI_API_KEY=sk-your_api_key_here
NAVER_CLIENT_ID=your_client_id_here
NAVER_CLIENT_SECRET=your_client_secret_here
```

> ⚠️ **주의**: `.env` 파일은 절대 Git에 커밋하지 마세요!

---

## 📖 기능 상세

### 🗺️ 홈 (세계 산지 지도)

| 기능 | 설명 |
|------|------|
| 대화형 지도 | Folium 기반 커피 산지 마커 클릭 |
| 실시간 시세 | USD/KRW 환율, ICE Arabica 선물가 |
| 산지 상세정보 | HS코드, 선적항, 리드타임, 필수 서류 |
| 환율 히스토리 | 1년/5년/10년/전체 기간 차트 |

### 📈 소싱 시그널

| 지표 | 데이터 소스 |
|------|------------|
| Arabica | Yahoo Finance (KC=F) |
| Robusta | 추정치 (Arabica 기반) |
| USD/KRW | Yahoo Finance (KRW=X) |
| 운임지수 | Shanghai Freight Index |

**신호등 시스템**:
- 🟢 매수 적기 (가격 하락)
- 🟡 관망 (변동 적음)
- 🔴 주의 (가격 급등)

### 💰 원가 계산기

**지원 인코텀즈**:

| 조건 | 포함 비용 | 매도인 위험 |
|------|----------|------------|
| EXW | 물품대금만 | 최소 |
| FOB | + 수출통관 | 본선적재까지 |
| CFR | + 운임 | 본선적재까지 |
| CIF | + 운임 + 보험 | 본선적재까지 |
| DDP | 전체 비용 | 최대 |

---

## 👨‍💻 개발자 가이드

### 새 탭 추가하기

1. **뷰 파일 생성**

```python
# views/tab7_new_feature.py
import streamlit as st

def show():
    """새 기능 페이지"""
    st.title("새로운 기능")
    st.write("내용을 작성하세요")
```

2. **main.py에 메뉴 추가**

```python
MENU_OPTIONS = {
    # ... 기존 메뉴들 ...
    "새 기능": "tab7_new_feature"
}
```

3. **render_selected_page() 함수에 조건 추가**

```python
elif module_name == "tab7_new_feature":
    from views.tab7_new_feature import show
    show()
```

### 주의사항

| ⚠️ 규칙 | 설명 |
|---------|------|
| `st.set_page_config()` | **main.py에서만** 1회 호출 |
| `show()` 함수 | 모든 뷰 파일은 반드시 `show()` 함수 포함 |
| `.env` 파일 | 절대 Git에 커밋 금지 |
| CSS 스타일 | `styles.py`에서 통합 관리 |

### 코드 컨벤션

- 파일 인코딩: UTF-8 (`# -*- coding: utf-8 -*-`)
- 독스트링: 모든 함수에 설명 포함
- 타입 힌트: 가능한 모든 곳에 적용
- 에러 처리: try-except로 폴백 처리

---

## 🛠️ 기술 스택

### 프레임워크
- **Streamlit** - 웹 애플리케이션 프레임워크

### 데이터 처리
- **Pandas** - 데이터 분석
- **NumPy** - 수치 연산

### 시각화
- **Plotly** - 대화형 차트
- **Folium** - 대화형 지도
- **Matplotlib** - 워드클라우드

### API 연동
- **yfinance** - 금융 데이터
- **requests** - HTTP 요청
- **feedparser** - RSS 파싱

### AI/NLP
- **OpenAI** - GPT API
- **TextBlob** - 감성 분석
- **newspaper3k** - 기사 추출
- **deep-translator** - 번역

### 문서 생성
- **ReportLab** - PDF 생성
- **openpyxl** - Excel 생성

---

## 👥 팀 정보

**무역 AX 마스터 1기 "원조맛집" 팀**

---

## 📄 라이선스

이 프로젝트는 **교육 목적**으로 제작되었습니다.

---

<div align="center">

Made with ☕ by **원조맛집** Team

</div>
