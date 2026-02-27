# AgentSkills

Shared AI agent skills compatible with both **Claude Code** and **OpenClaw**.

## Structure

Each skill follows the standard Claude Code skill format:

```
skill-name/
├── SKILL.md          # Skill definition (YAML frontmatter + instructions)
├── scripts/          # Automation scripts
├── requirements.txt  # Python dependencies
└── .gitignore
```

## Installation

### Claude Code
```bash
cp -r <skill-name> ~/.claude/skills/<skill-name>
```

### OpenClaw
```bash
cp -r <skill-name> ~/.openclaw/skills/<skill-name>
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [github](./github/) | GitHub operations via CLI, REST API, SDK, MCP — repos, issues, PRs, releases, Actions |
| [notebooklm](./notebooklm/) | Query, create, and manage Google NotebookLM notebooks via notebooklm-py API |
| [skill-builder](./skill-builder/) | Create, validate, and deploy AI agent skills following Anthropic best practices |
| [supabase](./supabase/) | Supabase development + self-hosted ops + pgvector/RAG (with references/) |

## License

MIT
