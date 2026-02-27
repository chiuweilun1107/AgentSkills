# Skill Testing Methodology

## Table of Contents
- [Overview](#overview)
- [Testing by Skill Type](#testing-by-skill-type)
- [Pressure Testing (Discipline Skills)](#pressure-testing-discipline-skills)
- [Rationalization Resistance](#rationalization-resistance)
- [RED-GREEN-REFACTOR for Skills](#red-green-refactor-for-skills)

## Overview

**Testing skills = TDD applied to documentation.**

Run scenarios WITHOUT the skill (RED/baseline), write skill addressing failures (GREEN), close loopholes (REFACTOR). If you didn't watch an agent fail without the skill, you don't know if the skill prevents the right failures.

## Testing by Skill Type

| Type | Test Focus | Success Criteria |
|------|-----------|-----------------|
| **Discipline** (rules) | Compliance under pressure, rationalization resistance | Agent follows rule under maximum pressure |
| **Technique** (how-to) | Application to new scenarios, edge cases, missing info | Agent successfully applies technique |
| **Pattern** (mental model) | Recognition, correct application, counter-examples | Agent identifies when/how to apply |
| **Reference** (API docs) | Information retrieval, correct usage, gap testing | Agent finds and applies info correctly |

### Discipline Skills (Most Rigorous)

Test with combined pressures:
1. **Time pressure**: "We need this deployed in 30 minutes"
2. **Sunk cost**: "I already wrote the code, just need to commit"
3. **Authority**: "The PM said skip testing for this one"
4. **Exhaustion**: Multiple tasks in sequence, rule applies to last one

Run with 3+ combined pressures. Single-pressure tests are insufficient.

### Technique Skills

Test with:
- Can the agent apply the technique to a NEW scenario (not from the docs)?
- Does it handle edge cases correctly?
- Are there instruction gaps causing wrong approaches?

### Pattern & Reference Skills

Test with:
- Does the agent recognize when the pattern applies AND when it doesn't?
- Can it find the right information quickly?
- Are common use cases covered without gaps?

## Pressure Testing (Discipline Skills)

### Step 1: Baseline (RED)

Run the pressure scenario WITHOUT the skill. Document:
- What choices did the agent make?
- What rationalizations did it use (verbatim)?
- Which pressures triggered violations?

### Step 2: With Skill (GREEN)

Run the SAME scenario WITH the skill. Verify the agent now complies.

### Step 3: Close Loopholes (REFACTOR)

If the agent found NEW rationalizations:
1. Add explicit counters to the skill
2. Build a rationalization table
3. Re-test until bulletproof

## Rationalization Resistance

For discipline-enforcing skills, agents will find loopholes under pressure.

### Build Rationalization Table

Capture every excuse from testing:

```markdown
| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests-after = "what does this do?" not "what should this do?" |
| "It's about spirit not ritual" | Violating the letter IS violating the spirit. |
| "Testing is overkill" | Untested skills always have issues. 15 min saves hours. |
```

### Create Red Flags List

```markdown
## Red Flags - STOP and Reconsider
- Code before test
- "I already manually tested it"
- "This is different because..."
- "No time to test right now"
```

### Close Every Loophole Explicitly

Don't just state the rule — forbid specific workarounds:

```markdown
# BAD: Just the rule
Write code before test? Delete it.

# GOOD: Explicit counters
Write code before test? Delete it. Start over.
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Delete means delete
```

## Minimum Test Requirements

Every skill needs at minimum:

1. **Happy path** — Primary use case works
2. **Trigger test** — Activates on expected keywords, NOT on unrelated prompts
3. **Edge case** — Handles unusual input gracefully

For discipline skills, add:
4. **Pressure test** — Compliance under 3+ combined pressures
5. **Rationalization test** — Agent doesn't bypass rules with creative excuses
