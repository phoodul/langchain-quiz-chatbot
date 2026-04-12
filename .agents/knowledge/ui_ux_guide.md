# 🎨 UI/UX Design & State Guide Knowledge

이 지식은 Streamlit을 활용한 챗봇의 인터페이스 설계 및 사용자 경험 기준을 정의합니다.

## 1. Design Principles (Premium UI)
- **Typography**: Google Sans Flex 등 고품질 폰트 적용 고려.
- **Color Contrast**: 텍스트 가독성을 최우선으로 하며, Streamlit의 테마 시스템을 적극 활용합니다.
- **Micro-animations**: `st.spinner`, `st.status` 등을 사용하여 AI의 처리 과정을 시각적으로 피드백합니다.

## 2. State Management (`st.session_state`)
- **Persistence**: 대화 기록(`messages`), 분석된 컨텍스트(`pdf_context`), 벡터 DB 로드 여부 등을 세션 상태로 유지합니다.
- **Rerender handling**: 사용자의 입력이나 모드 변경 시 `st.rerun()`을 적절히 호출하여 UI를 즉각 업데이트합니다.

## 3. Interaction Flow
- **Mode Switching**: '퀴즈 풀기'와 '질문하기' 모드 간의 명확한 구분 및 상태 전환 가이드를 제공합니다.
- **Error Feedback**: JSON 파싱 오류나 PDF 로직 실패 시 사용자에게 직관적인 안내 메시지를 노출합니다.
