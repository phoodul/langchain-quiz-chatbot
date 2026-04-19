from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.schema import AgentState

# 퀴즈 문제 스키마 정의
class QuizQuestion(BaseModel):
    """생성된 퀴즈 문제 정보입니다."""
    question: str = Field(description="문제 질문 내용")
    options: List[str] = Field(description="4개의 선택지 리스트 (예: ['1. 보기', ...])")
    answer: str = Field(description="정답 번호 (1~4 중 하나)")
    explanation: str = Field(description="정답에 대한 상세 해설")

def quiz_master_node(state: AgentState):
    """
    퀴즈를 생성하거나 사용자의 정답을 채점합니다.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    structured_llm = llm.with_structured_output(QuizQuestion)
    
    last_message = state["messages"][-1]
    
    # 만약 마지막 사용자 메시지가 숫자로 되어 있다면 '채점' 로직 수행
    if last_message.content.strip().isdigit() and state.get("current_question"):
        user_ans = last_message.content.strip()
        q_data = state["current_question"]
        correct_ans = q_data["answer"]
        
        if user_ans == correct_ans:
            response_text = f"✅ 정답입니다! 🎉\n\n해설: {q_data['explanation']}\n\n다음 문제를 준비해 드릴까요?"
            return {
                "messages": [AIMessage(content=response_text)],
                "current_question": None # 문제 풀이 완료
            }
        else:
            response_text = (
                f"❌ 오답입니다. 정답은 {correct_ans}번입니다.\n\n"
                f"해설: {q_data['explanation']}\n\n"
                "혹시 이 내용이 잘 이해가 안 가시나요? '더 자세히 설명해줘'라고 말씀하시면 제가 관련 내용을 튜터 모드로 쉽게 알려드릴게요!"
            )
            # 오답 노트에 추가
            new_wrongs = state.get("wrong_answers", [])
            new_wrongs.append(q_data)
            return {
                "messages": [AIMessage(content=response_text)],
                "wrong_answers": new_wrongs,
                "current_question": None
            }

    # 숫자가 아니거나 현재 진행 중인 문제가 없다면 '퀴즈 생성' 로직 수행
    system_prompt = """당신은 교육용 AI 퀴즈 박사입니다. 제공된 텍스트 또는 이미지에서 
    학습 목표에 부합하는 4지선다 객관식 문제를 1개 생성하세요. 
    반드시 한국어로 작성하고, 정답에 대한 논리적인 해설을 포함하세요."""
    
    # 멀티모달 입력 구성
    content = [{"type": "text", "text": "새로운 문제를 하나 내주세요."}]
    
    if state.get("image_context"):
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{state['image_context']}"}
        })
    
    # 텍스트 컨텍스트 추가
    text_context = state["pdf_context"] or "제공된 텍스트가 없습니다."
    content[0]["text"] += f"\n\n텍스트 컨텍스트: {text_context}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", content)
    ])
    
    chain = prompt | structured_llm
    new_q = chain.invoke({})
    
    quiz_msg = f"📝 **새로운 문제**\n\n{new_q.question}\n\n" + "\n".join(new_q.options)
    
    return {
        "messages": [AIMessage(content=quiz_msg)],
        "current_question": new_q.model_dump()
    }
