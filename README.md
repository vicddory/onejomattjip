# ☕ Coffee AX Master Hub

> 글로벌 커피 무역 인텔리전스 플랫폼 | Global Coffee Trade Intelligence Platform

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [환경 변수 설정](#-환경-변수-설정)
- [사용 가이드](#-사용-가이드)
- [기술 스택](#-기술-스택)
- [API 키 발급 가이드](#-api-키-발급-가이드)
- [팀 정보](#-팀-정보)
- [라이선스](#-라이선스)

---

## 🎯 프로젝트 소개

**Coffee AX Master Hub**는 커피 무역업계 종사자를 위한 올인원 인텔리전스 플랫폼입니다. 
실시간 시장 데이터, 환율 분석, 원가 계산, 뉴스 수집, 전략 분석 등 커피 무역에 필요한 
모든 정보를 하나의 대시보드에서 제공합니다.

### 💡 핵심 가치

- 🌍 **글로벌 인사이트**: 주요 커피 산지의 실시간 정보와 환율 분석
- 📊 **데이터 기반 의사결정**: 아라비카/로부스타 선물 시장 분석 및 매수 신호
- 💰 **정확한 원가 계산**: 인코텀즈별 수입 원가 자동 계산
- 🤖 **AI 지원**: OpenAI 기반 맞춤형 제안서 자동 생성
- 📰 **실시간 뉴스**: 글로벌 및 국내 커피 시장 뉴스 자동 수집

---

## ✨ 주요 기능

### 1. 🌍 산지 지도 (Landing Page)
- 세계 주요 커피 생산국 인터랙티브 지도
- 국가별 실시간 환율 조회 (1년/5년/10년/전체 기간)
- 산지별 무역 정보 (HS코드, 선적항, 리드타임, 필수 서류)
- ICE Arabica 선물 시세 실시간 모니터링

### 2. 📊 시장 대시보드
- 아라비카 (KC=F) / 로부스타 (RC=F) 선물 가격 추이
- 기술적 분석 기반 매수/매도 신호 제공
- 이동평균선(MA) 기반 추세 분석
- 가격 변동성 및 거래량 분석

### 3. 🌿 원두 품종 분석
- 10개 주요 산지별 원두 특성 비교
- 품종별 상세 정보 (향미, 산미, 바디감 등)
- OpenAI 기반 맞춤형 제안서 자동 생성
- PDF 형식 제안서 다운로드

### 4. 🧮 원가 계산기
- 5가지 인코텀즈 지원 (EXW, FOB, CFR, CIF, DDP)
- 실시간 환율 적용 또는 수동 입력
- 관세/부가세 자동 계산
- Excel 형식 원가 분석표 다운로드
- 과세가격(CIF) 자동 산출

### 5. 📰 뉴스 인사이트
- **글로벌 리스크**: 공급망, EUDR 규제, 물류 리스크 뉴스
- **산지별 동향**: 10개국 커피 생산 및 수출 뉴스
- **국내 시장**: 네이버 API 기반 한국 커피 시장 뉴스
- 감성 분석 및 워드클라우드 시각화
- 기사 요약 기능 (영문 기사 자동 번역)

### 6. 📈 전략 분석
- FTA 활용 전략 및 관세율 비교
- 국가별 관세 시뮬레이션
- 기후 리밸런싱 전략 (산지 다변화)
- 무역 최적화 시나리오 분석

### 7. 🇰🇷 국내 시장 분석
- 한국 커피 수입량/수입액 연도별 추이
- 전년 대비 증가율 분석
- 평균 수입 단가 추정
- 시장 규모 및 성장률 인사이트

---

## 📁 프로젝트 구조

```
coffee_app/
│
├── 📄 main.py                      # 메인 진입점 (streamlit run main.py)
├── 📄 requirements.txt             # 필요 라이브러리 목록
├── 📄 .env.example                # 환경 변수 템플릿
├── 📄 .env                        # 실제 API 키 (git ignore)
├── 📄 README.md                   # 프로젝트 문서
│
├── 📂 data/
│   └── 📊 coffee_data.csv         # 한국 커피 수입 통계 데이터
│
└── 📂 tabs/                        # 각 기능별 모듈
    ├── 📄 __init__.py              # 패키지 초기화
    ├── 🌍 tab_landing.py           # Home - 산지 지도
    ├── 📊 tab1_dashboard.py        # Dashboard - 시장 신호
    ├── 🌿 tab2_coffeebeans.py      # Bean Analysis - 품종 분석
    ├── 🧮 tab3_costcal.py          # Cost Calculator - 원가 계산
    ├── 📰 tab4_news.py             # News - 뉴스 인사이트
    ├── 📈 tab5_strategy.py         # Strategy - 전략 분석
    └── 🇰🇷 tab6_korean_coffee.py   # Korean Market - 국내 시장
```

---

## 🚀 설치 및 실행

### 📋 시스템 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- 인터넷 연결 (API 호출 및 데이터 수집)

### 1️⃣ 저장소 클론

```bash
git clone https://github.com/your-username/coffee-ax-hub.git
cd coffee-ax-hub
```

### 2️⃣ 가상환경 생성 및 활성화 (권장)

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ 의존성 설치

```bash
pip install -r requirements.txt
```

### 4️⃣ 환경 변수 설정

```bash
# .env.example 파일을 .env로 복사
cp .env.example .env

# .env 파일을 편집기로 열어 API 키 입력
nano .env  # 또는 vim, code 등
```

### 5️⃣ 애플리케이션 실행

```bash
streamlit run main.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱을 확인할 수 있습니다.

---

## 🔑 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 API 키를 입력하세요:

```env
# ==========================================
# Coffee AX Master Hub - Environment Variables
# ==========================================

# Exchange Rate API (환율 조회)
EXCHANGE_RATE=your_exchange_rate_api_key_here

# OpenWeather API (날씨 정보)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# OpenAI API (AI 제안서 생성)
OPENAI_API_KEY=your_openai_api_key_here

# Naver Search API (국내 뉴스)
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here
```

---

## 📖 사용 가이드

### 홈 화면 네비게이션

앱 실행 시 홈 화면에서 7개의 주요 기능 카드가 표시됩니다.
원하는 기능을 클릭하여 해당 페이지로 이동할 수 있습니다.

### 각 탭 사용법

#### 🌍 산지 지도
1. 지도에서 커피 생산국 아이콘 클릭
2. 우측 패널에서 해당 국가의 상세 정보 확인
3. 환율 추이 그래프에서 기간 선택 (1y, 5y, 10y, max)

#### 📊 시장 대시보드
1. 아라비카/로부스타 선물 가격 차트 확인
2. 이동평균선 기반 매수/매도 신호 참고
3. 기간별 수익률 비교

#### 🌿 원두 품종 분석
1. 드롭다운에서 산지 선택
2. 원두 특성 및 상세 정보 확인
3. "AI 제안서 생성" 버튼 클릭
4. 생성된 PDF 다운로드

#### 🧮 원가 계산기
1. 인코텀즈 선택 (EXW, FOB, CFR, CIF, DDP)
2. 물품대금, 운송비, 보험료 입력
3. 관세율 및 국내 발생비용 입력
4. "계산 결과 보기" 클릭
5. 엑셀 파일 다운로드

#### 📰 뉴스 인사이트
- **글로벌 리스크**: "리스크 뉴스 검색" 버튼 클릭
- **산지별 동향**: 국가 선택 후 "뉴스 검색" 클릭
- **국내 시장**: 키워드 선택 후 "국내 뉴스 검색" 클릭

#### 📈 전략 분석
1. FTA 체결국 관세율 비교표 확인
2. 국가별 관세 시뮬레이션
3. 기후 리밸런싱 전략 시나리오 검토

#### 🇰🇷 국내 시장 분석
- 연도별 수입량/수입액 그래프 확인
- 전년 대비 증가율 추이 분석
- 주요 인사이트 메트릭 확인

---

## 🛠 기술 스택

### Frontend & Framework
- **Streamlit** 1.28+ - 웹 애플리케이션 프레임워크
- **Plotly** 5.18+ - 인터랙티브 차트 라이브러리
- **Folium** 0.14+ - 지도 시각화
- **Matplotlib** - 정적 그래프

### Data Processing
- **Pandas** 2.0+ - 데이터 분석 및 처리
- **NumPy** 1.24+ - 수치 계산
- **yfinance** - 금융 데이터 (선물 가격)

### AI & NLP
- **OpenAI API** - GPT 기반 제안서 생성
- **TextBlob** - 감성 분석
- **NLTK** - 자연어 처리
- **Deep Translator** - 자동 번역
- **Newspaper3k** - 기사 크롤링 및 요약

### External APIs
- **Exchange Rate API** - 실시간 환율
- **OpenWeather API** - 날씨 정보
- **Naver Search API** - 국내 뉴스
- **Google News RSS** - 글로벌 뉴스

### Document Generation
- **ReportLab** - PDF 생성
- **OpenPyXL** - Excel 파일 생성
- **XlsxWriter** - 고급 Excel 서식

### Utilities
- **python-dotenv** - 환경 변수 관리
- **requests** - HTTP 통신
- **feedparser** - RSS 파싱
- **wordcloud** - 워드클라우드 시각화

---

## 🔐 API 키 발급 가이드

### 1. Exchange Rate API
1. [Exchange Rate API](https://www.exchangerate-api.com/) 접속
2. "Get Free Key" 클릭
3. 이메일 인증 후 API 키 복사
4. **무료 플랜**: 월 1,500회 요청 가능

### 2. OpenWeather API
1. [OpenWeather](https://openweathermap.org/api) 접속
2. 회원가입 후 API Keys 메뉴 이동
3. API 키 생성
4. **무료 플랜**: 분당 60회 요청 가능

### 3. OpenAI API
1. [OpenAI Platform](https://platform.openai.com/) 접속
2. 회원가입 후 API Keys 생성
3. **주의**: 유료 서비스 (사용량 기반 과금)
4. 초기 크레딧 제공 (신규 가입 시)

### 4. Naver Search API
1. [네이버 개발자센터](https://developers.naver.com/) 접속
2. 애플리케이션 등록
3. "검색" API 추가
4. Client ID / Client Secret 발급
5. **무료 플랜**: 일 25,000회 요청 가능

---

## 👥 팀 정보

### 프로젝트 팀
- **조성빈** - Lead Developer
- **강정민** - Data Analyst & Developer

### 과정
무역 AX 마스터 1기 (2026)

### 연락처
- 📧 Email: your-email@example.com
- 🔗 GitHub: [github.com/your-username](https://github.com/your-username)

---

## 📝 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 감사의 말

- Streamlit 커뮤니티
- Anthropic Claude
- OpenAI
- 네이버 개발자센터
- Exchange Rate API
- OpenWeather
- 모든 오픈소스 기여자들

---

## 📞 문의 및 기여

버그 리포트, 기능 제안, 또는 기여를 원하시면 
[GitHub Issues](https://github.com/your-username/coffee-ax-hub/issues)를 통해 연락주세요.

---

<div align="center">

**Made with ☕ and ❤️ by Coffee AX Team**

⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!

</div>
