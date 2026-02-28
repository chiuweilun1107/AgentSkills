# Operation Mode Analysis

When building a skill for an external service or tool, map all interaction modes to decide what to include.

## Mode Matrix

| Mode | Description | Example | Include when... |
|------|-------------|---------|-----------------|
| **CLI** | Command-line tool | `gh`, `docker`, `supabase` | Tool is installed on target machines |
| **Exec** | Execute inside container | `docker exec db psql` | Service runs in Docker |
| **REST API** | HTTP endpoints | `curl api.github.com` | Programmatic access needed |
| **SDK** | Language libraries | `supabase-py`, `@octokit` | Integrating into code |
| **MCP** | Model Context Protocol | Cloudflare MCP server | MCP server exists |
| **GUI** | Web dashboard | Supabase Studio, GitHub web | Reference only (not for skill) |

## Decision

Include modes the agent will ACTUALLY USE in practice. Don't document what Claude already knows (e.g., generic curl syntax). Focus on non-obvious commands, gotchas, and environment-specific details.

## Architecture Decision Based on Modes

| Condition | Architecture |
|-----------|-------------|
| Single mode, <300 lines total | SKILL.md only |
| Single mode, 300-500 lines | SKILL.md + 1-2 references |
| Multiple modes or domains | SKILL.md (decision flow) + `references/` per mode/domain |
| Heavy reference data (schemas, API docs) | SKILL.md (workflow) + `references/` per topic |

## When to Use references/

- Skill covers 2+ distinct domains or operation modes
- Total content would exceed 400 lines in SKILL.md alone
- Some content is only needed in specific scenarios (conditional loading)
- Heavy reference data (API docs, schemas, SQL templates)

## When NOT to Use references/

- All content fits in <300 lines
- Content is always needed (not conditional)
- Only one domain/mode

Name reference files by TOPIC, not by sequence:
- `references/operations.md` (NOT `references/part1.md`)
- `references/development.md` (NOT `references/advanced.md`)
