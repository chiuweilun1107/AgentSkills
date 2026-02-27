# GitHub REST API, SDK & MCP Reference

## Table of Contents
- [REST API via gh api](#rest-api-via-gh-api)
- [REST API via curl](#rest-api-via-curl)
- [GraphQL API](#graphql-api)
- [Python SDK (PyGithub)](#python-sdk-pygithub)
- [JavaScript SDK (@octokit/rest)](#javascript-sdk-octokitrest)
- [GitHub MCP Server](#github-mcp-server)
- [Mode Selection Guide](#mode-selection-guide)

## REST API via gh api

`gh api` wraps GitHub REST API with automatic authentication. No token management needed.

```bash
# GET — read data
gh api repos/<owner>/<repo>
gh api repos/<owner>/<repo>/issues
gh api repos/<owner>/<repo>/pulls?state=open

# POST — create resources
gh api repos/<owner>/<repo>/issues --method POST \
  -f title="Bug report" -f body="Description"

# PATCH — update resources
gh api repos/<owner>/<repo>/issues/<number> --method PATCH \
  -f state="closed"

# DELETE
gh api repos/<owner>/<repo>/issues/<number>/labels/<label> --method DELETE

# Pagination
gh api repos/<owner>/<repo>/issues --paginate

# JSON output with jq
gh api repos/<owner>/<repo>/contributors --jq '.[].login'

# Upload files (releases)
gh api repos/<owner>/<repo>/releases/<id>/assets \
  --method POST \
  -H "Content-Type: application/zip" \
  --input ./dist/app.zip
```

### Common API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `repos/{owner}/{repo}` | GET | Repo info |
| `repos/{owner}/{repo}/issues` | GET/POST | Issues |
| `repos/{owner}/{repo}/pulls` | GET/POST | PRs |
| `repos/{owner}/{repo}/pulls/{n}/comments` | GET/POST | PR comments |
| `repos/{owner}/{repo}/branches/{branch}/protection` | GET/PUT | Branch protection |
| `repos/{owner}/{repo}/actions/runs` | GET | Workflow runs |
| `repos/{owner}/{repo}/collaborators/{user}` | PUT/DELETE | Collaborators |
| `repos/{owner}/{repo}/hooks` | GET/POST | Webhooks |
| `user/repos` | GET | Current user's repos |
| `orgs/{org}/repos` | GET/POST | Org repos |

## REST API via curl

Use when `gh` is not available (CI/CD, Docker containers, remote servers).

```bash
# Set token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# GET
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/<owner>/<repo>

# POST
curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/<owner>/<repo>/issues \
  -d '{"title":"Bug","body":"Description"}'

# Check rate limit
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/rate_limit | jq '.rate'
```

### Rate Limits

| Type | Limit | Reset |
|------|-------|-------|
| Authenticated | 5,000/hour | Check `X-RateLimit-Reset` header |
| Unauthenticated | 60/hour | Avoid for any real usage |
| GraphQL | 5,000 points/hour | Variable cost per query |

## GraphQL API

For complex queries that would need multiple REST calls.

```bash
# Via gh api
gh api graphql -f query='
{
  repository(owner: "owner", name: "repo") {
    issues(first: 10, states: OPEN) {
      nodes {
        title
        number
        labels(first: 5) { nodes { name } }
      }
    }
  }
}'

# Via curl
curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d '{"query":"{ viewer { login repositories(first:5) { nodes { name } } } }"}'
```

**When to use GraphQL over REST:**
- Need nested/related data in one call (e.g., issues + labels + assignees)
- Want specific fields only (reduce response size)
- Complex filtering not available in REST

## Python SDK (PyGithub)

```bash
pip install PyGithub
```

```python
from github import Github

# Auth
g = Github("ghp_your_token")
# Or from environment:
import os
g = Github(os.environ["GITHUB_TOKEN"])

# Repos
repo = g.get_repo("owner/repo")
repos = g.get_user().get_repos()

# Issues
issue = repo.create_issue(title="Bug", body="Description", labels=["bug"])
issues = repo.get_issues(state="open")
for i in issues:
    print(f"#{i.number}: {i.title}")

# Pull Requests
pulls = repo.get_pulls(state="open")
pr = repo.get_pull(123)
pr.create_review(body="LGTM", event="APPROVE")
pr.merge(merge_method="squash")

# Releases
release = repo.create_git_release(
    tag="v1.0.0", name="v1.0.0",
    message="Release notes", draft=False
)
release.upload_asset("/path/to/file.zip")

# Search
results = g.search_repositories(query="language:python stars:>1000")
results = g.search_issues(query="repo:owner/repo is:open label:bug")

# Rate limit check
rate = g.get_rate_limit()
print(f"Remaining: {rate.core.remaining}/{rate.core.limit}")
```

## JavaScript SDK (@octokit/rest)

```bash
npm install @octokit/rest
```

```typescript
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

// Repos
const { data: repo } = await octokit.repos.get({ owner: "owner", repo: "repo" });

// Issues
const { data: issue } = await octokit.issues.create({
  owner: "owner", repo: "repo",
  title: "Bug", body: "Description", labels: ["bug"]
});

const { data: issues } = await octokit.issues.listForRepo({
  owner: "owner", repo: "repo", state: "open"
});

// Pull Requests
const { data: pr } = await octokit.pulls.create({
  owner: "owner", repo: "repo",
  title: "Feature", head: "feature-branch", base: "main"
});

await octokit.pulls.merge({
  owner: "owner", repo: "repo",
  pull_number: 123, merge_method: "squash"
});

// Releases
const { data: release } = await octokit.repos.createRelease({
  owner: "owner", repo: "repo",
  tag_name: "v1.0.0", name: "v1.0.0",
  body: "Release notes", generate_release_notes: true
});

// Pagination
const allIssues = await octokit.paginate(octokit.issues.listForRepo, {
  owner: "owner", repo: "repo", state: "all"
});
```

## GitHub MCP Server

GitHub's official MCP server allows AI agents to interact with GitHub directly.

### Setup

```bash
# Install via Claude Code
claude mcp add github-mcp-server \
  --env GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx \
  -- npx -y @anthropic-ai/github-mcp-server

# Or via Docker
docker run -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx \
  ghcr.io/github/github-mcp-server

# Verify
claude mcp list
claude mcp get github-mcp-server
```

### Capabilities

| Category | Operations |
|----------|------------|
| Repos | List, get, create, fork, search |
| Issues | List, get, create, update, comment, search |
| PRs | List, get, create, merge, review, diff |
| Files | Get content, create/update, search code |
| Branches | List, create, delete, get protection |
| Actions | List workflows, trigger, view runs |

### Token Scopes Needed

| Scope | For |
|-------|-----|
| `repo` | Full repo access |
| `read:org` | Org membership |
| `workflow` | GitHub Actions |

### When to Use MCP vs CLI

| Scenario | Use |
|----------|-----|
| Claude Code direct operations | MCP (if configured) or gh CLI |
| Shell scripts, CI/CD | gh CLI |
| Python/JS application code | SDK |
| No tools installed, only curl | REST API |

## Mode Selection Guide

```
Need to do something on GitHub?
    │
    ├─ One-off task from terminal?
    │   → gh CLI (fastest, interactive)
    │
    ├─ Automated shell script?
    │   → gh CLI or gh api (auth handled)
    │
    ├─ CI/CD pipeline (no gh)?
    │   → curl + GITHUB_TOKEN (minimal deps)
    │
    ├─ Python project integration?
    │   → PyGithub (pip install PyGithub)
    │
    ├─ JS/TS project integration?
    │   → @octokit/rest (npm install @octokit/rest)
    │
    ├─ AI agent needs GitHub access?
    │   → MCP server (github-mcp-server)
    │
    └─ Complex nested data query?
        → GraphQL (via gh api graphql or SDK)
```
