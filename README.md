
# 🧠 AI Personal Memory Layer

This project is a **local AI-powered memory assistant** that integrates your **Gmail**, **Notion**, and **Google Calendar** data into a unified searchable memory. It uses **RAG (Retrieval-Augmented Generation)** with **local LLMs (via Ollama)** to answer questions about your digital life—fully on your machine.

---

## ✨ Features

- 📧 Retrieve recent Gmail emails
- 📅 Extract events from Google Calendar
- 🗃️ Load structured notes from Notion
- 🧠 Build a vector-based memory using FAISS
- 💬 Ask natural language questions about your own data
- 🔒 100% private, runs locally using **Ollama**

---

## ⚙️ Technologies Used

- 🧠 LangChain + FAISS for RAG
- 🗃️ Notion API
- 📧 Gmail + Google Calendar API
- 🧪 Local LLMs via [Ollama](https://ollama.com/)
- 🐳 Docker (optional)
- 🐍 Python 3.9+

---

## 📁 Project Structure

```
personal_memory_ai/
├── main.py                    # Entry point
├── config.py                  # Loads environment variables
├── .env                       # Secrets file
├── loaders/
│   ├── gmail_loader.py
│   ├── calendar_loader.py
│   └── notion_loader.py
├── memory/
│   ├── vectorstore.py
│   └── rag_chain.py
├── agent/
│   └── memory_agent.py
├── ui/
│   └── chat_terminal.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🚀 How to Run This Project

### 1. ✅ Prerequisites

- Python 3.9+
- `pip install -r requirements.txt`
- [Install Ollama](https://ollama.com/) and run a model like `llama3`

```bash
ollama serve
ollama run llama3
```

### 2. 🛠 Set Up APIs

#### 🔐 Create `.env` file with:

```env
OPENAI_API_KEY=sk-...         # Optional if using OpenAI fallback
NOTION_API_KEY=secret_xxxx    # From https://www.notion.so/my-integrations
NOTION_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CLIENT_SECRET_FILE=credentials.json
```

#### 🔑 Google Setup:

- Go to [Google Cloud Console](https://console.cloud.google.com)
- Enable Gmail API and Calendar API
- Create OAuth credentials (`Desktop App`)
- Download `credentials.json` and place it in project root
- Add your Google account as test user under OAuth Consent Screen

### 3. 🧪 Run for the First Time

```bash
python main.py
```

- A browser will open for Gmail & Calendar auth
- Authorize the app
- The assistant will index your emails, notes, and events

### 4. 💬 Start Chatting

```
You: What was my last Gmail about?
You: What's on my calendar this week?
You: Summarize my Notion meeting notes.
```

---

## 🔄 Docker Option

```bash
docker-compose build
docker-compose up
```

---

## 🧠 Local LLM via Ollama

You can replace OpenAI with a local model using LangChain Ollama integration:

```python
from langchain_community.llms import Ollama
llm = Ollama(model="llama3")
```

---

## 📌 Notes

- Make sure `.env` and `credentials.json` are correctly set
- Ollama must be running in background
- You can load `.pdf` or `.txt` files later via `personal_docs/`

---

## 🧑‍💻 Maintainer

Built for high-impact personal productivity. Customize it to use other APIs or memory stores.

