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
from notebook_manager import NotebookLibrary
from config import extract_notebook_id

# Follow-up reminder for Claude to evaluate completeness
FOLLOW_UP_REMINDER = (
    "\n\nEXTREMELY IMPORTANT: Is that ALL you need to know? "
    "You can always ask another question! Think about it carefully: "
    "before you reply to the user, review their original request and this answer. "
    "If anything is still unclear or missing, ask me another comprehensive question."
)


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

        async with await NotebookLMClient.from_storage() as client:
            result = await client.chat.ask(notebook_id, question)

            answer = result.answer
            if not answer:
                print("No answer received")
                return None

            print(f"Got answer ({len(answer)} chars)")

            # Show references if available
            if result.references:
                print(f"References: {len(result.references)} citations")

            return answer + FOLLOW_UP_REMINDER

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def resolve_notebook_id(args) -> str | None:
    """Resolve notebook ID from args (URL, library ID, or active notebook)."""
    # Direct notebook URL
    if args.notebook_url:
        nid = extract_notebook_id(args.notebook_url)
        if nid:
            return nid
        print(f"Could not extract notebook ID from URL: {args.notebook_url}")
        return None

    # Library notebook ID
    if args.notebook_id:
        library = NotebookLibrary()
        notebook = library.get_notebook(args.notebook_id)
        if notebook:
            url = notebook["url"]
            nid = extract_notebook_id(url)
            if nid:
                # Also try notebooklm_id if stored
                return notebook.get("notebooklm_id") or nid
        print(f"Notebook '{args.notebook_id}' not found in library")
        return None

    # Active notebook
    library = NotebookLibrary()
    active = library.get_active_notebook()
    if active:
        print(f"Using active notebook: {active['name']}")
        nid = extract_notebook_id(active["url"])
        return active.get("notebooklm_id") or nid

    # Show available notebooks
    notebooks = library.list_notebooks()
    if notebooks:
        print("\nAvailable notebooks:")
        for nb in notebooks:
            mark = " [ACTIVE]" if nb.get("id") == library.active_notebook_id else ""
            print(f"  {nb['id']}: {nb['name']}{mark}")
        print("\nSpecify with --notebook-id or --notebook-url")
    else:
        print("No notebooks in library. Add one first:")
        print("  python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS")
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
