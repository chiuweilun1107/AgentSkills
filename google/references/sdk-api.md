# Google SDK & API Reference

## Python SDK (google-api-python-client)

### Installation

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Authentication

```python
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/youtube.readonly',
]

def get_credentials():
    creds = None
    token_path = 'token.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

    return creds

creds = get_credentials()
```

### Service Account (Server-to-Server)

```python
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=SCOPES
)
# For domain-wide delegation:
creds = creds.with_subject('user@domain.com')
```

---

### Gmail API

```python
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64

service = build('gmail', 'v1', credentials=creds)

# List messages
results = service.users().messages().list(
    userId='me', q='is:unread', maxResults=10
).execute()
messages = results.get('messages', [])

# Read message
msg = service.users().messages().get(
    userId='me', id=msg_id, format='full'
).execute()
subject = next(h['value'] for h in msg['payload']['headers'] if h['name'] == 'Subject')
snippet = msg['snippet']

# Send plain text
def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['to'] = to
    msg['subject'] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()

# Send HTML
def send_html_email(to, subject, html):
    msg = MIMEMultipart('alternative')
    msg['to'] = to
    msg['subject'] = subject
    msg.attach(MIMEText(html, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()

# Send with attachment
def send_with_attachment(to, subject, body, filepath):
    msg = MIMEMultipart()
    msg['to'] = to
    msg['subject'] = subject
    msg.attach(MIMEText(body))

    with open(filepath, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
    msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()

# Search (Gmail query syntax)
results = service.users().messages().list(
    userId='me',
    q='from:boss@company.com has:attachment newer_than:7d'
).execute()

# Labels
labels = service.users().labels().list(userId='me').execute()

# Modify labels
service.users().messages().modify(
    userId='me', id=msg_id,
    body={'addLabelIds': ['STARRED'], 'removeLabelIds': ['UNREAD']}
).execute()

# Trash
service.users().messages().trash(userId='me', id=msg_id).execute()
```

---

### Calendar API

```python
service = build('calendar', 'v3', credentials=creds)

# List upcoming events
from datetime import datetime, timezone
now = datetime.now(timezone.utc).isoformat()

events = service.events().list(
    calendarId='primary',
    timeMin=now,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()

for event in events.get('items', []):
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(f"{start}: {event['summary']}")

# Create event
event = service.events().insert(calendarId='primary', body={
    'summary': 'Team Meeting',
    'location': 'Conference Room',
    'description': 'Weekly sync',
    'start': {
        'dateTime': '2026-03-01T10:00:00',
        'timeZone': 'Asia/Taipei',
    },
    'end': {
        'dateTime': '2026-03-01T11:00:00',
        'timeZone': 'Asia/Taipei',
    },
    'attendees': [
        {'email': 'alice@example.com'},
        {'email': 'bob@example.com'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'popup', 'minutes': 10},
        ],
    },
}).execute()

# Create all-day event
event = service.events().insert(calendarId='primary', body={
    'summary': 'Holiday',
    'start': {'date': '2026-03-01'},
    'end': {'date': '2026-03-02'},
}).execute()

# Update event
service.events().update(
    calendarId='primary', eventId=event_id,
    body={**event, 'summary': 'Updated Title'}
).execute()

# Delete event
service.events().delete(calendarId='primary', eventId=event_id).execute()

# List calendars
calendars = service.calendarList().list().execute()

# Free/Busy query
freebusy = service.freebusy().query(body={
    'timeMin': '2026-03-01T09:00:00+08:00',
    'timeMax': '2026-03-01T18:00:00+08:00',
    'items': [{'id': 'primary'}],
}).execute()
```

---

### Sheets API

```python
service = build('sheets', 'v4', credentials=creds)

SHEET_ID = 'your-spreadsheet-id'

# Read range
result = service.spreadsheets().values().get(
    spreadsheetId=SHEET_ID, range='Sheet1!A1:D10'
).execute()
rows = result.get('values', [])
for row in rows:
    print(row)

# Write range
service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID,
    range='Sheet1!A1',
    valueInputOption='USER_ENTERED',
    body={'values': [
        ['Name', 'Score', 'Grade'],
        ['Alice', 95, 'A'],
        ['Bob', 87, 'B+'],
    ]}
).execute()

# Append rows (adds at end of data)
service.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range='Sheet1!A:C',
    valueInputOption='USER_ENTERED',
    body={'values': [['Charlie', 92, 'A-']]}
).execute()

# Create spreadsheet
spreadsheet = service.spreadsheets().create(body={
    'properties': {'title': 'New Spreadsheet'}
}).execute()
new_id = spreadsheet['spreadsheetId']

# Batch update (formatting, add sheets, etc.)
service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={
    'requests': [
        {'addSheet': {'properties': {'title': 'New Tab'}}},
    ]
}).execute()

# Clear range
service.spreadsheets().values().clear(
    spreadsheetId=SHEET_ID, range='Sheet1!A1:D10'
).execute()
```

---

### Docs API

```python
service = build('docs', 'v1', credentials=creds)

# Create document
doc = service.documents().create(body={'title': 'My Document'}).execute()
doc_id = doc['documentId']

# Read document
doc = service.documents().get(documentId=doc_id).execute()
title = doc['title']
# Parse content elements
for elem in doc['body']['content']:
    if 'paragraph' in elem:
        for run in elem['paragraph'].get('elements', []):
            if 'textRun' in run:
                print(run['textRun']['content'], end='')

# Insert text at beginning
service.documents().batchUpdate(documentId=doc_id, body={
    'requests': [{
        'insertText': {
            'location': {'index': 1},
            'text': 'Hello World\n'
        }
    }]
}).execute()

# Find and replace
service.documents().batchUpdate(documentId=doc_id, body={
    'requests': [{
        'replaceAllText': {
            'containsText': {'text': 'old text', 'matchCase': True},
            'replaceText': 'new text'
        }
    }]
}).execute()
```

