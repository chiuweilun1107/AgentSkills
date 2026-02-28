#!/bin/bash
# Hook: UserPromptSubmit — remind Claude to follow skill-creator process
# Reads user prompt from stdin JSON, checks for skill-related keywords

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt','').lower())" 2>/dev/null)

# Check for skill creation/modification keywords
if echo "$PROMPT" | grep -qiE '(create.*skill|build.*skill|make.*skill|write.*skill|new skill|modify.*skill|improve.*skill|update.*skill|skill.*creator|skill.*builder|skill.*validate|validate.*skill)'; then
  cat <<'EOF'
[Skill Creator Reminder] You are working on a skill. Follow the skill-creator process:
1. Use /skill-creator (the official skill from ~/.claude/skills/skill-creator/)
2. After writing the skill, run validation: python -m scripts.quick_validate <skill-path>
3. Create eval test cases before claiming the skill is done
4. Run description optimization via run_loop.py for better triggering
Do NOT skip validation or eval steps.
EOF
fi
