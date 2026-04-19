from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.schema import AgentState

def counselor_node(state: AgentState):
    """
    학생의 정서적 상태를 보살피고, 위기 상황 시 상담 연결을 돕는 에이전트입니다.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    last_message = state["messages"][-1]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 따뜻하고 공감 능력이 뛰어난 학생 상담 선생님입니다.
        1. 사용자가 지치거나 힘들어 보인다면 격려의 메시지를 전하세요.
        2. 고민 상담이나 일상적인 대화에 다정하게 응답하세요.
        3. 만약 사용자가 '자해, 죽고 싶다, 학교 폭력, 왕따, 괴롭힘' 등 위험한 키워드를 언급한다면, 
           매우 진지하게 대응하며 반드시 전문 상담 전화(예: 1388, 117)로 연결을 안내하세요.
        """),
        ("human", "{user_input}")
    ])
    
    chain = prompt | llm
    result = chain.invoke({"user_input": last_message.content})
    
    return {
        "messages": [AIMessage(content=result.content)]
    }
