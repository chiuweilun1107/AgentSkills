---
name: skill-builder
description: 'Create, validate, and deploy AI agent skills following Anthropic best practices. Use when user asks to create a skill, build a skill, make a new skill, write a skill, or says "幫我做一個skill". Automated SKILL.md validation, trigger optimization, dual-platform deployment to Claude Code and OpenClaw.'
---

# Skill Builder

Create production-quality skills with automated validation and dual-platform deployment. Based on Anthropic official best practices, community research, and real-world trigger optimization data.

## Process Overview

```
0. RESEARCH  → Web search + local audit + operation mode analysis
1. GATHER    → Requirements, triggers, resources needed
2. SCAFFOLD  → SKILL.md + scripts/references/assets
3. VALIDATE  → Run validate_skill.py (automated checks)
4. TEST      → 3+ real usage scenarios
5. DEPLOY    → Claude Code + OpenClaw + AgentSkills repo
```

Follow ALL steps. Never skip research, validation, or testing.

## Step 0: Research (MANDATORY)

**Before writing a single line, search the web.** Never assume no prior art exists.

### 0a. Web search (REQUIRED — do this FIRST)

Search for existing skills, official docs, and community best practices:

```
Search queries (run at least 2-3):
- "claude code skill <service-name>"
- "<service-name> AI agent skill"
- "<service-name> CLI reference"
- "<service-name> official documentation"
- "awesome <service-name>" (community curated lists)
```

What to look for:
- Official agent/skill repos (e.g., github.com/supabase/agent-skills)
- Community skills that already solve the problem
- Official CLI/API/SDK documentation to understand full capabilities
- Best practices and common patterns others use

### 0b. Local audit (supplement)

```bash
# Check Claude Code
ls ~/.claude/skills/ | grep <keyword>

# Check OpenClaw
ssh macmini "ls ~/.openclaw/skills/ | grep <keyword>"

# Check AgentSkills repo
ls ~/path/to/AgentSkills/ | grep <keyword>
```

### 0c. Operation mode analysis (for service/tool skills)

When building a skill for an external service or tool, map ALL interaction modes:

| Mode | Description | Example | Include when... |
|------|-------------|---------|-----------------|
| **CLI** | Command-line tool | `gh`, `docker`, `supabase` | Tool is installed on target machines |
| **Exec** | Execute inside container | `docker exec db psql` | Service runs in Docker |
| **REST API** | HTTP endpoints | `curl api.github.com` | Programmatic access needed |
| **SDK** | Language libraries | `supabase-py`, `@octokit` | Integrating into code |
| **MCP** | Model Context Protocol | Cloudflare MCP server | MCP server exists |
| **GUI** | Web dashboard | Supabase Studio, GitHub web | Reference only (not for skill) |

**Decision**: Include modes the agent will ACTUALLY USE in practice. Don't document what Claude already knows (e.g., generic curl syntax). Focus on non-obvious commands, gotchas, and environment-specific details.

### 0d. Decide architecture

| Condition | Architecture |
|-----------|-------------|
| Single mode, <300 lines total | SKILL.md only |
| Single mode, 300-500 lines | SKILL.md + 1-2 references |
| Multiple modes or domains | SKILL.md (decision flow) + `references/` per mode/domain |
| Heavy reference data (schemas, API docs) | SKILL.md (workflow) + `references/` per topic |

Conclude Step 0 when you have: prior art summary, operation modes list, and architecture decision.

## Step 1: Gather Requirements

Ask the user (max 3 questions at once):

1. **What does the skill do?** Get 2-3 concrete usage examples.
2. **What triggers it?** Keywords, phrases, file types, situations.
3. **What resources?** Scripts, APIs, references, templates.
4. **What operation modes?** (for service/tool skills) Which of CLI/API/SDK/Exec/MCP does the agent need?

Conclude when you have clear: purpose, triggers, resource list, and operation modes.

## Step 2: Scaffold

### Directory Structure

```
skill-name/
├── SKILL.md              # Required - frontmatter + instructions
├── scripts/              # Optional - executable code (token efficient, deterministic)
├── references/           # Optional - docs loaded into context as needed
├── assets/               # Optional - output files (templates, icons, fonts)
└── .gitignore            # Exclude .venv/, data/, __pycache__/
```

**Do NOT create:** README.md, CHANGELOG.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, or any auxiliary docs.

### Frontmatter (CRITICAL)

```yaml
---
name: lowercase-with-hyphens-only
description: 'Single-quoted string. Max 1024 chars.'
---
```

