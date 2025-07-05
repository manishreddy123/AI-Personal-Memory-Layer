from config import load_api_keys
from loaders.gmail_loader import load_gmail_emails
from loaders.notion_loader import load_notion_pages
from loaders.calendar_loader import load_calendar_events
from memory.vectorstore import build_vectorstore
from memory.rag_chain import build_qa_chain
from agent.memory_agent import build_agent
from ui.chat_terminal import run_chat

if __name__ == "__main__":
    load_api_keys()
    local_data = []  # You can add file loaders later
    gmail_data = load_gmail_emails()
    notion_data = load_notion_pages()
    calendar_data = load_calendar_events()

    all_data = local_data + gmail_data + notion_data + calendar_data
    vectorstore = build_vectorstore(all_data)
    qa_chain = build_qa_chain(vectorstore)
    agent = build_agent(qa_chain)
    run_chat(agent)
