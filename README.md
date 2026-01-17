# 🤖 Agentic RAG Framework - Enterprise Edition

> **A production-ready, full-stack framework for building intelligent RAG applications with an interactive web interface.**

This framework provides everything you need to build sophisticated AI agents that can:
- **Retrieve Information**: Use semantic vector search (RAG) to find relevant documents
- **Make Intelligent Decisions**: Automatically determine when to search vs. answer directly
- **Maintain Context**: Persist conversation history across sessions
- **Interactive UI**: Modern, responsive web interface with smooth typing animations
- **Flexible Deployment**: Supports OpenAI, Azure OpenAI, or local models (LM Studio)

---

## ✨ Features

### Backend (Python + FastAPI)
- 🤖 **Intelligent Tool Use**: LLM calls `search_docs` only when necessary
- 🎯 **Semantic Filtering**: Relevance threshold (≥0.5) removes irrelevant results
- 📊 **Optimized Retrieval**: Configurable TOP_K and chunk sizing for accuracy
- 🔄 **Session Memory**: Persists chat history to disk
- 🌐 **Multi-Provider**: OpenAI, Azure OpenAI, or LM Studio (local)
- ⚡ **FastAPI Server**: Production-ready REST API

### Frontend (React + Vite)
- 🎨 **Modern UI**: Dark theme with glassmorphism effects
- ✨ **Smooth Typing Animation**: ChatGPT-like letter-by-letter responses
- 📋 **Copy-to-Clipboard**: Easy code snippet copying
- 💫 **Interactive Animations**: Hover effects, loading states, transitions
- 📚 **Source Citations**: Clear attribution for all retrieved information
- 🎯 **Real-time Feedback**: Shake validation, pulse effects, status indicators

---

## 📂 Project Structure

```text
Agentic-RAG-Framework/
├── src/agentic_rag/        # Backend Python package
│   ├── api.py              # FastAPI server
│   ├── agent.py            # Core agent logic
│   ├── tools.py            # Search tools with semantic filtering
│   ├── index.py            # Document indexing
│   ├── chat.py             # CLI interface
│   └── ...
├── frontend/               # React + Vite web app
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── index.css       # Styles & animations
│   │   └── App.jsx
│   ├── tailwind.config.js  # Tailwind CSS config
│   └── package.json
├── data/
│   ├── docs/               # Your documents (.txt, .md, .pdf)
│   ├── index/              # Generated embeddings
│   └── sessions/           # Chat history
├── .env                    # Configuration
└── requirements.txt        # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **LM Studio** (for local models) OR OpenAI/Azure API keys

### 1. Backend Setup

**Windows (PowerShell)**
```powershell
cd Agentic-RAG-Framework
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac/Linux**
```bash
cd Agentic-RAG-Framework
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file (or copy from `.env.example`):

```env
# Provider: openai, azure, or use LM Studio
PROVIDER=openai
OPENAI_BASE_URL=http://127.0.0.1:1234/v1  # LM Studio endpoint
OPENAI_API_KEY=lm-studio-local            # Dummy key for LM Studio

# Model names (use deployment names for Azure)
CHAT_MODEL=qwen2.5-7b-instruct-1m
EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5

# Retrieval settings (optimized defaults)
TOP_K=8                # Number of chunks to retrieve
CHUNK_TOKENS=600       # Chunk size for faster processing
CHUNK_OVERLAP=120      # Overlap between chunks
```

**For OpenAI:**
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

**For Azure OpenAI:**
```env
PROVIDER=azure
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/v1/
CHAT_MODEL=gpt-4o-mini  # deployment name
EMBEDDING_MODEL=text-embedding-ada-002  # deployment name
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## 💡 Usage

### Step 1: Add Documents
Place your documents (`.txt`, `.md`, `.pdf`) in `data/docs/`:
```bash
# Sample document included for testing
data/docs/sample_policy.md
```

### Step 2: Build Index
Generate embeddings for your documents:
```bash
python -m agentic_rag.index
```

### Step 3: Start the Application

