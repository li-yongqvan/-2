#!/usr/bin/env python3
"""
Install the /capture skill into the Claude Code user-level skills directory.

Usage:
    python scripts/install-capture-skill.py
    python scripts/install-capture-skill.py --symlink
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "capture"
TARGET_SKILL_DIR = Path.home() / ".claude" / "skills" / "capture"


def install_copy() -> None:
    if TARGET_SKILL_DIR.exists():
        shutil.rmtree(TARGET_SKILL_DIR)
    shutil.copytree(SOURCE_SKILL_DIR, TARGET_SKILL_DIR)


def install_symlink() -> None:
    if TARGET_SKILL_DIR.exists() or TARGET_SKILL_DIR.is_symlink():
        TARGET_SKILL_DIR.unlink()
    try:
        TARGET_SKILL_DIR.symlink_to(SOURCE_SKILL_DIR, target_is_directory=True)
    except OSError as exc:
        print(f"symlink failed ({exc}); falling back to copy", file=sys.stderr)
        install_copy()


def main() -> int:
    parser = argparse.ArgumentParser(description="Install /capture skill globally for Claude Code.")
    parser.add_argument("--symlink", action="store_true", help="Symlink instead of copy (keeps repo changes live).")
    args = parser.parse_args()

    if not SOURCE_SKILL_DIR.exists():
        print(f"error: source skill dir not found: {SOURCE_SKILL_DIR}", file=sys.stderr)
        return 1

    TARGET_SKILL_DIR.parent.mkdir(parents=True, exist_ok=True)

    if args.symlink:
        install_symlink()
    else:
        install_copy()

    print(f"Installed /capture skill to {TARGET_SKILL_DIR}")
    print("Restart Claude Code or start a new session to use /capture.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
