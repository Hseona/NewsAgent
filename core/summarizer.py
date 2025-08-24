from openai import OpenAI
from openai import OpenAIError
import time
import logging
from datetime import datetime

# 로깅 설정
logger = logging.getLogger(__name__)

class NewsSummarizer:
    """뉴스 요약을 담당하는 클래스"""
    
    def __init__(self, client: OpenAI, model: str = "gpt-3.5-turbo", max_retries: int = 3):
        self.client = client
        self.model = model
        self.max_retries = max_retries
    
    def _get_optimal_max_tokens(self, text_length: int) -> int:
        """텍스트 길이에 따라 최적의 토큰 수를 반환"""
        if text_length < 200:
            return 150
        elif text_length < 500:
            return 250
        elif text_length < 1000:
            return 350
        else:
            return 500
    
    def _create_enhanced_prompt(self, text: str) -> str:
        """향상된 프롬프트 생성"""
        return f"""
당신은 전문 뉴스 에디터입니다. 다음 영어 뉴스 기사를 한국어로 정확하고 간결하게 요약해주세요.

요약 가이드라인:
1. 핵심 내용을 놓치지 말고 정확하게 전달
2. 원문의 톤과 의미를 유지
3. 불필요한 세부사항은 제외
4. 읽기 쉬운 한국어로 작성
5. 3-4문장으로 간결하게 요약

영어 기사:
{text}

한국어 요약:"""
    
    def _truncate_text(self, text: str, max_chars: int = 2000) -> str:
        """텍스트를 적절한 길이로 자르기"""
        if len(text) <= max_chars:
            return text
        
        # 문장 단위로 자르기 시도
        sentences = text.split('. ')
        truncated = ""
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_chars:
                truncated += sentence + '. '
            else:
                break
        
        return truncated.strip() or text[:max_chars] + "..."
    
    def summarize_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 요약하는 메인 함수"""
        if not text or not text.strip():
            return ""
        
        # 텍스트 전처리
        clean_text = text.strip()
        truncated_text = self._truncate_text(clean_text)
        
        # 프롬프트 및 파라미터 설정
        prompt = self._create_enhanced_prompt(truncated_text)
        max_tokens = self._get_optimal_max_tokens(len(truncated_text))
        
        # 재시도 로직
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "당신은 뉴스 요약 전문가입니다. 정확하고 간결한 한국어 요약을 제공합니다."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,  # 일관된 결과를 위해 낮은 temperature
                    presence_penalty=0.1
                )
                
                summary = response.choices[0].message.content
                if summary and summary.strip():
                    return summary.strip()
                else:
                    logger.warning(f"빈 응답 받음 (시도 {attempt}/{self.max_retries})")
                    
            except OpenAIError as e:
                logger.error(f"OpenAI API 오류 (시도 {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # 지수 백오프
                    logger.info(f"{wait_time}초 대기 후 재시도...")
                    time.sleep(wait_time)
                else:
                    return f"[요약 실패 - API 오류: {type(e).__name__}]"
                    
            except Exception as e:
                logger.error(f"예상치 못한 오류 (시도 {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(1)
                else:
                    return f"[요약 실패 - 시스템 오류]"
        
        return "[요약 실패 - 최대 재시도 횟수 초과]"

# 기존 함수 호환성을 위한 래퍼 함수
def summarize_to_korean(client: OpenAI, text: str) -> str:
    """기존 코드와의 호환성을 위한 래퍼 함수"""
    summarizer = NewsSummarizer(client)
    return summarizer.summarize_to_korean(text)