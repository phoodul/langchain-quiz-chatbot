from typing import Annotated, Sequence, TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    LangGraph 에이전트 간의 공유 상태를 정의합니다.
    """
    # 대화 이력 (add_messages를 통해 리스트가 계속 누적됨)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # PDF 관련 컨텍스트
    pdf_context: str
    
    # 현재 모드 (quiz, tutor, counselor)
    current_mode: str
    
    # 현재 진행 중인 퀴즈 데이터
    current_question: Dict[str, Any]
    
    # 틀린 문제 데이터베이스
    wrong_answers: List[Dict[str, Any]]
    
    # 다음으로 이동할 에이전트 제어용 (Optional)
    next_step: str
    
    # 멀티모달 확장용: 업로드된 이미지 데이터 (base64 또는 URI 등)
    image_context: Optional[str]
