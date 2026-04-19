from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from src.schema import AgentState

def auditor_node(state: AgentState):
    """
    최종 응답의 교육적 적절성 및 품질을 검수하는 Safety/Quality Auditor 노드입니다.
    이전 에이전트가 생성한 응답을 검토하고 필요 시 교정합니다.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    # 마지막 에이전트 응답 가져오기
    messages = state["messages"]
    if not messages or not isinstance(messages[-1], AIMessage):
        # 만약 AI 메시지가 없다면(이례적 상황) 그대로 종료
        return {"messages": []}
    
    last_ai_msg = messages[-1].content
    last_human_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human_msg = msg.content
            break

    # 검수 프롬프트 구성
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 '교육용 AI 가드레일 감사관(Auditor)'입니다. 
AI 에이전트의 응답이 다음 기준을 만족하는지 확인하고, 최종적으로 학생에게 전달할 '최적의 응답'을 생성하세요.

[검수 기준]
1. **정답 유출 금지**: 학생이 질문을 했을 때 바로 정답을 알려주지 마세요. 대신 힌트를 주거나 스스로 생각하도록 유도하세요.
2. **교육적 말투**: 친절하고 격려하는 어투를 사용하세요. (예: "참 잘했어요!", "함께 고민해 볼까요?")
3. **부적절 내용 차단**: 비속어, 교육과 무관한 유해 내용이 포함되어 있다면 삭제하거나 정제하세요.
4. **일관성**: 이전 질문과 응답의 맥락이 자연스럽게 이어져야 합니다.

[사용자 질문]
{human_input}

[에이전트 초안 응답]
{ai_draft}"""),
        ("human", "위 가이드라인에 따라 응답을 최종 검수하여 학생에게 보낼 최종 메시지만 작성해 주세요. 내용이 적절하다면 초안을 그대로 유지해도 좋습니다.")
    ])
    
    chain = prompt | llm
    audited_response = chain.invoke({
        "human_input": last_human_msg,
        "ai_draft": last_ai_msg
    })
    
    # 기존 마지막 AIMessage를 교체하는 대신, 새로운 메시지를 추가하는 것이 LangGraph의 기본 동작입니다.
    # 하지만 여기서는 '검수된 최종 결과'를 내보내는 것이 목적이므로 
    # UI 단에서 마지막 메시지만 보여주도록 처리하거나, 상태 설계를 조정해야 할 수도 있습니다.
    # 여기서는 감사 완료된 메시지를 반환합니다.
    return {
        "messages": [AIMessage(content=audited_response.content)]
    }
