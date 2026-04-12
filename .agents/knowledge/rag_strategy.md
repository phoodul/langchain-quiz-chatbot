# 🧠 RAG Implementation Strategy Knowledge

이 지식은 프로젝트의 핵심인 RAG(Retrieval-Augmented Generation) 파이프라인의 설계 및 구현 원칙을 정의합니다.

## 1. Document Processing (PDF)
- **추출 엔진**: `PyMuPDFLoader`를 사용하여 텍스트 데이터의 무결성을 유지합니다.
- **분할(Chunking) 전략**: 
  - `RecursiveCharacterTextSplitter` 사용.
  - `chunk_size`: 1000
  - `chunk_overlap`: 100
  - 논리적 문맥 보존을 위해 문장 단위 분할을 선호합니다.

## 2. Embedding & Vector DB
- **Embedding Model**: `gemini-embedding-001` (정식 출시된 안정적인 텍스트 임베딩 모델)
- **Vector DB**: `FAISS` (Local 기반)
- **데이터 보존**: 인덱싱 후 `faiss_index_pdf_quiz` 폴더에 로컬 저장하여 세션 간 재사용을 보장합니다.

## 3. Retrieval & Prompting
- **검색 방식**: 유사도 검색(Similarity Search) 기반 `k=3` 설정.
- **도구 설계**: `search_pdf_documents` 도구를 통해 에이전트가 능동적으로 지식을 조회하도록 유도합니다.
- **출처 준수**: 답변 생성 시 반드시 검색된 문서 내의 정보만을 사용하며, 정보 부재 시 "모름"을 명확히 합니다.
