# 🤖 Agentic RAG Framework

> **A minimal, extensible framework for building Agentic RAG applications.**

This project acts as a starter kit for building intelligent agents that can:
- **Retrieve Information**: Use Vector Search (RAG) to find relevant documents.
- **Make Decisions**: Decide when to answer directly and when to search.
- **Maintain Context**: Remember conversation history across sessions.
- **Scale**: Support both **OpenAI** and **Azure OpenAI** providers.

---

## ✨ Features

- **Tool Use**: The LLM intelligently calls the `search_docs` tool only when necessary.
- **Vector Search**: Includes a simple indexing pipeline for your local documents.
- **Session Memory**: Persists chat history to disk for continuity.
- **Dual Provider Support**: Seamlessly switch between OpenAI and Azure OpenAI.
- **API Ready**: Includes a FastAPI server for deployment.

---

## 📂 Project Structure

```text
src/
├── agentic_rag/
│   ├── chat.py         # CLI Chat Interface
│   ├── api.py          # FastAPI Server
│   ├── index.py        # Indexing Script
│   ├── agent.py        # Core Logic
│   └── ...
data/
├── docs/               # Place your policy documents here
└── index/              # Generated embeddings and index files
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.9+** installed.
- An API Key for **OpenAI** OR **Azure OpenAI**.

### 2. Installation

Clone the repository and set up the environment:

**Windows (PowerShell)**
```powershell
cd Agentic-RAG-framework
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**Mac/Linux**
```bash
cd Agentic-RAG-framework
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Configuration

Open `.env` and configure your credentials:

- **OpenAI**: Set `OPENAI_API_KEY`.
- **Azure**: Set `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, etc.
- **Models**: Configure `CHAT_MODEL` and `EMBEDDING_MODEL` (deployment names for Azure).

---

## 💡 Usage

### Step 1: Add Documents
Place your text files (`.txt`, `.md`, `.pdf`) in the `data/docs/` directory.
> *A sample `data/docs/sample_policy.md` is included for testing.*

### Step 2: Build Index
Generate embeddings for your documents:

```bash
python -m agentic_rag.index
```

### Step 3: Run Chat Agent
Start the interactive CLI to chat with your agent:

```bash
python -m agentic_rag.chat
```
_Resume a previous session with `--session SESSION_ID`_

### Step 4: Run as API (Optional)
Start the FastAPI server:

```bash
uvicorn agentic_rag.api:app --reload
```

**Test with CURL:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the vacation policy?"}'
```

---

## 🛠️ Customization

- **Embedding Model**: Supports `text-embedding-3-small` by default. Change in `config.py`.
- **Vector Store**: Uses `numpy` for simplicity. Can be swapped for Qdrant/Chroma/etc. in `index_store.py`.

---

**Happy Hacking!** 🚀
