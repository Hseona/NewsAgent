from config.settings import *
from core.collector import fetch_all_news
from core.storage import load_sent_articles, save_sent_articles, filter_new_articles
from core.mailer import send_news_email
from core.scheduler import register_schedules
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def job():
    sent_set = load_sent_articles(DB_FILE)
    articles = fetch_all_news(KEYWORDS, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
    new_articles = filter_new_articles(articles, sent_set)
    send_news_email(new_articles, client, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL)
    save_sent_articles(sent_set, DB_FILE)

if __name__ == "__main__":
    register_schedules(job, BATCH_TIMES)