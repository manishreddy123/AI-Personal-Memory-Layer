
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
├── main.py
├── config.py
├── .env
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
- [Install Ollama](https://ollama.com/)

---

## 🔧 Setting Up Google Cloud APIs (Gmail & Calendar)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., `Personal Memory`)
3. Navigate to **APIs & Services > Library**
   - Enable **Gmail API** and **Google Calendar API**
4. Go to **APIs & Services > OAuth consent screen**
   - User type: `External`
   - Fill required fields
   - Add your Google account as a **test user**
5. Go to **Credentials > Create Credentials > OAuth Client ID**
   - Application type: `Desktop App`
   - Download the `credentials.json`
6. Place `credentials.json` in your project root

---

## 🗃️ Setting Up Notion API

1. Visit [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **+ New integration**
   - Name: `Personal Memory AI`
   - Capabilities: Check `Read content`
   - Submit and **copy your Internal Integration Token**
3. In Notion, open the database (table view)
   - Click **Share**
   - Invite your integration
4. Copy the database ID from the URL
   ```
   https://www.notion.so/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   Use the first 32-character string as `NOTION_DB_ID`

---

## 🦙 Setting Up Ollama & LLM (LLaMA)

1. Download Ollama from [https://ollama.com/download](https://ollama.com/download)
2. Install and restart terminal
3. Start Ollama server:
   ```bash
   ollama serve
   ```
4. Download and start a model (e.g., LLaMA 3):
   ```bash
   ollama run llama3
   ```

---

## 🛠 Create `.env` File

```env
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxx
NOTION_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CLIENT_SECRET_FILE=credentials.json
```

---

## 🧪 Run the App

```bash
python main.py
```

- Authorize access to Gmail and Calendar in browser
- Data will be loaded into local vectorstore
- Chat with your memory

---

## 💬 Example Queries

```
What was my last email about?
What’s on my calendar this week?
Summarize my recent Notion project notes.
```

---

## 🐳 Docker Option

```bash
docker-compose build
docker-compose up
```

---

## 🧠 LLM Integration (Ollama)

Use Ollama in LangChain like this:

```python
from langchain_community.llms import Ollama
llm = Ollama(model="llama3")
```

---

## 📌 Notes

- You can expand support to local PDFs, TXT, Markdown files
- Ollama must be running in the background
- Add error handling or UI using Streamlit optionally

---

