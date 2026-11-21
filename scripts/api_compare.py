#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Compare explicitly supplied API contracts; never infer full compatibility."""
import argparse
import json
from pathlib import Path
import re
from typing import Any

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


def _scan_balanced_signature(lines: list[str], start_idx: int) -> tuple[str, int]:
    """Accumulate a potentially multi-line signature until parentheses balance."""
    buf: list[str] = []
    depth = 0
    saw_paren = False
    idx = start_idx
    while idx < len(lines) and idx < start_idx + 12:
        line = lines[idx].strip()
        buf.append(line)
        for ch in line:
            if ch == '(':
                depth += 1
                saw_paren = True
            elif ch == ')':
                depth -= 1
        if saw_paren and depth <= 0 and ('{' in line or '=' in line or ':' in line or ';' in line or ')' in line):
            break
        idx += 1
    joined = ' '.join(' '.join(buf).split())
    # Strip trailing function body opening if present
    joined = re.sub(r'\s*\{.*$', '', joined).strip()
    return joined, idx


def analyze_source_quality(text: str, ecosystem: str) -> list[dict[str, Any]]:
    """Detect ecosystem-specific Kotlin/TypeScript semantic anti-patterns statically."""
    if ecosystem not in ECOSYSTEMS:
        raise ValueError(f'invalid ecosystem: {ecosystem!r}')
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    if ecosystem in {'keiyoushi', 'yuzono'}:
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            if '!!' in line:
                findings.append({'line': i, 'severity': 'WARN', 'code': 'UNSAFE_NOT_NULL', 'message': 'Avoid non-null assertion (!!); HTML/JSON fields may be null.'})
            if '@Serializable' in line and i < len(lines) and re.search(r'\bdata\s+class\b', lines[i]):
                findings.append({'line': i + 1, 'severity': 'FAIL', 'code': 'SERIALIZABLE_DATA_CLASS', 'message': 'Keiyoushi/Yuzono require regular class (not data class) for @Serializable DTOs.'})
            if 'injectLazy()' in line and 'Json' in line:
                findings.append({'line': i, 'severity': 'WARN', 'code': 'LOCAL_JSON_INJECT', 'message': 'Use shared keiyoushi.utils parseAs<T>() / toJsonRequestBody() instead of local Json injectLazy().'})
            if re.search(r'\bcatch\s*\([^)]*Exception[^)]*\)[^{]*\{[^}]*emptyList\(\)', line):
                findings.append({'line': i, 'severity': 'WARN', 'code': 'SILENT_EMPTY_CATCH', 'message': 'Catching Exception and returning emptyList() silently hides parser/network errors.'})
        if re.search(r'\bGlobalScope\b', text):
            findings.append({'line': 1, 'severity': 'WARN', 'code': 'UNSTRUCTURED_COROUTINE', 'message': 'Avoid GlobalScope; preserve structured coroutine cancellation.'})
    else:
        for i, line in enumerate(lines, start=1):
            if re.search(r"""from\s+['"]@/(?:lib|libs)/""", line):
                findings.append({'line': i, 'severity': 'FAIL', 'code': 'LNREADER_WRONG_ALIAS', 'message': 'Use @libs/* (not @/lib/*) for Hermes/React Native plugin bundles.'})
            if re.search(r'\b(?:require\s*\(\s*[\'"](?:fs|path|child_process|http|https)[\'"]\)|window\.|document\.)', line):
                findings.append({'line': i, 'severity': 'FAIL', 'code': 'HERMES_UNSUPPORTED_GLOBAL', 'message': 'Node/DOM globals (fs, path, window, document) fail in Hermes ES5 runtime.'})
        if 'parseNovel' in text and 'trailing' not in text and re.search(r'novels?/', text) and '.replace(' not in text:
            findings.append({'line': 1, 'severity': 'INFO', 'code': 'CHECK_TRAILING_SLASH', 'message': 'Ensure parseNovel normalizes leading/trailing slashes if migrated from multisrc (e.g., Fictioneer).'})
    return findings


def extract_structural(text: str, ecosystem: str, scope: str) -> dict[str, Any]:
    """Extract multi-line declarations with overloads/generics plus static anti-patterns."""
    if ecosystem not in ECOSYSTEMS or not scope:
        raise ValueError('invalid ecosystem or scope')
    lines = text.splitlines()
    symbols: dict[str, str] = {}
    overloads: dict[str, int] = {}
    idx = 0
    kt_re = re.compile(r'^\s*(?:(?:public|private|protected|internal|abstract|override|suspend|open|inline)\s+)*fun\s+(?:<[^>]+>\s*)?(?:\w+\.)?(\w+)\s*\(')
    ts_re = re.compile(r'^\s*(?:(?:public|private|protected|readonly|async|static)\s+)*(\w+)\s*\(')

    while idx < len(lines):
        line = lines[idx]
        m = kt_re.match(line) if ecosystem != 'lnreader' else ts_re.match(line)
        if m and m.group(1) not in {'if', 'for', 'while', 'switch', 'catch', 'constructor'}:
            name = m.group(1)
            sig, end_idx = _scan_balanced_signature(lines, idx)
            count = overloads.get(name, 0) + 1
            overloads[name] = count
            key = name if count == 1 else f'{name}#{count}'
            symbols[key] = sig
            idx = end_idx + 1
            continue
        idx += 1

    return {
        'ecosystem': ecosystem,
        'scope': scope,
        'complete': False,
        'symbols': symbols,
        'versions': {},
        'quality_findings': analyze_source_quality(text, ecosystem),
    }


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
    parser.add_argument('--structural', action='store_true', help='use multi-line overload-aware extractor and static anti-pattern audit')
    args = parser.parse_args()
    try:
        if args.extract:
            extractor = extract_structural if args.structural else extract
            old = extractor(args.old.read_text(), args.extract, 'source-comparison')
            new = extractor(args.new.read_text(), args.extract, 'source-comparison')
            result = compare(old, new)
            if args.structural:
                result['quality_findings_old'] = old.get('quality_findings', [])
                result['quality_findings_new'] = new.get('quality_findings', [])
        else:
            old, new = json.loads(args.old.read_text()), json.loads(args.new.read_text())
            result = compare(old, new)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f'Cannot compare contracts: {exc}\n')


if __name__ == '__main__':
    main()
