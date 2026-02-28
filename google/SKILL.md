---
name: google
description: 'Google Workspace operations — Gmail, Calendar, Drive, Docs, Sheets, Slides, YouTube. Use when user mentions gmail, email, 信件, calendar, 行事曆, google docs, 文件, sheets, 試算表, slides, 簡報, youtube, drive, 雲端硬碟, "寄信", "查行程", "開試算表". Covers gog CLI, Python SDK, MCP server, and Apps Script.'
---

# Google Workspace Operations

Comprehensive skill for Google services: Gmail, Calendar, Drive, Docs, Sheets, Slides, YouTube. Choose the right mode for each task.

## Mode Decision Flow

```
Google task?
    │
    ├─ Quick terminal operation?
    │   → gog CLI — no code needed, OAuth stored in keychain
    │
    ├─ AI agent direct integration?
    │   → MCP Server — Claude can call tools directly
    │
    ├─ Python/JS application code?
    │   → SDK — full API access with typed responses
    │
    ├─ Scheduled automation inside Google?
    │   → Apps Script — runs server-side, no infra needed
    │
    └─ Bulk data / complex logic?
        → Python SDK — most flexible, handles pagination
```

## Quick Reference (CLI)

Most tasks start with gog CLI. For SDK code, see `references/sdk-api.md`.

### Gmail
```bash
gog gmail search "is:unread newer_than:1d"         # Search emails
gog gmail send --to user@example.com --subject "Hi" --body "Hello"
gog gmail labels                                     # List labels
```

### Calendar
```bash
gog calendar events --today                          # Today's events
gog calendar events --days 7 --json                  # Next 7 days
gog calendar create --title "Meeting" --start "2026-03-01T10:00" --duration 1h
```

### Sheets
```bash
gog sheets read SPREADSHEET_ID "Sheet1!A1:D10"      # Read range
gog sheets write SPREADSHEET_ID "Sheet1!A1" "Hello"  # Write cell
```

### Docs & Slides
```bash
gog docs create --title "My Document"
gog docs export DOCUMENT_ID --format pdf -o output.pdf
gog slides create --title "My Presentation"
gog slides export PRESENTATION_ID --format pptx -o output.pptx
```

### YouTube
```bash
gog youtube search "python tutorial" --max 5 --json
yt-dlp --write-auto-sub --sub-lang zh-TW,en -o "%(title)s.%(ext)s" URL
```

### Drive
```bash
gog drive list                                       # List files
gog drive upload ./file.pdf                           # Upload
gog drive download FILE_ID -o ./output.pdf            # Download
```

## Mode Comparison

| Mode | Best For | Why Choose This | Install |
|------|----------|-----------------|---------|
| **gog CLI** | Quick terminal ops | No code needed, OAuth in keychain | `brew install steipete/tap/gogcli` |
| **MCP Server** | AI agent integration | Claude calls tools directly without scripts | `pip install workspace-mcp` |
| **Python SDK** | App code, bulk ops | Full API access, handles pagination and batching | `pip install google-api-python-client` |
| **JS SDK** | Node.js/TS projects | Native TypeScript types, async/await | `npm install googleapis` |
| **Apps Script** | Scheduled automation | Runs inside Google, no infra to manage | script.google.com |

## Authentication

### gog CLI (recommended for terminal — stores OAuth token in OS keychain)
```bash
brew install steipete/tap/gogcli
gog auth login                    # Opens browser for OAuth
gog auth status                   # Check current auth
```

### MCP Server
```bash
claude mcp add google-workspace \
  --env GOOGLE_OAUTH_CLIENT_ID=xxx \
  --env GOOGLE_OAUTH_CLIENT_SECRET=xxx \
  -- uvx workspace-mcp
```

For Python SDK OAuth setup and scope configuration, see `references/sdk-api.md`.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| OAuth token expired | `gog auth login` or refresh via SDK |
| Scope insufficient | Add required scope and re-authenticate |
| Rate limit (quota) | Check [Google API Console](https://console.cloud.google.com/apis/dashboard) quotas |
| File not found (Drive) | Check file ID and sharing permissions |
| Can't send email | Verify `gmail.send` scope is granted |
| Calendar timezone wrong | Specify timezone in event: `timeZone: 'Asia/Taipei'` |
| Sheets formula not evaluated | Use `valueInputOption: 'USER_ENTERED'` |

## References

Extended documentation in `references/`:
- **`cli.md`** — Complete gog CLI commands for all Google services
- **`sdk-api.md`** — Python SDK, JS SDK, REST API, OAuth setup, common patterns
- **`mcp.md`** — MCP server setup, available tools, multi-account configuration
