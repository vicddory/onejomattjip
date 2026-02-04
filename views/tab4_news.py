# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab4_news.py - 글로벌 & 로컬 커피 뉴스 인사이트
================================================================================
Google RSS와 네이버 API를 활용한 커피 관련 뉴스 수집 및 분석
================================================================================
"""

import streamlit as st
import feedparser
import requests
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from deep_translator import GoogleTranslator
from newspaper import Article, Config
import nltk

# 경로 설정
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

# NLTK 데이터 다운로드 (최초 1회)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


# ===========================================
# 유틸리티 함수
# ===========================================
@st.cache_resource
def get_translator():
    return GoogleTranslator(source='auto', target='ko')


def translate_text(text):
    """텍스트를 한국어로 번역"""
    try:
        if not text:
            return ""
        translator = get_translator()
        return translator.translate(text[:4999])
    except:
        return text


def get_article_summary(url):
    """뉴스 기사 요약"""
    try:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        config.request_timeout = 10
        article = Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()
        return article.summary if article.summary else "⚠️ 요약 실패"
    except Exception as e:
        return f"🚫 에러: {str(e)}"


def analyze_sentiment(text):
    """감성 분석"""
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    if score > 0.1:
        return "🟢 긍정적"
    elif score < -0.1:
        return "🔴 부정적"
    return "⚪ 중립적"


def display_wordcloud(news_list):
    """워드클라우드 표시"""
    if not news_list:
        return
    text = " ".join([item.get('원제', '') for item in news_list])
    if not text.strip():
        return
    
    try:
        wc = WordCloud(width=800, height=400, background_color='white', colormap='copper', max_words=80).generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        plt.close(fig)
    except:
        st.warning("워드클라우드 생성 실패")


# ===========================================
# Google 뉴스 수집 (해외)
# ===========================================
def fetch_google_news(query, target_keywords=None, period='30d'):
    """Google RSS로 해외 뉴스 수집"""
    noise_filter = "-Starbucks -store -closing -travel -hotel"
    full_query = f"{query} {noise_filter}"
    encoded_query = full_query.replace(" ", "%20")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:{period}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    seen_titles = set()
    coffee_guard_terms = ["coffee", "bean", "arabica", "robusta", "commodity", "harvest", "crop", "farm", "export"]

    if not feed.entries:
        return []

    count = 0
    for entry in feed.entries[:100]:
        if count >= 30:
            break
        
        title_en = entry.title
        link = entry.link
        summary_text = entry.get('summary', '')
        title_signature = title_en[:30].lower()
        
        if title_signature in seen_titles:
            continue
        
        content_to_check = (title_en + " " + summary_text).lower()
        
        if target_keywords:
            has_target = any(k.lower() in content_to_check for k in target_keywords)
            has_coffee_context = any(term in content_to_check for term in coffee_guard_terms)
            if not (has_target and has_coffee_context):
                continue

        seen_titles.add(title_signature)
        sentiment = analyze_sentiment(title_en)
        korean_title = translate_text(title_en)
        
        news_list.append({
            "제목": korean_title,
            "원제": title_en,
            "링크": link,
            "게시일": entry.get('published', ''),
            "감성": sentiment
        })
        count += 1
    
    return news_list


# ===========================================
# 네이버 뉴스 API (국내)
# ===========================================
def fetch_naver_news_api(query):
    """네이버 API로 국내 뉴스 수집"""
    if "네이버" in NAVER_CLIENT_ID or not NAVER_CLIENT_ID:
        return [{"제목": "⚠️ API 키 미설정: config.py에 키를 입력하세요.", "링크": "#", "게시일": "", "언론사": "시스템"}]

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": 10, "sort": "sim"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            items = response.json().get('items', [])
            results = []
            for item in items:
                clean_title = re.sub('<.*?>', '', item['title']).replace("&quot;", "'").replace("&amp;", "&")
                link = item.get('originallink') or item.get('link')
                pub_date = item.get('pubDate', '')[:16]
                
                results.append({
                    "제목": clean_title,
                    "링크": link,
                    "게시일": pub_date,
                    "언론사": "네이버뉴스"
                })
            return results
        return [{"제목": f"⚠️ 통신 오류 (Code: {response.status_code})", "링크": "#", "게시일": "", "언론사": "오류"}]
    except Exception as e:
        return [{"제목": f"⚠️ 에러: {str(e)}", "링크": "#", "게시일": "", "언론사": "오류"}]


# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """뉴스 인사이트 페이지를 렌더링합니다."""
    
    st.markdown("<h1 style='text-align: center;'>글로벌 & 로컬 커피 인사이트</h1>", unsafe_allow_html=True)
    st.divider()

    # 세션 상태 초기화
    if 'risk_news' not in st.session_state:
        st.session_state['risk_news'] = []
    if 'origin_news' not in st.session_state:
        st.session_state['origin_news'] = []
    if 'korea_news' not in st.session_state:
        st.session_state['korea_news'] = []

    tab1, tab2, tab3 = st.tabs([" 글로벌 리스크", " 산지별 동향", " 국내 시장"])

    # ===========================================
    # Tab 1: 글로벌 리스크
    # ===========================================
    with tab1:
        st.subheader("글로벌 공급망 & 정책 리스크")
        
        if st.button("리스크 뉴스 검색 (Google)", key="btn_risk"):
            with st.spinner('해외 뉴스 분석 중...'):
                q = "Coffee Supply Chain OR EUDR Regulation OR Red Sea Logistics"
                targets = ["Coffee", "EUDR", "Red Sea", "Supply", "Logistics", "Price"]
                st.session_state['risk_news'] = fetch_google_news(q, targets, period='365d')
                
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

    # ===========================================
    # Tab 2: 산지별 동향
    # ===========================================
    with tab2:
        st.subheader("주요 산지별 동향")
        country = st.selectbox("국가 선택", ["Brazil", "Vietnam", "Colombia", "Ethiopia", "Indonesia", "Kenya"], key="news_country")
        
        def get_params(c):
            if c == "Vietnam":
                return '"Vietnam Coffee" (Export OR Production)', ["Vietnam", "Robusta"]
            elif c == "Brazil":
                return '"Brazil Coffee" (Harvest OR Export)', ["Brazil", "Arabica"]
            else:
                return f'"{c} Coffee" (Export OR Price)', [c]

        if st.button(f"{country} 뉴스 검색", key="btn_origin"):
            with st.spinner('뉴스 분석 중...'):
                query, targets = get_params(country)
                st.session_state['origin_news'] = fetch_google_news(query, targets, period='90d')
                
        if st.session_state['origin_news']:
            display_wordcloud(st.session_state['origin_news'])
            st.divider()
            for i, item in enumerate(st.session_state['origin_news'][:10]):
                with st.expander(f"[{item['감성']}] {item['제목']}"):
                    st.caption(item['게시일'])
                    st.write(f"원제: {item['원제']}")
                    st.markdown(f"[기사 보기]({item['링크']})")
                    if st.button("요약", key=f"origin_{i}"):
                        summary = get_article_summary(item['링크'])
                        st.success(translate_text(summary))

    # ===========================================
    # Tab 3: 국내 뉴스 (네이버 API)
    # ===========================================
    with tab3:
        st.subheader("국내 커피 시장 & 원두 뉴스")
        
        if "네이버" in NAVER_CLIENT_ID:
            st.warning("⚠️ 네이버 API 키가 입력되지 않았습니다. config.py를 확인하세요!")
        
        korea_keyword = st.radio(
            "관심 키워드 선택", 
            ["커피 원두 가격", "생두 수입", "카페 창업 시장", "스페셜티 커피", "저가 커피 프랜차이즈"], 
            horizontal=True,
            key="korea_keyword"
        )
        
        if st.button("국내 뉴스 검색 (Naver API)", key="btn_korea"):
            with st.spinner(f"'{korea_keyword}' 뉴스 검색 중..."):
                st.session_state['korea_news'] = fetch_naver_news_api(korea_keyword)
                
        if st.session_state['korea_news']:
            st.success(f"검색 결과 {len(st.session_state['korea_news'])}건")
            for i, item in enumerate(st.session_state['korea_news']):
                with st.container():
                    st.markdown(f"**{i+1}. {item['제목']}**")
                    st.caption(f" {item['게시일']}")
                    st.markdown(f"[기사 원문 읽기]({item['링크']})")
                    st.divider()


if __name__ == "__main__":
    show()
