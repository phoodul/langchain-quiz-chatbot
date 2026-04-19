from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.schema import AgentState

# 의도 분류 결과를 담을 스키마 정의
class IntentClassification(BaseModel):
    """사용자의 입력을 분류한 결과입니다."""
    intent: Literal["quiz", "tutor", "counselor"] = Field(
        description="사용자의 의도 분류 (quiz: 퀴즈 생성/풀이, tutor: 정보 검색/질문, counselor: 고민 상담/일상 대화)"
    )
    reason: str = Field(description="해당 의도로 분류한 이유")

def router_node(state: AgentState):
    """
    사용자의 마지막 메시지를 분석하여 의도를 분류하고 current_mode를 결정합니다.
    """
    if not state.get("messages"):
        return {"current_mode": "tutor"} # 기본 모드로 설정
        
    last_message = state["messages"][-1].content.strip()
    
    # [최적화] 퀴즈 진행 중 숫자가 입력되면 즉시 quiz 모드로 고정
    if last_message.isdigit() and state.get("current_question"):
        return {
            "current_mode": "quiz"
        }

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    structured_llm = llm.with_structured_output(IntentClassification)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 교육용 AI 챗봇의 지휘관입니다. 사용자의 메시지를 분석하여 '퀴즈 풀기(quiz)', '학습 질문/문서 검색(tutor)', '고민 상담/상담 이관(counselor)' 중 하나로 분류하세요."),
        ("human", "{user_input}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({"user_input": last_message})
    
    # 상태 업데이트
    return {
        "current_mode": result.intent
    }
