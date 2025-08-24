import os
import html
from datetime import datetime
from core.summarizer import summarize_to_korean


class EmailTemplateRenderer:
    """이메일 템플릿 렌더링을 담당하는 클래스"""
    
    def __init__(self):
        self.templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self._template_cache = {}
    
    def load_template(self, template_name):
        """HTML 템플릿 파일을 로드하는 메서드 (캐싱 포함)"""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
            
        template_path = os.path.join(self.templates_dir, template_name)
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
            self._template_cache[template_name] = content
            return content
    
    def render_template(self, template_content, **kwargs):
        """템플릿에 데이터를 주입하는 렌더링 메서드"""
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        return template_content
    
    def generate_content_section(self, news, client):
        """뉴스 언어에 따라 적절한 컨텐츠 섹션을 생성하는 메서드"""
        if news["language"] == "en":
            template = self.load_template('content_english.html')
            summary = summarize_to_korean(client, news["content"])
            return self.render_template(
                template,
                summary=summary,
                original_content=self._clean_html_entities(self._truncate_content(news['content']))
            )
        else:
            template = self.load_template('content_korean.html')
            return self.render_template(
                template,
                content=self._clean_html_entities(self._truncate_content(news['content']))
            )
    
    def generate_news_item(self, news, client):
        """개별 뉴스 아이템을 생성하는 메서드"""
        template = self.load_template('news_item.html')
        content_section = self.generate_content_section(news, client)
        
        return self.render_template(
            template,
            title=self._clean_html_entities(news['title']),
            url=news['url'],
            content_section=content_section
        )
    
    def generate_news_section(self, source_name, source_news, client):
        """특정 소스의 뉴스 섹션을 생성하는 메서드"""
        template = self.load_template('news_section.html')
        
        # 각 뉴스 아이템 생성
        news_items = []
        for news in source_news:
            news_item = self.generate_news_item(news, client)
            news_items.append(news_item)
        
        # 소스별 아이콘과 표시명 매핑
        source_info = self._get_source_info(source_name)
        
        return self.render_template(
            template,
            source_name=source_name,
            source_icon=source_info['icon'],
            source_display_name=source_info['display_name'],
            news_count=len(source_news),
            news_items=''.join(news_items)
        )
    
    def generate_news_sections(self, news_by_source, client):
        """모든 뉴스 섹션들을 생성하는 메서드"""
        news_sections = []
        for source, source_news in news_by_source.items():
            section = self.generate_news_section(source, source_news, client)
            news_sections.append(section)
        return news_sections
    
    def generate_email_html(self, news_list, news_by_source, client):
        """완전한 이메일 HTML을 생성하는 메서드"""
        template = self.load_template('news_email.html')
        news_sections = self.generate_news_sections(news_by_source, client)
        current_datetime = datetime.now()
        
        return self.render_template(
            template,
            current_date=current_datetime.strftime('%Y년 %m월 %d일 %H:%M'),
            current_time=current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            total_count=len(news_list),
            source_count=len(news_by_source),
            news_sections=''.join(news_sections)
        )
    
    def clear_cache(self):
        """템플릿 캐시를 지우는 메서드"""
        self._template_cache.clear()
    
    def _truncate_content(self, content, max_length=500):
        """컨텐츠를 지정된 길이로 자르는 유틸리티 메서드"""
        if len(content) > max_length:
            return content[:max_length] + '...'
        return content
    
    def _clean_html_entities(self, text):
        """HTML 엔티티를 깔끔하게 디코딩하는 유틸리티 메서드"""
        if not text:
            return ""
        # HTML 엔티티 디코딩
        cleaned = html.unescape(text)
        return cleaned.strip()
    
    def _get_source_info(self, source_name):
        """소스별 아이콘과 표시명을 반환하는 메서드"""
        source_mapping = {
            "Naver News": {
                "icon": "🟢",
                "display_name": "네이버 뉴스"
            },
            "Google News": {
                "icon": "🔍",
                "display_name": "구글 뉴스"
            },
            "BBC": {
                "icon": "🌍",
                "display_name": "BBC 뉴스"
            }
        }
        
        return source_mapping.get(source_name, {
            "icon": "📰",
            "display_name": source_name
        })
    
    def _escape_html(self, text):
        """HTML 특수 문자를 이스케이프하는 유틸리티 메서드"""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))