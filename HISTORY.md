# 🚀 Project Build History & Troubleshooting

이 문서는 프로젝트의 빌딩 과정에서 발생하는 주요 기술적 결정, 이슈, 트러블슈팅 사례를 기록하는 타임라인 프로젝트 로그입니다. 이 기록은 추후 포트폴리오 작성 시 핵심적인 증거 자료로 활용됩니다.

## 📅 Build Log

### [2026-04-18] 가드레일 시스템 (Guardrails) 기반 구축
- **상황(Situation)**: 퀴즈 챗봇의 안전성, 교육적 가치 유지, 개인정보 보호를 위해 `01_guardrails.ipynb`에서 검사된 4계층 가드레일 시스템을 프로젝트에 공식 통합해야 함.
- **결정(Action)**:
    - [x] 가드레일용 상수 정의 (차단 키워드, 상담 이관 키워드 등)
    - [x] 정규표현식(Regex)을 이용한 개인정보 패턴(전화번호, 이메일) 정의
- **상세**: 
    - `src/guardrails.py`에 4계층 미들웨어 함수 구현:
        1. `education_guardrail`: 키워드 기반 입력 필터링 (부정행위/딴짓/유해물)
        2. `student_safety_middleware`: Regex 기반 개인정보 마스킹 (전화번호/이메일)
        3. `counseling_escalation_middleware`: 위기 키워드 감지 및 상담 이관 안내
        4. `answer_leakage_guardrail`: LLM 기반 출력 검증 및 정답 유출 방지 (Auditor 모델 활용)
- **에이전트 통합**:
    - `src/quiz_chatbot.py`의 `initialize_agent` 함수에서 `create_agent` 호출 시 상기 4개 미들웨어를 실시간 파이프라인으로 연결.
    - 입출력의 모든 흐름에 가드레일이 자동 적용되도록 구성.
- **결과(Result)**: 챗봇의 모든 입출력 경로에 안전 장치가 마련되었으며, 교육적 목표에 부합하는 대화 환경 구축. 테스트 시나리오(부정행위, 개인정보 보호 등)에 대한 대응력 확보.

### [2026-04-12] 프로젝트 전체 임베딩 모델 `gemini-embedding-2-preview` 통일 및 task_type 제거
- **상황(Situation)**: 코드에서는 `gemini-embedding-2-preview`를 사용 중이었으나, 문서 파일 6개(ARCHITECTURE.md, README.md, AGENTS.md, SKILL.md, rag_strategy.md 등)에는 여전히 `text-embedding-004`로 기재되어 코드-문서 간 불일치 발생.
- **추가 이슈**: 공식 문서(ai.google.dev)에 따르면 `gemini-embedding-2-preview`는 `task_type` 파라미터 대신 프롬프트 기반 작업 접두사를 사용하는 것이 권장됨. 기존 코드의 `task_type="RETRIEVAL_DOCUMENT"` 설정이 API 호환성 문제를 유발할 가능성 확인.
- **결정(Action)**:
    - `quiz_chatbot.py`: `task_type="RETRIEVAL_DOCUMENT"` 파라미터 제거 (공식 권장 방식 준수).
    - `ARCHITECTURE.md`, `README.md`, `AGENTS.md`, `SKILL.md`, `rag_strategy.md`: 임베딩 모델 참조를 `gemini-embedding-2-preview`로 일괄 수정.
    - 기존 FAISS 인덱스 삭제 (모델 차원 불일치 대응).
- **결과(Result)**: 코드와 문서가 완벽히 일치하며, 공식 API 권장 사양에 맞게 설정 최적화 완료.

### [2026-04-12] 모델 안정화: gemini-2.5-flash + gemini-embedding-001 전환
- **상황(Situation)**: `gemini-3-flash` 모델이 `v1beta` API에서 404 NOT_FOUND 에러 발생. `gemini-2.0-flash`는 무료 할당량 초과(429). `gemini-embedding-2-preview`도 배치 임베딩 시 라이브러리 호환성 이슈 지속.
- **조사(Investigation)**: `client.models.list()`로 사용 가능한 모델 목록을 직접 확인. `gemini-3-flash`는 `gemini-3-flash-preview`로만 존재, `gemini-2.5-flash`가 정식 사용 가능 확인.
- **결정(Action)**:
    - LLM: `gemini-2.5-flash` (정식 출시, 안정적)
    - Embedding: `gemini-embedding-001` (정식 출시, `task_type` 지원)
    - 프로젝트 전체 문서 7개 일괄 수정 (README, ARCHITECTURE, AGENTS, SKILL, rag_strategy 등)
