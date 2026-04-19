from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.schema import AgentState

def study_tutor_node(state: AgentState):
    """
    제공된 문서 내용을 바탕으로 사용자의 질문에 답변합니다. (RAG 기반 교육 튜터)
    특히 사용자가 틀린 문제(wrong_answers)가 있다면 해당 개념을 중점적으로 설명합니다.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    # 마지막 사용자 메시지
    last_message = state["messages"][-1]
    
    # 오답 노트 정보 구성
    wrong_context = ""
    if state.get("wrong_answers"):
        last_wrong = state["wrong_answers"][-1]
        wrong_context = f"\n\n[학습 보충 필요 사항]: 학생이 최근 '{last_wrong['question']}' 문제를 틀렸습니다. 이에 대한 오답 해설은 '{last_wrong['explanation']}'입니다. 이 개념과 연관된 내용을 중심으로 설명해 주세요."

    # 멀티모달 입력 구성
    human_content = [{"type": "text", "text": last_message.content}]
    
    if state.get("image_context"):
        human_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{state['image_context']}"}
        })

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""당신은 업로드된 학습 자료(텍스트 또는 이미지)를 전문적으로 설명하는 교육 튜터입니다.
        1. 반드시 제공된 '학습 컨텍스트'와 '학습 보충 필요 사항'에 기반하여 답변하세요.
        2. 학생이 특정 문제를 틀렸다면, 정답을 바로 말해주기보다 그 원리가 되는 개념을 쉽게 풀어서 설명해 주세요.
        3. 친절하고 격려하는 어조를 사용하세요. (예: "좋은 질문입니다!", "이 부분은 정말 중요해요.")
        
        학습 컨텍스트: {{context}}{wrong_context}"""),
        ("human", human_content)
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "context": state["pdf_context"] or "아직 분석된 문서가 없습니다.",
    })
    
    return {
        "messages": [AIMessage(content=result.content)]
    }
