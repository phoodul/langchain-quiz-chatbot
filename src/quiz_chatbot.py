import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import tempfile
import os
import json
import re
import base64
from dotenv import load_dotenv

# .env 파일 로드 (모듈 임포트 전 실행)
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from src.graph import app as graph_app

# --- [초기 설정] ---
# 모델 초기화 (누락된 chat 객체 추가)
chat = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="RETRIEVAL_DOCUMENT",
)
db_path = "faiss_index_pdf_quiz"

# 세션 상태 초기화 (UI 상태 유지용)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "mode" not in st.session_state:
    st.session_state.mode = "관찰 중" # Router가 판단하도록 함
if "image_context" not in st.session_state:
    st.session_state.image_context = None


# --- [유틸리티 함수: 스캐폴딩 제공] ---
def parse_ai_json(ai_response):
    """AI 응답에서 JSON 부분을 추출하여 파싱합니다."""
    try:
        json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        st.error(f"JSON 파싱 오류: {e}")
    return None


@st.cache_resource
def get_vectorstore():
    """FAISS 저장소가 있으면 로드합니다. 모델 변경 등으로 로드 실패 시 예외 처리합니다."""
    if os.path.exists(db_path):
        try:
            return FAISS.load_local(
                db_path, embeddings, allow_dangerous_deserialization=True
            )
        except Exception as e:
            st.error(f"기존 인덱스 로드 실패(모델 차원 불일치 등): {e}")
            st.warning("새로운 PDF를 업로드하여 인덱스를 재생성해 주세요.")
    return None


st.session_state.vectorstore = get_vectorstore()


def load_and_parse_pdf(pdf_path: str) -> None:
    # (주의: embeddings, db_path 등은 scaffold의 전역 변수나 세션 상태를 활용한다고 가정)
    # 1. PDF 로드 (하나의 객체로 로드됨)
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    # 2. 텍스트 분할 (청크 크기 1000, 겹침 100)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = text_splitter.split_documents(docs)

    # 3. 벡터스토어 생성 및 로컬 저장 (안전한 개별 임베딩 방식 사용)
    with st.spinner("벡터 데이터 생성 중..."):
        texts = [doc.page_content for doc in split_docs]
        metadatas = [doc.metadata for doc in split_docs]

        # 모델의 배치 처리 버그 대응을 위해 개별 임베딩 수행
        embedded_docs = [embeddings.embed_query(text) for text in texts]

        st.session_state.vectorstore = FAISS.from_embeddings(
            text_embeddings=zip(texts, embedded_docs),
            embedding=embeddings,
            metadatas=metadatas,
        )

    st.session_state.vectorstore.save_local(db_path)

    # 캐시 초기화 (새로운 PDF가 로드되면 캐시된 벡터스토어를 지워야 함)
    get_vectorstore.clear()

    # 전체 컨텍스트 저장 (퀴즈 생성용)
    st.session_state.pdf_context = "\n".join([doc.page_content for doc in docs])


@tool
def search_pdf_documents(query: str) -> str:
    """업로드된 PDF 문서 내에서 정보를 검색합니다.
    사실 확인이나 전문적인 내용이 필요할 때 사용하세요.
    """
    # st.session_state에서 안전하게 vectorstore를 가져옵니다.
    # 에이전트 실행 시 스레드 분리 등으로 인해 session_state 접근이 불안정한 경우를 대비해 get_vectorstore()를 활용합니다.
    vectorstore = st.session_state.get("vectorstore")
    if vectorstore is None:
        vectorstore = get_vectorstore()

    if vectorstore is not None:
        # 벡터스토어에서 유사도 검색 수행 (k=3)
        docs = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in docs])
    return "검색할 문서가 없습니다."


def convert_to_langgraph_messages(streamlit_messages):
    """Streamlit 메시지 형식을 LangGraph 메시지 객체로 변환합니다."""
    lg_messages = []
    for m in streamlit_messages:
        if m["role"] == "user":
            lg_messages.append(HumanMessage(content=m["content"]))
        else:
            lg_messages.append(AIMessage(content=m["content"]))
    return lg_messages

def invoke_chatbot(user_input: str):
    """LangGraph를 통해 에이전트 워크플로우를 실행합니다."""
    # 1. 메시지 목록 구성 (사용자 입력 추가)
    messages = convert_to_langgraph_messages(st.session_state.messages)
    messages.append(HumanMessage(content=user_input))
    
    current_state = {
        "messages": messages,
        "pdf_context": st.session_state.pdf_context,
        "current_mode": "auto", # Router가 판단하도록 설정
        "current_question": st.session_state.current_question,
        "wrong_answers": st.session_state.wrong_answers,
        "image_context": st.session_state.image_context
    }
    
    # 2. 그래프 실행
    with st.spinner("에이전트들이 협업 중..."):
        # LangGraph invoke 실행
        result = graph_app.invoke(current_state)
    
    # 3. 결과 상태 업데이트 (동기화)
    # 마지막 AI 응답 가져오기
    last_ai_msg = result["messages"][-1].content
    
    st.session_state.current_question = result.get("current_question")
    st.session_state.wrong_answers = result.get("wrong_answers", [])
    st.session_state.mode = result.get("current_mode", "관찰 중")
    
    return last_ai_msg


# --- Streamlit UI 시작 ---
st.title("📖 PDF AI 퀴즈 챗봇")

# 사이드바 설정 영역
with st.sidebar:
    st.info(f"📍 현재 모드: **{st.session_state.mode}**")
    st.write("에이전트가 대화 맥락에 따라 모드를 자동으로 전환합니다.")

    if st.session_state.wrong_answers:
        st.write("---")
        st.write(f"❌ 틀린 문제: {len(st.session_state.wrong_answers)}개")
        if st.button("오답 노트 초기화"):
            st.session_state.wrong_answers = []
            st.rerun()

uploaded_file = st.file_uploader("학습 자료(PDF 또는 이미지)를 업로드하세요", type=["pdf", "png", "jpg", "jpeg"])
if st.button("학습 시작") and uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        with st.spinner("PDF 문서를 분석 중..."):
            load_and_parse_pdf(tmp_path)
            st.session_state.pdf_processed = True
            st.session_state.image_context = None # PDF 모드일 때는 이미지 제거
            
            resp = invoke_chatbot("안녕! 업로드한 PDF 파일로 공부를 도와줘.")
            st.session_state.messages.append({"role": "assistant", "content": resp})
        os.unlink(tmp_path)
    else:
        # 이미지 처리
        with st.spinner("이미지 분석 중..."):
            image_bytes = uploaded_file.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            st.session_state.image_context = encoded_image
            st.session_state.pdf_context = "" # 이미지 모드일 때는 텍스트 컨텍스트 초기화
            st.session_state.pdf_processed = True
            
            st.image(image_bytes, caption="업로드된 이미지", use_container_width=True)
            resp = invoke_chatbot("이 이미지의 내용을 바탕으로 문제를 내주거나 설명해줘.")
            st.session_state.messages.append({"role": "assistant", "content": resp})

# 대화 창 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 메시지 입력 및 답변 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    # PDF가 아직 처리되지 않은 경우 입력 차단
    if not st.session_state.pdf_processed:
        st.warning("먼저 PDF 파일을 업로드하고 '학습 시작'을 눌러주세요.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        resp = invoke_chatbot(prompt)
        st.write(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
