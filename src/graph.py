from langgraph.graph import StateGraph, END
from src.schema import AgentState
from src.agents.router import router_node
from src.agents.quiz_master import quiz_master_node
from src.agents.study_tutor import study_tutor_node
from src.agents.counselor import counselor_node
from src.agents.auditor import auditor_node

def create_graph():
    """
    모든 에이전트 노드를 연결하여 LangGraph 워크플로우를 구축합니다.
    """
    workflow = StateGraph(AgentState)

    # 1. 노드 추가
    workflow.add_node("router", router_node)
    workflow.add_node("quiz_master", quiz_master_node)
    workflow.add_node("study_tutor", study_tutor_node)
    workflow.add_node("counselor", counselor_node)
    workflow.add_node("auditor", auditor_node)

    # 2. 엣지 연결 설정 (Entry Point: Router)
    workflow.set_entry_point("router")

    # 3. Router 결과에 따른 조건부 분기
    workflow.add_conditional_edges(
        "router",
        lambda state: state["current_mode"],
        {
            "quiz": "quiz_master",
            "tutor": "study_tutor",
            "counselor": "counselor"
        }
    )

    # 4. 각 에이전트 실행 후 Auditor로 이동
    workflow.add_edge("quiz_master", "auditor")
    workflow.add_edge("study_tutor", "auditor")
    workflow.add_edge("counselor", "auditor")

    # 5. Auditor 검수 후 종료
    workflow.add_edge("auditor", END)

    # 6. 그래프 컴파일
    return workflow.compile()

# 전역 그래프 객체 생성
app = create_graph()
