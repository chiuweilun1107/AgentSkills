# GitHub CLI (gh) Complete Reference

## Table of Contents
- [Repository Management](#repository-management)
- [Issues](#issues)
- [Pull Requests](#pull-requests)
- [Releases](#releases)
- [GitHub Actions](#github-actions)
- [Common Workflows](#common-workflows)
- [Auth & Config](#auth--config)

## Repository Management

```bash
# Create
gh repo create <name> --public --description "desc" --clone
gh repo create <name> --private --description "desc" --clone
gh repo create <org>/<name> --public --description "desc"

# From existing local project
cd /path/to/project && git init
gh repo create <name> --source=. --public --push

# View / List / Clone
gh repo view <owner>/<repo>
gh repo list --limit 20
gh repo clone <owner>/<repo>

# Delete (requires delete_repo scope)
gh repo delete <owner>/<repo> --yes

# Fork
gh repo fork <owner>/<repo> --clone
```

## Issues

```bash
# Create
gh issue create --title "Title" --body "Description"
gh issue create --title "T" --body "B" --label "bug" --assignee "@me"
gh issue create --title "T" --body "B" --milestone "v1.0"

# List / View
gh issue list
gh issue list --state closed --limit 10
gh issue list --label "bug" --assignee "@me"
gh issue view <number>

# Update
gh issue close <number>
gh issue reopen <number>
gh issue comment <number> --body "Comment text"
gh issue edit <number> --add-label "priority"
gh issue pin <number>
gh issue transfer <number> <destination-repo>
```

## Pull Requests

```bash
# Create
gh pr create --title "Title" --body "Description"
gh pr create --title "T" --body "B" --reviewer user1,user2
gh pr create --title "T" --body "B" --draft
gh pr create --title "T" --body "B" --base develop

# List / View
gh pr list
gh pr list --state merged --limit 10
gh pr view <number>
gh pr diff <number>

# Review
gh pr review <number> --approve
gh pr review <number> --request-changes --body "Feedback"
gh pr review <number> --comment --body "Looks good"

# Merge
gh pr merge <number> --merge     # merge commit
gh pr merge <number> --squash    # squash merge
gh pr merge <number> --rebase    # rebase merge
gh pr merge <number> --auto      # auto-merge when checks pass

# Status
gh pr checks <number>
gh pr status                     # PRs relevant to you

# Update
gh pr close <number>
gh pr reopen <number>
gh pr ready <number>             # mark ready for review
gh pr comment <number> --body "text"
gh pr edit <number> --add-reviewer user1
```

## Releases

```bash
# Create
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes"
gh release create v1.0.0 --generate-notes
gh release create v1.0.0 ./dist/*.zip --title "v1.0.0"
gh release create v1.0.0 --prerelease --title "Beta"

# List / View / Download
gh release list
gh release view v1.0.0
gh release download v1.0.0

# Delete
gh release delete v1.0.0 --yes
```

## GitHub Actions

```bash
# Workflow runs
gh run list
gh run list --workflow build.yml
gh run view <run-id>
gh run view <run-id> --log        # full logs
gh run watch <run-id>             # live progress
gh run rerun <run-id> --failed    # retry failed jobs
gh run cancel <run-id>

# Workflows
gh workflow list
gh workflow run <workflow-name>
gh workflow run <workflow-name> -f param=value
gh workflow enable <workflow-name>
gh workflow disable <workflow-name>

# Cache (cleanup)
gh cache list
gh cache delete <cache-id>
```

## Common Workflows

### New Project Setup
```bash
gh repo create my-project --public --description "My project" --clone
cd my-project
echo "# My Project" > README.md
git add . && git commit -m "Initial commit" && git push
```

### Feature Branch → PR → Merge
```bash
git checkout -b feature/my-feature
# ... make changes, commit ...
git push -u origin feature/my-feature
gh pr create --title "Add my feature" --body "Description"
# After review:
gh pr merge <number> --squash
```

### Branch Protection (via gh api)
```bash
gh api repos/<owner>/<repo>/branches/main/protection \
  --method PUT \
  -f 'required_pull_request_reviews[required_approving_review_count]=1' \
  -F 'enforce_admins=true'
```

## Auth & Config

```bash
# Authentication
gh auth login                        # interactive login
gh auth status                       # check current auth
gh auth refresh -s <scope>           # add scope
gh auth setup-git                    # configure git to use gh auth
gh auth token                        # print current token

# Common scopes
# repo          — full repo access (default)
# read:org      — org membership
# workflow      — GitHub Actions
# delete_repo   — delete repositories
# admin:org     — org admin

# Configuration
gh config set editor vim
gh config set git_protocol ssh       # or https
gh config list

# Storage
# Auth: ~/.config/gh/hosts.yml
# Config: ~/.config/gh/config.yml
```

### Platform Install

| Platform | Command |
|----------|---------|
| macOS | `brew install gh` |
| Ubuntu/Debian | `sudo apt install gh` |
| Windows | `winget install GitHub.cli` |

Ensure PATH includes the install location (macOS: `/opt/homebrew/bin`).
