---
name: notebooklm
description: 'Query, create, and manage Google NotebookLM notebooks via notebooklm-py API. Use when user mentions NotebookLM, shares a notebooklm.google.com URL, wants to query documentation, create notebooks, add sources from text/files/URLs, or says "問我的筆記本", "開新筆記本", "加入來源". Source-grounded Gemini answers with citations.'
---

# NotebookLM Research Assistant Skill

Interact with Google NotebookLM via `notebooklm-py` Python API to create notebooks, add sources (text, files, URLs), and query documentation with Gemini's source-grounded answers.

## When to Use This Skill

Trigger when user:
- Mentions NotebookLM explicitly
- Shares NotebookLM URL (`https://notebooklm.google.com/notebook/...`)
- Asks to query their notebooks/documentation
- Wants to **create a new notebook** from text content
- Wants to **add text/documents** to an existing notebook
- Wants to add documentation to NotebookLM library
- Uses phrases like "ask my NotebookLM", "check my docs", "query my notebook"

## CRITICAL: Always Use run.py Wrapper

**NEVER call scripts directly. ALWAYS use `python scripts/run.py [script]`:**

```bash
# CORRECT:
python scripts/run.py auth_manager.py status
python scripts/run.py notebook_manager.py list
python scripts/run.py ask_question.py --question "..."

# WRONG - never call directly:
python scripts/auth_manager.py status  # Fails without venv!
```

The `run.py` wrapper auto-creates `.venv`, installs deps, and runs correctly.

## CRITICAL: Smart Add Workflow

When user wants to add a notebook without providing details:

```bash
# Step 1: Query the notebook to discover content
python scripts/run.py ask_question.py --question "What is the content of this notebook? What topics are covered?" --notebook-url "[URL]"

# Step 2: Use discovered info to add to library
python scripts/run.py notebook_manager.py add --url "[URL]" --name "[name]" --description "[desc]" --topics "[topics]"
```

NEVER guess descriptions. Use Smart Add or ask user.

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

### Step 3: Test API Access
```bash
python scripts/run.py auth_manager.py test
```

### Step 4: Ask Questions
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

### Step 5: Create Notebook with Source
```bash
# Create with inline text
python scripts/run.py create_notebook.py \
  --name "Project Docs" \
  --content "Text content here..." \
  --description "Project documentation" \
  --topics "project,docs"

# Create with file
python scripts/run.py create_notebook.py \
  --name "Research Notes" \
  --content-file /path/to/file.md \
  --topics "research"

# Create with URL source
python scripts/run.py create_notebook.py \
  --name "Web Research" \
  --source-url "https://example.com/article" \
  --topics "web,research"

# Create empty notebook
python scripts/run.py create_notebook.py --name "Empty Notebook"
```

### Step 6: Add Source to Existing Notebook
```bash
# Add text content
python scripts/run.py add_source.py \
  --notebook-url "https://notebooklm.google.com/notebook/..." \
  --content "New text content..." \
  --source-name "Source Name"

# Add file
python scripts/run.py add_source.py \
  --notebook-id my-notebook \
  --content-file /path/to/document.pdf \
  --source-name "PDF Document"

# Add URL
python scripts/run.py add_source.py \
  --notebook-id my-notebook \
  --source-url "https://example.com/page" \
  --source-name "Web Page"
```

### Step 7: Manage Library
```bash
python scripts/run.py notebook_manager.py list              # List all
python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS
python scripts/run.py notebook_manager.py search --query "keyword"
python scripts/run.py notebook_manager.py activate --id ID   # Set active
python scripts/run.py notebook_manager.py remove --id ID
python scripts/run.py notebook_manager.py sync               # Sync with NotebookLM API
python scripts/run.py notebook_manager.py stats
```

## Follow-Up Mechanism (CRITICAL)

Every NotebookLM answer ends with: **"EXTREMELY IMPORTANT: Is that ALL you need to know?"**

**Required Claude Behavior:**
1. **STOP** - Do not immediately respond to user
2. **ANALYZE** - Compare answer to user's original request
3. **IDENTIFY GAPS** - Determine if more information needed
4. **ASK FOLLOW-UP** - If gaps exist, immediately ask another question
5. **REPEAT** - Continue until information is complete
6. **SYNTHESIZE** - Combine all answers before responding to user

## Script Reference

### Authentication (`auth_manager.py`)
```bash
python scripts/run.py auth_manager.py setup    # Browser login (one-time)
python scripts/run.py auth_manager.py status   # Check auth status
python scripts/run.py auth_manager.py test     # Test API access
python scripts/run.py auth_manager.py reauth   # Clear + re-login
python scripts/run.py auth_manager.py clear    # Clear all auth data
```

### Create Notebook (`create_notebook.py`)
```bash
python scripts/run.py create_notebook.py \
  --name "Name" \
  [--content "text"] [--content-file path] [--source-url URL] \
  [--description "desc"] [--topics "t1,t2"]
```

### Add Source (`add_source.py`)
```bash
python scripts/run.py add_source.py \
  [--notebook-url URL | --notebook-id ID] \
  [--content "text"] [--content-file path] [--source-url URL] \
  [--source-name "name"]
```

### Ask Question (`ask_question.py`)
```bash
python scripts/run.py ask_question.py \
  --question "..." \
  [--notebook-url URL | --notebook-id ID] \
  [--source-ids "id1,id2"]
```

### Notebook Manager (`notebook_manager.py`)
```bash
python scripts/run.py notebook_manager.py add|list|search|activate|remove|stats|sync
```

## Decision Flow

```
User mentions NotebookLM
    |
Check auth -> python scripts/run.py auth_manager.py status
    |
Not authenticated -> python scripts/run.py auth_manager.py setup
    |
CREATE notebook? -> create_notebook.py --name NAME --content "..."
    |
ADD source to existing? -> add_source.py --notebook-url URL --content "..."
    |
QUERY notebook? -> ask_question.py --question "..."
    |
Follow-up until complete -> Synthesize and respond
```

## Data Storage

- `~/.notebooklm/storage_state.json` - Auth cookies (Playwright format)
- `~/.notebooklm/browser_profile/` - Persistent browser profile for login
- `<skill_dir>/data/library.json` - Local notebook metadata
- `<skill_dir>/data/auth_info.json` - Auth timestamps

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Use `run.py` wrapper, never call scripts directly |
| Auth fails | Run `auth_manager.py setup` - browser opens for manual login |
| Cookies expired | Run `auth_manager.py reauth` (cookies last ~1-2 weeks) |
| API test fails | Run `auth_manager.py test` to diagnose |
| Notebook not found | Run `notebook_manager.py sync` to refresh from API |
| Rate limited | Google enforces limits - wait and retry |

## Architecture Notes

**notebooklm-py** is a Python client that communicates with NotebookLM's internal API via HTTP (httpx). No browser needed for queries/operations - only for initial Google login.

- **Login**: Uses Playwright persistent context to open browser for Google OAuth (auto-detects login completion)
- **All other ops**: Pure HTTP API calls (fast, no browser overhead)
- **Auth**: Cookies stored in Playwright storage state format at `~/.notebooklm/storage_state.json`
- **Async API**: All operations are async; scripts use `asyncio.run()`
