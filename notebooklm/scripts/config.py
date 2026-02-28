"""
Configuration for NotebookLM Skill
Centralizes constants and paths.
Uses notebooklm-py package for API access.
"""

import re
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
LIBRARY_FILE = DATA_DIR / "library.json"
AUTH_INFO_FILE = DATA_DIR / "auth_info.json"

# notebooklm-py stores auth at ~/.notebooklm/
NOTEBOOKLM_HOME = Path.home() / ".notebooklm"
STORAGE_STATE_FILE = NOTEBOOKLM_HOME / "storage_state.json"

# Timeouts (seconds)
QUERY_TIMEOUT = 120
SOURCE_WAIT_TIMEOUT = 300


def extract_notebook_id(url: str) -> str | None:
    """Extract notebook ID from a NotebookLM URL.

    URL format: https://notebooklm.google.com/notebook/{id}
    """
    match = re.search(r"/notebook/([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None


def notebook_url_from_id(notebook_id: str) -> str:
    """Build a NotebookLM URL from a notebook ID."""
    return f"https://notebooklm.google.com/notebook/{notebook_id}"


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    return name.lower().replace(" ", "-").replace("_", "-")


def resolve_notebook_id(args) -> str | None:
    """Resolve notebook API ID from args (URL, library ID, or active notebook).

    Expects args to have optional notebook_url and notebook_id attributes.
    """
    from notebook_manager import NotebookLibrary

    # Direct notebook URL
    if getattr(args, "notebook_url", None):
        nid = extract_notebook_id(args.notebook_url)
        if nid:
            return nid
        print(f"Could not extract notebook ID from URL: {args.notebook_url}")
        return None

    # Library notebook ID
    if getattr(args, "notebook_id", None):
        library = NotebookLibrary()
        notebook = library.get_notebook(args.notebook_id)
        if notebook:
            return notebook.get("notebooklm_id") or extract_notebook_id(notebook["url"])
        print(f"Notebook '{args.notebook_id}' not found in library")
        return None

    # Active notebook
    library = NotebookLibrary()
    active = library.get_active_notebook()
    if active:
        print(f"Using active notebook: {active['name']}")
        return active.get("notebooklm_id") or extract_notebook_id(active["url"])

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
