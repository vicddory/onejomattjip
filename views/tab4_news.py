# -*- coding: utf-8 -*-
"""
================================================================================
📁 views/tab4_news.py - 글로벌 & 로컬 커피 뉴스 인사이트 (Optimized v2)
================================================================================
Google RSS와 네이버 API를 활용한 커피 관련 뉴스 수집 및 분석
- 병렬 처리를 통한 성능 최적화
- 실시간 진행률 표시
- 이미지 제거 및 텍스트 중심 깔끔한 레이아웃
- 글로벌 리스크 탭 버그 수정
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import time

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


def translate_text(text: str) -> str:
    """텍스트를 한국어로 번역"""
    try:
        if not text:
            return ""
        translator = get_translator()
        return translator.translate(text[:4999])
    except Exception as e:
        return text


def get_article_config() -> Config:
    """newspaper3k Config 객체 생성 (봇 탐지 회피)"""
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    config.request_timeout = 3
    config.MAX_TEXT = 200000
    return config


def analyze_sentiment(text: str) -> str:
    """감성 분석"""
    try:
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        if score > 0.1:
            return "🟢 긍정적"
        elif score < -0.1:
            return "🔴 부정적"
        return "⚪ 중립적"
    except:
        return "⚪ 중립적"


def display_wordcloud(news_list: List[Dict]):
    """워드클라우드 표시"""
    if not news_list:
        return
    text = " ".join([item.get('원제', '') for item in news_list])
    if not text.strip():
        return
    
    try:
        wc = WordCloud(
            width=800, 
            height=400, 
            background_color='white', 
            colormap='copper', 
            max_words=80
        ).generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.warning(f"워드클라우드 생성 실패: {str(e)}")


# ===========================================
# 병렬 처리 함수
# ===========================================
def process_single_news(entry: Dict, target_keywords: Optional[List[str]], 
                       coffee_guard_terms: List[str]) -> Optional[Dict]:
    """개별 뉴스 항목 처리 (병렬 실행용)"""
    try:
        title_en = entry.title
        link = entry.link
        summary_text = entry.get('summary', '')
        content_to_check = (title_en + " " + summary_text).lower()
        
        # 키워드 필터링
        if target_keywords:
            has_target = any(k.lower() in content_to_check for k in target_keywords)
            has_coffee_context = any(term in content_to_check for term in coffee_guard_terms)
            if not (has_target and has_coffee_context):
                return None
        
        # 감성 분석 및 번역
        sentiment = analyze_sentiment(title_en)
        korean_title = translate_text(title_en)
        
        return {
            "제목": korean_title,
            "원제": title_en,
            "링크": link,
            "게시일": entry.get('published', '')[:16],
            "감성": sentiment
        }
    except Exception as e:
        return None


@st.cache_data(ttl=600)
def fetch_google_news(query: str, target_keywords: Optional[List[str]] = None, 
                     period: str = '30d') -> List[Dict]:
    """Google RSS로 해외 뉴스 수집 (병렬 처리 + 캐싱)"""
    noise_filter = "-Starbucks -store -closing -travel -hotel"
    full_query = f"{query} {noise_filter}"
    encoded_query = full_query.replace(" ", "%20")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:{period}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        return []

    if not feed.entries:
        return []

    coffee_guard_terms = ["coffee", "bean", "arabica", "robusta", "commodity", 
                         "harvest", "crop", "farm", "export", "price", "supply"]
    
    news_list = []
    seen_titles = set()
    
    # 병렬 처리
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for entry in feed.entries[:100]:
            title_signature = entry.title[:30].lower()
            if title_signature not in seen_titles:
                seen_titles.add(title_signature)
                futures.append(
                    executor.submit(process_single_news, entry, target_keywords, coffee_guard_terms)
                )
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                news_list.append(result)
            if len(news_list) >= 30:
                break
    
    return news_list[:30]


# ===========================================
# 네이버 뉴스 API (국내)
# ===========================================
@st.cache_data(ttl=600)
def fetch_naver_news_api(query: str) -> List[Dict]:
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
# UI 컴포넌트
# ===========================================
def render_news_item(item: Dict, index: int, tab_key: str, show_summary: bool = True):
    """뉴스 항목 렌더링 (이미지 제거, 텍스트 중심)"""
    with st.container():
        st.markdown(f"### {index + 1}. {item['감성']} {item['제목']}")
        st.caption(f"{item['게시일']}")
        
        # 원제 표시 (영문 기사만)
        if '원제' in item:
            st.caption(f"원제: _{item['원제']}_")
        
        # 버튼 영역
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            st.link_button("기사 보기", item['링크'], use_container_width=True)
    
        
        st.divider()


def search_with_progress(search_func, label: str, *args, **kwargs):
    """실시간 진행률 표시와 함께 검색 실행"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 단계 1: RSS 파싱
    status_text.text(f"{label} - RSS 피드 파싱 중...")
    progress_bar.progress(20)
    time.sleep(0.2)
    
    # 단계 2: 수집 시작
    status_text.text(f"{label} - 뉴스 수집 및 필터링 중...")
    progress_bar.progress(40)
    
    # 실제 검색 실행
    results = search_func(*args, **kwargs)
    
    # 단계 3: 처리 완료
    progress_bar.progress(70)
    status_text.text(f"{label} - 번역 및 감성 분석 완료 ({len(results)}건 수집)...")
    time.sleep(0.2)
    
    # 단계 4: 완료
    progress_bar.progress(100)
    status_text.text(f"{label} - 검색 완료!")
    time.sleep(0.3)
    
    progress_bar.empty()
    status_text.empty()
    
    return results


