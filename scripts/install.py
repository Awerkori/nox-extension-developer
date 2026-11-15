#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Link the canonical skill into one explicitly selected user skill directory."""
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESTINATIONS = {
    'opencode': Path.home() / '.config/opencode/skills',
    'codex': Path.home() / '.agents/skills',
    'claude': Path.home() / '.claude/skills',
    'antigravity': Path.home() / '.gemini/antigravity/skills',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('platform', choices=DESTINATIONS)
    args = parser.parse_args()
    if not (ROOT / 'SKILL.md').is_file():
        parser.error('canonical SKILL.md missing')
    parent = DESTINATIONS[args.platform]
    if not parent.is_dir():
        parser.error(f'skill directory does not exist: {parent}; verify platform installation first')
    dest = parent / 'nox-extension-developer'
    if os.path.lexists(dest):
        if dest.is_symlink() and dest.resolve() == ROOT:
            print(f'already installed: {dest}')
            return
        parser.error(f'refusing to replace existing path: {dest}')
    dest.symlink_to(ROOT, target_is_directory=True)
    print(f'installed: {dest} -> {ROOT}')


if __name__ == '__main__':
    main()
