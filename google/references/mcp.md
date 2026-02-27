# Google MCP Server Reference

## Available MCP Servers

| Server | Language | Services | Install |
|--------|----------|----------|---------|
| **google_workspace_mcp** | Python | Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Tasks, Contacts, Chat | `pip install workspace-mcp` |
| **google-mcp-server** | Go | Gmail, Calendar, Drive, Docs, Sheets, Slides | `brew install ngs/tap/google-mcp-server` |
| **gworkspace-mcp** | Node.js | Gmail, Calendar, Drive, Docs, Tasks | `npx gworkspace-mcp` |

## google_workspace_mcp (Recommended)

Most comprehensive — 100+ tools, 10+ services.

### Setup

```bash
# Install
pip install workspace-mcp

# Add to Claude Code
claude mcp add google-workspace \
  --env GOOGLE_OAUTH_CLIENT_ID=your-client-id \
  --env GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret \
  -- uvx workspace-mcp

# Verify
claude mcp list
claude mcp get google-workspace
```

### OAuth Setup (One-Time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable APIs (Gmail, Calendar, Drive, Sheets, Docs, Slides, YouTube)
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download `credentials.json`
5. Set env vars: `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`

### Available Tools by Service

#### Gmail (18+ tools)
| Tool | Description |
|------|-------------|
| `gmail_search` | Search emails with Gmail query syntax |
| `gmail_read` | Read message content |
| `gmail_send` | Send email (plain/HTML) |
| `gmail_reply` | Reply to message |
| `gmail_forward` | Forward message |
| `gmail_draft` | Create draft |
| `gmail_labels` | List labels |
| `gmail_label` | Add/remove label |
| `gmail_trash` | Trash message |
| `gmail_mark_read` | Mark as read |
| `gmail_mark_unread` | Mark as unread |
| `gmail_star` | Star/unstar |
| `gmail_archive` | Archive message |
| `gmail_batch_modify` | Batch label/read operations |

#### Calendar (10+ tools)
| Tool | Description |
|------|-------------|
| `calendar_list` | List calendars |
| `calendar_events` | List events (time range) |
| `calendar_get_event` | Get event details |
| `calendar_create_event` | Create event |
| `calendar_update_event` | Update event |
| `calendar_delete_event` | Delete event |
| `calendar_freebusy` | Free/busy query |
| `calendar_quick_add` | Quick add (natural language) |

#### Drive (10+ tools)
| Tool | Description |
|------|-------------|
| `drive_list` | List files |
| `drive_search` | Search files |
| `drive_get` | Get file metadata |
| `drive_download` | Download file |
| `drive_upload` | Upload file |
| `drive_create_folder` | Create folder |
| `drive_move` | Move file |
| `drive_copy` | Copy file |
| `drive_delete` | Delete file |
| `drive_share` | Share file |
| `drive_export` | Export Google Docs format |

#### Sheets
| Tool | Description |
|------|-------------|
| `sheets_read` | Read cell range |
| `sheets_write` | Write cell range |
| `sheets_append` | Append rows |
| `sheets_clear` | Clear range |
| `sheets_create` | Create spreadsheet |
| `sheets_metadata` | Get spreadsheet info |

#### Docs
| Tool | Description |
|------|-------------|
| `docs_create` | Create document |
| `docs_read` | Read document content |
| `docs_insert` | Insert text |
| `docs_append` | Append text |
| `docs_replace` | Find and replace |
| `docs_export` | Export to PDF/DOCX |

#### Slides
| Tool | Description |
|------|-------------|
| `slides_create` | Create presentation |
| `slides_read` | Read presentation |
| `slides_add_slide` | Add slide |
| `slides_insert_text` | Insert text |
| `slides_add_image` | Add image |
| `slides_export` | Export to PDF/PPTX |

#### Tasks
| Tool | Description |
|------|-------------|
| `tasks_list` | List tasks |
| `tasks_create` | Create task |
| `tasks_update` | Update task |
| `tasks_complete` | Mark complete |
| `tasks_delete` | Delete task |

---

## google-mcp-server (Go, Lightweight)

### Setup

```bash
# Install
brew tap ngs/tap
brew install google-mcp-server

# Add to Claude Code
claude mcp add google -- google-mcp-server

# Auth
google-mcp-server auth login
```

### Features
- Slides support with Markdown-to-Slides conversion
- Auto-pagination for large slide decks
- Multi-account management
- Lightweight single binary

---

## Multi-Account Configuration

### google_workspace_mcp
```bash
# Add multiple accounts
claude mcp add google-personal \
  --env GOOGLE_OAUTH_CLIENT_ID=xxx \
  --env GOOGLE_OAUTH_CLIENT_SECRET=xxx \
  --env GOOGLE_ACCOUNT=personal \
  -- uvx workspace-mcp

claude mcp add google-work \
  --env GOOGLE_OAUTH_CLIENT_ID=xxx \
  --env GOOGLE_OAUTH_CLIENT_SECRET=xxx \
  --env GOOGLE_ACCOUNT=work \
  -- uvx workspace-mcp
```

### google-mcp-server
```bash
google-mcp-server auth login --alias personal
google-mcp-server auth login --alias work
google-mcp-server auth switch work
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| OAuth consent screen error | Ensure app is in "Testing" mode and your email is added as test user |
| Token expired | MCP server auto-refreshes; if not, delete token and re-auth |
| API not enabled | Enable required APIs in [Google Cloud Console](https://console.cloud.google.com/apis/library) |
| Quota exceeded | Check quotas in API Console; default: 10,000 requests/100 seconds |
| MCP server not connecting | Check `claude mcp list`, verify env vars are set |
| Permission denied | Verify OAuth scopes include required service |

## Required APIs to Enable

Enable these in Google Cloud Console → APIs & Services → Library:

| API | For |
|-----|-----|
| Gmail API | Email |
| Google Calendar API | Calendar |
| Google Drive API | File management |
| Google Sheets API | Spreadsheets |
| Google Docs API | Documents |
| Google Slides API | Presentations |
| YouTube Data API v3 | YouTube |
| Google Tasks API | Tasks |
| People API | Contacts |
