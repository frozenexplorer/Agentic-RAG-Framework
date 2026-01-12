from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class Settings:
    provider: str
    openai_api_key: str | None
    azure_api_key: str | None
    azure_base_url: str | None

    chat_model: str
    embedding_model: str

    docs_dir: Path
    index_dir: Path
    sessions_dir: Path

    top_k: int
    chunk_tokens: int
    chunk_overlap: int

def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be an integer, got: {raw!r}") from e

def get_settings() -> Settings:
    provider = os.getenv("PROVIDER", "openai").strip().lower()

    s = Settings(
        provider=provider,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        azure_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_base_url=os.getenv("AZURE_OPENAI_BASE_URL"),

        chat_model=os.getenv("CHAT_MODEL", "gpt-4o-mini").strip(),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small").strip(),

        docs_dir=REPO_ROOT / os.getenv("DOCS_DIR", "data/docs"),
        index_dir=REPO_ROOT / os.getenv("INDEX_DIR", "data/index"),
        sessions_dir=REPO_ROOT / os.getenv("SESSIONS_DIR", "data/sessions"),

        top_k=_get_int("TOP_K", 5),
        chunk_tokens=_get_int("CHUNK_TOKENS", 800),
        chunk_overlap=_get_int("CHUNK_OVERLAP", 120),
    )

    if s.provider not in {"openai", "azure"}:
        raise ValueError("PROVIDER must be 'openai' or 'azure'")

    if s.provider == "openai":
        if not s.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when PROVIDER=openai")
    else:
        if not s.azure_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required when PROVIDER=azure")
        if not s.azure_base_url:
            raise ValueError("AZURE_OPENAI_BASE_URL is required when PROVIDER=azure")
        # Small sanity check
        if not s.azure_base_url.endswith("/openai/v1/"):
            raise ValueError("AZURE_OPENAI_BASE_URL must end with '/openai/v1/' (see README)")

    s.docs_dir.mkdir(parents=True, exist_ok=True)
    s.index_dir.mkdir(parents=True, exist_ok=True)
    s.sessions_dir.mkdir(parents=True, exist_ok=True)

    return s
