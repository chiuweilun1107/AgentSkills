# Skill Detection Hook: Reliable Skill Triggering

## Problem

Claude has a documented tendency to "under-trigger" skills — even well-written descriptions in SKILL.md typically achieve only **20-30% activation rates**. This means users often write prompts that should clearly trigger your skill, but Claude doesn't recognize it and proceeds with generic responses instead.

## Solution: Hook-Based Detection

Rather than relying solely on description text, use Claude Code hooks to **explicitly detect** when a skill should be triggered and **suggest it to Claude** before implementation.

Two approaches exist:

1. **Detection Hook (Recommended)** — Keyword/pattern matching + suggestion (~80% activation)
2. **Forced Eval Hook** — Explicit skill evaluation step (~84% activation, higher token cost)

## Approach 1: Detection Hook (Recommended)

### How It Works

1. Define skill triggers in `~/.claude/skills/skill-rules.json` (keywords + regex patterns)
2. Install a `UserPromptSubmit` hook that runs before every prompt
3. Hook matches user prompt against triggers
4. If match found, hook suggests the skill to Claude
5. Claude decides whether to use it based on the suggestion

### Cost & Performance

| Metric | Value |
|--------|-------|
| Activation rate | ~80% |
| Token overhead | ~50 tokens per prompt (only when matched) |
| Setup time | 30 minutes |
| Maintenance | Edit `skill-rules.json` as needed |

### Implementation

#### Step 1: Create skill-rules.json

```json
{
  "skills": [
    {
      "name": "your-skill-name",
      "triggers": {
        "keywords": [
          "keyword1",
          "keyword2",
          "exact phrase to match"
        ],
        "patterns": [
          "regex.*pattern",
          "another.*regex"
        ]
      }
    }
  ]
}
```

**Save to:** `~/.claude/skills/skill-rules.json`

#### Step 2: Create detection hook script

**File:** `~/.claude/hooks/skill-detection.py`

```python
#!/usr/bin/env python3
"""
Claude Code Hook: Skill Detection
Detects relevant skills and suggests them to Claude.
"""

import json
import re
import sys
from pathlib import Path


def load_skill_rules() -> dict:
    """Load skill-rules.json from ~/.claude/skills/"""
    rules_path = Path.home() / ".claude" / "skills" / "skill-rules.json"
    try:
        return json.loads(rules_path.read_text())
    except Exception as e:
        print(f"Error loading skill rules: {e}", file=sys.stderr)
        sys.exit(1)


def check_match(prompt: str, skill_triggers: dict) -> bool:
    """Check if prompt matches skill triggers."""
    prompt_lower = prompt.lower()

    # Check keywords
    keywords = skill_triggers.get("keywords", [])
    for kw in keywords:
        if kw.lower() in prompt_lower:
            return True

    # Check patterns (regex)
    patterns = skill_triggers.get("patterns", [])
    for pattern in patterns:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return True

    return False


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    prompt = input_data.get("prompt", "").strip()
    if not prompt:
        sys.exit(0)

    rules = load_skill_rules()
    matched_skills = []

    for skill in rules.get("skills", []):
        skill_name = skill.get("name", "")
        triggers = skill.get("triggers", {})
        if check_match(prompt, triggers):
            matched_skills.append(skill_name)

    if matched_skills:
        suggestion = (
            f"\n[Skill Detection] Based on your prompt, these skills might be relevant:\n"
            f"- {', '.join(matched_skills)}\n"
        )
        print(suggestion, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

#### Step 3: Register hook in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "command": "python3 ~/.claude/hooks/skill-detection.py",
        "timeout": 1000
      }
    ]
  }
}
```

#### Step 4: Test

```bash
echo '{"prompt":"your test prompt that should trigger the skill"}' | python3 ~/.claude/hooks/skill-detection.py
```

Should output:
```
[Skill Detection] Based on your prompt, these skills might be relevant:
- your-skill-name
```

### Writing Good Triggers

**Keywords** (exact string match, case-insensitive):
- Skill name itself: `"docker"`, `"github"`
- Tool names: `"postgresql"`, `"kubernetes"`
- Domain terms: `"machine learning"`, `"rest api"`
- Common phrases: `"write a script"`, `"refactor code"`

**Patterns** (regex, case-insensitive):
- Phrasings: `"build.*image"`, `"run.*container"`
- Variations: `"(docker|pod|container).*logs"`
- Context: `"need.*database.*help"`

**Avoid:**
- Too many keywords (causes false positives)
- Generic terms like `"help"`, `"do something"`
- Overlapping keywords between skills (causes conflicts)

## Approach 2: Forced Eval Hook

For critical skills requiring absolute reliability, use a `UserPromptSubmit` hook that forces Claude to evaluate each skill before responding.

This approach uses aggressive language ("MANDATORY SKILL EVALUATION") to prevent Claude from skipping the evaluation step. See [How to Make Claude Code Skills Activate Reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably) for implementation.

### Tradeoffs

| Metric | Detection Hook | Forced Eval |
|--------|----------------|------------|
| Activation | ~80% | ~84% |
| Token cost | ~50/prompt | ~200-500/prompt |
| Setup complexity | 30 min | 1 hour |
| User experience | Seamless suggestions | Verbose evaluation step |

**Recommendation:** Start with Detection Hook. Switch to Forced Eval only if detection misses critical cases.

## Maintenance

As you use the skill, track which prompts should/shouldn't trigger:

```bash
# Add new triggers if you notice false negatives
# (user asks something that SHOULD trigger, but hook didn't catch it)

# Remove triggers if you notice false positives
# (hook suggests skill but user doesn't need it)

# Edit ~/.claude/skills/skill-rules.json and reload (no restart needed)
```

## Integration with Description Optimization

Description optimization (run_loop.py) works best as a **secondary tool** after hook infrastructure is in place:

1. **First:** Implement Detection Hook
2. **Second:** Use description optimization to refine the description for cases where the hook detects relevance
3. **Result:** Skill triggers reliably (80%+) AND description is optimized for the context Claude sees

This avoids wasting time optimizing descriptions for triggering that won't happen anyway.

## See Also

- [Scott Spence: How to Make Claude Code Skills Activate Reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)
- [Hooks Reference - Claude Code Docs](https://code.claude.com/docs/en/hooks)
