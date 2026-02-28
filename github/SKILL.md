---
name: github
description: 'GitHub operations via CLI, REST API, SDK, and MCP. Use when user wants to create repos, manage issues, pull requests, releases, GitHub Actions, or automate GitHub workflows. Triggers on "github", "gh", "repo", "PR", "issue", "release", "建立repo", "開repo", "推上github". Covers gh CLI, gh api, REST API, Python/JS SDK, and GitHub MCP server.'
---

# GitHub Operations

Comprehensive GitHub skill covering all operation modes: CLI, REST API, SDK, and MCP. Choose the right mode for each task.

## When to Use

- User mentions GitHub, gh, repo, PR, issue, release, Actions
- User says "建立repo", "開repo", "推上github", "建PR"
- Need to automate GitHub workflows
- Need to query GitHub data programmatically

## When NOT to Use

- Local git operations only (commit, branch, merge) — use git directly
- GitHub web UI operations — tell user to use browser

## Operation Mode Decision Flow

```
What do you need?
    │
    ├─ Interactive CLI operations (create repo, merge PR, check status)
    │   → gh CLI — fastest for one-off tasks
    │   → See references/cli.md
    │
    ├─ API calls beyond gh CLI coverage (webhooks, branch protection, advanced queries)
    │   → gh api (wraps REST API with auth) or direct curl
    │   → See references/api-sdk.md
    │
    ├─ Integrate GitHub into application code (Python/JS/TS project)
    │   → SDK (PyGithub, @octokit/rest)
    │   → See references/api-sdk.md
    │
    └─ AI agent tool access (Claude Code, OpenClaw)
        → GitHub MCP server
        → See references/api-sdk.md → MCP section
```

## Quick Reference (Most Common Operations)

### Auth Check (run first — most errors trace back to auth)
```bash
gh auth status
# If not authenticated: gh auth login
# If missing scope: gh auth refresh -s <scope>
```

### Repo
```bash
gh repo create <name> --public --clone            # New repo
gh repo create <name> --source=. --public --push   # Existing local → GitHub
gh repo list --limit 20                            # List repos
```

### Issues & PRs
```bash
gh issue create --title "T" --body "B" --label "bug"
gh pr create --title "T" --body "B"
gh pr merge <n> --squash
gh pr checks <n>                                   # CI status
```

### Releases & Actions
```bash
gh release create v1.0.0 --generate-notes
gh run list && gh run view <id>
gh workflow run <name>
```

### API (REST & GraphQL)
```bash
gh api repos/<owner>/<repo>                        # GET
gh api repos/<owner>/<repo>/issues -f title="T"    # POST
gh api graphql -f query='{ viewer { login } }'     # GraphQL
```

## Mode Comparison

| Mode | Best For | Auth | Requires |
|------|----------|------|----------|
| **gh CLI** | One-off tasks, scripts | `gh auth login` | gh installed |
| **gh api** | Any GitHub API endpoint | Same as gh CLI | gh installed |
| **curl + REST** | No gh available, CI/CD | `GITHUB_TOKEN` header | curl only |
| **Python SDK** | Python apps/automation | Token or env var | `pip install PyGithub` |
| **JS/TS SDK** | Node.js apps | Token or env var | `npm install @octokit/rest` |
| **MCP server** | AI agent integration | GitHub PAT | `github-mcp-server` |

## References

- **[references/cli.md](references/cli.md)** — Complete gh CLI commands: repos, issues, PRs, releases, Actions, auth troubleshooting
- **[references/api-sdk.md](references/api-sdk.md)** — REST API (gh api + curl), GraphQL, Python SDK (PyGithub), JS SDK (@octokit), GitHub MCP server setup

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `gh: command not found` | `brew install gh` — ensure `/opt/homebrew/bin` in PATH |
| Not logged in | `gh auth login` |
| Permission denied (403) | `gh auth refresh -s <missing-scope>` |
| Can't create org repo | Need `admin:org` scope |
| Token expired | `gh auth login` to re-authenticate |
| SSH vs HTTPS | `gh auth setup-git` to configure |
| Rate limit (API) | Use authenticated requests, check `X-RateLimit-Remaining` |
