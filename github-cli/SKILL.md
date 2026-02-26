---
name: github-cli
description: 'GitHub operations via gh CLI. Use when user wants to create repos, manage issues, pull requests, releases, or GitHub Actions. Triggers on "create repo", "github", "gh", "建立repo", "開repo", "PR", "issue", "release". Handles auth detection and guides setup.'
---

# GitHub CLI Operations

Perform GitHub operations using `gh` CLI. Covers repository management, issues, pull requests, releases, and GitHub Actions.

## When to Use

- User wants to create/manage GitHub repositories
- User mentions GitHub, gh, repo, PR, issue, release
- User says "建立repo", "開repo", "推上github", "建PR"
- Need to check GitHub status or authentication

## When NOT to Use

- Local git operations only (commit, branch, merge) — use git directly
- Reading file contents from a repo — use `gh api` or clone

## Step 1: Check Authentication (ALWAYS FIRST)

```bash
gh auth status
```

**If not authenticated:**
```bash
gh auth login
```
Tell user: "需要登入 GitHub。請在瀏覽器中完成授權。"

**If token lacks required scope:**
```bash
# Add specific scope
gh auth refresh -s <scope>

# Common scopes needed:
# repo          — Full repo access (default)
# read:org      — Org membership
# workflow      — GitHub Actions
# delete_repo   — Delete repositories
# admin:org     — Org admin (create repos in org)
```

## Step 2: Operations Reference

### Repository Management

```bash
# Create public repo
gh repo create <name> --public --description "desc" --clone

# Create private repo
gh repo create <name> --private --description "desc" --clone

# Create from existing local directory
cd /path/to/project
git init
gh repo create <name> --source=. --public --push

# Create in organization
gh repo create <org>/<name> --public --description "desc"

# View repo info
gh repo view <owner>/<repo>

# List user's repos
gh repo list --limit 20

# Clone
gh repo clone <owner>/<repo>

# Delete (requires delete_repo scope)
gh repo delete <owner>/<repo> --yes
```

### Issues

```bash
# Create issue
gh issue create --title "Title" --body "Description"

# Create with labels and assignee
gh issue create --title "Title" --body "Body" --label "bug" --assignee "@me"

# List issues
gh issue list
gh issue list --state closed --limit 10

# View issue
gh issue view <number>

# Close issue
gh issue close <number>

# Comment on issue
gh issue comment <number> --body "Comment text"
```

### Pull Requests

```bash
# Create PR from current branch
gh pr create --title "Title" --body "Description"

# Create PR with reviewers
gh pr create --title "Title" --body "Body" --reviewer user1,user2

# Create draft PR
gh pr create --title "Title" --body "Body" --draft

# List PRs
gh pr list

# View PR details
gh pr view <number>

# Check PR status (CI checks)
gh pr checks <number>

# Merge PR
gh pr merge <number> --merge    # merge commit
gh pr merge <number> --squash   # squash merge
gh pr merge <number> --rebase   # rebase merge

# Review PR
gh pr review <number> --approve
gh pr review <number> --request-changes --body "Feedback"
```

### Releases

```bash
# Create release from tag
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes"

# Create release with auto-generated notes
gh release create v1.0.0 --generate-notes

# Upload assets
gh release create v1.0.0 ./dist/*.zip --title "v1.0.0"

# List releases
gh release list

# Download release assets
gh release download v1.0.0
```

### GitHub Actions

```bash
# List workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch run in progress
gh run watch <run-id>

# Re-run failed jobs
gh run rerun <run-id> --failed

# List workflows
gh workflow list

# Trigger workflow manually
gh workflow run <workflow-name>
```

### GitHub API (Advanced)

```bash
# GET request
gh api repos/<owner>/<repo>

# POST request
gh api repos/<owner>/<repo>/issues --method POST -f title="Title" -f body="Body"

# GraphQL query
gh api graphql -f query='{ viewer { login } }'

# Paginated list
gh api repos/<owner>/<repo>/issues --paginate
```

## Common Workflows

### New Project Setup
```bash
# 1. Create repo
gh repo create my-project --public --description "My project" --clone
cd my-project

# 2. Add initial content
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit"
git push

# 3. Set up branch protection (via API)
gh api repos/<owner>/my-project/branches/main/protection \
  --method PUT \
  -f 'required_pull_request_reviews[required_approving_review_count]=1' \
  -F 'enforce_admins=true'
```

### From Local to GitHub
```bash
# For existing local project
cd /path/to/existing-project
gh repo create <name> --source=. --public --push
```

## Auth Troubleshooting

| Problem | Solution |
|---------|----------|
| `gh: command not found` | Install: `brew install gh` (macOS) or check PATH |
| Not logged in | `gh auth login` — follow browser prompts |
| Permission denied (403) | `gh auth refresh -s <missing-scope>` |
| Can't create org repo | Need `admin:org` scope or org permissions |
| Can't delete repo | `gh auth refresh -s delete_repo` |
| Token expired | `gh auth login` to re-authenticate |
| SSH vs HTTPS | `gh auth setup-git` to configure git protocol |

## Platform Notes

- **macOS (Homebrew)**: `brew install gh` — ensure `/opt/homebrew/bin` in PATH
- **Linux**: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
- **Auth storage**: `~/.config/gh/hosts.yml`
- **Config**: `gh config set` for defaults (editor, browser, protocol)
