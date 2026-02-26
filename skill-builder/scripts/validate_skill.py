#!/usr/bin/env python3
"""
Skill Validator — Validates a skill directory against Anthropic best practices.
Checks frontmatter, description quality, body length, file structure, and more.

Usage:
    python validate_skill.py /path/to/skill-name/
"""

import re
import sys
import ast
from pathlib import Path
from typing import NamedTuple


class Result(NamedTuple):
    level: str   # "ERROR" or "WARN"
    check: str   # Category
    message: str


FORBIDDEN_FILES = {
    "README.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md",
    "CHANGELOG.md", "SETUP.md", "CONTRIBUTING.md",
}

FORBIDDEN_NAME_WORDS = {"anthropic", "claude"}

MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
MAX_BODY_LINES = 500
MIN_DESC_LEN = 30
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$")


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from SKILL.md content."""
    if not text.startswith("---"):
        return None, text

    end = text.find("---", 3)
    if end == -1:
        return None, text

    yaml_block = text[3:end].strip()
    body = text[end + 3:].strip()

    # Simple YAML parser (avoids PyYAML dependency)
    meta = {}
    for line in yaml_block.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            meta[key] = value

    return meta, body


def validate_frontmatter(meta: dict | None, results: list[Result]):
    """Validate YAML frontmatter."""
    if meta is None:
        results.append(Result("ERROR", "frontmatter", "No YAML frontmatter found (must start with ---)"))
        return

    # Check name
    name = meta.get("name", "")
    if not name:
        results.append(Result("ERROR", "frontmatter", "Missing 'name' field"))
    else:
        if len(name) > MAX_NAME_LEN:
            results.append(Result("ERROR", "name", f"Name too long: {len(name)} chars (max {MAX_NAME_LEN})"))
        if not NAME_PATTERN.match(name):
            results.append(Result("ERROR", "name", f"Name '{name}' must be lowercase letters, numbers, hyphens only"))
        for word in FORBIDDEN_NAME_WORDS:
            if word in name.lower():
                results.append(Result("ERROR", "name", f"Name must not contain '{word}'"))
        if "<" in name or ">" in name:
            results.append(Result("ERROR", "name", "Name must not contain XML tags"))

    # Check description
    desc = meta.get("description", "")
    if not desc:
        results.append(Result("ERROR", "frontmatter", "Missing 'description' field"))
    else:
        if len(desc) > MAX_DESC_LEN:
            results.append(Result("ERROR", "description", f"Description too long: {len(desc)} chars (max {MAX_DESC_LEN})"))
        if len(desc) < MIN_DESC_LEN:
            results.append(Result("WARN", "description", f"Description very short: {len(desc)} chars (recommend >{MIN_DESC_LEN})"))
        if "<" in desc and ">" in desc:
            results.append(Result("ERROR", "description", "Description must not contain XML tags"))
        if desc.startswith(">-") or desc.startswith("|"):
            results.append(Result("ERROR", "description", "YAML multiline indicators (>- or |) break the skill indexer. Use single-quoted string."))

        # Quality checks
        desc_lower = desc.lower()
        if desc_lower.startswith("i ") or "i can" in desc_lower or "i will" in desc_lower:
            results.append(Result("WARN", "description", "Description should be third person (not 'I can/will')"))
        if "you can" in desc_lower or "you should" in desc_lower:
            results.append(Result("WARN", "description", "Description should be third person (not 'you can/should')"))
        if "use when" not in desc_lower and "use this" not in desc_lower:
            results.append(Result("WARN", "description", "Description should include 'Use when...' language for better triggering"))

    # Check for extra fields
    allowed_fields = {"name", "description", "argument-hint", "disable-model-invocation",
                      "user-invocable", "allowed-tools", "model", "context", "agent",
                      "hooks", "license", "compatibility", "metadata"}
    for key in meta:
        if key not in allowed_fields:
            results.append(Result("WARN", "frontmatter", f"Unknown frontmatter field: '{key}'"))


def validate_body(body: str, results: list[Result]):
    """Validate SKILL.md body content."""
    lines = body.split("\n")
    line_count = len(lines)

    if line_count > MAX_BODY_LINES:
        results.append(Result("ERROR", "body", f"Body too long: {line_count} lines (max {MAX_BODY_LINES})"))
    elif line_count > MAX_BODY_LINES * 0.8:
        results.append(Result("WARN", "body", f"Body approaching limit: {line_count} lines (max {MAX_BODY_LINES})"))

    if line_count < 5:
        results.append(Result("WARN", "body", "Body is very short — may lack sufficient instructions"))

    # Check for heading structure
    has_h1 = any(line.startswith("# ") for line in lines)
    if not has_h1:
        results.append(Result("WARN", "body", "No H1 heading found — recommended to start with # Skill Name"))


def validate_structure(skill_dir: Path, results: list[Result]):
    """Validate skill directory structure."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        results.append(Result("ERROR", "structure", "SKILL.md not found"))
        return None

    # Check for forbidden files
    for item in skill_dir.iterdir():
        if item.name in FORBIDDEN_FILES:
            results.append(Result("ERROR", "structure", f"Forbidden file: {item.name} (skills should not include auxiliary docs)"))

    # Check .gitignore
    gitignore = skill_dir / ".gitignore"
    if not gitignore.exists():
        results.append(Result("WARN", "structure", "No .gitignore found — recommend excluding .venv/, data/, __pycache__/"))
    else:
        gi_content = gitignore.read_text()
        for pattern in [".venv", "__pycache__"]:
            if pattern not in gi_content:
                results.append(Result("WARN", "structure", f".gitignore missing '{pattern}' exclusion"))

    # Check scripts
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        for py_file in py_files:
            # Basic syntax check
            try:
                source = py_file.read_text(encoding="utf-8")
                ast.parse(source)
            except SyntaxError as e:
                results.append(Result("ERROR", "scripts", f"Syntax error in {py_file.name}: {e}"))
            except Exception:
                pass  # Non-Python or encoding issue, skip

    # Check references depth (no nested chains)
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for ref_file in refs_dir.rglob("*"):
            if ref_file.is_file():
                rel = ref_file.relative_to(skill_dir)
                depth = len(rel.parts)
                if depth > 3:  # skill/references/subdir/file = 3 deep max
                    results.append(Result("WARN", "structure", f"Deep nesting: {rel} — keep references one level deep"))

    return skill_md.read_text(encoding="utf-8")