**Rules:**
- `name`: Lowercase letters/numbers/hyphens. Max 64 chars. No "anthropic" or "claude".
- `description`: **Single-quoted string only** — YAML multiline (`>-`, `|`) breaks the skill indexer.
- Only `name` and `description` in frontmatter. No other fields.

### Description Optimization (Trigger Rate Data)

Research-measured activation rates:

| Optimization Level | Trigger Rate |
|---|---|
| No optimization | ~20% |
| Simple description | ~20% |
| Optimized with "Use when..." | ~50% |
| "Use when..." + 5+ keywords | **72-90%** |

**Formula:**
```
[What it does in 1 sentence]. Use when [specific trigger conditions]. [Keywords/file types].
```

**CRITICAL anti-pattern — Description Shortcutting:**

When a description summarizes the skill's workflow, Claude follows the description instead of reading the full body. A description saying "dispatches subagent per task with code review between tasks" caused Claude to do ONE review, even though the body specified TWO.

Fix: Description = WHEN to use. Body = HOW to use.

**Examples:**

```yaml
# GOOD — triggers only, no workflow
description: 'Create and manage Google NotebookLM notebooks via API. Use when user mentions NotebookLM, wants to query notebooks, create notebooks, or add sources.'

# GOOD — specific conditions
description: 'Use when implementing any feature or bugfix, before writing implementation code'

# BAD — summarizes workflow (Claude will shortcut)
description: 'Opens browser, logs into Google, creates notebook, adds source, then queries.'

# BAD — first person
description: 'I can help you create and query notebooks'

# BAD — YAML multiline (indexer breaks)
description: >-
  Create notebooks and query them.
```

**Description quality checklist:**
- [ ] Third person (not "I can" or "you should")
- [ ] Starts with verb or includes "Use when..."
- [ ] 5+ specific trigger keywords
- [ ] No workflow summary
- [ ] Single-quoted YAML string
- [ ] Includes file types if applicable (.pdf, .xlsx, etc.)
- [ ] <1024 chars total

### Body Rules

**Token budget:**

| Level | What | Budget |
|---|---|---|
| Metadata (name+description) | Always in context | ~100 tokens |
| SKILL.md body | Loaded when triggered | <5000 tokens (~500 lines) |
| Bundled resources | Loaded as needed | Unlimited (scripts execute without context) |

**Writing rules:**
- Under 500 lines
- Imperative form ("Run the script" not "You should run")
- Concrete examples over verbose explanations
- One excellent example beats many mediocre ones
- Only add what Claude doesn't already know
- Challenge each paragraph: "Does this justify its token cost?"

**Progressive disclosure patterns:**

For multi-domain or large skills, split content:

```
# Pattern 1: High-level guide + references
SKILL.md          → Core workflow + navigation
references/aws.md → AWS-specific details (loaded only when needed)
references/gcp.md → GCP-specific details

# Pattern 2: Conditional details
SKILL.md       → Basic usage inline
REDLINING.md   → Advanced tracked changes (loaded only for that feature)
```

**When to use references/:**
- Skill covers 2+ distinct domains or operation modes
- Total content would exceed 400 lines in SKILL.md alone
- Some content is only needed in specific scenarios (conditional loading)
- Heavy reference data (API docs, schemas, SQL templates)

**When NOT to use references/:**
- All content fits in <300 lines
- Content is always needed (not conditional)
- Only one domain/mode

**Naming convention:** Name by TOPIC, not by sequence:
- `references/operations.md` (NOT `references/part1.md`)
- `references/development.md` (NOT `references/advanced.md`)

**Rules for references:**
- One level deep only (SKILL.md → file, never SKILL.md → A → B)
- Files >100 lines must have table of contents at top
- Files >10k words: include grep search patterns in SKILL.md

### Body Structure Template

```markdown
# Skill Name

Brief description (1-2 sentences).

## When to Use
- Bullet list of triggers and situations
- When NOT to use

## Core Workflow
Step-by-step with code examples.

## Script Reference
Commands and arguments for each script.

## Common Mistakes
| Problem | Solution |
|---------|----------|
```

### Content Anti-Patterns

| Anti-Pattern | Why Bad | Fix |
|---|---|---|
| Explaining what Claude knows | Token waste | Only add non-obvious info |
| Magic numbers without context | Unreliable | Document/justify constants |
| Multi-language examples | Diluted quality | One excellent example |
| Narrative storytelling | Not reusable | Pattern-based writing |
| Code inside flowcharts | Can't copy-paste | Separate code blocks |
| Generic labels (step1, helper2) | No semantic meaning | Descriptive names |
| Offering many alternatives without default | Decision paralysis | Recommend one, list others |

