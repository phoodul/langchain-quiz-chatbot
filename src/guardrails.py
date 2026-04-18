import re
from langchain.agents.middleware import before_agent, after_agent
from langchain.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# [Layer 1] 교육적 가드레일 차단 키워드
FORBIDDEN_TOPICS = {
    "cheating": ["답지", "정답 알려줘", "숙제 대신", "써줘", "베끼기"],
    "distraction": ["롤", "게임", "유튜브", "아이돌", "웹툰", "웃긴"],
    "harmful": ["담배", "술", "폭력", "싸움", "바보"]
}

# [Layer 2] 개인정보 보호 정규표현식 패턴
PHONE_PATTERN = r'01[016789]-?[0-9]{3,4}-?[0-9]{4}'
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# [Layer 3] 상담 이관(Escalation) 키워드
ESCALATION_KEYWORDS = [
    "왕따", "괴롭힘", "우울해", "학교 폭력", "상담 선생님", "사람 불러줘",
    "죽고 싶어", "괴로워", "도와줘요"
]

# 응답 메시지 정의
GUARDRAIL_RESPONSES = {
    "cheating": "🚫 스스로 고민해봐야 실력이 늘어요! 정답을 바로 알려드리는 대신, 힌트를 드릴까요? 어떤 부분이 가장 어려운지 말해주세요.",
    "distraction": "⏰ 지금은 공부에 집중할 시간이에요! 딴짓은 쉬는 시간에 하고, 지금 풀고 있는 문제에 집중해볼까요?",
    "harmful": "⚠️ 부적절한 대화 주제입니다. 바르고 고운 말을 사용해주세요.",
    "privacy": "🔒 [학생 보호] 개인정보(전화번호, 이메일 등)가 감지되어 안전을 위해 마스킹 처리되었습니다.",
    "escalation": "학생, 많이 힘들었겠구나. 이 문제는 내가 답변하기보다는 전문 상담 선생님이 직접 듣고 도와주시는 게 좋을 것 같아. \n\n지금 바로 상담 선생님께 연결해 드렸으니 잠시만 기다려 줄래? 🍀 (상담실 연결 중...)"
}

# 출력 검증용 모델 초기화 (Layer 4)
safety_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

@before_agent(can_jump_to=["end"])
def education_guardrail(state, runtime):
    """부정행위, 학습 방해, 유해 콘텐츠를 사전에 필터링합니다."""
    if not state.get("messages"): return None
    last_message = state["messages"][-1]
    if last_message.type != "human": return None
    
    user_text = last_message.content

    # Case A: 부정행위 방지
    for keyword in FORBIDDEN_TOPICS["cheating"]:
        if keyword in user_text:
            return {
                "messages": [{"role": "assistant", "content": GUARDRAIL_RESPONSES["cheating"]}],
                "jump_to": "end"
            }

    # Case B: 학습 집중 유도
    for keyword in FORBIDDEN_TOPICS["distraction"]:
        if keyword in user_text:
            return {
                "messages": [{"role": "assistant", "content": GUARDRAIL_RESPONSES["distraction"]}],
                "jump_to": "end"
            }

    # Case C: 유해 콘텐츠 차단
    for keyword in FORBIDDEN_TOPICS["harmful"]:
        if keyword in user_text:
            return {
                "messages": [{"role": "assistant", "content": GUARDRAIL_RESPONSES["harmful"]}],
                "jump_to": "end"
            }
    
    return None

@before_agent
def student_safety_middleware(state, runtime):
    """사용자 입력에서 개인정보를 감지하여 마스킹합니다."""
    if not state.get("messages"): return None
    last_message = state["messages"][-1]
    if last_message.type != "human": return None

    content = last_message.content
    is_redacted = False

    if re.search(PHONE_PATTERN, content):
        content = re.sub(PHONE_PATTERN, "<PHONE_REDACTED>", content)
        is_redacted = True

    if re.search(EMAIL_PATTERN, content):
        content = re.sub(EMAIL_PATTERN, "<EMAIL_REDACTED>", content)
        is_redacted = True

    if is_redacted:
        # 메시지 내용을 수정하여 LLM에게 전달
        last_message.content = content
        # 콘솔 로깅 (디버깅용)
        print(f"🔒 [개인정보 보호] 마스킹 처리 완료")
        
    return None

@before_agent(can_jump_to=["end"])
def counseling_escalation_middleware(state, runtime):
    """위기 상황 시 인간 상담원 연결 안내를 수행합니다."""
    if not state.get("messages"): return None
    last_message = state["messages"][-1]
    if last_message.type != "human": return None

    for keyword in ESCALATION_KEYWORDS:
        if keyword in last_message.content:
            return {
                "messages": [{"role": "assistant", "content": GUARDRAIL_RESPONSES["escalation"]}],
                "jump_to": "end"
            }
            
    return None

@after_agent
def answer_leakage_guardrail(state, runtime):
    """생성된 답변이 직접적인 정답 유출인지 검사하고 필요 시 교정합니다."""
    if not state.get("messages"): return None
    last_message = state["messages"][-1]

    # 마지막 메시지가 AI 응답인 경우에만 검사
    if not isinstance(last_message, AIMessage):
        return None

    auditor_prompt = f"""
    당신은 엄격한 교육 감독관입니다.
    다음 '튜터의 답변'을 확인하세요.
    답변이 학생을 지도하지 않고 문제의 정답이나 전체 풀이를 직접적으로 제공한다면 'LEAKED'라고 답하세요.
    답변이 적절한 힌트나 설명을 제공한다면 'SAFE'라고 답하세요.

    튜터의 답변: {last_message.content}
    """

    result = safety_model.invoke([{"role": "user", "content": auditor_prompt}])

    if "LEAKED" in str(result.content):
        print(f"🚨 [가드레일 발동] 정답 유출 감지됨! 답변을 수정합니다.")
        last_message.content = "앗, 제가 정답을 바로 말할 뻔했네요! 😅 정답보다는 푸는 방법을 먼저 생각해볼까요? 이 주제의 핵심 개념부터 차근차근 짚어봅시다."

    return None
