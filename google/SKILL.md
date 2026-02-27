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
    │   → gog CLI (brew install steipete/tap/gogcli)
    │
    ├─ AI agent direct integration?
    │   → MCP Server (google_workspace_mcp)
    │
    ├─ Python/JS application code?
    │   → SDK (google-api-python-client / googleapis)
    │
    ├─ Scheduled automation inside Google?
    │   → Apps Script (server-side, cron triggers)
    │
    └─ Bulk data / complex logic?
        → Python SDK (most flexible)
```

## Quick Reference by Service

### Gmail

```bash
# CLI (gog)
gog gmail search "is:unread newer_than:1d"         # Search emails
gog gmail search "from:boss@company.com" --json     # JSON output
gog gmail send --to user@example.com --subject "Hi" --body "Hello"
gog gmail send --to user@example.com --subject "Report" --html "<h1>Report</h1>"
gog gmail labels                                     # List labels
gog gmail drafts                                     # List drafts
```

```python
# Python SDK
from googleapiclient.discovery import build
service = build('gmail', 'v1', credentials=creds)

# Search
results = service.users().messages().list(userId='me', q='is:unread').execute()

# Send
from email.mime.text import MIMEText
import base64
msg = MIMEText('Hello')
msg['to'] = 'user@example.com'
msg['subject'] = 'Hi'
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
service.users().messages().send(userId='me', body={'raw': raw}).execute()
```

### Google Calendar

```bash
# CLI (gog)
gog calendar events --today                          # Today's events
gog calendar events --week                           # This week
gog calendar events --days 7 --json                  # Next 7 days (JSON)
gog calendar create --title "Meeting" --start "2026-03-01T10:00" --end "2026-03-01T11:00"
gog calendar create --title "Lunch" --start "2026-03-01T12:00" --duration 1h
```

```python
# Python SDK
service = build('calendar', 'v3', credentials=creds)

# List events
events = service.events().list(
    calendarId='primary',
    timeMin='2026-03-01T00:00:00Z',
    maxResults=10, singleEvents=True,
    orderBy='startTime'
).execute()

# Create event
event = service.events().insert(calendarId='primary', body={
    'summary': 'Meeting',
    'start': {'dateTime': '2026-03-01T10:00:00+08:00'},
    'end': {'dateTime': '2026-03-01T11:00:00+08:00'},
}).execute()
```

### Google Sheets

```bash
# CLI (gog)
gog sheets read SPREADSHEET_ID "Sheet1!A1:D10"      # Read range
gog sheets write SPREADSHEET_ID "Sheet1!A1" "Hello"  # Write cell
gog sheets update SPREADSHEET_ID "Sheet1!A1:B2" --values '[["a","b"],["c","d"]]'
```

```python
# Python SDK
service = build('sheets', 'v4', credentials=creds)

# Read
result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID, range='Sheet1!A1:D10'
).execute()
rows = result.get('values', [])

# Write
service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range='Sheet1!A1',
    valueInputOption='USER_ENTERED',
    body={'values': [['Hello', 'World'], [1, 2]]}
).execute()

# Append row
service.spreadsheets().values().append(
    spreadsheetId=SHEET_ID, range='Sheet1!A:A',
    valueInputOption='USER_ENTERED',
    body={'values': [['New', 'Row', 'Data']]}
).execute()
```

### Google Docs

```bash
# CLI (gog)
gog docs create --title "My Document"
gog docs export DOCUMENT_ID --format pdf -o output.pdf
gog docs export DOCUMENT_ID --format docx -o output.docx
```

```python
# Python SDK
service = build('docs', 'v1', credentials=creds)

# Create
doc = service.documents().create(body={'title': 'My Doc'}).execute()

# Read
doc = service.documents().get(documentId=DOC_ID).execute()
content = doc.get('body', {}).get('content', [])

