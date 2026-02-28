---
name: notebooklm
description: 'Query, create, and manage Google NotebookLM notebooks via notebooklm-py API. Use when user mentions NotebookLM, shares a notebooklm.google.com URL, wants to query documentation, create notebooks, add sources from text/files/URLs, or says "問我的筆記本", "開新筆記本", "加入來源", "查筆記", "幫我查文件", "check my docs", "ask my notebook", "query my notebook". Source-grounded Gemini answers with citations.'
---

# NotebookLM Research Assistant Skill

Interact with Google NotebookLM via `notebooklm-py` Python API to create notebooks, add sources (text, files, URLs), and query documentation with Gemini's source-grounded answers.

## When to Use This Skill

Trigger when user:
- Mentions NotebookLM explicitly
- Shares NotebookLM URL (`https://notebooklm.google.com/notebook/...`)
- Asks to query their notebooks/documentation
- Wants to create a new notebook from text content
- Wants to add text/documents to an existing notebook
- Wants to add documentation to NotebookLM library
- Uses phrases like "ask my NotebookLM", "check my docs", "query my notebook"

## Use the run.py Wrapper

Run all scripts through `python scripts/run.py [script]` — it manages the virtual environment, installs dependencies, and ensures correct Python version. Calling scripts directly (e.g., `python scripts/auth_manager.py`) bypasses venv activation and will fail with `ModuleNotFoundError`.

```bash
python scripts/run.py auth_manager.py status
python scripts/run.py notebook_manager.py list
python scripts/run.py ask_question.py --question "..."
```

## Smart Add Workflow

When adding a notebook to the library without details, query it first to discover its content rather than guessing — inaccurate descriptions degrade future search and selection quality.

```bash
# Step 1: Query the notebook to discover content
python scripts/run.py ask_question.py --question "What is the content of this notebook? What topics are covered?" --notebook-url "[URL]"

# Step 2: Use discovered info to add to library
python scripts/run.py notebook_manager.py add --url "[URL]" --name "[name]" --description "[desc]" --topics "[topics]"
```

## Core Workflow

### Step 1: Check Auth
```bash
python scripts/run.py auth_manager.py status
```

### Step 2: Authenticate (One-Time)
```bash
python scripts/run.py auth_manager.py setup
```
A browser window opens for Google login. User logs in manually.
Login completion is auto-detected (no Enter needed).
Auth is stored at `~/.notebooklm/storage_state.json` (cookies valid ~1-2 weeks).

Other auth commands:
```bash
python scripts/run.py auth_manager.py test     # Test API access
python scripts/run.py auth_manager.py reauth   # Clear + re-login
python scripts/run.py auth_manager.py clear    # Clear all auth data
```

### Step 3: Ask Questions
```bash
# Uses active notebook
python scripts/run.py ask_question.py --question "Your question here"

# Specific notebook by library ID
python scripts/run.py ask_question.py --question "..." --notebook-id my-notebook

# Specific notebook by URL
python scripts/run.py ask_question.py --question "..." --notebook-url "https://notebooklm.google.com/notebook/abc123"

# Target specific sources
python scripts/run.py ask_question.py --question "..." --source-ids "id1,id2"
```

### Step 4: Create Notebook with Source
```bash
python scripts/run.py create_notebook.py \
  --name "Project Docs" \
  --content "Text content here..." \
  --description "Project documentation" \
  --topics "project,docs"

# Or from file / URL
python scripts/run.py create_notebook.py --name "Notes" --content-file /path/to/file.md
python scripts/run.py create_notebook.py --name "Web" --source-url "https://example.com/article"
python scripts/run.py create_notebook.py --name "Empty Notebook"
```

### Step 5: Add Source to Existing Notebook
```bash
python scripts/run.py add_source.py \
  --notebook-url "https://notebooklm.google.com/notebook/..." \
  --content "New text content..." \
  --source-name "Source Name"

# Or from file / URL
python scripts/run.py add_source.py --notebook-id my-notebook --content-file /path/to/doc.pdf --source-name "PDF"
python scripts/run.py add_source.py --notebook-id my-notebook --source-url "https://example.com" --source-name "Web"
```

### Step 6: Manage Library
```bash
python scripts/run.py notebook_manager.py list              # List all
python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS
python scripts/run.py notebook_manager.py search --query "keyword"
python scripts/run.py notebook_manager.py activate --id ID   # Set active
python scripts/run.py notebook_manager.py remove --id ID
python scripts/run.py notebook_manager.py sync               # Sync with NotebookLM API
python scripts/run.py notebook_manager.py stats
```

## Follow-Up on Answers

NotebookLM answers may be incomplete for complex queries. After receiving an answer, compare it to the user's original request. If there are gaps, ask follow-up questions before responding to the user — it's better to make 2-3 targeted queries than to give an incomplete answer.

## Decision Flow

```
User mentions NotebookLM
    |
Check auth -> auth_manager.py status
    |
Not authenticated -> auth_manager.py setup
    |
CREATE notebook? -> create_notebook.py --name NAME --content "..."
    |
ADD source to existing? -> add_source.py --notebook-url URL --content "..."
    |
QUERY notebook? -> ask_question.py --question "..."
    |
Follow-up if gaps -> Synthesize and respond
```

## Data Storage

- `~/.notebooklm/storage_state.json` - Auth cookies (Playwright format)
- `~/.notebooklm/browser_profile/` - Persistent browser profile for login
- `<skill_dir>/data/library.json` - Local notebook metadata
- `<skill_dir>/data/auth_info.json` - Auth timestamps

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Use `run.py` wrapper — it activates the venv |
| Auth fails | Run `auth_manager.py setup` — browser opens for manual login |
| Cookies expired | Run `auth_manager.py reauth` (cookies last ~1-2 weeks) |
| API test fails | Run `auth_manager.py test` to diagnose |
| Notebook not found | Run `notebook_manager.py sync` to refresh from API |
| Rate limited | Google enforces limits — wait and retry |

## Architecture Notes

**notebooklm-py** is a Python client that communicates with NotebookLM's internal API via HTTP (httpx). No browser needed for queries/operations — only for initial Google login.

- **Login**: Uses Playwright persistent context to open browser for Google OAuth (auto-detects login completion)
- **All other ops**: Pure HTTP API calls (fast, no browser overhead)
- **Auth**: Cookies stored in Playwright storage state format at `~/.notebooklm/storage_state.json`
- **Async API**: All operations are async; scripts use `asyncio.run()`
