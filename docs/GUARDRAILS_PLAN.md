# 🛡️ 가드레일 시스템 구현 태스크 리스트

이 문서는 `01_guardrails.ipynb`에서 검증된 4계층 가드레일 시스템을 프로젝트에 통합하기 위한 구체적인 실행 계획을 담고 있습니다.

## 1. 기반 구조 준비
- [x] `src/guardrails.py` 신규 파일 생성
- [x] 가드레일용 상수 정의 (차단 키워드, 상담 이관 키워드 등)
- [x] 정규표현식(Regex)을 이용한 개인정보 패턴(전화번호, 이메일) 정의

## 2. 가드레일 미들웨어 구현 (`src/guardrails.py`)
- [x] **Layer 1: 입력 필터 (`education_guardrail`)**
    - [x] 부정행위(cheating), 학습 방해(distraction), 유해 주제(harmful) 키워드 매칭 로직 구현
- [x] **Layer 2: 개인정보 보호 (`student_safety_middleware`)**
    - [x] Regex 매칭 및 마스킹 처리 로직 구현
- [x] **Layer 3: 상담 이관 (`counseling_escalation_middleware`)**
    - [x] 심리적 위기 키워드 감지 시 AI 답변 중단 및 안내 멘트 출력 로직 구현
- [x] **Layer 4: 출력 필터 (`answer_leakage_guardrail`)**
    - [x] 감독용 모델(`gemini-2.5-flash-lite`)을 활용한 답변 검증 및 교정 로직 구현 (Prompt Engineering 포함)

## 3. 에이전트 통합 (`src/quiz_chatbot.py`)
- [x] `initialize_agent` 함수에서 `create_agent` 호출 시 `middleware` 인자 추가
- [x] 구현된 4개의 가드레일 함수를 계층 순서대로 등록
- [x] 필요한 모듈 임포트문 추가

## 4. 기록 및 검증
- [x] `HISTORY.md`에 가드레일 시스템 도입 배경 및 구현 상세 기록
- [x] 다음 5가지 시나리오에 대한 수동 테스트 수행 및 결과 확인
    - [x] 숙제 대행 요청 차단
    - [x] 학습과 무관한 게임/연예 주제 독려 전환
    - [x] 개인정보 입력 시 마스킹 처리
    - [x] 위험 키워드 입력 시 상담 안내 활성화
    - [x] 질문에 대한 직접적 정답 유출 교정

---
*참조: 01_guardrails.ipynb*
