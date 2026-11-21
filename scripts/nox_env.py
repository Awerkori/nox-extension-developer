#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Environment doctor, ecosystem/architecture detector, and source identity continuity checks."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
from typing import Any, Sequence
from urllib.parse import urlsplit
import zipfile

from nox_core import atomic_write_text, is_safe_public_url, sanitize_text


ECOSYSTEMS = ('keiyoushi', 'yuzono', 'lnreader')


def _run_version(cmd: list[str], timeout: float = 5.0) -> dict[str, Any]:
    exe = shutil.which(cmd[0])
    if not exe:
        return {'present': False, 'path': None, 'version': None, 'healthy': False}
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or proc.stderr or '').strip()
        first_line = out.splitlines()[0] if out else ''
        return {
            'present': True,
            'path': exe,
            'version': first_line,
            'healthy': proc.returncode == 0,
            'returncode': proc.returncode,
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {'present': True, 'path': exe, 'version': None, 'healthy': False, 'error': str(exc)}


def detect_platform_details() -> dict[str, Any]:
    """Detect OS, CPU architecture, WSL vs Linux native, and console encoding."""
    sys_name = platform.system()
    release = platform.release().lower()
    is_wsl = sys_name == 'Linux' and ('microsoft' in release or 'wsl' in release or bool(os.environ.get('WSL_DISTRO_NAME')))
    return {
        'system': sys_name,
        'machine': platform.machine(),
        'release': platform.release(),
        'is_wsl': is_wsl,
        'wsl_distro': os.environ.get('WSL_DISTRO_NAME'),
        'python_version': platform.python_version(),
        'posix_supported': os.name == 'posix',
    }


def _inspect_android_sdk() -> dict[str, Any]:
    candidates = [
        os.environ.get('ANDROID_HOME'),
        os.environ.get('ANDROID_SDK_ROOT'),
        str(Path.home() / '.local/share/android-sdk'),
        str(Path.home() / 'Android/Sdk'),
    ]
    configured = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    sdk_path: Path | None = None
    broken_env = False
    if configured and not Path(configured).is_dir():
        broken_env = True
    for c in candidates:
        if c and Path(c).is_dir():
            sdk_path = Path(c)
            break

    if not sdk_path:
        return {
            'present': False,
            'healthy': False,
            'broken_env': broken_env,
            'configured_env': configured,
            'sdk_path': None,
            'platforms': [],
            'build_tools': [],
            'tools': {},
        }

    platforms_dir = sdk_path / 'platforms'
    build_tools_dir = sdk_path / 'build-tools'
    platforms = sorted(p.name for p in platforms_dir.iterdir() if p.is_dir()) if platforms_dir.is_dir() else []
    build_tools = sorted(p.name for p in build_tools_dir.iterdir() if p.is_dir()) if build_tools_dir.is_dir() else []

    latest_bt = sdk_path / 'build-tools' / build_tools[-1] if build_tools else None
    aapt2 = (latest_bt / 'aapt2') if latest_bt and (latest_bt / 'aapt2').is_file() else shutil.which('aapt2')
    apksigner = (latest_bt / 'apksigner') if latest_bt and (latest_bt / 'apksigner').is_file() else shutil.which('apksigner')
    sdkmanager = (sdk_path / 'cmdline-tools/latest/bin/sdkmanager')
    if not sdkmanager.is_file():
        sm = shutil.which('sdkmanager')
        sdkmanager_path = sm
    else:
        sdkmanager_path = str(sdkmanager)

    adb_path = str(sdk_path / 'platform-tools/adb') if (sdk_path / 'platform-tools/adb').is_file() else shutil.which('adb')
    healthy = bool(platforms and build_tools and aapt2 and apksigner)
    return {
        'present': True,
        'healthy': healthy,
        'broken_env': broken_env,
        'configured_env': configured,
        'sdk_path': str(sdk_path),
        'platforms': platforms,
        'build_tools': build_tools,
        'tools': {
            'aapt2': str(aapt2) if aapt2 else None,
            'apksigner': str(apksigner) if apksigner else None,
            'sdkmanager': sdkmanager_path,
            'adb': adb_path,
        },
    }


def run_doctor(ecosystem: str | None = None, *, check_path: Path | None = None) -> dict[str, Any]:
    """Diagnose local tools, separating optional missing tools from broken installations."""
    if ecosystem is not None and ecosystem not in ECOSYSTEMS:
        raise ValueError(f'unknown ecosystem: {ecosystem!r}')

    target = (check_path or Path.cwd()).resolve()
    disk = shutil.disk_usage(target if target.exists() else Path.home())
    free_gb = round(disk.free / (1024 ** 3), 2)

    tools = {
        'python3': _run_version(['python3', '--version']),
        'git': _run_version(['git', '--version']),
        'java': _run_version(['java', '-version']),
        'javac': _run_version(['javac', '-version']),
        'node': _run_version(['node', '--version']),
        'npm': _run_version(['npm', '--version']),
        'adb': _run_version(['adb', 'version']),
        'gh': _run_version(['gh', '--version']),
    }
    android_sdk = _inspect_android_sdk()
    plat = detect_platform_details()

    issues: list[dict[str, str]] = []
    if not plat['posix_supported']:
        issues.append({'severity': 'BLOCKED', 'area': 'os', 'message': 'Native Windows is unsupported by POSIX scripts; use WSL2.'})
    if android_sdk['broken_env']:
        issues.append({'severity': 'FAIL', 'area': 'android_sdk', 'message': f"ANDROID_HOME/ANDROID_SDK_ROOT points to missing directory: {android_sdk['configured_env']}"})
    if tools['java']['present'] != tools['javac']['present']:
        issues.append({'severity': 'FAIL', 'area': 'jdk', 'message': 'Incomplete JDK: java and javac do not both resolve.'})
    if free_gb < 1.0:
        issues.append({'severity': 'WARN', 'area': 'disk', 'message': f'Low free disk space ({free_gb} GB). Android/Gradle builds usually need >2 GB.'})

    # Determine ecosystem readiness honestly
    readiness: dict[str, dict[str, Any]] = {}
    core_ok = tools['python3']['healthy'] and tools['git']['healthy'] and plat['posix_supported']
    android_build_ok = core_ok and tools['java']['healthy'] and tools['javac']['healthy'] and android_sdk['healthy']
    lnreader_ok = core_ok and tools['node']['healthy'] and tools['npm']['healthy']

    readiness['keiyoushi'] = {
        'status': 'PASS' if (android_build_ok and not android_sdk['broken_env']) else ('FAIL' if android_sdk['broken_env'] else 'BLOCKED'),
        'missing': [k for k, ok in [('java', tools['java']['healthy']), ('javac', tools['javac']['healthy']), ('android_sdk', android_sdk['healthy'])] if not ok],
    }
    readiness['yuzono'] = dict(readiness['keiyoushi'])
    readiness['lnreader'] = {
        'status': 'PASS' if lnreader_ok else 'BLOCKED',
        'missing': [k for k, ok in [('node', tools['node']['healthy']), ('npm', tools['npm']['healthy'])] if not ok],
        'note': 'Android SDK is NOT required for LNReader novel plugins.',
    }

    if ecosystem:
        overall = readiness[ecosystem]['status']
    else:
        if any(i['severity'] == 'FAIL' for i in issues):
            overall = 'FAIL'
        elif core_ok:
            overall = 'PASS'
        else:
            overall = 'BLOCKED'

    return {
        'status': overall,
        'platform': plat,
        'disk_free_gb': free_gb,
        'tools': tools,
        'android_sdk': android_sdk,
        'ecosystem_readiness': readiness,
        'issues': issues,
    }


def compute_source_id(name: str, lang: str, version_id: int = 1) -> int:
    """Compute canonical Tachiyomi/Mihon/Aniyomi 64-bit signed source ID (lower 63 bits positive)."""
    key = f'{name.lower()}/{lang}/{version_id}'.encode('utf-8')
    digest = hashlib.md5(key).digest()
    raw = struct.unpack('>Q', digest[:8])[0]
    return raw & ((1 << 63) - 1)


def _find_repo_root(path: Path) -> Path | None:
    cur = path if path.is_dir() else path.parent
    for candidate in (cur, *cur.parents):
        if (candidate / '.git').exists() or (candidate / 'settings.gradle.kts').is_file() or (candidate / 'package.json').is_file():
            return candidate
    return None


def inspect_project(project_path: Path | str) -> dict[str, Any]:
    """Detect ecosystem (Keiyoushi/Yuzono/LNReader), modern vs legacy architecture, and source identity."""
    target = Path(project_path).resolve()
    if not target.exists():
        return {'status': 'FAIL', 'error': f'path does not exist: {target}'}

    root = _find_repo_root(target) or (target if target.is_dir() else target.parent)
    evidence: list[str] = []
    ecosystem: str | None = None
    architecture = 'unknown'
    warnings: list[str] = []

    build_gradle = target / 'build.gradle.kts' if target.is_dir() else (target if target.name == 'build.gradle.kts' else target.parent / 'build.gradle.kts')
    root_settings = root / 'settings.gradle.kts'
    pkg_json = root / 'package.json'

    settings_text = root_settings.read_text(errors='replace') if root_settings.is_file() else ''
    build_text = build_gradle.read_text(errors='replace') if build_gradle.is_file() else ''
    pkg_text = pkg_json.read_text(errors='replace') if pkg_json.is_file() else ''

    # Detect LNReader first if TypeScript / package.json markers exist
    if 'lnreader' in pkg_text.lower() or (root / 'plugins').is_dir() or target.suffix == '.ts':
        ecosystem = 'lnreader'
        evidence.append('package.json/plugins/*.ts markers match LNReader')
        if 'multisrc' in str(target) or (target.name == 'sources.json'):
            architecture = 'lnreader-multisrc'
        else:
            architecture = 'lnreader-standalone'
    else:
        # Distinguish Yuzono (Anime) vs Keiyoushi (Manga) strictly
        kt_files = [target] if target.suffix == '.kt' else sorted((target / 'src' if (target / 'src').is_dir() else target).rglob('*.kt'))[:25]
        kt_combined = '\n'.join(f.read_text(errors='replace')[:8000] for f in kt_files if f.is_file())
        joined = '\n'.join([build_text, settings_text, kt_combined])

        if 'yuzono' in joined.lower() or 'animesource' in joined.lower() or 'animeextension' in joined.lower() or 'AniSource' in joined:
            ecosystem = 'yuzono'
            evidence.append('yuzono / animesource / animeextension markers detected')
        elif 'keiyoushi' in joined.lower() or 'KeiSource' in joined or 'tachiyomi.source' in joined or 'extension' in joined.lower():
            ecosystem = 'keiyoushi'
            evidence.append('keiyoushi / KeiSource / tachiyomi.source markers detected')

        if ecosystem in {'keiyoushi', 'yuzono'}:
            has_dsl_block = bool(re.search(r'\b(?:keiyoushi|yuzono)\s*\{', build_text))
            has_source_ann = '@Source' in kt_combined
            has_keisource = 'KeiSource' in kt_combined
            has_anisource = 'AniSource' in kt_combined
            has_legacy_http = bool(re.search(r'\b(?:Parsed)?(?:Anime)?HttpSource\b', kt_combined))
            has_source_factory = 'SourceFactory' in kt_combined
            has_manual_meta = bool(re.search(r'override\s+val\s+(?:name|lang|baseUrl|id)\b', kt_combined))

            if has_keisource or has_anisource or has_source_ann:
                architecture = 'modern-ksp'
                if has_source_factory:
                    warnings.append('Modern KSP module still references obsolete SourceFactory.')
                if has_manual_meta and has_source_ann:
                    warnings.append('KSP @Source module manually overrides name/lang/baseUrl/id; verify KSP rules to prevent compilation/runtime drift.')
            elif has_legacy_http or has_source_factory:
                architecture = 'legacy-dsl-http' if has_dsl_block else 'legacy-http-source'
                warnings.append('Legacy module detected; do NOT auto-migrate to KeiSource/AniSource without explicit authorization.')
            elif has_dsl_block:
                architecture = 'dsl-gradle-hybrid'

            # Check Keiyoushi DTO anti-pattern (data class @Serializable) and injectLazy Json
            if '@Serializable' in kt_combined and re.search(r'@Serializable[^\n]*\n\s*(?:private\s+)?data\s+class\b', kt_combined):
                warnings.append('Found @Serializable data class; Keiyoushi/Yuzono conventions require regular class for DTOs to avoid bytecode bloat.')
            if 'injectLazy()' in kt_combined and 'Json' in kt_combined:
                warnings.append('Found local Json by injectLazy(); prefer keiyoushi.utils parseAs<T>() / toJsonRequestBody().')

    # Extract declared sources and compute deterministic source IDs
    sources: list[dict[str, Any]] = []
    if build_text:
        ext_name_m = re.search(r'^\s*name\s*=\s*"([^"]+)"', build_text, re.M)
        ext_name = ext_name_m.group(1) if ext_name_m else ''
        ver_code_m = re.search(r'^\s*versionCode\s*=\s*(\d+)', build_text, re.M)
        lib_ver_m = re.search(r'^\s*libVersion\s*=\s*"([^"]+)"', build_text, re.M)
        for block in re.finditer(r'(?:(listOf\s*\(([^)]+)\)\s*\.forEach\s*\{\s*(?:(\w+)\s*->)?)\s*)?\bsource\s*\{([^}]*)\}', build_text, re.S):
            foreach_raw, foreach_items, iter_var, body = block.group(1), block.group(2), block.group(3) or 'it', block.group(4)
            lang_m = re.search(r'\blang\s*=\s*"([^"]+)"', body)
            lang_var_m = re.search(rf'\blang\s*=\s*{re.escape(iter_var)}\b', body)
            url_m = re.search(r'\bbaseUrl\s*=\s*"([^"]+)"', body)
            sname_m = re.search(r'\bname\s*=\s*"([^"]+)"', body)
            vid_m = re.search(r'\bversionId\s*=\s*(\d+)', body)
            id_m = re.search(r'\bid\s*=\s*(-?\d+)L?', body)
            sname = sname_m.group(1) if sname_m else ext_name
            vid = int(vid_m.group(1)) if vid_m else 1

            langs: list[str]
            if foreach_raw and foreach_items and lang_var_m:
                langs = re.findall(r'"([^"]+)"', foreach_items) or ['unknown']
            else:
                langs = [lang_m.group(1) if lang_m else 'unknown']

            for lang in langs:
                computed_id = int(id_m.group(1)) if id_m else (compute_source_id(sname, lang, vid) if sname and lang != 'unknown' else None)
                sources.append({
                    'name': sname,
                    'lang': lang,
                    'baseUrl': url_m.group(1) if url_m else None,
                    'versionId': vid,
                    'sourceId': computed_id,
                    'explicit_id': id_m is not None,
                })
        gradle_meta = {
            'name': ext_name,
            'versionCode': int(ver_code_m.group(1)) if ver_code_m else None,
            'libVersion': lib_ver_m.group(1) if lib_ver_m else None,
            'has_deeplink': 'deeplink {' in build_text or 'deeplink{' in build_text,
        }
    else:
        gradle_meta = {}

    is_nox_fork = 'ProjectNox-org' in (root / 'CONTRIBUTING.md').read_text(errors='replace') if (root / 'CONTRIBUTING.md').is_file() else False

    return {
        'status': 'PASS' if ecosystem else 'INCONCLUSIVE',
        'target': str(target),
        'repo_root': str(root),
        'ecosystem': ecosystem,
        'architecture': architecture,
        'is_project_nox_fork': is_nox_fork,
        'gradle_meta': gradle_meta,
        'sources': sources,
        'evidence': evidence,
        'warnings': warnings,
    }


def check_identity_continuity(old_sources: list[dict[str, Any]], new_sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect sourceId / lang / versionId / path breaks that would orphan user library entries."""
    old_map = {(s.get('name'), s.get('lang')): s for s in old_sources}
    new_map = {(s.get('name'), s.get('lang')): s for s in new_sources}
    breaks: list[dict[str, Any]] = []

    old_ids = {s.get('sourceId'): s for s in old_sources if s.get('sourceId') is not None}
    new_ids = {s.get('sourceId'): s for s in new_sources if s.get('sourceId') is not None}

    for sid, old_s in old_ids.items():
        if sid not in new_ids:
            breaks.append({
                'type': 'SOURCE_ID_LOST',
                'sourceId': sid,
                'old': old_s,
                'risk': 'Users will lose saved manga/anime/novel associations in library.',
            })

    # Detect collisions within new_sources
    seen_ids: dict[int, dict[str, Any]] = {}
    for s in new_sources:
        sid = s.get('sourceId')
        if sid is None:
            continue
        if sid in seen_ids:
            breaks.append({
                'type': 'SOURCE_ID_COLLISION',
                'sourceId': sid,
                'first': seen_ids[sid],
                'second': s,
            })
        else:
            seen_ids[sid] = s

    # Detect renamed entries even if old_ids was empty
    for key, old_s in old_map.items():
        if key not in new_map and len(old_sources) == len(new_sources) == 1:
            breaks.append({
                'type': 'IDENTITY_RENAMED',
                'old': old_s,
                'new': new_sources[0],
                'risk': 'Changing name or lang alters computed sourceId unless explicit id override is kept.',
            })

    return {
        'status': 'FAIL' if breaks else 'PASS',
        'breaks': breaks,
        'preserved_ids': sorted(set(old_ids) & set(new_ids)),
    }


def audit_git_safety(repo_path: Path | str) -> dict[str, Any]:
    """Audit .git/hooks and local .git/config for executable hooks or dangerous settings before running tools."""
    root = Path(repo_path).resolve()
    git_dir = root / '.git'
    findings: list[dict[str, str]] = []
    if not git_dir.exists():
        return {'status': 'PASS', 'has_git': False, 'findings': []}

    hooks_dir = git_dir / 'hooks'
    if hooks_dir.is_dir():
        for h in sorted(hooks_dir.iterdir()):
            if h.is_file() and not h.name.endswith('.sample') and os.access(h, os.X_OK):
                findings.append({'kind': 'executable_git_hook', 'path': str(h)})

    cfg = git_dir / 'config'
    if cfg.is_file():
        txt = cfg.read_text(errors='replace')
        for key in ('hooksPath', 'fsmonitor', 'sshCommand', 'credential.helper'):
            if re.search(rf'(?i)^\s*{re.escape(key)}\s*=', txt, re.M):
                findings.append({'kind': f'suspicious_git_config:{key}', 'path': str(cfg)})

    return {
        'status': 'FAIL' if findings else 'PASS',
        'has_git': True,
        'findings': findings,
    }


def check_skill_installations(canonical_root: Path | str) -> dict[str, Any]:
    """Audit where skill paths point across user agent directories without modifying them."""
    canon = Path(canonical_root).resolve()
    targets = {
        'agents_codex': Path.home() / '.agents/skills/nox-extension-developer',
        'gemini_config': Path.home() / '.gemini/config/skills/nox-extension-developer',
        'antigravity': Path.home() / '.gemini/antigravity/skills/nox-extension-developer',
        'opencode': Path.home() / '.config/opencode/skills/nox-extension-developer',
        'claude': Path.home() / '.claude/skills/nox-extension-developer',
    }
    entries: dict[str, dict[str, Any]] = {}
    drifted: list[str] = []
    for name, p in targets.items():
        exists = os.path.lexists(p)
        is_link = p.is_symlink()
        resolved = str(p.resolve()) if exists and p.exists() else None
        matches = (resolved == str(canon))
        if exists and not matches:
            drifted.append(name)
        entries[name] = {
            'path': str(p),
            'exists': exists,
            'is_symlink': is_link,
            'resolved': resolved,
            'points_to_canonical_repo': matches,
        }
    return {
        'status': 'INCONCLUSIVE' if drifted else 'PASS',
        'canonical_root': str(canon),
        'installations': entries,
        'drifted_copies': drifted,
        'note': 'Directories outside the canonical repo are never overwritten automatically.',
    }


_BUILTIN_ADVISORIES: tuple[dict[str, Any], ...] = (
    {'package': 'jsoup', 'below': (1, 15, 3), 'severity': 'WARN', 'id': 'CVE-2022-36033', 'summary': 'Older jsoup versions have HTML cleaner XSS flaws.'},
    {'package': 'com.squareup.okhttp3:okhttp', 'below': (4, 9, 2), 'severity': 'WARN', 'id': 'CVE-2021-0341', 'summary': 'Older OkHttp hostname verification edge cases.'},
    {'package': 'cheerio', 'below': (1, 0, 0), 'severity': 'INFO', 'id': 'LNREADER-CHEERIO-VER', 'summary': 'Check Hermes-compatible cheerio version from repo package.json.'},
)


def _parse_ver_tuple(raw: str) -> tuple[int, ...] | None:
    nums = re.findall(r'\d+', raw)
    return tuple(int(n) for n in nums[:3]) if nums else None


def _scan_extension_modules(repo_root: Path) -> list[dict[str, Any]]:
    """Collect extension modules across Keiyoushi/Yuzono (src/) and LNReader (plugins/)."""
    modules: list[dict[str, Any]] = []
    src_dir = repo_root / 'src'
    if src_dir.is_dir():
        for gradle in sorted(src_dir.rglob('build.gradle.kts')):
            mod_dir = gradle.parent
            gtxt = gradle.read_text(errors='replace')
            name_m = re.search(r'^\s*(?:extName|name)\s*=\s*"([^"]+)"', gtxt, re.M)
            theme_m = re.search(r'\btheme\s*=\s*"([^"]+)"', gtxt)
            base_urls = re.findall(r'\bbaseUrl\s*=\s*"([^"]+)"', gtxt)
            libs = re.findall(r'implementation\s*\(\s*project\s*\(\s*"([^"]+)"\s*\)\s*\)', gtxt)
            kt_files = sorted(mod_dir.rglob('*.kt'))
            supers: list[str] = []
            for kf in kt_files[:5]:
                ktxt = kf.read_text(errors='replace')[:4000]
                m_sup = re.search(r'class\s+\w+\s*(?:\([^)]*\))?\s*:\s*([A-Za-z0-9_]+)', ktxt)
                if m_sup:
                    supers.append(m_sup.group(1))
            modules.append({
                'ecosystem': 'yuzono' if 'yuzono' in gtxt or 'animeextension' in str(kt_files[:1]) else 'keiyoushi',
                'path': str(mod_dir.relative_to(repo_root)),
                'name': name_m.group(1) if name_m else mod_dir.name,
                'theme': theme_m.group(1) if theme_m else None,
                'base_urls': base_urls,
                'shared_libs': libs,
                'superclasses': sorted(set(supers)),
                'package': f"{mod_dir.parent.name}.{mod_dir.name}",
            })

    plugins_dir = repo_root / 'plugins'
    if plugins_dir.is_dir():
        for ts in sorted(plugins_dir.rglob('*.ts')):
            ttxt = ts.read_text(errors='replace')[:4000]
            id_m = re.search(r"\bid\s*[:=]\s*['\"]([^'\"]+)['\"]", ttxt)
            name_m = re.search(r"\bname\s*[:=]\s*['\"]([^'\"]+)['\"]", ttxt)
            site_m = re.search(r"\bsite\s*[:=]\s*['\"]([^'\"]+)['\"]", ttxt)
            modules.append({
                'ecosystem': 'lnreader',
                'path': str(ts.relative_to(repo_root)),
                'name': name_m.group(1) if name_m else (id_m.group(1) if id_m else ts.stem),
                'theme': 'multisrc' if 'multisrc' in str(ts) else None,
                'base_urls': [site_m.group(1)] if site_m else [],
                'shared_libs': re.findall(r"from\s+['\"](@libs/[^'\"]+)['\"]", ttxt),
                'superclasses': [],
                'package': id_m.group(1) if id_m else ts.stem,
            })
    return modules


def search_existing_extensions(repo_root: Path | str, query_or_domain: str) -> dict[str, Any]:
    """Search repository for existing extensions, multisrc themes, shared libraries, and family trees (0003/0006/0098)."""
    root = Path(repo_root).resolve()
    if not root.exists():
        return {'status': 'FAIL', 'error': f'path does not exist: {root}', 'matches': []}

    q = query_or_domain.strip().lower()
    q_host = (urlsplit(q).hostname or q).lower().removeprefix('www.') if ('://' in q or '.' in q) else q
    if not q:
        return {'status': 'FAIL', 'error': 'query_or_domain must not be empty', 'matches': []}

    modules = _scan_extension_modules(root)
    matches: list[dict[str, Any]] = []
    themes: dict[str, list[str]] = {}
    lib_users: dict[str, list[str]] = {}

    for m in modules:
        if m['theme']:
            themes.setdefault(m['theme'], []).append(m['path'])
        for sup in m['superclasses']:
            if sup not in {'KeiSource', 'AniSource', 'AnimeHttpSource', 'HttpSource', 'ParsedHttpSource'}:
                themes.setdefault(sup, []).append(m['path'])
        for lib in m['shared_libs']:
            lib_users.setdefault(lib, []).append(m['path'])

        hosts = [(urlsplit(u).hostname or '').lower().removeprefix('www.') for u in m['base_urls']]
        hit_reason: list[str] = []
        if q_host and any(q_host == h or q_host in h for h in hosts if h):
            hit_reason.append('domain_match')
        if q in m['name'].lower() or q in m['path'].lower():
            hit_reason.append('name_or_path_match')
        if m['theme'] and q in m['theme'].lower():
            hit_reason.append('theme_match')
        if hit_reason:
            matches.append({**m, 'match_reasons': hit_reason})

    multisrc_dir = root / 'multisrc'
    if multisrc_dir.is_dir():
        for d in sorted(multisrc_dir.glob('src/main/java/**/multisrc/*')):
            if d.is_dir():
                themes.setdefault(d.name, []).append(str(d.relative_to(root)))

    if matches:
        recommendation = 'reuse_or_update_existing'
    elif q in themes:
        recommendation = f'reuse_multisrc_theme:{q}'
    else:
        recommendation = 'create_new_or_check_multisrc_dna'

    return {
        'status': 'PASS',
        'query': query_or_domain,
        'scanned_modules': len(modules),
        'matches': matches,
        'multisrc_themes': {k: sorted(set(v)) for k, v in sorted(themes.items())},
        'shared_libraries': {k: sorted(set(v)) for k, v in sorted(lib_users.items())},
        'recommendation': recommendation,
    }


def detect_package_and_namespace_conflicts(repo_root: Path | str) -> dict[str, Any]:
    """Detect collisions across package names, sourceIds, and plugin IDs in a repository (0062/0070)."""
    root = Path(repo_root).resolve()
    if not root.exists():
        return {'status': 'FAIL', 'error': f'path does not exist: {root}', 'conflicts': []}

    modules = _scan_extension_modules(root)
    pkg_map: dict[str, list[str]] = {}
    id_map: dict[int, list[str]] = {}
    conflicts: list[dict[str, Any]] = []

    for m in modules:
        pkg_key = f"{m['ecosystem']}:{m['package'].lower()}"
        pkg_map.setdefault(pkg_key, []).append(m['path'])
        if m['ecosystem'] in {'keiyoushi', 'yuzono'}:
            insp = inspect_project(root / m['path'])
            for s in insp.get('sources', []):
                sid = s.get('sourceId')
                if sid is not None:
                    id_map.setdefault(int(sid), []).append(f"{m['path']}:{s.get('lang')}")

    for pkg, paths in pkg_map.items():
        if len(paths) > 1:
            conflicts.append({'kind': 'package_or_plugin_id_collision', 'key': pkg, 'paths': paths})
    for sid, paths in id_map.items():
        if len(paths) > 1:
            conflicts.append({'kind': 'source_id_collision', 'sourceId': sid, 'paths': paths})

    return {
        'status': 'FAIL' if conflicts else 'PASS',
        'scanned_modules': len(modules),
        'conflicts_count': len(conflicts),
        'conflicts': conflicts,
    }


def audit_dependency_vulnerabilities(
    repo_root: Path | str,
    advisories: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Check Gradle version catalogs and package.json dependencies against advisories without forced upgrades (0073)."""
    root = Path(repo_root).resolve()
    if not root.exists():
        return {'status': 'FAIL', 'error': f'path does not exist: {root}', 'findings': []}

    adv_list = list(advisories) if advisories is not None else list(_BUILTIN_ADVISORIES)
    findings: list[dict[str, Any]] = []
    scanned_files: list[str] = []

    toml = root / 'gradle/libs.versions.toml'
    if toml.is_file():
        scanned_files.append('gradle/libs.versions.toml')
        txt = toml.read_text(errors='replace')
        for adv in adv_list:
            pkg = str(adv.get('package', '')).lower()
            short = pkg.split(':')[-1]
            for m in re.finditer(rf'(?i)\b{re.escape(short)}\s*=\s*["\']([0-9][^"\']+)["\']', txt):
                ver = _parse_ver_tuple(m.group(1))
                below = tuple(adv.get('below', ()))
                if ver and below and ver < below:
                    findings.append({
                        'file': 'gradle/libs.versions.toml',
                        'package': adv['package'],
                        'found_version': m.group(1),
                        'advisory': adv['id'],
                        'severity': adv.get('severity', 'WARN'),
                        'note': 'Verify upstream extension-lib compatibility before upgrading.',
                    })

    pkg_json = root / 'package.json'
    if pkg_json.is_file():
        scanned_files.append('package.json')
        try:
            pdata = json.loads(pkg_json.read_text(errors='replace'))
            deps = {**(pdata.get('dependencies') or {}), **(pdata.get('devDependencies') or {})}
            for adv in adv_list:
                pkg = str(adv.get('package', ''))
                if pkg in deps:
                    ver = _parse_ver_tuple(str(deps[pkg]))
                    below = tuple(adv.get('below', ()))
                    if ver and below and ver < below:
                        findings.append({
                            'file': 'package.json',
                            'package': pkg,
                            'found_version': str(deps[pkg]),
                            'advisory': adv['id'],
                            'severity': adv.get('severity', 'WARN'),
                            'note': adv.get('summary', ''),
                        })
        except json.JSONDecodeError:
            findings.append({'file': 'package.json', 'severity': 'FAIL', 'advisory': 'INVALID_JSON'})

    return {
        'status': 'FAIL' if any(f.get('severity') == 'FAIL' for f in findings) else 'PASS',
        'scanned_files': scanned_files,
        'findings_count': len(findings),
        'findings': findings,
    }


def check_build_reproducibility(
    artifact_a: Path | str,
    artifact_b: Path | str,
    env_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare two APK/ZIP artifacts globally and entry-by-entry to distinguish metadata drift from code changes (0071)."""
    pa, pb = Path(artifact_a), Path(artifact_b)
    if not pa.is_file() or not pb.is_file():
        return {'status': 'FAIL', 'error': 'both artifacts must exist on disk'}

    hash_a = hashlib.sha256(pa.read_bytes()).hexdigest()
    hash_b = hashlib.sha256(pb.read_bytes()).hexdigest()
    exact_match = (hash_a == hash_b)

    def _entry_hashes(p: Path) -> dict[str, str]:
        with zipfile.ZipFile(p) as zf:
            return {n: hashlib.sha256(zf.read(n)).hexdigest() for n in sorted(zf.namelist())}

    entries_a = _entry_hashes(pa)
    entries_b = _entry_hashes(pb)
    all_keys = sorted(set(entries_a) | set(entries_b))
    diff_entries = [k for k in all_keys if entries_a.get(k) != entries_b.get(k)]
    code_diff = [k for k in diff_entries if k.endswith('.dex') or k == 'AndroidManifest.xml' or k.endswith('.so')]
    sig_only = bool(diff_entries) and all(k.startswith('META-INF/') for k in diff_entries)

    return {
        'status': 'PASS' if (exact_match or not code_diff) else 'INCONCLUSIVE',
        'exact_sha256_match': exact_match,
        'sha256_a': hash_a,
        'sha256_b': hash_b,
        'differing_entries_count': len(diff_entries),
        'differing_entries_sample': diff_entries[:20],
        'code_or_manifest_differs': bool(code_diff),
        'signature_metadata_diff_only': sig_only,
        'env_meta': env_meta or {},
    }


def analyze_shared_library_impact(repo_root: Path | str, changed_target: str) -> dict[str, Any]:
    """Compute blast radius of extensions impacted by changing a shared library or multisrc theme (0086)."""
    root = Path(repo_root).resolve()
    if not root.exists():
        return {'status': 'FAIL', 'error': f'path does not exist: {root}', 'affected_extensions': []}

    needle = changed_target.strip().lower().strip('/')
    modules = _scan_extension_modules(root)
    affected: list[dict[str, Any]] = []
    for m in modules:
        refs = [x.lower() for x in (m['shared_libs'] + m['superclasses'] + ([m['theme']] if m['theme'] else []))]
        if any(needle in r or r in needle for r in refs):
            affected.append({'path': m['path'], 'name': m['name'], 'ecosystem': m['ecosystem']})

    return {
        'status': 'PASS',
        'changed_target': changed_target,
        'scanned_modules': len(modules),
        'blast_radius_count': len(affected),
        'affected_extensions': affected,
    }


def compare_fork_and_upstream(local_info: dict[str, Any], upstream_info: dict[str, Any]) -> dict[str, Any]:
    """Compare local fork contract/version against upstream before adapting changes (0088)."""
    issues: list[str] = []
    local_eco = local_info.get('ecosystem')
    up_eco = upstream_info.get('ecosystem')
    if local_eco and up_eco and local_eco != up_eco:
        issues.append(f'ecosystem_mismatch:{local_eco}!={up_eco}')

    local_arch = local_info.get('architecture', '')
    up_arch = upstream_info.get('architecture', '')
    requires_adaptation = bool(local_arch and up_arch and local_arch != up_arch)
    local_lib = str(local_info.get('libVersion', ''))
    up_lib = str(upstream_info.get('libVersion', ''))
    if local_lib and up_lib and local_lib != up_lib:
        issues.append(f'libVersion_diff:local={local_lib},upstream={up_lib}')

    direct_copy_safe = (not issues) and (not requires_adaptation)
    return {
        'status': 'PASS' if direct_copy_safe else 'INCONCLUSIVE',
        'direct_copy_safe': direct_copy_safe,
        'requires_adaptation': requires_adaptation,
        'differences': issues,
        'guidance': 'Adapt principles to local architecture without copying incompatible APIs.' if not direct_copy_safe else 'Contracts align.',
    }


def save_and_resume_recovery_checkpoint(
    checkpoint_path: Path | str,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Atomically save or resume task technical checkpoints without clobbering uncommitted local work (0101)."""
    cp = Path(checkpoint_path)
    if state is not None:
        safe_payload = json.loads(sanitize_text(json.dumps(state, ensure_ascii=False), redact_home=True))
        atomic_write_text(cp, json.dumps(safe_payload, indent=2, ensure_ascii=False) + '\n')
        return {'status': 'PASS', 'action': 'saved', 'path': str(cp), 'state': safe_payload}
    if not cp.is_file():
        return {'status': 'NOT_RUN', 'action': 'resume', 'error': f'checkpoint missing: {cp}', 'state': None}
    try:
        loaded = json.loads(cp.read_text(encoding='utf-8'))
        return {'status': 'PASS', 'action': 'resumed', 'path': str(cp), 'state': loaded}
    except (OSError, json.JSONDecodeError) as exc:
        return {'status': 'FAIL', 'action': 'resume', 'error': f'corrupted checkpoint: {exc}', 'state': None}


def evaluate_compliance_and_license(
    repo_root: Path | str,
    *,
    target_url: str | None = None,
    allows_bypass: bool = False,
) -> dict[str, Any]:
    """Verify repository license, contribution guidelines, and legal/network URL compliance (0109)."""
    root = Path(repo_root).resolve()
    violations: list[str] = []
    license_file = next((root / name for name in ('LICENSE', 'LICENSE.md', 'COPYING') if (root / name).is_file()), None)
    license_id = None
    if not license_file:
        violations.append('missing_license_file')
    else:
        ltxt = license_file.read_text(errors='replace')[:1000]
        up_ltxt = ltxt.upper()
        if 'AGPL' in up_ltxt or 'AFFERO GENERAL PUBLIC LICENSE' in up_ltxt:
            license_id = 'AGPL-3.0'
        elif 'APACHE' in up_ltxt:
            license_id = 'Apache-2.0'
        elif 'MIT' in up_ltxt:
            license_id = 'MIT'
        else:
            license_id = 'CUSTOM'

    if target_url:
        ok, msg = is_safe_public_url(target_url)
        if not ok:
            violations.append(f'unsafe_target_url:{msg}')
    if allows_bypass:
        violations.append('drm_or_auth_bypass_prohibited')

    return {
        'status': 'FAIL' if violations else 'PASS',
        'license_id': license_id,
        'has_contributing': (root / 'CONTRIBUTING.md').is_file(),
        'violations': violations,
    }