**Terminal 1 - Backend:**
```bash
python -m uvicorn agentic_rag.api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Open your browser:**
```
http://localhost:5173
```

### Alternative: CLI Chat
Start the interactive CLI (without frontend):
```bash
python -m agentic_rag.chat
```

Resume a session:
```bash
python -m agentic_rag.chat --session <SESSION_ID>
```

---

## 🎨 UI Features

### Typing Animation
- **Smooth letter-by-letter** reveal (10ms per character)
- **Blinking cursor** during typing
- **ChatGPT/Gemini-like** experience

### Interactive Elements
- **Hover effects** on all components
- **Shake animation** on validation errors
- **Pulse glow** on active send button
- **Copy-to-clipboard** for code blocks
- **Smooth transitions** throughout

### Source Citations
Every response shows its sources:
```
SOURCES
📄 sample_policy.md
📄 document.pdf
```

---

## ⚙️ Configuration Deep Dive

### Retrieval Parameters

**TOP_K** (default: 8)
- Number of chunks to retrieve from vector store
- Higher = better coverage, but more noise
- Recommended: 5-10

**CHUNK_TOKENS** (default: 600)
- Size of each document chunk
- Smaller = faster processing
- Recommended: 400-800

**CHUNK_OVERLAP** (default: 120)
- Overlap between consecutive chunks
- Prevents information loss at boundaries
- Recommended: 15-20% of CHUNK_TOKENS

### Semantic Filtering

The framework automatically filters results with relevance score < 0.5:
```python
# In tools.py
RELEVANCE_THRESHOLD = 0.5  # Only keep relevant results
```

This prevents irrelevant answers and improves accuracy.

---

## 🛠️ Customization

### Add New Tools

Edit `src/agentic_rag/tools.py`:
```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "your_custom_tool",
            "description": "What this tool does",
            "parameters": {...}
        }
    }
]
```

### Modify UI Styling

- **Colors**: Edit CSS variables in `frontend/src/index.css`
- **Animations**: Adjust keyframes in `frontend/src/index.css`
- **Components**: Modify files in `frontend/src/components/`

### Change Typing Speed

In `frontend/src/components/ChatInterface.jsx`:
```javascript
const typingSpeed = 10; // milliseconds per character
```

---

## 🚀 Deployment

### Backend (Azure/Railway/Render)
```bash
# Build and deploy the FastAPI app
pip install -r requirements.txt
uvicorn agentic_rag.api:app --host 0.0.0.0 --port 8000
```

### Frontend (Vercel/Netlify/Azure Static Web Apps)
```bash
cd frontend
npm run build  # Creates dist/ folder
# Deploy dist/ folder to your hosting service
```

**Update frontend proxy for production:**
Edit `frontend/vite.config.js`:
```javascript
server: {
  proxy: {
    '/ask': {
      target: process.env.VITE_API_URL || 'https://your-backend.com',
      changeOrigin: true,
    }
  }
}
```

---

## 📊 Performance

### Optimizations Applied
- **Agent loop**: 3 iterations max (prevents timeout)
- **Message history**: Last 10 messages (reduced context)
- **Semantic filtering**: Score ≥ 0.5 (better accuracy)
- **Reduced chunk size**: 600 tokens (faster embedding)

### Expected Response Time
- **Simple queries**: 1-2 seconds
- **Complex queries**: 2-4 seconds
- **LM Studio (local)**: 3-6 seconds (depends on hardware)

---

## 🧪 Testing

### Test Queries
```
1. "What is the POSH policy?"
   → Should return Prevention of Sexual Harassment policy

2. "Tell me about leave policy"
   → Should return vacation/leave information

3. "Remote work guidelines"
   → Should return remote work policies

4. "What is Python?" (general knowledge)
   → Should answer directly without searching docs
```

### Verify Features
- ✅ Typing animation is smooth
- ✅ Sources are displayed
- ✅ Hover effects work
- ✅ Copy-to-clipboard on code blocks
- ✅ Empty submit triggers shake animation

---

## 📝 API Reference

### POST /ask
Query the agent:

**Request:**
```json
{
  "query": "What is the vacation policy?",
  "session_id": "sess_abc123"  // Optional
}
```

**Response:**
```json
{
  "answer": "Unused leave can be carried forward...",
  "source": ["sample_policy.md", "hr_handbook.pdf"]
}
```

---

## 🎯 Key Technologies

- **Backend**: Python, FastAPI, OpenAI API, FAISS
- **Frontend**: React, Vite, Tailwind CSS
- **Vector Store**: FAISS (cosine similarity)
- **Embeddings**: OpenAI text-embedding-3-small or custom models

---

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [LM Studio](https://lmstudio.ai/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using modern AI and web technologies** 🚀