- **결과(Result)**: 모든 API 호출이 정식 출시 모델을 사용하게 되어 안정성 대폭 향상. 프리뷰 모델의 불안정성 이슈 완전 해소.

### [2026-04-12] 인덱스 로드 로직 안전화 (모델 변경 대응)
- **상황(Situation)**: `gemini-3-flash` 및 `text-embedding-004`로 업그레이드한 후, 기존의 다른 차원 모델로 생성된 인덱스 파일이 존재할 경우 앱 실행 시 크래시가 발생할 수 있음.
- **결정(Action)**: `get_vectorstore` 함수에 예외 처리(try-except)를 추가하여 로드 실패 시 에러를 방지하고 사용자에게 재구축을 안내하도록 수정.
- **결과(Result)**: 모델 변경 시에도 앱의 안정성이 유지되며, README에 기술된 '자동 갱신 및 안내' 로직을 실질적인 코드로 뒷받침함.

### [2026-04-12] 포트폴리오 최적화(Checklist 반영) 및 문서 심화 업데이트
- **상황(Situation)**: 초기 README가 단순히 기능 나열에 그쳤다면, 실제 포트폴리오 활용을 위해 '문제 정의', '설계 철학', '기술 선택 근거' 등 더 깊이 있는 내용이 필요했음.
- **결정(Action)**: 
    - `PORTFOLIO_CHECKLIST.md`를 전수 조사하여 누락된 핵심 항목(타겟 페르소나, 핵심 구현 상세, 자가 성찰)을 README에 통합.
    - **문제 정의 섹션 추가**: 개발 동기 및 핵심 가치 구체화.
    - **기술 선택 이유(Rationale)**: `uv`, `Gemini 3 Flash`, `FAISS` 등을 선택한 기술적 이유 기술.
    - **미래 로드맵**: RAG 고도화 및 멀티모달 확장 계획 수립.
- **결과(Result)**: 결과물 중심의 단순 문서에서 개발자의 사고 과정과 문제 해결 능력을 보여주는 '프리미엄 포트폴리오 문서'로 탈바꿈함.

### [2026-04-12] 프로젝트 공식 문서(README.md) 작성 및 브랜딩 강화
- **상황(Situation)**: 프로젝트의 전체적인 모습과 기술 스택을 한눈에 파약하고, 외부 사용자나 평가자에게 프로젝트의 가치를 전달할 공식 문서가 부재했음.
- **결정(Action)**: 
    - **README.md**: 프로젝트 소개, 주요 기능, 시스템 아키텍처(Mermaid), 기술 스택, 실행 가이드(uv 기반) 등을 포함한 종합 문서 작성.
    - **브랜딩**: 프리미엄한 디자인 감각을 위해 뱃지, 이모지, 명확한 섹션 구분을 적용하여 포트폴리오 가시성 증대.
- **결과(Result)**: 프로젝트의 완성도가 대외적으로 증명 가능한 수준으로 향상되었으며, 누구나 `uv run main.py` 한 줄로 프로젝트를 실행해 볼 수 있는 사용자 친화적 환경 구축 완료.

### [2026-04-12] 워크스페이스 최적화 및 불필요 리소스 제거
- **상황(Situation)**: Antigravity 시스템 분석을 위해 임시로 포함되었던 `Google Antigravity Documentation.html` 및 관련 리소스 폴더가 Skill/Agent 설정 완료 후 불필요해짐.
- **결정(Action)**: 지식 추출이 완료된 외부 문서와 대용량 리소스 폴더(`_files`)를 삭제하여 워크스페이스를 정렬함.
- **결과(Result)**: 프로젝트 구조가 간결해지고, Git 저장소 및 로컬 환경의 가독성이 향상됨.

### [2026-04-12] Antigravity 전문 개발 프로토콜 및 전용 스킬 도입
- **상황(Situation)**: 에이전트(Antigravity)가 프로젝트의 맥락을 완벽히 이해하고, 일관된 품질(uv 사용, 기록 관리 등)을 유지하며 개발을 가이드할 전용 지침이 필요했음.
- **결정(Action)**: 
    - **Skill 개발**: `.agents/skills/quiz_chatbot_expert` 폴더를 생성하고 `SKILL.md`를 작성하여 퀴즈 생성 로직 및 개발 프로세스 표준화.
    - **Agent 설정**: `AGENTS.md`를 업데이트하여 에이전트의 역할과 '포트폴리오 중심 기록' 원칙을 공식화함.