# ===========================================
# 메인 show() 함수
# ===========================================
def show():
    """뉴스 인사이트 페이지를 렌더링합니다."""
    
    st.markdown("<h1 style='text-align: center;'>뉴스 큐레이션</h1>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

    # 세션 상태 초기화
    if 'risk_news' not in st.session_state:
        st.session_state['risk_news'] = []
    if 'origin_news' not in st.session_state:
        st.session_state['origin_news'] = []
    if 'korea_news' not in st.session_state:
        st.session_state['korea_news'] = []

    tab1, tab2, tab3 = st.tabs(["글로벌 리스크", "산지별 동향", "국내 시장"])

    # ===========================================
    # Tab 1: 글로벌 리스크 (버그 수정)
    # ===========================================
    with tab1:
        st.subheader("글로벌 공급망 & 정책 리스크")
        st.markdown("EUDR 규제, 홍해 물류 위기, 공급망 리스크 등 커피 산업에 영향을 미치는 글로벌 이슈를 추적합니다.")
        
        if st.button("리스크 뉴스 검색", key="btn_risk", use_container_width=True):
            # 검색 쿼리 및 키워드 정의
            q = "Coffee Supply Chain OR EUDR Regulation OR Red Sea Logistics OR Coffee Price"
            targets = ["Coffee", "EUDR", "Red Sea", "Supply", "Logistics", "Price", "Regulation"]
            
            # 진행률 표시와 함께 검색 실행
            st.session_state['risk_news'] = search_with_progress(
                fetch_google_news, 
                "글로벌 리스크",
                q, 
                targets, 
                period='365d'
            )
                
        if st.session_state['risk_news']:
            st.success(f"**최신 커피 뉴스 TOP {len(st.session_state['risk_news'][:10])}**")
            
            # 워드클라우드 표시
            with st.expander("키워드 워드클라우드 보기"):
                display_wordcloud(st.session_state['risk_news'])
            
            st.divider()
            
            # 뉴스 항목 표시
            for i, item in enumerate(st.session_state['risk_news'][:10]):
                render_news_item(item, i, "risk", show_summary=True)

    # ===========================================
    # Tab 2: 산지별 동향 (요약 기능 제거)
    # ===========================================
    with tab2:
        st.subheader("주요 산지별 동향")
        st.markdown("브라질, 베트남, 콜롬비아 등 주요 커피 생산국의 수확, 수출, 가격 동향을 확인합니다.")
        
        country = st.selectbox(
            "국가 선택", 
            ["Brazil", "Vietnam", "Colombia", "Ethiopia", "Indonesia", "Kenya"], 
            key="news_country"
        )
        
        def get_params(c):
            if c == "Vietnam":
                return '"Vietnam Coffee" (Export OR Production)', ["Vietnam", "Robusta", "Export"]
            elif c == "Brazil":
                return '"Brazil Coffee" (Harvest OR Export)', ["Brazil", "Arabica", "Harvest"]
            elif c == "Colombia":
                return '"Colombia Coffee" (Production OR Export)', ["Colombia", "Coffee"]
            elif c == "Ethiopia":
                return '"Ethiopia Coffee" (Export OR Production)', ["Ethiopia", "Coffee"]
            else:
                return f'"{c} Coffee" (Export OR Price)', [c, "Coffee"]

        if st.button(f"{country} 뉴스 검색", key="btn_origin", use_container_width=True):
            query, targets = get_params(country)
            st.session_state['origin_news'] = search_with_progress(
                fetch_google_news,
                f"{country} 산지 동향",
                query, 
                targets, 
                period='90d'
            )
                
        if st.session_state['origin_news']:
            st.success(f"**최신 커피 뉴스 TOP {len(st.session_state['origin_news'][:10])}**")
            
            # 워드클라우드 표시
            with st.expander("키워드 워드클라우드 보기"):
                display_wordcloud(st.session_state['origin_news'])
            
            st.divider()
            
            # 뉴스 항목 표시 (요약 기능 제거)
            for i, item in enumerate(st.session_state['origin_news'][:10]):
                render_news_item(item, i, "origin", show_summary=False)

    # ===========================================
    # Tab 3: 국내 뉴스 (네이버 API)
    # ===========================================
    with tab3:
        st.subheader("국내 커피 시장 & 원두 뉴스")
        st.markdown("네이버 검색 API를 활용하여 국내 커피 시장의 최신 동향을 파악합니다.")
        
        if "네이버" in NAVER_CLIENT_ID:
            st.warning("⚠️ 네이버 API 키가 입력되지 않았습니다. config.py를 확인하세요!")
        
        korea_keyword = st.radio(
            "관심 키워드 선택", 
            ["커피 원두 가격", "생두 수입", "카페 창업 시장", "스페셜티 커피", "저가 커피 프랜차이즈"], 
            horizontal=True,
            key="korea_keyword"
        )
        
        if st.button("국내 뉴스 검색 (Naver API)", key="btn_korea", use_container_width=True):
            st.session_state['korea_news'] = search_with_progress(
                fetch_naver_news_api,
                "국내 뉴스",
                korea_keyword
            )
                
        if st.session_state['korea_news']:
            st.success(f"**최신 커피 뉴스 TOP {len(st.session_state['korea_news'])}**")
            
            for i, item in enumerate(st.session_state['korea_news']):
                with st.container():
                    st.markdown(f"### {i + 1}. {item['제목']}")
                    st.caption(f"{item['게시일']} | {item['언론사']}")
                    st.link_button("기사 원문 읽기", item['링크'], use_container_width=True)
                    st.divider()


if __name__ == "__main__":
    show()