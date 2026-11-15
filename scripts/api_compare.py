#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Compare explicitly supplied API contracts; never infer full compatibility."""
import argparse
import json
from pathlib import Path
import re

ECOSYSTEMS = {'keiyoushi', 'yuzono', 'lnreader'}


def extract(text, ecosystem, scope):
    """Extract simple single-line declarations. Results are always incomplete."""
    if ecosystem not in ECOSYSTEMS or not scope:
        raise ValueError('invalid ecosystem or scope')
    pattern = (r'^\s*(?:(?:public|abstract|override|suspend|open)\s+)*fun\s+(\w+)\s*\([^\n]*$'
               if ecosystem != 'lnreader' else
               r'^\s*(?:readonly\s+)?(\w+)\s*\([^\n]*\)\s*:\s*[^\n]+$')
    symbols = {}
    for line in text.splitlines():
        match = re.match(pattern, line)
        if not match:
            continue
        key = match.group(1)
        if key in symbols:
            raise ValueError(f'ambiguous overloaded declaration: {key}')
        symbols[key] = ' '.join(line.strip().split())
    return {'ecosystem': ecosystem, 'scope': scope, 'complete': False, 'symbols': symbols, 'versions': {}}


def validate(contract):
    if not isinstance(contract, dict) or contract.get('ecosystem') not in ECOSYSTEMS:
        raise ValueError('invalid ecosystem')
    if not isinstance(contract.get('scope'), str) or not contract['scope'].strip():
        raise ValueError('scope is required')
    if not isinstance(contract.get('complete'), bool):
        raise ValueError('complete must be a boolean')
    for key in ('symbols', 'versions'):
        values = contract.get(key)
        if not isinstance(values, dict) or not all(isinstance(k, str) and k and isinstance(v, str) and v for k, v in values.items()):
            raise ValueError(f'{key} must map nonempty strings to nonempty strings')


def compare(old, new):
    validate(old)
    validate(new)
    if old['ecosystem'] != new['ecosystem'] or old['scope'] != new['scope']:
        raise ValueError('ecosystem and scope must match')
    before, after = old['symbols'], new['symbols']
    removed = sorted(before.keys() - after.keys()) if new['complete'] else []
    changed = sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
    added = sorted(after.keys() - before.keys())
    versions = sorted(k for k in old['versions'].keys() | new['versions'].keys() if old['versions'].get(k) != new['versions'].get(k))
    major = []
    for key in versions:
        a = re.fullmatch(r'(\d+)\.\d+\.\d+', old['versions'].get(key, ''))
        b = re.fullmatch(r'(\d+)\.\d+\.\d+', new['versions'].get(key, ''))
        if a and b and int(b.group(1)) > int(a.group(1)):
            major.append(key)
    if removed or changed or major:
        category = 'POTENCIALMENTE_INCOMPATIVEL'
    elif (not old['complete'] or not new['complete'] or versions or added or not before or not old['versions']
          or any(not re.fullmatch(r'\d+(?:\.\d+)*', v) for v in old['versions'].values())):
        category = 'INDETERMINADO'
    else:
        category = 'COMPATIVEL_NO_ESCOPO_DECLARADO'
    return {'classification': category, 'removed': removed, 'changed': changed, 'added': added,
            'version_changes': versions, 'major_increases': major,
            'warning': 'Comparison covers only supplied declarations; semantic and runtime compatibility require manual review.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old', type=Path, help='old contract JSON or source file with --extract')
    parser.add_argument('new', type=Path, help='new contract JSON or source file with --extract')
    parser.add_argument('--extract', choices=sorted(ECOSYSTEMS), help='heuristically compare single-line declarations in source files')
    args = parser.parse_args()
    try:
        if args.extract:
            old = extract(args.old.read_text(), args.extract, 'source-comparison')
            new = extract(args.new.read_text(), args.extract, 'source-comparison')
        else:
            old, new = json.loads(args.old.read_text()), json.loads(args.new.read_text())
        print(json.dumps(compare(old, new), indent=2, ensure_ascii=False))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f'Cannot compare contracts: {exc}\n')


if __name__ == '__main__':
    main()
