from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json
import uuid
from typing import List, Dict, Any

@dataclass
class SessionMemory:
    sessions_dir: Path
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    messages: List[Dict[str, Any]] = field(default_factory=list)

    def path(self) -> Path:
        return self.sessions_dir / f"{self.session_id}.json"

    @classmethod
    def load(cls, sessions_dir: Path, session_id: str) -> "SessionMemory":
        p = sessions_dir / f"{session_id}.json"
        if not p.exists():
            return cls(sessions_dir=sessions_dir, session_id=session_id)
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(sessions_dir=sessions_dir, session_id=data["session_id"], messages=data.get("messages", []))

    def save(self) -> None:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        data = {"session_id": self.session_id, "messages": self.messages[-50:]}  # keep last 50
        self.path().write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, message: Dict[str, Any]) -> None:
        self.messages.append(message)
