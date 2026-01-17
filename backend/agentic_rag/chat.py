from __future__ import annotations
import argparse
from rich.console import Console
from rich.prompt import Prompt

from .config import get_settings
from .index_store import IndexStore
from .memory import SessionMemory
from .agent import PolicyAgent

import asyncio

def main():
    asyncio.run(async_main())

async def async_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", type=str, default=None, help="Resume an existing session id")
    args = parser.parse_args()

    s = get_settings()
    index = IndexStore.load(s.index_dir)
    agent = PolicyAgent(index=index)

    mem = SessionMemory.load(s.sessions_dir, args.session) if args.session else SessionMemory(s.sessions_dir)
    console = Console()

    console.print(f"[bold]Session:[/bold] {mem.session_id}")
    console.print("Type 'exit' to quit.\n")

    while True:
        # Prompt.ask is blocking, which is fine for a CLI
        user = Prompt.ask("[bold cyan]You[/bold cyan]")
        if user.strip().lower() in {"exit", "quit"}:
            break

        mem.add({"role": "user", "content": user})
        answer = await agent.reply(mem.messages)
        mem.add({"role": "assistant", "content": answer})
        mem.save()

        console.print("\n[bold green]Assistant[/bold green]")
        console.print(answer)
        console.print("\n")

if __name__ == "__main__":
    main()
