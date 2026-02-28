# Skill Deployment

After a skill passes evaluation, deploy to one or more targets.

## Deploy to Claude Code (local)

```bash
cp -r skill-name/ ~/.claude/skills/skill-name/
```

Verify: restart Claude Code session and test with a trigger phrase.

## Deploy to OpenClaw (Mac Mini)

```bash
# Create dir first, then copy files
ssh macmini "mkdir -p ~/.openclaw/skills/skill-name/scripts"
scp -r skill-name/* macmini:~/.openclaw/skills/skill-name/

# If Python dependencies exist
ssh macmini "cd ~/.openclaw/skills/skill-name && /opt/homebrew/bin/python3 scripts/run.py --help"
```

After deploy, clear any active OpenClaw sessions so the new skill loads:
```bash
ssh macmini "cat ~/.openclaw/agents/main/sessions/sessions.json"
# Remove the relevant session key
```

## Push to AgentSkills Repo

```bash
cp -r /path/to/skill-name/ ./skill-name/
git add skill-name/
git commit -m "feat: add skill-name - [brief description]"
git push
```

Update the repo's README Available Skills table.

## Deployment Checklist

- [ ] Skill passes `quick_validate.py`
- [ ] Description optimized via `run_loop.py` (optional but recommended)
- [ ] Copied to `~/.claude/skills/` (local)
- [ ] Copied to OpenClaw via scp (if applicable)
- [ ] Pushed to AgentSkills repo (if applicable)
- [ ] Tested trigger phrase in fresh session
