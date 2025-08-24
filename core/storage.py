import json
import hashlib
from datetime import datetime, date
import os

def get_daily_db_file(base_filename):
    """오늘 날짜를 기반으로 데이터베이스 파일명을 생성하는 함수"""
    today = date.today().strftime('%Y-%m-%d')
    name, ext = os.path.splitext(base_filename)
    return f"{name}_{today}{ext}"

def cleanup_old_db_files(base_filename, keep_days=1):
    """오래된 데이터베이스 파일들을 정리하는 함수"""
    try:
        name, ext = os.path.splitext(base_filename)
        base_dir = os.path.dirname(base_filename) or '.'
        
        # 현재 디렉토리의 파일들 확인
        for filename in os.listdir(base_dir):
            if filename.startswith(os.path.basename(name)) and filename.endswith(ext):
                # 날짜 추출 시도
                try:
                    date_part = filename.replace(os.path.basename(name) + '_', '').replace(ext, '')
                    file_date = datetime.strptime(date_part, '%Y-%m-%d').date()
                    
                    # keep_days 이상 오래된 파일 삭제
                    days_diff = (date.today() - file_date).days
                    if days_diff >= keep_days:
                        old_file_path = os.path.join(base_dir, filename)
                        os.remove(old_file_path)
                        print(f"오래된 데이터베이스 파일 삭제: {old_file_path}")
                except (ValueError, OSError):
                    # 날짜 형식이 맞지 않거나 파일 삭제 실패 시 무시
                    continue
    except Exception as e:
        print(f"오래된 파일 정리 중 오류 발생: {e}")

def load_sent_articles(base_db_file):
    """오늘 날짜 기준으로 발송된 기사들을 로드하는 함수"""
    # 오늘 날짜 기반 파일명 생성
    daily_db_file = get_daily_db_file(base_db_file)
    
    # 오래된 파일들 정리 (어제까지의 파일들 삭제)
    cleanup_old_db_files(base_db_file, keep_days=1)
    
    try:
        with open(daily_db_file, "r", encoding='utf-8') as f:
            data = json.load(f)
            # 기존 형식 호환성 유지
            if isinstance(data, list):
                return set(data)
            elif isinstance(data, dict):
                # 새로운 형식: {'date': 'YYYY-MM-DD', 'articles': [...]}
                stored_date = data.get('date', '')
                today_str = date.today().strftime('%Y-%m-%d')
                if stored_date == today_str:
                    return set(data.get('articles', []))
                else:
                    # 날짜가 다르면 빈 set 반환
                    return set()
            return set()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_sent_articles(sent_set, base_db_file):
    """오늘 날짜 기준으로 발송된 기사들을 저장하는 함수"""
    daily_db_file = get_daily_db_file(base_db_file)
    
    data = {
        'date': date.today().strftime('%Y-%m-%d'),
        'articles': list(sent_set),
        'count': len(sent_set),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(daily_db_file, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_article_id(article):
    """기사 URL을 기반으로 고유 ID를 생성하는 함수"""
    return hashlib.md5(article["url"].encode()).hexdigest()

def filter_new_articles(articles, sent_set):
    """오늘 내에서 새로운 기사만 필터링하는 함수"""
    new_articles = []
    for article in articles:
        article_id = get_article_id(article)
        if article_id not in sent_set:
            new_articles.append(article)
            sent_set.add(article_id)
    return new_articles

def get_today_stats(base_db_file):
    """오늘 발송된 기사 통계를 반환하는 함수"""
    daily_db_file = get_daily_db_file(base_db_file)
    
    try:
        with open(daily_db_file, "r", encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {
                    'date': data.get('date', ''),
                    'count': data.get('count', 0),
                    'last_updated': data.get('last_updated', '')
                }
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return {
        'date': date.today().strftime('%Y-%m-%d'),
        'count': 0,
        'last_updated': ''
    }