# Insert text
service.documents().batchUpdate(documentId=DOC_ID, body={
    'requests': [{'insertText': {'location': {'index': 1}, 'text': 'Hello World\n'}}]
}).execute()
```

### Google Slides

```bash
# CLI (gog)
gog slides create --title "My Presentation"
gog slides export PRESENTATION_ID --format pdf -o output.pdf
gog slides export PRESENTATION_ID --format pptx -o output.pptx
```

```python
# Python SDK
service = build('slides', 'v1', credentials=creds)

# Create
pres = service.presentations().create(body={'title': 'My Deck'}).execute()

# Get slides
pres = service.presentations().get(presentationId=PRES_ID).execute()
slides = pres.get('slides', [])

# Add slide
service.presentations().batchUpdate(presentationId=PRES_ID, body={
    'requests': [{'createSlide': {'slideLayoutReference': {'predefinedLayout': 'TITLE_AND_BODY'}}}]
}).execute()
```

### YouTube

```bash
# Search (via gog or yt-dlp)
gog youtube search "python tutorial" --max 5 --json

# Download video (yt-dlp)
yt-dlp "https://youtube.com/watch?v=VIDEO_ID"
yt-dlp --write-auto-sub --sub-lang zh-TW,en -o "%(title)s.%(ext)s" URL

# Extract transcript only
yt-dlp --write-auto-sub --skip-download URL
```

```python
# Python SDK
service = build('youtube', 'v3', credentials=creds)

# Search
results = service.search().list(q='python tutorial', part='snippet', maxResults=5).execute()

# Get video details
video = service.videos().list(part='snippet,statistics', id='VIDEO_ID').execute()

# List playlist items
items = service.playlistItems().list(part='snippet', playlistId='PLAYLIST_ID', maxResults=50).execute()
```

### Google Drive

```bash
# CLI (gog)
gog drive list                                       # List files
gog drive search "name contains 'report'"            # Search
gog drive upload ./file.pdf                           # Upload
gog drive download FILE_ID -o ./output.pdf            # Download
gog drive export FILE_ID --format pdf -o output.pdf   # Export Google Docs/Sheets
```

```python
# Python SDK
service = build('drive', 'v3', credentials=creds)

# List files
results = service.files().list(pageSize=10, fields='files(id, name, mimeType)').execute()

# Upload
from googleapiclient.http import MediaFileUpload
media = MediaFileUpload('report.pdf', mimetype='application/pdf')
file = service.files().create(body={'name': 'report.pdf'}, media_body=media).execute()

# Download
from googleapiclient.http import MediaIoBaseDownload
import io
request = service.files().get_media(fileId=FILE_ID)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    status, done = downloader.next_chunk()
```

## Mode Comparison

| Mode | When | Auth | Install |
|------|------|------|---------|
| **gog CLI** | Quick terminal ops, scripting | OAuth (keyring) | `brew install steipete/tap/gogcli` |
| **MCP Server** | AI agent integration | OAuth | `pip install workspace-mcp` |
| **Python SDK** | Application code, bulk ops | Service account / OAuth | `pip install google-api-python-client` |
| **JS SDK** | Node.js/TS projects | Service account / OAuth | `npm install googleapis` |
| **Apps Script** | Scheduled automation | Built-in (Google account) | script.google.com |

## Authentication Setup

### gog CLI (Recommended for terminal)
```bash
brew install steipete/tap/gogcli
gog auth login                    # Opens browser for OAuth
gog auth status                   # Check current auth
```

### Python SDK
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/youtube.readonly',
]

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)
# Save creds for reuse: creds.to_json()
```

### MCP Server
```bash
# Claude Code
claude mcp add google-workspace \
  --env GOOGLE_OAUTH_CLIENT_ID=xxx \
  --env GOOGLE_OAUTH_CLIENT_SECRET=xxx \
  -- uvx workspace-mcp

# Or Go-based
brew tap ngs/tap && brew install google-mcp-server
claude mcp add google -- google-mcp-server
```

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