def validate_skill(skill_path: str) -> int:
    """Run all validations on a skill directory. Returns exit code."""
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        print(f"ERROR: Path not found: {skill_dir}")
        return 1

    if not skill_dir.is_dir():
        print(f"ERROR: Not a directory: {skill_dir}")
        return 1

    results: list[Result] = []

    # Structure validation
    content = validate_structure(skill_dir, results)
    if content is None:
        # SKILL.md not found, can't continue
        print_results(skill_dir.name, results)
        return 1

    # Frontmatter validation
    meta, body = parse_frontmatter(content)
    validate_frontmatter(meta, results)

    # Body validation
    validate_body(body, results)

    # Print results
    return print_results(skill_dir.name, results)


def print_results(skill_name: str, results: list[Result]) -> int:
    """Print validation results. Returns exit code."""
    errors = [r for r in results if r.level == "ERROR"]
    warnings = [r for r in results if r.level == "WARN"]

    print(f"\n{'=' * 60}")
    print(f"  Skill Validation: {skill_name}")
    print(f"{'=' * 60}\n")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for r in errors:
            print(f"  [x] [{r.check}] {r.message}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for r in warnings:
            print(f"  [!] [{r.check}] {r.message}")
        print()

    total = len(errors) + len(warnings)
    if not errors and not warnings:
        print("  ALL CHECKS PASSED")
        print()

    print(f"{'=' * 60}")
    if errors:
        print(f"  RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
    else:
        print(f"  RESULT: PASS ({len(warnings)} warnings)")
    print(f"{'=' * 60}\n")

    return 1 if errors else 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py /path/to/skill-name/")
        print("\nValidates a skill directory against Anthropic best practices.")
        sys.exit(1)

    exit_code = validate_skill(sys.argv[1])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
