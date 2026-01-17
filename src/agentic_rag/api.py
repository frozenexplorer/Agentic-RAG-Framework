from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from .config import get_settings
from .index_store import IndexStore
from .memory import SessionMemory
from .agent import PolicyAgent

app = FastAPI(title="Agentic RAG Backend API")

# CORS middleware for production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "http://localhost:5174",
        "https://*.vercel.app",   # Vercel deployments
        "*",  # Allow all origins (change this in production to specific domain)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    source: List[str]


@app.on_event("startup")
def _startup():
    s = get_settings()
    app.state.settings = s
    app.state.index = IndexStore.load(s.index_dir)
    app.state.agent = PolicyAgent(index=app.state.index)


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    s = app.state.settings
    agent: PolicyAgent = app.state.agent

    # Session-based memory only if session_id provided
    if req.session_id:
        mem = SessionMemory.load(s.sessions_dir, req.session_id)
        mem.add({"role": "user", "content": req.query})
        payload = await agent.reply_with_sources(mem.messages)
        mem.add({"role": "assistant", "content": payload["answer"]})
        mem.save()
    else:
        # Stateless call
        payload = await agent.reply_with_sources([{"role": "user", "content": req.query}])

    return AskResponse(answer=payload["answer"], source=payload["sources"])
