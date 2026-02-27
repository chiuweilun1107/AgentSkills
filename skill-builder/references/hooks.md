# Claude Code Hooks for Skill Enforcement

## Table of Contents
- [Overview](#overview)
- [Hook Types](#hook-types)
- [Configuration](#configuration)
- [Enforcement Levels](#enforcement-levels)
- [Testing Hooks](#testing-hooks)

## Overview

Claude Code supports hooks that execute shell commands at specific lifecycle events. These can enforce skill activation and code quality rules automatically.

**Two practical hook types for skills:**

| Hook | When | Purpose |
|------|------|---------|
| `UserPromptSubmit` | Before Claude sees prompt | Suggest relevant skills |
| `PreToolUse` | Before Edit/Write executes | Block until skill used |

## Hook Types

### UserPromptSubmit (Skill Suggestions)

Runs before Claude processes user input. Outputs to stdout are injected as context.

```json
// .claude/settings.json
{
  "hooks": {
    "UserPromptSubmit": [{
      "command": "npx tsx .claude/hooks/skill-activation-prompt.ts",
      "timeout": 5000
    }]
  }
}
```

**Flow**: User prompt → hook reads stdin JSON → matches keywords → outputs suggestion → Claude sees suggestion + prompt.

**Input (stdin):**
```json
{"session_id": "abc123", "prompt": "create a new skill for PDF processing"}
```

**Output (stdout):** Formatted skill suggestion text (injected before Claude's prompt).

### PreToolUse (Guardrail Blocks)

Runs before tool execution. Can block Edit/Write until a skill is consulted.

```json
{
  "hooks": {
    "PreToolUse": [{
      "command": "npx tsx .claude/hooks/skill-verification-guard.ts",
      "timeout": 3000
    }]
  }
}
```

**Exit codes (CRITICAL):**

| Exit Code | Effect |
|-----------|--------|
| 0 | Allow — tool proceeds |
| 2 | Block — stderr message shown to Claude, tool cancelled |
| Other | Ignored — tool proceeds |

## Configuration

### skill-rules.json

Central config defining all skill triggers and enforcement:

```json
{
  "skill-name": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "medium",
    "promptTriggers": {
      "keywords": ["keyword1", "keyword2"],
      "intentPatterns": ["(create|add).*?something"]
    },
    "filePaths": ["src/components/**/*.tsx"],
    "contentPatterns": ["import.*from.*@prisma"]
  }
}
```

**Skill types:**
- `guardrail` — Prevents critical errors (enforcement: `block`)
- `domain` — Provides expertise (enforcement: `suggest`)

## Enforcement Levels

| Level | Mechanism | When to Use |
|-------|-----------|-------------|
| **block** | PreToolUse exit code 2 | Critical: data integrity, security |
| **suggest** | UserPromptSubmit stdout | Common: best practices, how-to |
| **warn** | Low-priority suggestion | Rare: nice-to-have tips |

## Skip Conditions

Prevent repeated nagging:

| Method | Scope | How |
|--------|-------|-----|
| Session tracking | Per session | State file: `.claude/hooks/state/skills-used-{session_id}.json` |
| File markers | Permanent | Add `// @skip-validation` to file |
| Env vars | Temporary | `SKIP_SKILL_GUARDRAILS=true` |

## Testing Hooks

```bash
# Test UserPromptSubmit
echo '{"session_id":"test","prompt":"create a new skill"}' | \
  npx tsx .claude/hooks/skill-activation-prompt.ts

# Test PreToolUse
cat <<'EOF' | npx tsx .claude/hooks/skill-verification-guard.ts
{"session_id":"test","tool_name":"Edit","tool_input":{"file_path":"test.ts"}}
EOF
```

Verify:
- Correct skills suggested for matching keywords
- No false positives on unrelated prompts
- Block (exit 2) triggers correctly for guardrail skills
- Skip conditions prevent repeated blocks in same session
