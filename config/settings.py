import os
from dotenv import load_dotenv
from openai import OpenAI
import yagmail

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
KEYWORDS = os.getenv("KEYWORDS", "AI").split(",")
DB_FILE = "sent_articles.json"
BATCH_TIMES = ["09:00", "15:00", "21:00"]


# 쉼표로 구분된 문자열 → 리스트로 변환
#TODO 입력 받아서 처리하는 걸로 변경
KEYWORDS = os.getenv("KEYWORDS", "AI,Trump,Elon Musk,IT,OpenAI,Sam Altman,Google,US,삼성,Samsung,정치,박물관,전시회,그림").split(",")
BATCH_TIMES = os.getenv("BATCH_TIMES", "09:00,15:00,21:00").split(",")

DB_FILE = os.getenv("DB_FILE", "sent_articles.json")

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_API_KEY)

# Gmail 세팅
yag = yagmail.SMTP(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)