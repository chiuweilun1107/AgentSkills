#!/usr/bin/env python3
"""
Universal runner for NotebookLM skill scripts.
Ensures all scripts run with the correct virtual environment.
Works on both Claude Code and OpenClaw (handles Homebrew Python on macOS).
"""

import os
import sys
import subprocess
from pathlib import Path

# Minimum Python version required by notebooklm-py
MIN_PYTHON = (3, 11)


def find_suitable_python() -> str:
    """Find a Python >= 3.11 executable. Checks Homebrew paths on macOS."""
    if sys.version_info >= MIN_PYTHON:
        return sys.executable

    # Common locations for newer Python (macOS Homebrew, Linux)
    candidates = [
        "/opt/homebrew/bin/python3",
        "/opt/homebrew/bin/python3.13",
        "/opt/homebrew/bin/python3.14",
        "/opt/homebrew/bin/python3.12",
        "/opt/homebrew/bin/python3.11",
        "/usr/local/bin/python3",
        "/usr/local/bin/python3.13",
        "/usr/local/bin/python3.12",
        "/usr/local/bin/python3.11",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                result = subprocess.run(
                    [path, "-c", "import sys; print(sys.version_info >= (3, 11))"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.stdout.strip() == "True":
                    return path
            except Exception:
                continue

    return sys.executable  # fallback


def get_venv_python():
    """Get the virtual environment Python executable"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    if os.name == 'nt':
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def ensure_venv():
    """Ensure virtual environment exists"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    setup_script = skill_dir / "scripts" / "setup_environment.py"

    if not venv_dir.exists():
        print("First-time setup: Creating virtual environment...")
        python = find_suitable_python()
        print(f"Using Python: {python}")
        result = subprocess.run([python, str(setup_script)])
        if result.returncode != 0:
            print("Failed to set up environment")
            sys.exit(1)
        print("Environment ready!")

    return get_venv_python()


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print("  auth_manager.py     - Handle authentication (setup/status/test)")
        print("  notebook_manager.py - Manage notebook library (add/list/search/sync)")
        print("  ask_question.py     - Query a NotebookLM notebook")
        print("  create_notebook.py  - Create new notebook with source")
        print("  add_source.py       - Add source to existing notebook")
        print("  cleanup_manager.py  - Clean up skill data")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    if script_name.startswith('scripts/'):
        script_name = script_name[8:]
    if not script_name.endswith('.py'):
        script_name += '.py'

    skill_dir = Path(__file__).parent.parent
    script_path = skill_dir / "scripts" / script_name

    if not script_path.exists():
        print(f"Script not found: {script_name}")
        sys.exit(1)

    venv_python = ensure_venv()
    cmd = [str(venv_python), str(script_path)] + script_args

    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
