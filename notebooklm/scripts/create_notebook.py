#!/usr/bin/env python3
"""
Create a new NotebookLM notebook and optionally add text/file as a source.
Uses notebooklm-py async API.
"""

import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from notebook_manager import NotebookLibrary
from config import notebook_url_from_id


async def create_notebook(
    name: str,
    content: str | None = None,
    content_file: str | None = None,
    source_url: str | None = None,
    description: str = "",
    topics: str = "",
) -> dict:
    """
    Create a new NotebookLM notebook and optionally add a source.

    Args:
        name: Name for the notebook
        content: Text content to add as source
        content_file: Path to a file to add as source
        source_url: URL to add as source
        description: Description for local library
        topics: Comma-separated topics for local library

    Returns:
        dict with notebook_id, notebook_url, and status
    """
    auth = AuthManager()
    if not auth.is_authenticated():
        print("Not authenticated. Run: python scripts/run.py auth_manager.py setup")
        return {"status": "error", "error": "Not authenticated"}

    # Resolve content
    if content_file and not content:
        file_path = Path(content_file)
        if not file_path.exists():
            print(f"File not found: {content_file}")
            return {"status": "error", "error": f"File not found: {content_file}"}
        content = file_path.read_text(encoding="utf-8")
        print(f"Read {len(content)} chars from {content_file}")

    print(f"Creating notebook: {name}")

    try:
        from notebooklm import NotebookLMClient

        async with await NotebookLMClient.from_storage() as client:
            # Step 1: Create notebook
            nb = await client.notebooks.create(name)
            notebook_id = nb.id
            notebook_url = notebook_url_from_id(notebook_id)
            print(f"  Notebook created: {notebook_id}")
            print(f"  URL: {notebook_url}")

            # Step 2: Add source if provided
            source_added = False

            if source_url:
                # Add URL source
                print(f"  Adding URL source: {source_url}")
                await client.sources.add_url(notebook_id, source_url, wait=True)
                source_added = True
                print("  URL source added")

            elif content_file and Path(content_file).exists():
                # Add file source directly
                print(f"  Adding file source: {content_file}")
                await client.sources.add_file(notebook_id, content_file, wait=True)
                source_added = True
                print("  File source added")

            elif content:
                # Write text content to temp file and add as source
                print(f"  Adding text source ({len(content)} chars)...")
                suffix = ".txt"
                # Use .md if content looks like markdown
                if content.startswith("#") or "##" in content[:200]:
                    suffix = ".md"

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=suffix, prefix=f"{name[:20]}_",
                    delete=False, encoding="utf-8"
                ) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    await client.sources.add_file(notebook_id, tmp_path, wait=True)
                    source_added = True
                    print("  Text source added")
                finally:
                    Path(tmp_path).unlink(missing_ok=True)

            # Step 3: Register in local library
            try:
                library = NotebookLibrary()
                topic_list = [t.strip() for t in topics.split(",")] if topics else ["general"]
                library.add_notebook(
                    url=notebook_url,
                    name=name,
                    description=description or f"Auto-created notebook: {name}",
                    topics=topic_list,
                    notebooklm_id=notebook_id,
                )
                library.select_notebook(name.lower().replace(" ", "-").replace("_", "-"))
                print("  Registered in local library and set as active")
            except Exception as e:
                print(f"  Could not register in library: {e}")

            status = "success" if source_added else "partial"
            result = {
                "status": status,
                "notebook_id": notebook_id,
                "notebook_url": notebook_url,
                "name": name,
                "source_added": source_added,
            }

            print(f"\nNotebook created successfully!")
            print(f"URL: {notebook_url}")
            if not source_added and (content or content_file or source_url):
                print("Warning: Source was not added")

            return result

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Create a new NotebookLM notebook")

    parser.add_argument("--name", required=True, help="Name for the notebook")
    parser.add_argument("--content", help="Text content to add as source")
    parser.add_argument("--content-file", help="Path to file to add as source")
    parser.add_argument("--source-url", help="URL to add as source")
    parser.add_argument("--description", default="", help="Description for local library")
    parser.add_argument("--topics", default="", help="Comma-separated topics")
    args = parser.parse_args()

    if not args.content and not args.content_file and not args.source_url:
        print("No source provided. Creating empty notebook.")

    result = asyncio.run(create_notebook(
        name=args.name,
        content=args.content,
        content_file=args.content_file,
        source_url=args.source_url,
        description=args.description,
        topics=args.topics,
    ))

    if result["status"] == "success":
        print(f"\nDone! Notebook URL: {result['notebook_url']}")
    elif result["status"] == "partial":
        print(f"\nNotebook created but source not added: {result['notebook_url']}")
    else:
        print(f"\nFailed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
