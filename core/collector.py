import requests
import feedparser
from datetime import datetime, date, timedelta
from dateutil import parser
from urllib.parse import quote

def is_today_article(pub_date_str):
    """발행일이 오늘인지 확인하는 함수"""
    if not pub_date_str:
        return True  # 날짜 정보가 없으면 포함
    
    try:
        # 다양한 날짜 형식 파싱
        pub_date = parser.parse(pub_date_str).date()
        today = date.today()
        return pub_date == today
    except (ValueError, TypeError):
        return True  # 파싱 실패 시 포함

def get_date_range_for_naver():
    """네이버 API용 날짜 범위 반환 (오늘)"""
    today = date.today()
    return today.strftime('%Y%m%d')

def fetch_naver_news(keyword, client_id, client_secret):
    # todo 하드코딩 문자열 클래스? 파일? 변수로 변경
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": keyword,
        "display": 20,  # 필터링을 위해 더 많이 가져옴
        "start": 1,
        "sort": "date"
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        articles = []
        for item in data.get("items", []):
            # HTML 태그 제거
            title = item["title"].replace("<b>", "").replace("</b>", "")
            content = item["description"].replace("<b>", "").replace("</b>", "")
            
            # 발행일 확인 (네이버는 pubDate 필드)
            pub_date = item.get("pubDate", "")
            if not is_today_article(pub_date):
                continue  # 오늘이 아닌 기사는 건너뛰기
            
            # 키워드가 제목 또는 내용에 포함되어 있는지 확인 (대소문자 무시)
            if (keyword.lower() in title.lower() or 
                keyword.lower() in content.lower()):
                articles.append({
                    "title": title,
                    "url": item["originallink"] or item["link"],
                    "content": content,
                    "source": "Naver News",
                    "language": "ko"
                })
        return articles[:10]  # 최대 10개로 제한
    except requests.exceptions.RequestException as e:
        print(f"네이버 뉴스 API 요청 오류: {e}")
        return []

def fetch_google_rss(keyword):
    encoded_keyword = quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        # 발행일 확인 (RSS는 published 또는 pubDate 필드)
        pub_date = getattr(entry, 'published', '') or getattr(entry, 'pubDate', '')
        if not is_today_article(pub_date):
            continue  # 오늘이 아닌 기사는 건너뛰기
        
        # 제목과 내용에서 키워드 검색 (대소문자 무시)
        title = entry.title
        content = getattr(entry, "summary", "")
        
        # 키워드가 제목 또는 내용에 포함되어 있는지 확인
        if (keyword.lower() in title.lower() or 
            keyword.lower() in content.lower()):
            articles.append({
                "title": title,
                "url": entry.link,
                "content": content,
                "source": "Google News",
                "language": "ko"
            })
    return articles[:10]  # 최대 10개로 제한

def translate_keyword_to_english(keyword):
    """한글 키워드를 영어로 번역하는 딕셔너리 (.env 키워드 기준)"""
    translation_dict = {
        # .env에 있는 한글 키워드들
        "삼성": "Samsung",
        "정치": "politics", 
        "박물관": "museum",
        "전시회": "exhibition",
        "그림": "art",
        
        # 영어 키워드는 그대로 유지
        "AI": "AI",
        "Trump": "Trump", 
        "Elon Musk": "Elon Musk",
        "IT": "IT",
        "OpenAI": "OpenAI",
        "Sam Altman": "Sam Altman",
        "Google": "Google",
        "US": "US",
        "Samsung": "Samsung"
    }
    
    # 한글이 포함된 경우 번역 시도, 없으면 원본 키워드 사용
    if any('\uac00' <= char <= '\ud7a3' for char in keyword):
        return translation_dict.get(keyword, keyword)
    return keyword

def fetch_bbc_rss(keyword):
    # 한글 키워드를 영어로 번역
    english_keyword = translate_keyword_to_english(keyword)
    
    # 여러 BBC RSS 피드 사용
    rss_urls = [
        "http://feeds.bbci.co.uk/news/rss.xml",  # 전체 뉴스
        "http://feeds.bbci.co.uk/news/technology/rss.xml",  # 기술
        "http://feeds.bbci.co.uk/news/business/rss.xml",  # 비즈니스
        "http://feeds.bbci.co.uk/news/world/rss.xml"  # 세계 뉴스
    ]
    
    articles = []
    for rss_url in rss_urls:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                # 발행일 확인 (RSS는 published 또는 pubDate 필드)
                pub_date = getattr(entry, 'published', '') or getattr(entry, 'pubDate', '')
                if not is_today_article(pub_date):
                    continue  # 오늘이 아닌 기사는 건너뛰기
                
                # 제목과 내용에서 키워드 검색
                title = entry.title.lower()
                content = getattr(entry, "summary", "").lower()
                description = getattr(entry, "description", "").lower()
                
                # 영어 키워드로 검색
                if (english_keyword.lower() in title or 
                    english_keyword.lower() in content or 
                    english_keyword.lower() in description):
                    articles.append({
                        "title": entry.title,
                        "url": entry.link,
                        "content": getattr(entry, "summary", ""),
                        "source": "BBC",
                        "language": "en"
                    })
        except Exception as e:
            print(f"BBC RSS 피드 오류 ({rss_url}): {e}")
            continue
    
    return articles

def fetch_all_news(keywords, client_id, client_secret):
    all_articles = []
    for kw in keywords:
        all_articles += fetch_naver_news(kw, client_id, client_secret)
        all_articles += fetch_google_rss(kw)
        all_articles += fetch_bbc_rss(kw)
    return all_articles