### Freedom Levels

Match specificity to task fragility:

| Freedom | When | Example |
|---|---|---|
| **High** (text instructions) | Multiple valid approaches, context-dependent | "Choose appropriate data structure" |
| **Medium** (pseudocode/params) | Preferred pattern exists, some variation OK | "Use this template, adjust X and Y" |
| **Low** (specific scripts) | Fragile operations, consistency critical | "Run exactly: `python scripts/rotate.py`" |

## Step 3: Validate

Run BEFORE deployment:

```bash
python scripts/validate_skill.py /path/to/skill-name/
```

**Checks performed:**
- Frontmatter format (name, description, YAML syntax)
- Name conventions (lowercase, hyphens, length, forbidden words)
- Description quality (length, no XML, no multiline, third person, "Use when...")
- Body length (<500 lines)
- File structure (no forbidden files like README.md)
- Script syntax (Python AST parse)
- .gitignore presence and content
- Reference depth (no nested chains)

Fix ALL errors. Warnings are advisory.

## Step 4: Test

### Minimum 3 scenarios:

1. **Happy path** — Primary use case works correctly
2. **Trigger test** — Activates on expected keywords, does NOT activate on unrelated prompts
3. **Edge case** — Handles unusual input gracefully

### For each scenario verify:
- [ ] Skill triggers from description keywords
- [ ] Instructions followed as written (not shortcut from description)
- [ ] Scripts execute without errors
- [ ] Output matches expectations

### Testing by skill type:

| Type | Test Focus |
|---|---|
| **Technique** (how-to) | Application to new scenarios, edge cases |
| **Pattern** (mental model) | Recognition, correct application, counter-examples |
| **Reference** (API docs) | Information retrieval, correct usage |
| **Discipline** (rules) | Compliance under pressure, rationalization resistance |

For discipline-enforcing skills (TDD, guardrails), add pressure testing and rationalization resistance checks. See [references/testing.md](references/testing.md) for detailed methodology.

## Step 5: Deploy

### 5a. Deploy to Claude Code (local)
```bash
cp -r skill-name/ ~/.claude/skills/skill-name/
```

### 5b. Deploy to OpenClaw (Mac Mini)
```bash
# Create dir first, then copy files
ssh macmini "mkdir -p ~/.openclaw/skills/skill-name/scripts"
scp -r skill-name/* macmini:~/.openclaw/skills/skill-name/
```

If Python dependencies exist:
```bash
ssh macmini "cd ~/.openclaw/skills/skill-name && /opt/homebrew/bin/python3 scripts/run.py --help"
```

### 5c. Push to AgentSkills repo
```bash
cp -r /path/to/skill-name/ ./skill-name/
git add skill-name/
git commit -m "feat: add skill-name - [brief description]"
git push
```

### 5d. Update AgentSkills README
Add new skill to the Available Skills table.

## References

For detailed guidance on specific topics:

- **[references/hooks.md](references/hooks.md)** — Claude Code hooks for skill enforcement: UserPromptSubmit (suggest skills), PreToolUse (block until skill used), skill-rules.json, enforcement levels, testing commands
- **[references/testing.md](references/testing.md)** — Advanced testing methodology: pressure testing discipline skills, rationalization resistance, RED-GREEN-REFACTOR cycle for skills, testing by skill type

## Final Checklist

- [ ] Web search completed (2-3 queries, prior art reviewed)
- [ ] Operation modes analyzed (CLI/API/SDK/Exec/MCP)
- [ ] Architecture decided (SKILL.md only vs references/)
- [ ] Frontmatter: name + description only, single-quoted, <1024 chars
- [ ] Description: third person, "Use when...", 5+ keywords, no workflow summary
- [ ] Body: <500 lines, imperative form, concrete examples, no token waste
- [ ] No forbidden files (README, CHANGELOG, etc.)
- [ ] .gitignore excludes .venv/, data/, __pycache__/
- [ ] validate_skill.py passes with 0 errors
- [ ] 3+ test scenarios pass (happy path, trigger, edge case)
- [ ] Deployed to Claude Code
- [ ] Deployed to OpenClaw
- [ ] Pushed to AgentSkills repo
- [ ] AgentSkills README updated
