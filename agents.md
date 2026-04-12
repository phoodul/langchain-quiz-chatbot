# AGENTS.md

이 프로젝트의 에이전트(AI Assistant)는 매 세션 시작 시 이 파일을 읽고 다음 지침을 반드시 준수해야 합니다.

## 1. 프로젝트 정체성 (Core Identity)
- **프로젝트 명**: LangChain Quiz Chatbot
- **주요 목적**: PDF 문서를 분석하여 자동으로 학습 퀴즈를 생성하고, 인텔리전트한 상담을 제공하는 인터랙티브 교육 챗봇.
- **핵심 기술 스택**: 
    - **Language**: Python 3.12+
    - **Framework**: LangChain (LCEL), LangGraph, Streamlit
    - **LLM Model**: `gemini-3-flash` (최신 고성능/저지연 모델)
    - **Embedding Model**: `text-embedding-004` (안정적인 최신 텍스트 임베딩 모델)
    - **Vector DB**: FAISS (Local)
    - **Package Manager**: `uv`

## 2. 파일 구조 및 역할
- `main.py`: 애플리케이션 진입점 (Streamlit 실행 래퍼).
- `src/quiz_chatbot.py`: 메인 비즈니스 로직 및 UI (RAG 파이프라인, 퀴즈 생성기, 에이전트 포함).
- `HISTORY.md`: 개발 과정의 주요 결정, 이슈, 트러블슈팅 사례를 기록하는 로그 파일.
- `faiss_index_pdf_quiz/`: 로컬 벡터 데이터베이스 저장 경로.
- `.env`: API 키 및 환경 변수 관리 (Grit에 포함되지 않도록 주의).

## 3. 핵심 워크플로우 (Core Workflow)
1. **Document Loading**: PyMuPDF를 통한 PDF 텍스트 추출.
2. **Indexing**: 텍스트 분할(Chunking) 후 `text-embedding-004`를 활용해 FAISS 인덱스 빌드.
3. **Learning Mode (Quiz)**: 문서 컨텍스트를 기반으로 JSON 형식의 4지선다 퀴즈 자동 생성.
4. **Agentic Retrieval**: 사용자의 일반 질문에 대해 에이전트가 `search_pdf_documents` 도구를 사용하여 문서 기반 답변 수행.

## 4. 절대 규칙 (Mandatory Rules)
- **패키지 관리**: 모든 의존성 추가 및 실행은 **반드시 `uv`를 사용**합니다. (예: `uv add <package>`, `uv run <script>`)
- **모델 일관성**: 임베딩 모델(`.004`)이나 LLM(`.3-flash`) 변경 시, 반드시 이 문서와 코드를 동시에 업데이트합니다.
- **상태 관리**: Streamlit의 `st.session_state`를 활용하여 대화 이력 및 벡터스토어 세션을 안전하게 관리합니다.
- **기록 관리 (Logging)**: 모든 기술적 이슈, 성능 개선 시도, 예외 상황 해결 과정은 즉시 `HISTORY.md`에 기록합니다. 이는 포트폴리오의 '과정 중심 기록'을 위한 핵심 자료입니다.
- **에러 핸들링**: AI의 JSON 응답 파싱 실패 시 사용자에게 친절한 가이드를 제공하며, 로그를 남깁니다.

## 5. 실행 및 개발 명령어
| 작업 | 명령어 |
| :--- | :--- |
| **애플리케이션 실행** | `uv run main.py` |
| **의존성 동기화** | `uv sync` |
| **린트 및 포맷팅** | `uv run ruff check .` / `uv run ruff format .` |

---
*최종 업데이트: 2026-04-12*
*이 파일은 프로젝트의 일관성을 유지하기 위한 가이드입니다. 구조적 변경 시 반드시 업데이트 바랍니다.*
