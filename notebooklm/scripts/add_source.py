#!/usr/bin/env python3
"""
Add a source to an existing NotebookLM notebook.
Supports text content, files, and URLs.
Uses notebooklm-py async API.
"""

import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from config import resolve_notebook_id


async def add_source_to_notebook(
    notebook_id: str,
    content: str | None = None,
    content_file: str | None = None,
    source_url: str | None = None,
    source_name: str = "",
) -> dict:
    """
    Add a source to an existing NotebookLM notebook.

    Args:
        notebook_id: NotebookLM notebook API ID
        content: Text content to add as source
        content_file: Path to file to add as source
        source_url: URL to add as source
        source_name: Display name for the source

    Returns:
        dict with status
    """
    try:
        from notebooklm import NotebookLMClient

        async with await NotebookLMClient.from_storage() as client:
            if source_url:
                # Add URL source
                print(f"  Adding URL source: {source_url}")
                source = await client.sources.add_url(notebook_id, source_url, wait=True)
                print(f"  URL source added (ID: {source.id if hasattr(source, 'id') else 'ok'})")

            elif content_file and Path(content_file).exists():
                # Add file source
                file_path = Path(content_file)
                print(f"  Adding file source: {file_path.name} ({file_path.stat().st_size} bytes)")
                source = await client.sources.add_file(notebook_id, str(file_path), wait=True)
                print(f"  File source added (ID: {source.id if hasattr(source, 'id') else 'ok'})")

            elif content:
                # Write text to temp file and add
                print(f"  Adding text source ({len(content)} chars)...")
                suffix = ".md" if (content.startswith("#") or "##" in content[:200]) else ".txt"
                prefix = f"{source_name[:20]}_" if source_name else "source_"

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=suffix, prefix=prefix,
                    delete=False, encoding="utf-8"
                ) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    source = await client.sources.add_file(notebook_id, tmp_path, wait=True)
                    print(f"  Text source added (ID: {source.id if hasattr(source, 'id') else 'ok'})")
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            else:
                return {"status": "error", "error": "No source content provided"}

            # Rename source if name provided
            if source_name and hasattr(source, "id"):
                try:
                    await client.sources.rename(notebook_id, source.id, source_name)
                    print(f"  Renamed source to: {source_name}")
                except Exception:
                    pass  # rename is optional

            return {"status": "success", "source_id": getattr(source, "id", None)}

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Add source to NotebookLM notebook")

    parser.add_argument("--notebook-url", help="NotebookLM notebook URL")
    parser.add_argument("--notebook-id", help="Notebook ID from local library")
    parser.add_argument("--content", help="Text content to add")
    parser.add_argument("--content-file", help="Path to file to add as source")
    parser.add_argument("--source-url", help="URL to add as source")
    parser.add_argument("--source-name", default="", help="Display name for the source")
    args = parser.parse_args()

    # Check auth
    auth = AuthManager()
    if not auth.is_authenticated():
        print("Not authenticated. Run: python scripts/run.py auth_manager.py setup")
        sys.exit(1)

    # Resolve content
    content = args.content
    if args.content_file and not content:
        file_path = Path(args.content_file)
        if not file_path.exists():
            print(f"File not found: {args.content_file}")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
        print(f"Read {len(content)} chars from {args.content_file}")

    if not content and not args.source_url and not args.content_file:
        print("No content provided. Use --content, --content-file, or --source-url")
        sys.exit(1)

    # Resolve notebook
    notebook_id = resolve_notebook_id(args)
    if not notebook_id:
        sys.exit(1)

    print(f"Adding source to notebook: {notebook_id}")

    result = asyncio.run(add_source_to_notebook(
        notebook_id=notebook_id,
        content=content,
        content_file=args.content_file if not content else None,
        source_url=args.source_url,
        source_name=args.source_name,
    ))

    if result["status"] == "success":
        print(f"\nSource added successfully!")
    else:
        print(f"\nFailed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
