# AGENTS.md

이 프로젝트의 에이전트(AI Assistant)는 매 세션 시작 시 이 파일을 읽고 다음 지침을 반드시 준수해야 합니다.

## 1. 프로젝트 정체성 (Core Identity)
- **프로젝트 명**: LangChain Quiz Chatbot
- **주요 목적**: LangChain을 활용한 퀴즈 생성 및 인터랙티브 챗봇 서비스
- **핵심 기술 스택**: Python 3.12+, LangChain (LCEL), LangGraph, `uv` (Package Manager)

## 2. 절대 규칙 (Mandatory Rules) - 최우선 순위
- **패키지 관리**: 모든 Python 패키지 관리 및 실행은 **반드시 `uv`를 사용**합니다. (예: `pip` 대신 `uv add`)
- **타입 가드**: 모든 함수 정의 시 Python Type Hinting을 필수적으로 적용합니다.
- **비동기 지향**: LLM API 호출 및 I/O 작업은 `async/await` 구조를 우선합니다.
- **커밋 컨벤션**: 모든 커밋은 [COMMIT_CONVENTION.md](file:///d:/jss/langchain-quiz-chatbot/COMMIT_CONVENTION.md)의 가이드를 엄격히 준수합니다.
- **포트폴리오 준수**: 모든 작업 시 `PORTFOLIO_CHECKLIST.md`의 기준을 고려하며, 특히 트러블슈팅이나 성능 개선 사례가 발생할 경우 해당 문서에 기록할 것을 제안하거나 직접 반영합니다.

## 3. 실행 및 개발 명령어 (Commands)
| 작업 | 명령어 |
| :--- | :--- |
| **애플리케이션 실행** | `uv run main.py` |
| **의존성 설치/동기화** | `uv sync` |
| **새 패키지 추가** | `uv add <package_name>` |
| **린트 및 포맷팅** | `uv run ruff check .` / `uv run ruff format .` |
| **테스트 실행** | `uv run pytest` |

## 5. 코딩 스타일 및 설계 원칙
- **LangChain 구조**: 단순 체인보다는 확장성을 고려하여 `LCEL`과 `LangGraph`를 사용한 상태 중심 설계를 지향합니다.
- **에러 처리**: 사용자에게 노출되는 에러 메시지는 친절하고 명확해야 하며, 로그는 상세히 남깁니다.
- **문서화**: 모든 모듈과 주요 함수에는 Google 스타일의 Docstring을 작성합니다.

---
*이 파일은 프로젝트의 에이전트를 위한 가이드라인입니다. 변경 사항이 있을 경우 에이전트에게 업데이트를 요청하세요.*
