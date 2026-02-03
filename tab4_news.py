import streamlit as st
import feedparser
import pandas as pd
from deep_translator import GoogleTranslator
from newspaper import Article, Config
import nltk
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests
import re 

# ==========================================
# 🔑 [필수] 네이버 API 키 입력
# ==========================================
# 네이버 개발자 센터에서 발급받은 키를 여기에 넣으세요.
NAVER_CLIENT_ID = "네이버 API ID"
NAVER_CLIENT_SECRET = "네이버 API 비밀번호"

# --- [초기 설정] ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# --- [스타일 적용] ---
st.markdown(
    """
    <style>
    .stApp { background-color: #FDFbf7; }
    h1, h2, h3, p, span, div, label, .stMarkdown, .stTab { color: #000000 !important; }
    button[data-baseweb="tab"] p { color: #000000 !important; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #F5F0E6; }
    div.stButton > button { background-color: #6F4E37; color: #FFFFFF !important; border-radius: 5px; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- [공통 함수] 번역 및 요약 ---
@st.cache_resource
def get_translator():
    return GoogleTranslator(source='auto', target='ko')

def translate_text(text):
    try:
        if not text: return ""
        translator = get_translator()
        return translator.translate(text[:4999])
    except:
        return text

def get_article_summary(url):
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        article = Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()
        summary = article.summary
        if not summary: return "⚠️ 요약 실패 (본문 추출 불가)"
        return summary 
    except Exception as e:
        return f"🚫 에러 발생: {str(e)}"

def analyze_sentiment(text):
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    if score > 0.1: return "🟢 긍정적"
    elif score < -0.1: return "🔴 부정적"
    else: return "⚪ 중립적"

def display_wordcloud(news_list):
    if not news_list: return
    text = " ".join([item['원제'] for item in news_list])
    wc = WordCloud(width=800, height=400, background_color='white', colormap='copper', max_words=80).generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# --- [핵심 함수 1] 구글 뉴스 수집 (해외용 - RSS) ---
def fetch_google_news(query, target_keywords=None, period='30d'):
    # 노이즈 필터
    noise_filter = "-Starbucks -store -closing -opened -travel -vacation -hotel -resort -tourism -trip -guide -rice -voting -election -visa -immigration"
    full_query = f"{query} {noise_filter}"
    encoded_query = full_query.replace(" ", "%20")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:{period}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    seen_titles = set()
    # 커피 문맥 필터
    coffee_guard_terms = ["coffee", "bean", "arabica", "robusta", "commodity", "harvest", "crop", "farm", "roast", "export", "production"]

    if not feed.entries: return []

    count = 0
    # 1년치 데이터도 처리할 수 있게 100개까지 탐색
    for entry in feed.entries[:100]:
        if count >= 50: break # 분석용 최대 50개
        
        title_en = entry.title
        link = entry.link
        summary_text = entry.get('summary', '') 
        title_signature = title_en[:30].lower()
        if title_signature in seen_titles: continue
        
        content_to_check = (title_en + " " + summary_text).lower()
        
        if target_keywords:
            has_target = any(k.lower() in content_to_check for k in target_keywords)
            has_coffee_context = any(term in content_to_check for term in coffee_guard_terms)
            if not (has_target and has_coffee_context): continue 

        seen_titles.add(title_signature)
        sentiment = analyze_sentiment(title_en)
        korean_title = translate_text(title_en)
        
        news_list.append({
            "제목": korean_title,
            "원제": title_en,
            "링크": link,
            "게시일": entry.published,
            "감성": sentiment
        })
        count += 1
    return news_list

# --- [핵심 함수 2] 네이버 뉴스 API (국내용 - OpenAPI) ---
def fetch_naver_news_api(query):
    if "본인의" in NAVER_CLIENT_ID:
        return [{"제목": "⚠️ API 키 미설정: 코드 상단에 키를 입력해주세요.", "링크": "#", "게시일": "", "언론사": "시스템"}]

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": 10, # 10개 출력
        "sort": "sim"  # 관련도순
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            items = response.json().get('items', [])
            results = []
            for item in items:
                # HTML 태그 제거 및 특수문자 변환
                clean_title = re.sub('<.*?>', '', item['title']).replace("&quot;", "'").replace("&amp;", "&")
                link = item['originallink'] if item['originallink'] else item['link']
                # 날짜 포맷 정리 (예: Mon, 02 Feb 2026...)
                pub_date = item['pubDate'][:16]
                
                results.append({
                    "제목": clean_title,
                    "링크": link,
                    "게시일": pub_date,
                    "언론사": "네이버뉴스" # API는 언론사명을 직접 안줘서 통일
                })
            return results
        else:
            return [{"제목": f"⚠️ 통신 오류 (Code: {response.status_code})", "링크": "#", "게시일": "", "언론사": "오류"}]
    except Exception as e:
        return [{"제목": f"⚠️ 에러: {str(e)}", "링크": "#", "게시일": "", "언론사": "오류"}]

# ==========================================
# 🚀 메인 로직 (UI)
# ==========================================

st.title("☕ Global & Local 커피 인사이트")

# 세션 상태 초기화
if 'risk_news' not in st.session_state: st.session_state['risk_news'] = []
if 'origin_news' not in st.session_state: st.session_state['origin_news'] = []
if 'korea_news' not in st.session_state: st.session_state['korea_news'] = []
if 'summary_cache' not in st.session_state: st.session_state['summary_cache'] = {}

tab1, tab2, tab3 = st.tabs(["🔥 글로벌 리스크", "🌍 산지별 동향", "🇰🇷 국내 시장 뉴스"])

# --- [Tab 1] 글로벌 리스크 (Google) ---
with tab1:
    st.subheader("글로벌 공급망 & 정책 리스크")
    
    # 🔥 [수정] 데이터가 비어있으면(첫 실행 시) 자동으로 검색 실행
    if not st.session_state['risk_news']:
        with st.spinner('최신 글로벌 리스크 뉴스를 자동으로 분석 중입니다...'):
            q = "Coffee Supply Chain OR EUDR Regulation OR Red Sea Logistics"
            targets = ["Coffee", "EUDR", "Red Sea", "Supply", "Logistics", "Price", "Regulation"]
            st.session_state['risk_news'] = fetch_google_news(q, targets, period='365d')

    # 🔥 [수정] 수동 새로고침 버튼 (이미 데이터가 있어도 강제로 다시 불러옴)
    if st.button("🔄 뉴스 새로고침", key="btn_risk_refresh"):
        with st.spinner('데이터를 다시 분석 중...'):
            q = "Coffee Supply Chain OR EUDR Regulation OR Red Sea Logistics"
            targets = ["Coffee", "EUDR", "Red Sea", "Supply", "Logistics", "Price", "Regulation"]
            st.session_state['risk_news'] = fetch_google_news(q, targets, period='365d')
            st.rerun() # 화면 즉시 갱신

    # 뉴스 출력 로직
    if st.session_state['risk_news']:
        display_wordcloud(st.session_state['risk_news'])
        st.divider()
        for i, item in enumerate(st.session_state['risk_news'][:10]):
            with st.expander(f"[{item['감성']}] {item['제목']}"):
                st.caption(item['게시일'])
                st.write(f"원제: {item['원제']}")
                st.markdown(f"[기사 보기]({item['링크']})")
                if st.button("요약 (영문 기사)", key=f"risk_{i}"):
                    summary = get_article_summary(item['링크'])
                    st.success(translate_text(summary))

# --- [Tab 2] 산지별 동향 (Google) ---
with tab2:
    st.subheader("주요 산지별 동향")
    country = st.selectbox("국가 선택", ["Brazil", "Vietnam", "Colombia", "Ethiopia", "Indonesia", "Kenya", "Honduras", "Guatemala", "Costa Rica", "Peru"])
    
    def get_params(c):
        if c == "Vietnam": return '"Vietnam Coffee" (Export OR Production OR Price)', ["Vietnam", "Robusta"]
        elif c == "Brazil": return '"Brazil Coffee" (Harvest OR Export OR Crop)', ["Brazil", "Arabica"]
        else: return f'"{c} Coffee" (Export OR Price)', [c]

    if st.button(f"{country} 뉴스 검색 (Google)", key="btn_origin"):
        with st.spinner('해외 뉴스 데이터 분석 중...'):
            query, targets = get_params(country)
            period = '365d' if country in ["Guatemala", "Costa Rica", "Peru", "Honduras", "Kenya"] else '90d'
            st.session_state['origin_news'] = fetch_google_news(query, targets, period=period)
            
    if st.session_state['origin_news']:
        display_wordcloud(st.session_state['origin_news'])
        st.divider()
        for i, item in enumerate(st.session_state['origin_news'][:10]):
            with st.expander(f"[{item['감성']}] {item['제목']}"):
                st.caption(item['게시일'])
                st.write(f"원제: {item['원제']}")
                st.markdown(f"[기사 보기]({item['링크']})")
                if st.button("요약 (영문 기사)", key=f"origin_{i}"):
                    summary = get_article_summary(item['링크'])
                    st.success(translate_text(summary))

# --- [Tab 3] 국내 뉴스 (Naver API) ---
with tab3:
    st.subheader("🇰🇷 국내 커피 시장 & 원두 뉴스")
    
    # API 키 확인 메시지
    if "본인의" in NAVER_CLIENT_ID:
        st.warning("⚠️ 네이버 API 키가 입력되지 않았습니다. 코드 상단을 확인해주세요!")
    
    korea_keyword = st.radio("관심 키워드 선택", ["커피 원두 가격", "생두 수입", "카페 창업 시장", "스페셜티 커피", "저가 커피 프랜차이즈"], horizontal=True)
    
    if st.button("국내 뉴스 검색 (Naver API)", key="btn_korea"):
        with st.spinner(f"네이버에서 '{korea_keyword}' 관련 뉴스를 가져옵니다..."):
            st.session_state['korea_news'] = fetch_naver_news_api(korea_keyword)
            
    if st.session_state['korea_news']:
        st.success(f"검색 결과 {len(st.session_state['korea_news'])}건")
        for i, item in enumerate(st.session_state['korea_news']):
            with st.container():
                st.markdown(f"**{i+1}. {item['제목']}**")
                st.caption(f"📅 {item['게시일']}")
                st.markdown(f"[기사 원문 읽기]({item['링크']})")
                st.divider()