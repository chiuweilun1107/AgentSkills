#!/usr/bin/env python3
"""
Claude Code Hook: Skill Detection
==================================
UserPromptSubmit hook — detects relevant skills and suggests them.

Reads skill-rules.json, checks user prompt against keyword/pattern triggers,
and suggests relevant skills to Claude.

Exit codes:
  0 = success (suggestion injected or no match)
  1 = error reading config

Settings.json config:
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "command": "python3 ~/.claude/hooks/skill-detection.py"
      }
    ]
  }
}
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
    """Check if prompt matches skill triggers (keywords or patterns)."""
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
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
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
            f"Use `/skill {skill_name}` to load a specific skill if you need it.\n"
        )
        print(suggestion, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
