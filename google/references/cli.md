# Google CLI (gog) Complete Reference

## Installation & Auth

```bash
# Install
brew install steipete/tap/gogcli

# Authenticate
gog auth login                    # Opens browser for Google OAuth
gog auth status                   # Check auth status
gog auth logout                   # Logout
gog auth accounts                 # List accounts (multi-account support)
gog auth switch ALIAS             # Switch active account
```

## Gmail

```bash
# Search
gog gmail search "is:unread"
gog gmail search "from:user@example.com newer_than:7d"
gog gmail search "subject:invoice has:attachment" --json
gog gmail search "in:inbox is:unread" --max 20

# Common search operators
# is:unread, is:starred, is:important
# from:, to:, cc:, bcc:
# subject:, has:attachment
# newer_than:1d, older_than:7d
# after:2026/01/01, before:2026/03/01
# in:inbox, in:sent, in:trash
# label:work, category:primary
# filename:pdf, larger:5M

# Read message
gog gmail read MESSAGE_ID
gog gmail read MESSAGE_ID --json
gog gmail read MESSAGE_ID --format eml -o email.eml

# Send
gog gmail send --to user@example.com --subject "Hello" --body "Plain text body"
gog gmail send --to user@example.com --subject "Report" --html "<h1>HTML body</h1>"
gog gmail send --to user@example.com --subject "File" --attach ./report.pdf
gog gmail send --to a@x.com --cc b@x.com --bcc c@x.com --subject "Team" --body "..."

# Reply
gog gmail reply MESSAGE_ID --body "Thanks!"

# Labels
gog gmail labels                   # List all labels
gog gmail label MESSAGE_ID "Work"  # Add label
gog gmail unlabel MESSAGE_ID "Inbox"  # Remove label

# Drafts
gog gmail drafts                   # List drafts
gog gmail draft --to user@example.com --subject "Draft" --body "..."

# Trash / Archive
gog gmail trash MESSAGE_ID
gog gmail archive MESSAGE_ID

# Filters
gog gmail filters                  # List filters
```

## Google Calendar

```bash
# List events
gog calendar events --today
gog calendar events --tomorrow
gog calendar events --week
gog calendar events --days 7
gog calendar events --days 30 --json
gog calendar events --from "2026-03-01" --to "2026-03-31"

# Create event
gog calendar create --title "Meeting" \
  --start "2026-03-01T10:00" --end "2026-03-01T11:00"

gog calendar create --title "Lunch" \
  --start "2026-03-01T12:00" --duration 1h

gog calendar create --title "All Day" \
  --start "2026-03-01" --all-day

gog calendar create --title "Team Sync" \
  --start "2026-03-01T14:00" --duration 30m \
  --attendees "a@x.com,b@x.com" \
  --location "Conference Room A" \
  --description "Weekly sync meeting"

# Delete event
gog calendar delete EVENT_ID

# Calendars
gog calendar list                  # List all calendars
gog calendar freebusy --start "2026-03-01T09:00" --end "2026-03-01T18:00"
```

## Google Drive

```bash
# List files
gog drive list
gog drive list --type document     # Only Google Docs
gog drive list --type spreadsheet  # Only Sheets
gog drive list --type folder
gog drive list --json

# Search
gog drive search "name contains 'report'"
gog drive search "mimeType='application/pdf'"
gog drive search "modifiedTime > '2026-01-01'"

# Upload
gog drive upload ./report.pdf
gog drive upload ./data.csv --folder FOLDER_ID
gog drive upload ./image.png --name "Screenshot 2026"

# Download
gog drive download FILE_ID
gog drive download FILE_ID -o ./output.pdf

# Export (Google native formats)
gog drive export FILE_ID --format pdf -o report.pdf
gog drive export FILE_ID --format docx -o report.docx
gog drive export FILE_ID --format xlsx -o data.xlsx
gog drive export FILE_ID --format pptx -o deck.pptx
gog drive export FILE_ID --format csv -o data.csv

# Permissions
gog drive share FILE_ID --email user@example.com --role writer
gog drive share FILE_ID --email user@example.com --role reader
gog drive unshare FILE_ID --email user@example.com

# Delete
gog drive delete FILE_ID
gog drive trash FILE_ID
```

## Google Sheets

```bash
# Read
gog sheets read SPREADSHEET_ID "Sheet1!A1:D10"
gog sheets read SPREADSHEET_ID "Sheet1!A:A" --json

# Write
gog sheets write SPREADSHEET_ID "Sheet1!A1" "Hello"
gog sheets update SPREADSHEET_ID "Sheet1!A1:B2" --values '[["a","b"],["c","d"]]'

# Append (add rows at end)
gog sheets append SPREADSHEET_ID "Sheet1!A:D" --values '[["new","row","data","here"]]'

# Create
gog sheets create --title "New Spreadsheet"

# List sheets (tabs) in spreadsheet
gog sheets list SPREADSHEET_ID
```

## Google Docs

```bash
# Create
gog docs create --title "New Document"

# Read
gog docs read DOCUMENT_ID
gog docs read DOCUMENT_ID --json

# Export
gog docs export DOCUMENT_ID --format pdf -o output.pdf
gog docs export DOCUMENT_ID --format docx -o output.docx
gog docs export DOCUMENT_ID --format txt -o output.txt

# Copy
gog docs copy DOCUMENT_ID --title "Copy of Document"
```

## Google Slides

```bash
# Create
gog slides create --title "New Presentation"

# Read
gog slides read PRESENTATION_ID
gog slides read PRESENTATION_ID --json

# Export
gog slides export PRESENTATION_ID --format pdf -o output.pdf
gog slides export PRESENTATION_ID --format pptx -o output.pptx

# Copy
gog slides copy PRESENTATION_ID --title "Copy of Deck"
```

## Tasks

```bash
# List
gog tasks list
gog tasks list --json

# Create
gog tasks create --title "Buy groceries"
gog tasks create --title "Submit report" --due "2026-03-01"

# Complete
gog tasks complete TASK_ID

# Delete
gog tasks delete TASK_ID
```

## Common Flags

| Flag | Description |
|------|-------------|
| `--json` | JSON output (ideal for scripting/piping) |
| `--max N` | Limit results |
| `--account ALIAS` | Use specific account |
| `-o FILE` | Output to file |
| `--quiet` | Suppress output |

## Output Parsing

```bash
# Pipe JSON to jq
gog gmail search "is:unread" --json | jq '.[].subject'
gog calendar events --today --json | jq '.[] | {title: .summary, start: .start}'
gog drive list --json | jq '.[] | select(.mimeType | contains("pdf"))'
```
