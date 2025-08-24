import yagmail
from datetime import datetime
import time
from core.email_template_renderer import EmailTemplateRenderer

def classify_news_by_source(news_list):
    """뉴스를 소스별로 분류하는 함수"""
    news_by_source = {}
    for news in news_list:
        source = news["source"]
        if source not in news_by_source:
            news_by_source[source] = []
        news_by_source[source].append(news)
    return news_by_source

def send_email_with_retry(html_content, gmail_address, app_password, recipient, news_count):
    """재시도 로직을 포함한 이메일 발송 함수"""
    max_retries = 3
    retry_count = 0
    current_datetime = datetime.now()
    
    while retry_count < max_retries:
        try:
            yag = yagmail.SMTP(gmail_address, app_password)
            yag.send(
                to=recipient,
                subject=f"📰 [뉴스 요약] {current_datetime.strftime('%Y-%m-%d %H:%M')} - {news_count}건",
                contents=html_content,
                prettify_html=False  # CSS 오류 방지
            )
            yag.close()
            print(f"{datetime.now()} - 뉴스 발송 완료: {news_count}건")
            return True
            
        except Exception as e:
            retry_count += 1
            print(f"{datetime.now()} - 이메일 발송 실패 (시도 {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                print(f"{datetime.now()} - 5초 후 재시도...")
                time.sleep(5)
            else:
                print(f"{datetime.now()} - 이메일 발송 최종 실패")
                return False

def send_news_email(news_list, client, gmail_address, app_password, recipient):
    """뉴스 이메일 발송 메인 함수"""
    if not news_list:
        print(f"{datetime.now()} - 발송할 새 뉴스 없음")
        return

    # 1. 뉴스를 소스별로 분류
    news_by_source = classify_news_by_source(news_list)
    
    # 2. 템플릿 렌더러 생성 및 HTML 컨텐츠 생성
    template_renderer = EmailTemplateRenderer()
    html_content = template_renderer.generate_email_html(news_list, news_by_source, client)
    
    # 3. 이메일 발송
    send_email_with_retry(html_content, gmail_address, app_password, recipient, len(news_list))