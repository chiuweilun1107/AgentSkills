#!/usr/bin/env python3
"""
Authentication Manager for NotebookLM Skill
Uses Playwright directly for Google login (auto-detects login completion).
Compatible with notebooklm-py's storage_state.json format.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import AUTH_INFO_FILE, DATA_DIR, NOTEBOOKLM_HOME, STORAGE_STATE_FILE

# Browser profile for persistent login (same as notebooklm-py)
BROWSER_PROFILE = NOTEBOOKLM_HOME / "browser_profile"
NOTEBOOKLM_URL = "https://notebooklm.google.com/"


class AuthManager:
    """Manages authentication for NotebookLM via Playwright + notebooklm-py."""

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def is_authenticated(self) -> bool:
        """Check if valid authentication exists."""
        if not STORAGE_STATE_FILE.exists():
            return False

        mtime = os.path.getmtime(STORAGE_STATE_FILE)
        age_days = (datetime.now().timestamp() - mtime) / 86400
        if age_days > 7:
            print("  Auth cookies may be expired (>7 days old)")
            return False

        try:
            data = json.loads(STORAGE_STATE_FILE.read_text())
            cookies = data.get("cookies", [])
            if not cookies:
                return False
            return True
        except Exception:
            return False

    def check_auth(self, test: bool = False) -> dict:
        """Check authentication status, optionally test with API call."""
        info = {
            "authenticated": False,
            "storage_state": str(STORAGE_STATE_FILE),
            "storage_exists": STORAGE_STATE_FILE.exists(),
        }

        if not STORAGE_STATE_FILE.exists():
            info["error"] = "No storage_state.json found. Run: python scripts/run.py auth_manager.py setup"
            return info

        info["authenticated"] = self.is_authenticated()

        if test and info["authenticated"]:
            try:
                result = asyncio.run(self._test_api())
                info["api_test"] = result
                info["authenticated"] = result.get("success", False)
            except Exception as e:
                info["api_test"] = {"success": False, "error": str(e)}
                info["authenticated"] = False

        return info

    async def _test_api(self) -> dict:
        """Test API access by listing notebooks."""
        try:
            from notebooklm import NotebookLMClient

            async with await NotebookLMClient.from_storage() as client:
                notebooks = await client.notebooks.list()
                return {
                    "success": True,
                    "notebook_count": len(notebooks),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def setup_auth(self) -> bool:
        """Launch browser for Google login, auto-detect completion.

        Uses Playwright persistent context (same as notebooklm-py) but
        auto-detects when login is complete instead of requiring Enter.
        """
        print("Opening browser for Google login...")
        print("Please log in to your Google account in the browser window.")
        print("Login will be detected automatically - no need to press Enter.\n")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("Playwright not installed. Run: pip install 'notebooklm-py[browser]'")
            return False

        # Ensure directories exist with secure permissions
        NOTEBOOKLM_HOME.mkdir(parents=True, exist_ok=True)
        os.chmod(str(NOTEBOOKLM_HOME), 0o700)
        BROWSER_PROFILE.mkdir(parents=True, exist_ok=True)
        os.chmod(str(BROWSER_PROFILE), 0o700)

        try:
            with sync_playwright() as p:
                # Launch persistent context (same args as notebooklm-py)
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(BROWSER_PROFILE),
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--password-store=basic",
                    ],
                    ignore_default_args=["--enable-automation"],
                )

                page = context.pages[0] if context.pages else context.new_page()
                page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded")

                print("Waiting for login completion...")
                print("(Will auto-detect when you reach NotebookLM homepage)\n")

                # Poll until user is logged in (URL stays on notebooklm.google.com
                # and is NOT redirected to accounts.google.com)
                max_wait = 600  # 10 minutes
                poll_interval = 2  # seconds
                elapsed = 0
                logged_in = False

                while elapsed < max_wait:
                    time.sleep(poll_interval)
                    elapsed += poll_interval

                    try:
                        current_url = page.url
                    except Exception:
                        # Browser may have been closed by user
                        print("Browser was closed.")
                        break

                    # Check if on NotebookLM (not auth redirect)
                    if "notebooklm.google.com" in current_url and "accounts.google.com" not in current_url:
                        # Double-check: wait a moment and verify we're still there
                        time.sleep(2)
                        try:
                            final_url = page.url
                        except Exception:
                            break
                        if "notebooklm.google.com" in final_url and "accounts.google.com" not in final_url:
                            logged_in = True
                            break

                    if elapsed % 30 == 0:
                        print(f"  Still waiting... ({elapsed}s elapsed)")

                if not logged_in:
                    print("\nLogin not detected (timed out or browser closed).")
                    try:
                        context.close()
                    except Exception:
                        pass
                    return False

                # Save storage state (compatible with notebooklm-py)
                context.storage_state(path=str(STORAGE_STATE_FILE))
                os.chmod(str(STORAGE_STATE_FILE), 0o600)
                context.close()

                self._save_auth_info()
                print(f"\nAuthentication saved to: {STORAGE_STATE_FILE}")
                print("Authentication successful!")
                return True

        except Exception as e:
            print(f"\nAuthentication error: {e}")
            return False

    def clear_auth(self):
        """Clear all authentication data."""
        import shutil

        if STORAGE_STATE_FILE.exists():
            STORAGE_STATE_FILE.unlink()
            print(f"Removed: {STORAGE_STATE_FILE}")

        if AUTH_INFO_FILE.exists():
            AUTH_INFO_FILE.unlink()
            print(f"Removed: {AUTH_INFO_FILE}")

        if BROWSER_PROFILE.exists():
            shutil.rmtree(BROWSER_PROFILE)
            print(f"Removed: {BROWSER_PROFILE}")

        print("Authentication cleared.")

    def _save_auth_info(self):
        """Save authentication metadata."""
        info = {
            "authenticated_at": datetime.now().isoformat(),
            "storage_state": str(STORAGE_STATE_FILE),
            "method": "notebooklm-py",
        }
        AUTH_INFO_FILE.write_text(json.dumps(info, indent=2))

    def get_auth_info(self) -> dict:
        """Get authentication status information."""
        if AUTH_INFO_FILE.exists():
            try:
                return json.loads(AUTH_INFO_FILE.read_text())
            except Exception:
                pass
        return {"authenticated_at": None, "method": "unknown"}


def main():
    parser = argparse.ArgumentParser(description="Manage NotebookLM authentication")

    subparsers = parser.add_subparsers(dest="command", help="Commands")
    subparsers.add_parser("setup", help="Interactive browser login")
    subparsers.add_parser("status", help="Check authentication status")
    subparsers.add_parser("reauth", help="Clear and re-authenticate")
    subparsers.add_parser("clear", help="Clear authentication data")
    subparsers.add_parser("test", help="Test API access")

    args = parser.parse_args()
    auth = AuthManager()

    if args.command == "setup":
        success = auth.setup_auth()
        sys.exit(0 if success else 1)

    elif args.command == "status":
        if auth.is_authenticated():
            info = auth.get_auth_info()
            print(f"Authenticated (via {info.get('method', 'unknown')})")
            print(f"  Auth date: {info.get('authenticated_at', 'unknown')}")
            print(f"  Storage: {STORAGE_STATE_FILE}")
        else:
            print("Not authenticated.")
            print("Run: python scripts/run.py auth_manager.py setup")
            sys.exit(1)

    elif args.command == "reauth":
        auth.clear_auth()
        success = auth.setup_auth()
        sys.exit(0 if success else 1)

    elif args.command == "clear":
        auth.clear_auth()

    elif args.command == "test":
        info = auth.check_auth(test=True)
        if info["authenticated"]:
            api = info.get("api_test", {})
            print(f"API test passed! Found {api.get('notebook_count', '?')} notebooks.")
        else:
            error = info.get("api_test", {}).get("error", info.get("error", "unknown"))
            print(f"API test failed: {error}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
