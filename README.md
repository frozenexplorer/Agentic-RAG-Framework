# Agentic RAG Framework (Starter)

This is a minimal, **agentic RAG** implementation that:

- Accepts a user query
- Lets the LLM decide whether it can answer directly **or** should call a tool
- Implements a `search_docs` tool that retrieves from internal policy docs (vector search)
- Maintains **session-based memory** (conversation history persisted to disk)
- Works with **OpenAI API** or **Azure OpenAI (v1 endpoint)** using the same OpenAI Python SDK

---

## 0) Prerequisites

- Python **3.9+** (recommended 3.10+)
- An OpenAI API key **or** an Azure OpenAI resource + deployed models

---

## 1) Setup

### Windows (PowerShell)
```powershell
cd Agentic-RAG-framework
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### Mac/Linux (bash/zsh)
```bash
cd Agentic-RAG-framework
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with either `OPENAI_API_KEY` or `AZURE_OPENAI_*` values.

---

## 2) Add your documents

Put company policy docs in `data/docs/` (txt, md, pdf).

A sample policy doc is already included:
- `data/docs/sample_policy.md`

---

## 3) Build the index (embeddings)

```bash
python -m agentic_rag.index
```

This creates:
- `data/index/embeddings.npy`
- `data/index/meta.jsonl`
- `data/index/manifest.json`

---

## 4) Run the chat agent (CLI)

```bash
python -m agentic_rag.chat
```

You’ll get an interactive prompt. The agent will call `search_docs` **only when needed**.

To resume a previous session:
```bash
python -m agentic_rag.chat --session SESSION_ID
```

---

## 5) Run as an API (optional)

```bash
uvicorn agentic_rag.api:app --reload
```

Then POST:
- `POST http://127.0.0.1:8000/chat`
- body: `{"session_id": "optional", "message": "your question"}`

---

## Notes

- Azure OpenAI requires **deployment names** for `CHAT_MODEL` and `EMBEDDING_MODEL` (set these in `.env`).
- This starter uses a simple **numpy cosine similarity** vector store (no external DB).
