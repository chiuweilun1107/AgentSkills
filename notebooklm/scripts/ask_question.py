#!/usr/bin/env python3
"""
NotebookLM Question Interface
Uses notebooklm-py async API for querying notebooks.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from config import resolve_notebook_id

async def ask_notebooklm(question: str, notebook_id: str, source_ids: list[str] | None = None) -> str | None:
    """
    Ask a question to a NotebookLM notebook.

    Args:
        question: Question to ask
        notebook_id: NotebookLM notebook API ID
        source_ids: Optional list of source IDs to target

    Returns:
        Answer text from NotebookLM, or None on failure
    """
    try:
        from notebooklm import NotebookLMClient

        print(f"Asking: {question}")
        print(f"Notebook: {notebook_id}")
        if source_ids:
            print(f"Targeting sources: {source_ids}")

        async with await NotebookLMClient.from_storage() as client:
            result = await client.chat.ask(notebook_id, question, source_ids=source_ids)

            answer = result.answer
            if not answer:
                print("No answer received")
                return None

            print(f"Got answer ({len(answer)} chars)")

            # Show references if available
            if result.references:
                print(f"References: {len(result.references)} citations")

            return answer

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description="Ask NotebookLM a question")

    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument("--notebook-url", help="NotebookLM notebook URL")
    parser.add_argument("--notebook-id", help="Notebook ID from local library")
    parser.add_argument("--source-ids", help="Comma-separated source IDs to target")
    args = parser.parse_args()

    # Check auth
    auth = AuthManager()
    if not auth.is_authenticated():
        print("Not authenticated. Run: python scripts/run.py auth_manager.py setup")
        sys.exit(1)

    # Resolve notebook
    notebook_id = resolve_notebook_id(args)
    if not notebook_id:
        sys.exit(1)

    # Parse source IDs
    source_ids = None
    if args.source_ids:
        source_ids = [s.strip() for s in args.source_ids.split(",")]

    # Ask question
    answer = asyncio.run(ask_notebooklm(
        question=args.question,
        notebook_id=notebook_id,
        source_ids=source_ids,
    ))

    if answer:
        print("\n" + "=" * 60)
        print(f"Question: {args.question}")
        print("=" * 60)
        print()
        print(answer)
        print()
        print("=" * 60)
    else:
        print("\nFailed to get answer")
        sys.exit(1)


if __name__ == "__main__":
    main()
