import requests
import feedparser
import schedule
import time
import json
from openai import OpenAI
import yagmail
import hashlib
from datetime import datetime, timedelta

# -------------------------------
# 설정
# -------------------------------
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"  # Google News / NewsAPI.org
GMAIL_ADDRESS = "hseona28@gmail.com"
GMAIL_APP_PASSWORD = "lovs dpdo jzdz rjtk" # 여기 다 암호화 필요함
RECIPIENT_EMAIL = "hseona28@gmail.com"
OPENAI_API_KEY = "YOUR_OPENAI_KEY"
KEYWORDS = ["AI", "Trump", "Elon Musk", "IT", "OpenAI", "Sam Altman", "Google", "US", "삼성", "Samsung", "정치", "박물관", "전시회", "그림"]  # 관심 키워드 리스트
DB_FILE = "sent_articles.json"  # 발송 기록 저장
BATCH_TIMES = ["09:00", "15:00", "21:00"]
# -------------------------------

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_API_KEY)

# Gmail 세팅
yag = yagmail.SMTP(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)


# -------------------------------
# 발송 기록 관리
# -------------------------------
def load_sent_articles():
    try:
        with open(DB_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_sent_articles(sent_set):
    with open(DB_FILE, "w") as f:
        json.dump(list(sent_set), f)


# -------------------------------
# 뉴스 수집
# -------------------------------
def fetch_newsapi(keyword):
    url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
    resp = requests.get(url).json()
    articles = []
    for a in resp.get("articles", []):
        articles.append({
            "title": a["title"],
            "url": a["url"],
            "content": a["content"] or a["description"] or "",
            "source": a["source"]["name"],
            "language": "en"
        })
    return articles


def fetch_google_rss(keyword):
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "url": entry.link,
            "content": getattr(entry, "summary", ""),
            "source": "Google News",
            "language": "ko"
        })
    return articles


def fetch_bbc_rss(keyword):
    rss_url = f"http://feeds.bbci.co.uk/news/technology/rss.xml"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        if keyword.lower() in entry.title.lower():
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "content": getattr(entry, "summary", ""),
                "source": "BBC",
                "language": "en"
            })
    return articles

# -------------------------------
# 키워드별 뉴스 통합
# -------------------------------
def fetch_all_news():
    all_articles = []
    for kw in KEYWORDS:
        all_articles += fetch_newsapi(kw)
        all_articles += fetch_google_rss(kw)
        all_articles += fetch_bbc_rss(kw)
    return all_articles

# -------------------------------
# 중복 제거
# -------------------------------
def get_article_id(article):
    return hashlib.md5(article["url"].encode()).hexdigest()


def filter_new_articles(articles, sent_set):
    new_articles = []
    for a in articles:
        aid = get_article_id(a)
        if aid not in sent_set:
            new_articles.append(a)
            sent_set.add(aid)
    return new_articles


# -------------------------------
# GPT 한글 요약
# -------------------------------
def summarize_to_korean(english_text):
    if not english_text:
        return ""
    prompt = f"""
    다음 영어 기사를 한국어로 요약해 주세요. 
    내용이 왜곡되거나 누락되지 않게 정확하게 정리합니다.

    기사:
    {english_text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content
    except:
        return "[요약 실패]"


# -------------------------------
# 메일 발송
# -------------------------------
def send_news_email(news_list):
    if not news_list:
        print(f"{datetime.now()} - 발송할 새 뉴스 없음")
        return

    contents = []
    for news in news_list:
        if news["language"] == "en":
            summary = summarize_to_korean(news["content"])
            section = f"""
=== {news['title']} ===
[출처] {news['source']}
[링크] {news['url']}

[한글 요약]
{summary}

[영문 원문]
{news['content']}
"""
        else:
            section = f"""
=== {news['title']} ===
[출처] {news['source']}
[링크] {news['url']}

[요약]
{news['content']}
"""
        contents.append(section)

    yag.send(to=RECIPIENT_EMAIL, subject=f"[뉴스 요약] {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             contents="\n\n".join(contents))
    print(f"{datetime.now()} - 뉴스 발송 완료: {len(news_list)}건")


# -------------------------------
# 배치 작업 함수
# -------------------------------
def job():
    sent_set = load_sent_articles()
    articles = fetch_all_news()  # 키워드별 통합 수집
    new_articles = filter_new_articles(articles, sent_set)
    send_news_email(new_articles)
    save_sent_articles(sent_set)

# -------------------------------
# 스케줄 등록
# -------------------------------
for t in BATCH_TIMES:
    schedule.every().day.at(t).do(job)

print("뉴스 모니터링 서비스 시작...")
while True:
    schedule.run_pending()
    time.sleep(60)