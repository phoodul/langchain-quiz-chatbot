---
name: quiz-chatbot-expert
description: LangChain Quiz Chatbot 프로젝트의 개발 및 유지보수를 위한 전문가 스킬입니다. PDF 분석, LangChain(LCEL) 로직, Streamlit UI, 그리고 uv 패키지 관리에 최적격화된 지침을 제공합니다.
---

# 🚀 LangChain Quiz Chatbot Expert Skill

이 스킬은 **LangChain Quiz Chatbot** 프로젝트에 특화된 개발 지침을 제공합니다. 에이전트(Antigravity)는 이 프로젝트에서 코드를 수정하거나 기능을 추가할 때 다음의 **Core Protocol**을 반드시 준수해야 합니다.

## 📌 1. 개발 및 패키지 관리 (uv Protocol)
- 모든 외부 라이브러리 추가는 `uv add <package>`를 사용합니다.
- 스크립트 실행은 `uv run <script_name>.py`를 원칙으로 합니다.
- **실행 모드**: Streamlit 앱 실행 시 `uv run main.py`를 호출하여 전체 워크플로우를 테스트합니다.

## 📝 2. 기록 관리 (HISTORY.md Protocol)
- **모든 기술적 변경 사항**, 버그 수정, 성능 개선 시도는 즉시 `HISTORY.md`에 기록합니다.
- 기록 형식:
  - `## [YYYY-MM-DD HH:MM] - <Title>`
  - `- 작업 내용: <Details>`
  - `- 해결 방법/이유: <Rationale>`
  - `- 특이사항: <Issues>`

## 🧪 3. LangChain & LLM 스택 준수
- **LLM**: `gemini-3-flash` (주요 로직 및 퀴즈 생성용)
- **Embedding**: `text-embedding-004` (FAISS 인텍싱용)
- **Framework**: LangChain Expression Language(LCEL) 및 LangGraph 활용 권장.
- **RAG**: 사용자 질문 시 무조건 `search_pdf_documents` 도구를 통해 문서 기반 답변을 생성하도록 유도합니다.

## 🧩 4. 퀴즈 생성 및 검증
- 퀴즈는 반드시 **JSON** 형식의 4지선다형(A/B/C/D)으로 생성합니다.
- 생성된 퀴즈가 문서의 핵심 맥락을 정확히 반영하는지 자가 검증(Verification) 단계를 거칩니다.
- 파싱 오류가 발생하지 않도록 Pydantic 출력 파서를 적극 활용합니다.

## 🎨 5. UI/UX 디자인 가이드 (Streamlit)
- `st.session_state`를 활용하여 이전 대화 흐름(Conversation Memory)과 벡터스토어 상태를 영구적으로 관리합니다.
- 사용자 인터페이스는 **Modern & Premium**한 느낌을 주도록 CSS 커스텀 스타일링을 고려합니다.
- 진행 상황을 나타내기 위해 `st.spinner`나 `st.status`를 적절히 사용합니다.

---
*이 지침은 프로젝트의 품질과 포트폴리오의 전문성을 보장하기 위함입니다.*