---

### Slides API

```python
service = build('slides', 'v1', credentials=creds)

# Create presentation
pres = service.presentations().create(body={'title': 'My Deck'}).execute()
pres_id = pres['presentationId']

# Read slides
pres = service.presentations().get(presentationId=pres_id).execute()
for slide in pres.get('slides', []):
    print(f"Slide ID: {slide['objectId']}")

# Add slide
service.presentations().batchUpdate(presentationId=pres_id, body={
    'requests': [{
        'createSlide': {
            'slideLayoutReference': {'predefinedLayout': 'TITLE_AND_BODY'}
        }
    }]
}).execute()

# Predefined layouts:
# BLANK, TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS,
# TITLE_ONLY, SECTION_HEADER, ONE_COLUMN_TEXT, MAIN_POINT, BIG_NUMBER

# Insert text into shape
service.presentations().batchUpdate(presentationId=pres_id, body={
    'requests': [{
        'insertText': {
            'objectId': shape_id,
            'text': 'Hello Slides!',
            'insertionIndex': 0
        }
    }]
}).execute()
```

---

### Drive API

```python
service = build('drive', 'v3', credentials=creds)

# List files
results = service.files().list(
    pageSize=10,
    fields='files(id, name, mimeType, modifiedTime, size)'
).execute()

# Search files
results = service.files().list(
    q="name contains 'report' and mimeType='application/pdf'",
    fields='files(id, name)'
).execute()

# Upload file
from googleapiclient.http import MediaFileUpload
media = MediaFileUpload('report.pdf', mimetype='application/pdf')
file = service.files().create(
    body={'name': 'report.pdf', 'parents': [folder_id]},
    media_body=media,
    fields='id'
).execute()

# Download file
from googleapiclient.http import MediaIoBaseDownload
import io
request = service.files().get_media(fileId=file_id)
fh = io.FileIO('output.pdf', 'wb')
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    status, done = downloader.next_chunk()

# Export Google Doc as PDF
request = service.files().export_media(fileId=doc_id, mimeType='application/pdf')

# Create folder
folder = service.files().create(body={
    'name': 'My Folder',
    'mimeType': 'application/vnd.google-apps.folder'
}).execute()

# Share file
service.permissions().create(fileId=file_id, body={
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'user@example.com'
}).execute()

# Delete
service.files().delete(fileId=file_id).execute()
```

---

### YouTube Data API

```python
service = build('youtube', 'v3', credentials=creds)

# Search videos
results = service.search().list(
    q='python tutorial',
    part='snippet',
    type='video',
    maxResults=10,
    order='relevance'   # date, rating, relevance, title, viewCount
).execute()

for item in results['items']:
    print(f"{item['snippet']['title']} - {item['id']['videoId']}")

# Get video details
video = service.videos().list(
    part='snippet,statistics,contentDetails',
    id='VIDEO_ID'
).execute()
stats = video['items'][0]['statistics']
print(f"Views: {stats['viewCount']}, Likes: {stats['likeCount']}")

# List channel's uploads
channels = service.channels().list(part='contentDetails', mine=True).execute()
uploads_id = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']

videos = service.playlistItems().list(
    part='snippet', playlistId=uploads_id, maxResults=50
).execute()

# Get comments
comments = service.commentThreads().list(
    part='snippet', videoId='VIDEO_ID', maxResults=20
).execute()
```

---

## JavaScript SDK (googleapis)

### Installation

```bash
npm install googleapis
```

### Authentication

```typescript
import { google } from 'googleapis'

// OAuth2
const oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
oauth2Client.setCredentials({ refresh_token: REFRESH_TOKEN })

// Service Account
const auth = new google.auth.GoogleAuth({
  keyFile: 'service-account.json',
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
})
```

### Usage Examples

```typescript
// Gmail
const gmail = google.gmail({ version: 'v1', auth: oauth2Client })
const res = await gmail.users.messages.list({ userId: 'me', q: 'is:unread' })

// Calendar
const calendar = google.calendar({ version: 'v3', auth: oauth2Client })
const events = await calendar.events.list({
  calendarId: 'primary',
  timeMin: new Date().toISOString(),
  maxResults: 10,
  singleEvents: true,
  orderBy: 'startTime',
})

// Sheets
const sheets = google.sheets({ version: 'v4', auth: oauth2Client })
const data = await sheets.spreadsheets.values.get({
  spreadsheetId: SHEET_ID,
  range: 'Sheet1!A1:D10',
})

// Drive
const drive = google.drive({ version: 'v3', auth: oauth2Client })
const files = await drive.files.list({ pageSize: 10 })
```

---

## REST API (curl)

```bash
# Get access token
TOKEN=$(gog auth token)

# Gmail - list messages
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults=5"

# Calendar - list events
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=10&orderBy=startTime&singleEvents=true&timeMin=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Sheets - read range
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SHEET_ID/values/Sheet1!A1:D10"

# Drive - list files
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files?pageSize=10"
```

## Common Scopes

| Scope | Access |
|-------|--------|
| `gmail.readonly` | Read email only |
| `gmail.modify` | Read + write (no delete) |
| `gmail.send` | Send only |
| `calendar` | Full calendar access |
| `calendar.readonly` | Read calendar only |
| `spreadsheets` | Full Sheets access |
| `spreadsheets.readonly` | Read Sheets only |
| `documents` | Full Docs access |
| `presentations` | Full Slides access |
| `drive` | Full Drive access |
| `drive.readonly` | Read Drive only |
| `youtube.readonly` | Read YouTube data |
| `youtube.upload` | Upload videos |
