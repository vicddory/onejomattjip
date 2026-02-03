# ☕ Coffee AX Master Hub

글로벌 커피 무역 인텔리전스 대시보드

## 📁 프로젝트 구조

```
coffee_app/
├── main.py                 # 메인 진입점 (streamlit run main.py)
├── requirements.txt        # 필요한 라이브러리
├── .env.example           # 환경 변수 템플릿
├── .env                   # 실제 API 키 (생성 필요)
├── data/
│   └── coffee_data.csv    # 한국 커피 수입 데이터
└── tabs/
    ├── __init__.py
    ├── tab_landing.py     # 🏠 Home - 글로벌 산지 지도
    ├── tab1_dashboard.py  # 📊 Dashboard - 시장 신호 분석
    ├── tab2_coffeebeans.py # 🌿 Bean Analysis - 품종 분석
    ├── tab3_costcal.py    # 🧮 Cost Calculator - 원가 계산
    ├── tab4_news.py       # 📰 News - 뉴스 인사이트
    ├── tab5_strategy.py   # 📈 Strategy - 전략 분석
    └── tab6_korean_coffee.py # 🇰🇷 Korean Market - 국내 시장
```

## 🚀 설치 및 실행

### 1. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 API 키 입력
```

### 4. 실행
```bash
streamlit run main.py
```

## 🔑 필요한 API 키

| API | 용도 | 발급 링크 |
|-----|------|----------|
| Exchange Rate API | 실시간 환율 | https://www.exchangerate-api.com/ |
| OpenWeather API | 산지 날씨 | https://openweathermap.org/api |
| OpenAI API | AI 분석 | https://platform.openai.com/ |
| Naver Search API | 국내 뉴스 | https://developers.naver.com/ |

## 📱 주요 기능

1. **Home (산지 지도)**: 세계 커피 산지 지도와 실시간 환율
2. **Dashboard (시장 신호)**: 아라비카/로부스타 선물 가격, 매수 신호
3. **Bean Analysis (품종 분석)**: 품종별 특성, AI 제안서 생성
4. **Cost Calculator (원가 계산)**: 인코텀즈별 수입 원가 계산
5. **News (뉴스)**: 글로벌/국내 커피 뉴스 수집
6. **Strategy (전략)**: FTA, 관세, 기후 리밸런싱 분석
7. **Korean Market (국내)**: 한국 커피 수입 트렌드

## 👥 팀원
- 조성빈
- 강정민

## 📅 프로젝트
무역 AX 마스터 1기 (2026)
