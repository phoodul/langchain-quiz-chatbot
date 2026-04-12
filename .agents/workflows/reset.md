# 🗑️ Reset Vector Database Workflow

이 워크플로우는 기존의 FAISS 인덱스를 삭제하여 새로운 인덱싱을 준비합니다. 모델 사양이 변경되었을 때 필수적으로 수행해야 합니다.

// turbo
1. **인덱스 폴더 삭제**: 기존 저장된 벡터 데이터를 제거합니다.
   ```powershell
   rm -rf faiss_index_pdf_quiz
   ```

2. **작업 완료 확인**: 폴더가 정상적으로 삭제되었는지 확인하고, `uv run main.py`를 통해 다시 인덱싱을 시작하세요.
