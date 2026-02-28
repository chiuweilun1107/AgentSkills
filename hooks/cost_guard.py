#!/usr/bin/env python3
"""
Claude Code Hook: Cost Guard
=============================
PreToolUse hook for Bash — blocks or warns on expensive operations.

Prevents:
1. Using Opus model in batch/eval scripts (use Haiku instead)
2. Multiple parallel claude -p invocations
3. Anthropic API batch calls without ANTHROPIC_API_KEY check
4. run_loop.py / run_eval.py with expensive models

Exit codes:
  0 = allow
  2 = block (stderr shown to Claude as error)

Settings.json config:
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/cost_guard.py"
          }
        ]
      }
    ]
  }
}
"""

import json
import re
import sys


def check_command(command: str) -> list[dict]:
    """Check command for expensive patterns. Returns list of {level, message}."""
    issues = []

    # --- BLOCK: Opus in batch/eval operations ---
    # run_loop.py or run_eval.py with opus model
    if re.search(r'run_(loop|eval)', command) and re.search(r'opus', command, re.IGNORECASE):
        issues.append({
            "level": "block",
            "message": (
                "BLOCKED: run_loop/run_eval with Opus model detected. "
                "Opus is ~50x more expensive than Haiku for eval. "
                "Use --model claude-haiku-4-5-20251001 instead."
            ),
        })

    # --- BLOCK: claude -p with opus in background ---
    if re.search(r'claude\s+-p', command) and re.search(r'opus', command, re.IGNORECASE):
        if re.search(r'run_in_background|&\s*$|\bfor\b|\bwhile\b|\bxargs\b|\bparallel\b', command):
            issues.append({
                "level": "block",
                "message": (
                    "BLOCKED: Batch/background claude -p with Opus detected. "
                    "Use Haiku or Sonnet for batch operations."
                ),
            })

    # --- WARN: Any run_loop.py execution ---
    if re.search(r'run_loop', command) and not any(i["level"] == "block" for i in issues):
        issues.append({
            "level": "warn",
            "message": (
                "WARNING: run_loop.py detected. This spawns many claude -p subprocesses. "
                "Estimated cost: queries * runs_per_query * model_cost_per_call. "
                "Confirm: (1) model is Haiku, (2) run 1 skill first to validate, "
                "(3) ANTHROPIC_API_KEY is set for improve_description step."
            ),
        })

    # --- WARN: Multiple claude -p in a single command ---
    claude_p_count = len(re.findall(r'claude\s+-p', command))
    if claude_p_count > 1:
        issues.append({
            "level": "warn",
            "message": (
                f"WARNING: {claude_p_count} claude -p calls in one command. "
                "Each spawns a full Claude session. Confirm this is intentional."
            ),
        })

    # --- WARN: Batch API calls without key check ---
    if re.search(r'anthropic\.Anthropic|client\.messages\.create', command):
        issues.append({
            "level": "warn",
            "message": (
                "WARNING: Direct Anthropic API call detected in command. "
                "Ensure ANTHROPIC_API_KEY is set."
            ),
        })

    return issues


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    issues = check_command(command)

    if not issues:
        sys.exit(0)

    # If any issue is a block, block the command
    has_block = any(i["level"] == "block" for i in issues)

    for issue in issues:
        print(f"{issue['message']}", file=sys.stderr)

    if has_block:
        sys.exit(2)  # Block the command
    else:
        # Warnings: exit 0 to allow but stderr is shown
        sys.exit(0)


if __name__ == "__main__":
    main()
