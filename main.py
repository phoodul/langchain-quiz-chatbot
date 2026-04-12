import sys
from streamlit.web import cli as stcli

def main() -> None:
    """Streamlit 애플리케이션을 실행하는 메인 함수입니다."""
    sys.argv = ["streamlit", "run", "src/quiz_chatbot.py"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
