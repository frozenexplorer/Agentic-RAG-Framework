# src/agentic_rag/agent.py
from __future__ import annotations

import json
from typing import Any, Dict, List

from .config import get_settings
from .llm_client import get_async_client
from .index_store import IndexStore
from .tools import TOOLS, run_tool

SYSTEM_PROMPT = """You are an AI assistant that answers questions about a company's internal policy documents.

Rules:
- If a question depends on company-specific policy (leave, reimbursements, remote work, security, HR), you MUST call the search_docs tool before answering.
- If the question is general knowledge and not policy-specific, you may answer directly without search_docs.
- Only state facts that are supported by the provided documents when discussing company policy.
- If the documents do not contain the answer, say so clearly and ask what document/section to check.
"""


def _tool_calls_to_dict(tool_calls: Any) -> List[Dict[str, Any]]:
    out = []
    for tc in tool_calls or []:
        out.append(
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
        )
    return out


def _extract_sources_from_tool_json(tool_content: str) -> List[str]:
    """
    Our search_docs tool returns JSON that contains:
      {"results": [{"doc_id": "...", ...}, ...]}
    We return unique doc_ids preserving first-seen order.
    """
    try:
        data = json.loads(tool_content)
    except Exception:
        return []

    results = data.get("results", [])
    seen = set()
    ordered = []
    for r in results:
        doc_id = r.get("doc_id")
        if doc_id and doc_id not in seen:
            seen.add(doc_id)
            ordered.append(doc_id)
    return ordered


class PolicyAgent:
    def __init__(self, index: IndexStore):
        self.s = get_settings()
        self.client = get_async_client()
        self.index = index

    async def reply(self, messages: List[Dict[str, Any]]) -> str:
        """Backward-compatible: return only the answer string (CLI uses this)."""
        payload = await self.reply_with_sources(messages)
        return payload["answer"]

    async def reply_with_sources(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Returns:
          {"answer": "...", "sources": ["doc1", "doc2", ...]}
        """
        # Limit to last 10 messages for latency optimization
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        msgs: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}] + recent_messages

        sources_ordered: List[str] = []
        sources_seen = set()

        # Agent loop: allow up to 2 tool turns
        for _ in range(2):
            resp = await self.client.chat.completions.create(
                model=self.s.chat_model,
                messages=msgs,
                tools=TOOLS,
                tool_choice="auto",
            )
            msg = resp.choices[0].message

            # If the model asked to call tools, run them and continue the loop.
            if getattr(msg, "tool_calls", None):
                msgs.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": _tool_calls_to_dict(msg.tool_calls),
                    }
                )

                for tc in msg.tool_calls:
                    tool_output = await run_tool(self.index, tc.function.name, tc.function.arguments)

                    # collect sources from this tool output
                    for doc_id in _extract_sources_from_tool_json(tool_output):
                        if doc_id not in sources_seen:
                            sources_seen.add(doc_id)
                            sources_ordered.append(doc_id)

                    msgs.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": tool_output,
                        }
                    )
                continue

            # Normal text response
            return {"answer": (msg.content or "").strip(), "sources": sources_ordered}

        # If it keeps asking for tools, stop safely.
        return {
            "answer": "I couldn't complete the request within the tool limit. Please rephrase or ask a narrower question.",
            "sources": sources_ordered,
        }
