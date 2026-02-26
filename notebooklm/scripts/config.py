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
