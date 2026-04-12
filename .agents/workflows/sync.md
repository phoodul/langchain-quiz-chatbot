# 📦 Environment Sync Workflow

이 워크플로우는 `uv`를 사용하여 프로젝트의 가상 환경과 의존성을 최신 상태로 동기화합니다.

// turbo
1. **의존성 동기화**: `uv.lock` 파일을 기반으로 패키지를 최신화합니다.
   ```powershell
   uv sync
   ```

2. **환경 확인**: `.venv` 폴더가 정상적으로 업데이트되었는지 확인합니다.
