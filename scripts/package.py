#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Create a deterministic candidate archive from an explicit allowlist."""
import argparse
import os
from pathlib import Path
import stat
import tempfile
import zipfile

FILES = (
    'SKILL.md', 'README.md', 'README.en.md', 'CHANGELOG.md', 'LICENSE', 'ATRIBUICOES.md', 'COMPATIBILIDADE.md', 'SEGURANCA.md',
    'CONTRIBUTING.md', 'CONTRIBUTING.en.md', 'CODE_OF_CONDUCT.md', 'SECURITY.md',
    'assets/banner.svg', 'assets/logo.svg', 'docs/pt-BR/guia.md', 'docs/en/guide.md',
    'prompts/install-pt-BR.txt', 'prompts/install-en.txt',
    'scripts/install.py', 'scripts/references.py', 'scripts/api_compare.py', 'scripts/package.py',
    'references/api-contracts.md', 'tests/test_api_compare.py', 'tests/test_install.py',
    'tests/test_package.py', 'tests/test_references.py',
)


def build(root, output):
    root = Path(root).resolve()
    contents = []
    rootfd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for name in FILES:
            directory = os.dup(rootfd)
            try:
                parts = name.split('/')
                for part in parts[:-1]:
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    os.close(directory)
                    directory = child
                fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
                with os.fdopen(fd, 'rb') as f:
                    if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
                        raise ValueError(f'not a regular file: {name}')
                    contents.append((name, f.read()))
            except OSError as exc:
                raise ValueError(f'cannot safely read package file {name}: {exc}') from exc
            finally:
                os.close(directory)
    finally:
        os.close(rootfd)
    output = Path(output)
    with tempfile.NamedTemporaryFile(prefix='.nox-package-', dir=output.parent, delete=False) as temp:
        temporary = Path(temp.name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in contents:
                entry = zipfile.ZipInfo('nox-extension-developer/' + name, (2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        os.link(temporary, output)
    finally:
        temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new ZIP path; existing files are never overwritten')
    args = parser.parse_args()
    try:
        build(Path(__file__).resolve().parent.parent, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Cannot create package: {exc}\n')
    print(args.output)


if __name__ == '__main__':
    main()
