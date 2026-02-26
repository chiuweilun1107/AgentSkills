---
name: skill-forge
description: 'Create, validate, and deploy AI agent skills with full lifecycle management. Use when user asks to create a skill, build a skill, make a new skill, or mentions "skill-forge". Handles SKILL.md generation, validation, testing, and deployment to Claude Code + OpenClaw + AgentSkills GitHub repo.'
---

# Skill Forge

Create production-quality skills following Anthropic best practices with automated validation and dual-platform deployment.

## Process Overview

```
1. GATHER   → Understand what the skill does and when to trigger
2. SCAFFOLD → Create SKILL.md + scripts/references/assets
3. VALIDATE → Run validate_skill.py (automated checks)
4. TEST     → 3+ real usage scenarios
5. DEPLOY   → Claude Code + OpenClaw + AgentSkills repo
```

Follow ALL steps in order. Never skip validation or testing.

## Step 1: Gather Requirements

Ask the user (max 3 questions at once):

1. **What does the skill do?** Concrete examples of usage.
2. **What triggers it?** Keywords, phrases, file types, situations.
3. **What resources does it need?** Scripts, APIs, references, templates.

If user gives a vague request, ask for 2-3 concrete examples of how they'd use it.

## Step 2: Scaffold the Skill

### Directory Structure

```
skill-name/
├── SKILL.md              # Required - frontmatter + instructions
├── scripts/              # Optional - executable Python/Bash
├── references/           # Optional - docs loaded as needed
├── assets/               # Optional - templates, icons, fonts
└── .gitignore            # Exclude .venv/, data/, __pycache__/
```

Do NOT create: README.md, CHANGELOG.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md.

### SKILL.md Frontmatter Rules

```yaml
---
name: lowercase-with-hyphens-only
description: 'Single-quoted string. Start with verb or "Use when...". Max 1024 chars.'
---
```

**CRITICAL rules:**
- `name`: Lowercase letters, numbers, hyphens only. Max 64 chars. No "anthropic" or "claude".
- `description`: Use **single-quoted string** (NOT `>-` or `|` — indexer breaks on YAML multiline).
- `description`: Describe WHEN to use, not HOW it works. Never summarize workflow.
- `description`: Third person. Include 5+ trigger keywords.
- No other frontmatter fields (no license, metadata, etc.)

**Description formula:**
```
[What it does in 1 sentence]. Use when [trigger conditions]. [File types/keywords].
```

**Examples:**

```yaml
# GOOD
description: 'Create and manage Google NotebookLM notebooks via API. Use when user mentions NotebookLM, wants to query notebooks, create notebooks, or add sources.'

# BAD - summarizes workflow
description: 'Opens browser, logs into Google, creates notebook, adds source, then queries.'

# BAD - uses YAML multiline (indexer breaks)
description: >-
  Create notebooks and query them.
```

### SKILL.md Body Rules

- Under 500 lines total
- Imperative/infinitive form ("Run the script" not "You should run")
- Concrete examples over verbose explanations
- One excellent example beats many mediocre ones
- No information Claude already knows
- Reference files for content >100 lines (with table of contents)
- All references one level deep from SKILL.md (no A → B → C chains)

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

## Step 3: Validate

Run the validation script BEFORE deployment:

```bash
python scripts/validate_skill.py /path/to/skill-name/
```

The script checks:
- Frontmatter format (name, description, YAML syntax)
- Name conventions (lowercase, hyphens, length)
- Description quality (length, no XML tags, no multiline)
- Body length (<500 lines)
- File structure (no forbidden files)
- Script existence and syntax
- .gitignore presence

Fix ALL errors before proceeding. Warnings are advisory.

## Step 4: Test

### Minimum 3 scenarios:

1. **Happy path** — Does the skill work for the primary use case?
2. **Trigger test** — Does it activate on expected keywords?
3. **Edge case** — Does it handle unusual input gracefully?

### Testing method:

For each scenario, verify:
- [ ] Skill triggers correctly from description keywords
- [ ] Instructions are followed as written
- [ ] Scripts execute without errors
- [ ] Output matches expectations

## Step 5: Deploy

### 5a. Deploy to Claude Code (local)
```bash
cp -r skill-name/ ~/.claude/skills/skill-name/
```

### 5b. Deploy to OpenClaw (Mac Mini)
```bash
# SSH to Mac Mini and copy
scp -r skill-name/ macmini:~/.openclaw/skills/skill-name/
```

If the skill has Python dependencies:
```bash
# Test venv setup on Mac Mini
ssh macmini "cd ~/.openclaw/skills/skill-name && /opt/homebrew/bin/python3 scripts/run.py --help"
```

### 5c. Push to AgentSkills repo
```bash
# From the AgentSkills repo directory
cp -r /path/to/skill-name/ ./skill-name/
git add skill-name/
git commit -m "feat: add skill-name skill - [brief description]"
git push
```

### 5d. Update AgentSkills README
Add the new skill to the Available Skills table in README.md.

## Validation Script Reference

```bash
# Full validation
python scripts/validate_skill.py /path/to/skill/

# Output: PASS/FAIL with detailed report
# Exit code: 0 = all pass, 1 = has errors
```

## Checklist (verify before marking complete)

- [ ] Frontmatter: name + description only, single-quoted, <1024 chars
- [ ] Description: third person, "Use when..." language, 5+ keywords, no workflow summary
- [ ] Body: <500 lines, imperative form, concrete examples
- [ ] No forbidden files (README, CHANGELOG, etc.)
- [ ] .gitignore excludes .venv/, data/, __pycache__/
- [ ] validate_skill.py passes with 0 errors
- [ ] 3+ test scenarios pass
- [ ] Deployed to Claude Code
- [ ] Deployed to OpenClaw
- [ ] Pushed to AgentSkills repo
- [ ] AgentSkills README updated
