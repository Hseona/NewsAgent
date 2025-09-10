# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NewsAgent는 자동화된 뉴스 수집 및 요약 서비스입니다. 여러 뉴스 소스에서 키워드 기반으로 뉴스를 수집하고, OpenAI GPT-4를 사용해 영문 기사를 한국어로 번역/요약한 후 이메일로 발송하는 Python 애플리케이션입니다.

## Project Structure

```
NewsAgent/
├── ai-agent.py              # 레거시 단일 파일 구현체
├── script.py               # PyCharm 기본 템플릿 스크립트
├── config/
│   └── settings.py         # 환경변수 기반 설정 관리
├── core/                   # 핵심 비즈니스 로직 모듈들
│   ├── collector.py        # 뉴스 데이터 수집 (네이버 뉴스 API, Google RSS, BBC RSS)
│   ├── storage.py          # 기사 중복 제거 및 저장 관리
│   ├── summarizer.py       # OpenAI GPT-4 한국어 번역/요약 통합
│   ├── mailer.py          # Gmail SMTP 이메일 발송 시스템
│   └── scheduler.py        # 스케줄된 작업 실행 관리
├── scripts/
│   └── run_agent.py       # 모듈형 아키텍처 메인 진입점
├── .env                   # 환경변수 (git에서 제외)
└── .venv/                 # Python 가상환경
```

## Development Commands

### 환경 설정
```bash
# NewsAgent 디렉토리로 이동
cd ../../NewsAgent

# 가상환경 활성화
source .venv/bin/activate

# 의존성 설치 (requirements.txt가 비어있으므로 수동 설치)
pip install requests feedparser schedule openai yagmail python-dotenv
```

### 애플리케이션 실행
```bash
# 모듈형 아키텍처 사용 (권장)
python scripts/run_agent.py

# 레거시 단일 파일 버전 사용
python ai-agent.py
```

### 환경 변수 설정
NewsAgent 디렉토리에 `.env` 파일이 필요합니다:
```env
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
OPENAI_API_KEY=your_openai_api_key
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=recipient_email
KEYWORDS=AI,Trump,Elon Musk,IT,OpenAI,Sam Altman,Google,US,삼성,Samsung,정치,박물관,전시회,그림
BATCH_TIMES=09:00,15:00,21:00
DB_FILE=sent_articles.json
```

## 아키텍처 세부사항

### 데이터 플로우
1. **수집**: 설정된 키워드를 기반으로 네이버 뉴스 API, Google News RSS, BBC RSS에서 뉴스 수집
2. **중복 제거**: 기사 URL의 MD5 해싱을 사용하여 중복 처리 방지
3. **요약**: 영문 기사를 OpenAI GPT-4로 한국어 번역/요약
4. **배포**: 집계된 뉴스를 Gmail을 통해 설정된 수신자에게 발송
5. **스케줄링**: 설정된 시간에 실행 (기본값: 오전 9시, 오후 3시, 오후 9시)

### 핵심 컴포넌트

**설정 관리 (`config/settings.py`)**:
- python-dotenv를 사용한 환경변수 로딩
- OpenAI 클라이언트 및 Gmail SMTP 연결 초기화
- 쉼표로 구분된 환경변수 파싱 처리

**뉴스 수집 (`core/collector.py`)**:
- 다중 소스 집계 (네이버 뉴스 API, Google News RSS, BBC RSS)
- 언어별 콘텐츠 추출
- BBC RSS 피드의 키워드 기반 필터링

**저장 시스템 (`core/storage.py`)**:
- 발송된 기사 추적을 위한 JSON 기반 저장
- MD5 기반 기사 중복 제거
- 간단한 파일 기반 데이터베이스 관리

**AI 통합 (`core/summarizer.py`)**:
- 한국어 번역을 위한 OpenAI GPT-4 통합
- 일관된 요약을 위한 구조화된 프롬프트
- 폴백 메시지가 있는 오류 처리

**이메일 시스템 (`core/mailer.py`)**:
- yagmail을 사용한 Gmail SMTP 통합
- 다국어 콘텐츠 포매팅
- 타임스탬프가 포함된 제목

### 레거시 vs 모듈형 아키텍처
- `ai-agent.py`: 하드코딩된 설정을 가진 원본 단일 파일 구현
- `scripts/run_agent.py`: 환경변수 기반 설정을 사용하는 현대적 모듈형 구현
- 모듈형 버전이 관심사 분리와 유지보수성에서 더 나은 구조 제공

## 개발 환경 정보

- Python 버전: 3.9
- 가상환경: `../NewsAgent/.venv`
- IDE 설정: PyCharm 프로젝트는 `../PyCharmMiscProject`에서 이 NewsAgent 모듈을 참조