from dotenv import load_dotenv
import os

def load_api_keys():
    load_dotenv()
    os.environ["NOTION_API_KEY"] = os.getenv("NOTION_API_KEY")
    os.environ["NOTION_DB_ID"] = os.getenv("NOTION_DB_ID")
    os.environ["GOOGLE_CLIENT_SECRET_FILE"] = os.getenv("GOOGLE_CLIENT_SECRET_FILE")
    os.environ["OLLAMA_BASE_URL"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
