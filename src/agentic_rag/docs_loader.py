from __future__ import annotations
from pathlib import Path
from typing import Iterable, Iterator
from pypdf import PdfReader

TEXT_EXTS = {".txt", ".md"}
PDF_EXTS = {".pdf"}

def iter_docs(docs_dir: Path) -> Iterator[dict]:
    """Yield dicts: {doc_id, path, text}."""
    for path in sorted(docs_dir.rglob("*")):
        if path.is_dir():
            continue
        ext = path.suffix.lower()
        if ext in TEXT_EXTS:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif ext in PDF_EXTS:
            text = _read_pdf(path)
        else:
            continue
        text = text.strip()
        if not text:
            continue
        yield {"doc_id": path.name, "path": str(path), "text": text}

def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)