- **결과(Result)**: 향후 모든 에이전트 세션에서 프로젝트 고유의 'Core Protocol'이 자동으로 적용되어, 수동 가이드 없이도 고퀄리티 개발 및 기록 유지가 가능해짐.
- **기여**: Google Antigravity Documentation을 분석하여 프로젝트에 최적화된 'Skills' 시스템을 구축함.

### [2026-04-12] 모델 엔진 업그레이드 및 환경 정비
- **상황(Situation)**: 초기 `gemini-2.5-flash-lite` 및 `gemini-embedding-001` 모델을 사용 중이었으나, 서비스 퀄리티 향상을 위해 최첨단 모델로의 업그레이드가 필요했음.
- **결정(Action)**: 
    - LLM: `gemini-3-flash` (속도와 지능의 최적 밸런스)
    - Embedding: `text-embedding-004` (정식 출시된 안정적인 최신 텍스트 최적화 모델)
- **이슈 & 해결(Troubleshooting)**: 
    - **이슈**: 임베딩 모델 변경 시 기존 FAISS 인덱스와의 벡터 차원 불일치 에러 발생 가능성 인지.
    - **해결**: 사용자에게 기존 `faiss_index_pdf_quiz` 폴더 삭제 및 인덱스 재생성 필요성을 강력하게 안내함.
- **배운 점(Learning)**: 모델 업그레이드 시 단순 코드 변경뿐만 아니라, 기존 영속 데이터(Vector DB)와의 호환성 체크가 필수적임을 재확인함.

---
*(이후 발생하는 이슈와 해결 과정은 이 아래에 역순으로 기록합니다.)*

### [2026-04-12] 임베딩 리스트 길이 불일치(ValueError) 최종 해결 (Robust Embedding 도입)
- **상황(Situation)**: `task_type` 지정 후에도 특정 환경에서 `doc(2) != embedding(1)` 에러 지속 발생.
- **원인(Cause)**: `gemini-embedding-2-preview` 프리뷰 모델 사용 시, `langchain-google-genai` 라이브러리의 배치 임베딩(`embed_documents`) 로직이 입력 리스트를 단일 리퀘스트로 묶으면서 응답을 단일 벡터로 잘못 파싱하는 라이브러리 내부 이슈 발견.
- **결정(Action)**: 
    - `FAISS.from_documents` 대신 `embed_query`를 활용한 **수동 개별 임베딩 생성** 로직 도입.
    - 리스트 컴프리헨션을 통해 각 청크를 독립적으로 임베딩하여 리스트 길이를 100% 일치시킴.
    - `task_type`을 대문자 `RETRIEVAL_DOCUMENT` 표준 규격으로 통일.
- **결과(Result)**: 모델이나 라이브러리의 배치 처리 버그에 상관없이 모든 PDF를 안정적으로 분석 가능함. 시스템 신뢰성(Reliability) 대폭 향상.

### [2026-04-12] 임베딩 모델 gemini-embedding-2-preview 적용 및 v1beta 설정
- **상황(Situation)**: 프로젝트 기획에 맞춰 최신 프리뷰 모델인 `gemini-embedding-2-preview`를 사용하여 임베딩 성능을 극대화하기로 결정.
- **결정(Action)**: 
    - `GoogleGenerativeAIEmbeddings`의 모델명을 `gemini-embedding-2-preview`로 변경.
    - 해당 모델이 프리뷰 단계이므로 안정적인 동작을 위해 `version="v1beta"`로 API 버전 조정.
- **결과(Result)**: 최첨단 임베딩 기술을 프로젝트에 도입 완료. 차세대 Gemini 생태계를 활용한 향후 확장성(멀티모달 등) 기반 마련.

### [2026-04-12] 임베딩 모델 404 NOT_FOUND 에러 해결 (API v1 명시)
- **상황(Situation)**: `text-embedding-004` 모델로 변경 후 `uv run main.py` 실행 시 `404 NOT_FOUND` 에러 발생. (에러 메시지: `models/text-embedding-004 is not found for API version v1beta`)
- **원인(Cause)**: `langchain-google-genai` 라이브러리가 기본적으로 `v1beta` 엔드포인트를 호출하려 했으나, `text-embedding-004` 모델은 `v1` 및 특정 명명 규칙을 따를 때 더 안정적으로 동작함.
- **결정(Action)**: 
    - `GoogleGenerativeAIEmbeddings` 초기화 시 `version="v1"`을 명시하여 최신 안정화 API 버전을 강제 지정.
    - 모델 이름에서 `models/` 접두사를 코드상에서 제거하여 라이브러리 내부 정규화 로직에 맡김.
- **결과(Result)**: 404 에러가 해결되고 앱이 정상 실행됨. 최신 모델을 사용하면서도 호환성 이슈를 완벽히 해결함.
